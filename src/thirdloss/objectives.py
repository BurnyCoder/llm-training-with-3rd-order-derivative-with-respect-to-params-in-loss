"""Ordinary CE, probe gradients and fair train-only calibration on identical initial weights."""

import statistics
import torch

from .models import build_model, logits_of, token_loss, token_nll
from .penalties import estimate, partials, random_signs
from .records import BATCHES, read_json, sha256, write_json
from .windows import TrainingWindows, generator, probe_rows


def ce_backward(model, inputs, targets, microbatch):
    """Accumulate the global token-mean CE despite physical microbatching."""
    total_loss = torch.zeros((), device=inputs.device)
    hits = torch.zeros((), device=inputs.device, dtype=torch.long)
    for start in range(0, len(inputs), microbatch):
        x, y = inputs[start:start+microbatch], targets[start:start+microbatch]
        logits = logits_of(model, x)
        contribution = token_nll(logits, y).sum() / targets.numel()
        contribution.backward()
        total_loss += contribution.detach()
        hits += (logits.detach().argmax(-1) == y).sum()
    return total_loss, hits / targets.numel()


def vector_norm(values):
    return torch.linalg.vector_norm(torch.stack([torch.linalg.vector_norm(x.detach()) for x in values]))


def probe_gradient(model, parameters, inputs, targets, kind, seed, step):
    """Differentiate the sampled penalty, including the fourth-order contraction."""
    rng = generator(inputs.device, seed, step, 827)
    rows = probe_rows(seed, step, len(inputs))
    base = token_loss(logits_of(model, inputs[rows]), targets[rows])
    value = estimate(base, parameters, kind, generator=rng)
    return value.detach(), partials(value, parameters, create_graph=False)


def calibrate(project, storage, stage, kind, device, microbatch):
    """Fix unit-strength scales for all seeds using only training data at pilot initialization."""
    path = project / "results" / "calibration" / f"{stage}-{kind}.json"
    data = storage / "data" / stage
    fingerprint = sha256(data/"manifest.json")
    if path.exists():
        existing = read_json(path)
        if existing["data_manifest_sha256"] != fingerprint:
            raise ValueError(f"Calibration data changed for {stage}")
        return existing["unit_lambda"]
    model = build_model(stage, 0, device, storage)
    parameters = tuple(p for p in model.parameters() if p.requires_grad)
    windows = TrainingWindows(data/"train.bin", 6247, BATCHES[stage])
    rows = []
    for step in range(16):
        inputs, targets = windows.get(step, device)
        model.zero_grad(set_to_none=True)
        ce_backward(model, inputs, targets, microbatch)
        ce_norm = vector_norm(p.grad for p in parameters if p.grad is not None).item()
        model.zero_grad(set_to_none=True)
        value, grads = probe_gradient(model, parameters, inputs, targets, kind, 6247, step)
        norm = vector_norm(grads).item()
        if not (0 < norm < float("inf") and 0 < ce_norm < float("inf")):
            raise FloatingPointError(f"Nonfinite or zero {kind} calibration norm at draw {step}: {norm}")
        rows.append({"draw":step, "ce_grad_norm":ce_norm, "penalty_grad_norm":norm,
                     "value":value.item(), "norm_ratio":ce_norm/norm})
        del grads
    result = statistics.median(row["norm_ratio"] for row in rows)
    write_json(path, {"stage":stage, "kind":kind, "data_manifest_sha256":fingerprint,
                      "unit_lambda":result, "draws":rows})
    return result


def add_penalty(model, parameters, inputs, targets, coefficients, method, seed, step):
    """Add the gated derivative contribution to already-accumulated CE gradients."""
    telemetry = {}
    for kind, weight in coefficients.items():
        if not weight:
            continue
        value, grads = probe_gradient(model, parameters, inputs, targets, kind, seed, step)
        raw_norm = vector_norm(grads).item()
        if method == "sham":
            signs = random_signs(parameters, generator(inputs.device, seed, step, 839))
            grads = tuple(g * sign for g, sign in zip(grads, signs, strict=True))
        with torch.no_grad():
            for param, grad in zip(parameters, grads, strict=True):
                if param.grad is None:
                    param.grad = torch.zeros_like(param)
                param.grad.add_(grad, alpha=8*weight)
        telemetry[kind] = {"estimate":value.item(), "raw_grad_norm":raw_norm, "lambda":weight}
    return telemetry
