"""Both study models use eager, differentiable attention on genuine next-token inputs.

The stories decoder uses RMSNorm, rotary attention and a gated SiLU MLP as in
https://arxiv.org/abs/2302.13971. The adapter stage uses the public Pythia weights
and PEFT LoRA (https://arxiv.org/abs/2106.09685).
"""

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

PYTHIA = "EleutherAI/pythia-410m"
REVISION = "9879c9b5f8bea9051dcb0e68dff21493d67e9d4f"


@dataclass(frozen=True)
class StoryConfig:
    vocab_size: int = 4096
    width: int = 192
    heads: int = 4
    layers: int = 4
    hidden: int = 512
    context: int = 128


class RMSNorm(nn.Module):
    """RMS-normalize the final dimension using differentiable elementary operations."""

    def __init__(self, width):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(width))

    def forward(self, x):
        return self.weight * x * torch.rsqrt(x.square().mean(dim=-1, keepdim=True) + 1e-5)


class Block(nn.Module):
    """Pre-normalized causal self-attention and gated feedforward residual branches."""

    def __init__(self, c):
        super().__init__()
        self.heads = c.heads
        self.head_width = c.width // c.heads
        if c.width % c.heads or self.head_width % 2:
            raise ValueError("Rotary attention requires an even head width")
        self.attn_norm, self.mlp_norm = RMSNorm(c.width), RMSNorm(c.width)
        self.qkv = nn.Linear(c.width, 3 * c.width, bias=False)
        self.out = nn.Linear(c.width, c.width, bias=False)
        self.gate_up = nn.Linear(c.width, 2 * c.hidden, bias=False)
        self.down = nn.Linear(c.hidden, c.width, bias=False)
        positions = torch.arange(c.context)[:, None]
        angles = positions / 10000 ** (torch.arange(0, self.head_width, 2) / self.head_width)
        self.register_buffer("cos", angles.cos(), persistent=False)
        self.register_buffer("sin", angles.sin(), persistent=False)
        self.register_buffer("allowed", torch.ones(c.context, c.context, dtype=torch.bool).tril(),
                             persistent=False)

    def rotate(self, x):
        """Rotate pairs of coordinates by a deterministic position-dependent phase."""
        n = x.shape[-2]
        a, b = x[..., ::2], x[..., 1::2]
        return torch.stack((a*self.cos[:n] - b*self.sin[:n], a*self.sin[:n] + b*self.cos[:n]),
                           dim=-1).flatten(-2)

    def forward(self, x):
        batch, length, width = x.shape
        q, k, v = self.qkv(self.attn_norm(x)).reshape(
            batch, length, 3, self.heads, self.head_width).permute(2, 0, 3, 1, 4)
        scores = self.rotate(q) @ self.rotate(k).transpose(-1, -2) * self.head_width**-0.5
        weights = scores.masked_fill(~self.allowed[:length, :length], float("-inf")).softmax(-1)
        attended = (weights @ v).transpose(1, 2).reshape(batch, length, width)
        x = x + self.out(attended)
        gate, up = self.gate_up(self.mlp_norm(x)).chunk(2, dim=-1)
        return x + self.down((gate * gate.sigmoid()) * up)


class StoryTransformer(nn.Module):
    """Small causal decoder with one shared input/output embedding parameter."""

    def __init__(self, config=None):
        super().__init__()
        self.config = config or StoryConfig()
        c = self.config
        self.embedding = nn.Embedding(c.vocab_size, c.width)
        self.blocks = nn.Sequential(*(Block(c) for _ in range(c.layers)))
        self.norm = RMSNorm(c.width)
        for layer in self.modules():
            if isinstance(layer, (nn.Linear, nn.Embedding)):
                nn.init.normal_(layer.weight, std=0.02)

    def forward(self, ids):
        return F.linear(self.norm(self.blocks(self.embedding(ids))), self.embedding.weight)


class PrimitiveLayerNorm(nn.Module):
    """Evaluate the pretrained LayerNorm formula with primitives supporting fourth derivatives."""

    def __init__(self, original):
        super().__init__()
        self.weight, self.bias, self.eps = original.weight, original.bias, original.eps

    def forward(self, x):
        centered = x - x.mean(-1, keepdim=True)
        return centered * torch.rsqrt(centered.square().mean(-1, keepdim=True) + self.eps) * self.weight + self.bias


def build_model(stage, seed, device, storage):
    """Build the same initialization across paired arms, with frozen Pythia backbone weights."""
    torch.manual_seed(seed)
    if stage == "stories":
        return StoryTransformer().to(device)
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM

    base = AutoModelForCausalLM.from_pretrained(PYTHIA, revision=REVISION, dtype=torch.float32,
                                              attn_implementation="eager", cache_dir=str(storage / "hub"))
    base.config.use_cache = False
    for parent in list(base.modules()):
        for name, child in list(parent.named_children()):
            if isinstance(child, nn.LayerNorm):
                setattr(parent, name, PrimitiveLayerNorm(child))
    lora = LoraConfig(task_type=TaskType.CAUSAL_LM, r=8, lora_alpha=16,
                      target_modules=["query_key_value"], lora_dropout=0.0, bias="none")
    return get_peft_model(base, lora).to(device)


def logits_of(model, ids):
    """Normalize native stories tensors and Transformers CausalLMOutput to [B,T,V]."""
    out = model(ids)
    return out if isinstance(out, torch.Tensor) else out.logits


def dtype_attention(module,query,key,value,attention_mask,scaling,dropout=0.0,**kwargs):
    """The upstream GPT-NeoX eager attention formula, retaining FP64 at softmax.

    https://github.com/huggingface/transformers/blob/main/src/transformers/models/gpt_neox/modeling_gpt_neox.py
    """
    scores = (query @ key.transpose(-2,-1))*scaling
    if attention_mask is not None:
        scores = scores+attention_mask
    weights = F.dropout(scores.softmax(-1),p=dropout,training=module.training)
    return (weights @ value).transpose(1,2).contiguous(),weights


def widen_pythia(model):
    """Use the registered eager mask with dtype-preserving attention on this replica only."""
    from transformers import AttentionInterface, AttentionMaskInterface
    from transformers.masking_utils import eager_mask
    # Register both hooks so attention stays causal. https://huggingface.co/docs/transformers/attention_interface
    name = "thirdloss_eager_fp64"
    AttentionInterface.register(name,dtype_attention)
    AttentionMaskInterface.register(name,eager_mask)
    model.get_base_model().set_attn_implementation(name)
    return model.double().eval()


def trainable_digest(model):
    """Fingerprint each named trainable tensor at initialization to audit seed pairing."""
    digest = hashlib.sha256()
    for name,p in model.named_parameters():
        if p.requires_grad:
            digest.update(name.encode("utf-8"))
            digest.update(p.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def token_nll(logits, targets):
    """Elementwise stable next-token NLL, exposing all derivative orders in the log partition."""
    observed = logits.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    return torch.logsumexp(logits, -1) - observed


def token_loss(logits, targets):
    return token_nll(logits, targets).mean()


def export_weights(model, path: Path):
    """Write a portable safetensors snapshot of exactly the fitted coordinates."""
    import json
    from safetensors.torch import save_file

    path.mkdir(parents=True, exist_ok=True)
    if isinstance(model, StoryTransformer):
        save_file({n: p.detach().cpu().contiguous() for n, p in model.named_parameters()},
                  str(path / "model.safetensors"))
        (path / "config.json").write_text(json.dumps(asdict(model.config), indent=2), encoding="utf-8")
        return path / "model.safetensors"
    model.save_pretrained(path, safe_serialization=True)
    return path / "adapter_model.safetensors"
