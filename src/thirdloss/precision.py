"""Independent, high-precision reference for the first real adapter calibration probe."""

import hashlib
import time
from unittest.mock import patch

import torch

from .models import build_model, logits_of, token_loss, trainable_digest
from .objectives import two_window_third_gradient
from .penalties import random_signs
from .records import storage_root, time_now, write_json
from .windows import TrainingWindows, generator, probe_rows


def dtype_attention(module,query,key,value,attention_mask,scaling,dropout=0.0,**kwargs):
    """The upstream eager formula with softmax retaining the study tensor's precision.

    https://github.com/huggingface/transformers/blob/main/src/transformers/models/gpt_neox/modeling_gpt_neox.py
    """
    scores = (query @ key.transpose(-2,-1))*scaling
    if attention_mask is not None:
        scores = scores+attention_mask
    weights = torch.nn.functional.dropout(scores.softmax(-1),p=dropout,training=module.training)
    return (weights @ value).transpose(1,2).contiguous(),weights


def reference_gradient(project,device):
    """Generate the production CUDA signs and promote the same pretrained weights to FP64."""
    from safetensors.torch import save_file
    from transformers.models.gpt_neox import modeling_gpt_neox as neox
    storage=storage_root(project)
    model=build_model("abstracts",0,device,storage).eval()
    initial=trainable_digest(model)
    parameters=tuple(p for p in model.parameters() if p.requires_grad)
    # Generate signs with the *same* device generator as the observed pilot, also for CPU AD.
    rng=generator(torch.device("cuda"),6247,0,827)
    shapes=tuple(torch.empty_like(p,device="cuda") for p in parameters)
    signs=[tuple(g.to(device=device,dtype=torch.float64) for g in random_signs(shapes,rng)) for _ in range(2)]
    del shapes,parameters
    model.double()
    parameters=tuple(p for p in model.parameters() if p.requires_grad)
    x,y=TrainingWindows(storage/"data"/"abstracts"/"train.bin",6247,8).get(0,device)
    rows=probe_rows(6247,0,8)
    x,y=x[rows],y[rows]
    # RoPE values are frozen position constants and follow the checkpoint's upstream formula.
    with patch.object(neox,"eager_attention_forward",dtype_attention):
        with torch.no_grad():
            logits=logits_of(model,x)
            nll=token_loss(logits,y).item()
            logit_gap=(logits-torch.cat([logits_of(model,t[None,:]) for t in x])).abs().max().item()
            del logits
        started=time.perf_counter()
        value,gradient=two_window_third_gradient(model,parameters,x,y,*signs)
        flat=torch.cat([p.detach().flatten().cpu() for p in gradient])
    elapsed=time.perf_counter()-started
    directory=storage/"diagnostics"
    directory.mkdir(parents=True,exist_ok=True)
    save_file({"gradient":flat},str(directory/f"pythia-reference-{device.type}.safetensors"))
    h=hashlib.sha256()
    for sign in (*signs[0],*signs[1]): h.update(sign.float().cpu().contiguous().numpy().tobytes())
    result={"timestamp":time_now(),"device":str(device),"dtype":"float64", "initial_trainable_sha256":initial,
            "probes_sha256":h.hexdigest(),"two_window_cross_entropy":nll,
            "max_logit_abs_difference":logit_gap,"penalty":value.item(),"gradient_norm":flat.norm().item(),
            "finite":bool(flat.isfinite().all()),"probe_seconds":elapsed}
    write_json(project/"results"/"verification"/f"pythia-fp64-{device.type}.json",result)
    print(result,flush=True)
    return result
