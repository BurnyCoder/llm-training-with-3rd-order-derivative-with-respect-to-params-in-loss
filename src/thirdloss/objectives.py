"""Ordinary CE, probe gradients and fair train-only calibration on identical initial weights."""

import statistics
import time
import os
import torch

from .models import build_model, logits_of, token_loss, token_nll, trainable_digest, widen_pythia
from .penalties import estimate, inner, partials, random_signs, third_contraction
from .records import BATCHES, read_json, sha256, time_now, write_json
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
    """Preserve the ordinary reduction and widen it when finite FP32 coordinates overflow."""
    blocks = tuple(x.detach() for x in values)
    def norm(dtype=None):
        return torch.linalg.vector_norm(torch.stack([torch.linalg.vector_norm(x, dtype=dtype) for x in blocks]))
    ordinary = norm()
    return ordinary if torch.isfinite(ordinary) and ordinary != 0 else norm(torch.float64)


def two_window_third_gradient(model, parameters, inputs, targets, u, v):
    """Keep one large fourth-order graph at a time, retaining the exact joint penalty gradient.

    Write R=(r0+r1)/2 for the two equal-length windows, using the same two probes for both.
    The derivative of ||R||² with respect to *each* r_i is R. Backpropagate that cotangent
    through both live third-derivative graphs, recomputing the first window only. This is
    the gradient-caching chain rule of https://arxiv.org/abs/2101.06983 applied to D³L.
    """
    if len(inputs)!=2 or targets.shape!=inputs.shape:
        raise ValueError("Two equal-length input/target windows are required for an adapter probe")
    def contraction(index, through_fourth):
        loss = token_loss(logits_of(model, inputs[index:index+1]), targets[index:index+1])
        return third_contraction(loss, parameters, u, v, create_graph=through_fourth)
    first = contraction(0,False)
    second = contraction(1,True)
    mean = tuple((a+b.detach())*0.5 for a,b in zip(first,second,strict=True))
    del first
    grad_second = partials(inner(second,mean),parameters,create_graph=False)
    del second
    grad_first = partials(inner(contraction(0,True),mean),parameters,create_graph=False)
    return inner(mean,mean), tuple(a+b for a,b in zip(grad_first,grad_second,strict=True))


def adapter_derivative_device():
    """The registered laptop uses host FP64 for adapter probes and CUDA for ordinary training."""
    return torch.device(os.environ.get("THIRDLOSS_ADAPTER_DERIVATIVE_DEVICE","cpu"))


def derivative_replica(stage,seed,storage):
    """Keep a high-precision frozen backbone for adapter derivatives. Preserve caller RNGs."""
    if stage!="abstracts":
        return None
    devices = [torch.cuda.current_device()] if torch.cuda.is_available() else []
    with torch.random.fork_rng(devices=devices):
        return widen_pythia(build_model(stage,seed,adapter_derivative_device(),storage))


def probe_gradient(model, parameters, inputs, targets, kind, seed, step, replica=None):
    """Differentiate the sampled penalty, including the fourth-order contraction."""
    rng = generator(inputs.device, seed, step, 827)
    rows = probe_rows(seed, step, len(inputs))
    if replica is not None:
        # All arms draw the original CUDA signs. Only the arithmetic and storage of
        # the small derivative batch change. Sync every factor at the current optimizer step.
        precise = tuple(p for p in replica.parameters() if p.requires_grad)
        with torch.no_grad():
            for dest,source in zip(precise,parameters,strict=True):
                dest.copy_(source)
        device = precise[0].device
        x,y = inputs[rows].to(device),targets[rows].to(device)
        def signs():
            return tuple(s.to(device=device,dtype=torch.float64) for s in random_signs(parameters,rng))
        u = signs()
        if kind=="third":
            return two_window_third_gradient(replica,precise,x,y,u,signs())
        loss = token_loss(logits_of(replica,x),y)
        value = estimate(loss,precise,kind,u=u)
        return value.detach(),partials(value,precise,create_graph=False)
    if kind == "third" and hasattr(model, "peft_config"):
        u, v = random_signs(parameters,rng), random_signs(parameters,rng)
        return two_window_third_gradient(model,parameters,inputs[rows],targets[rows],u,v)
    base = token_loss(logits_of(model, inputs[rows]), targets[rows])
    value = estimate(base, parameters, kind, generator=rng)
    return value.detach(), partials(value, parameters, create_graph=False)


def calibrate(project, storage, stage, kind, device, microbatch):
    """Fix unit-strength scales for all seeds using only training data at pilot initialization."""
    suffix = "-fp64" if stage=="abstracts" else ""
    path = project / "results" / "calibration" / f"{stage}-{kind}{suffix}.json"
    data = storage / "data" / stage
    fingerprint = sha256(data/"manifest.json")
    if path.exists():
        existing = read_json(path)
        if existing["data_manifest_sha256"] != fingerprint:
            raise ValueError(f"Calibration data changed for {stage}")
        if suffix and existing.get("derivative_device") != str(adapter_derivative_device()):
            raise ValueError("Adapter calibration uses a different derivative device")
        return existing["unit_lambda"]
    model = build_model(stage, 0, device, storage)
    replica = derivative_replica(stage,0,storage)
    parameters = tuple(p for p in model.parameters() if p.requires_grad)
    windows = TrainingWindows(data/"train.bin", 6247, BATCHES[stage])
    # Each draw has its own data/probe address. A reboot can resume a long calibration
    # without mixing corpora, physical batching or old estimator implementations.
    work = storage/"calibration"/f"{stage}-{kind}{suffix}-draws.json"
    identity = {"data_manifest_sha256":fingerprint,"microbatch":microbatch,"version":3,
                "derivative_device":str(adapter_derivative_device() if replica is not None else device)}
    partial = read_json(work) if work.exists() else {**identity,"draws":[]}
    if any(partial.get(k)!=v for k,v in identity.items()):
        raise ValueError(f"Different settings in partial calibration for {stage} {kind}")
    rows = partial["draws"]
    if [row["draw"] for row in rows] != list(range(len(rows))) or len(rows)>16:
        raise ValueError(f"Discontinuous calibration record for {stage} {kind}")
    for step in range(len(rows),16):
        inputs, targets = windows.get(step, device)
        model.zero_grad(set_to_none=True)
        ce_backward(model, inputs, targets, microbatch)
        ce_norm = vector_norm(p.grad for p in parameters if p.grad is not None).item()
        model.zero_grad(set_to_none=True)
        if device.type == "cuda":
            torch.cuda.reset_peak_memory_stats(device)
        started = time.perf_counter()
        value, grads = probe_gradient(model, parameters, inputs, targets, kind, 6247, step,replica)
        norm = vector_norm(grads).item()
        probe_seconds = time.perf_counter()-started
        if not (0 < norm < float("inf") and 0 < ce_norm < float("inf")):
            raise FloatingPointError(f"Nonfinite or zero {kind} calibration norm at draw {step}: {norm}")
        rows.append({"draw":step, "ce_grad_norm":ce_norm, "penalty_grad_norm":norm,
                     "value":value.item(), "norm_ratio":ce_norm/norm,"probe_seconds":probe_seconds,
                     "peak_allocated_mib":torch.cuda.max_memory_allocated(device)/2**20 if device.type=="cuda" else None})
        write_json(work,partial)
        print(f"{time_now()} [calibration] {stage} {kind} draw {step+1}/16 estimate {value.item():.6g}, "
              f"CE gradient norm {ce_norm:.6g}, penalty gradient norm {norm:.6g}, {probe_seconds:.2f} s",flush=True)
        del grads
    result = statistics.median(row["norm_ratio"] for row in rows)
    write_json(path, {"stage":stage, "kind":kind, "data_manifest_sha256":fingerprint,
                      "unit_lambda":result, "draws":rows,"derivative_device":identity["derivative_device"],
                      "derivative_dtype":"float64" if replica is not None else "float32",
                      "initial_trainable_sha256":trainable_digest(model)})
    work.unlink(missing_ok=True)
    return result


def add_penalty(model, parameters, inputs, targets, coefficients, method, seed, step, replica=None):
    """Add the gated derivative contribution to already-accumulated CE gradients."""
    telemetry = {}
    for kind, weight in coefficients.items():
        if not weight:
            continue
        started = time.perf_counter()
        value, grads = probe_gradient(model, parameters, inputs, targets, kind, seed, step,replica)
        raw_norm = vector_norm(grads).item()
        if method == "sham":
            signs = random_signs(parameters, generator(inputs.device, seed, step, 839))
            grads = tuple(g * sign.to(g.device) for g, sign in zip(grads, signs, strict=True))
        with torch.no_grad():
            for param, grad in zip(parameters, grads, strict=True):
                if param.grad is None:
                    param.grad = torch.zeros_like(param)
                if replica is None:
                    param.grad.add_(grad, alpha=8*weight)
                else:
                    # Scale in FP64 before returning the registered contribution to the FP32 optimizer.
                    param.grad.add_((grad*(8*weight)).to(param))
        telemetry[kind] = {"estimate":value.item(), "raw_grad_norm":raw_norm, "lambda":weight,
                           "probe_seconds":time.perf_counter()-started}
    return telemetry
