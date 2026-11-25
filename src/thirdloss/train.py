"""Time, train, checkpoint and export one fully specified arm of the registered experiment."""

import math
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

import torch
from filelock import FileLock

from .evaluation import sample_outputs, score, unigram_distribution
from .models import build_model, export_weights
from .objectives import add_penalty, calibrate, ce_backward
from .records import (BATCHES, CONTEXT, HORIZONS, RATIOS, Recorder, json_lines, read_json,
                      run_name, sha256, time_now, write_json)
from .windows import TrainingWindows, gate


def scientific_config(stage, method, phase, seed, ratio):
    """Validate identities so pilots, confirmations and smoke tests cannot be mixed in analysis."""
    if stage not in HORIZONS or phase not in {"pilot", "confirm", "control", "smoke"}:
        raise ValueError("Unknown study stage or phase")
    if phase == "confirm" and (seed not in range(1,9) or method not in {"ce","trace","third"}):
        raise ValueError("Confirmation uses seeds 1–8 and the three primary arms")
    if phase in {"control", "pilot"} and seed != 0:
        raise ValueError("Development and control runs use the reserved pilot seed")
    if method in {"ce","initial","unigram"}:
        ratio = 0.0
    elif ratio not in RATIOS:
        raise ValueError(f"Unregistered penalty strength {ratio}")
    budget = HORIZONS[stage] if phase == "confirm" else HORIZONS[stage]//8
    if phase == "smoke":
        budget = CONTEXT * BATCHES[stage] * 8
    if method in {"unigram","initial"}:
        budget = 0
    return {"id":run_name(stage, method, phase, seed, ratio), "stage":stage, "method":method,
            "phase":phase, "seed":seed, "ratio":ratio, "token_budget":budget,
            "batch_windows":BATCHES[stage], "context":CONTEXT}


def learning_rate(stage, step, steps):
    peak = 3e-4 if stage == "stories" else 1e-4
    warm = max(1, round(0.05*steps))
    if step < warm:
        return peak * (step+1)/warm
    progress = (step-warm+1) / max(1, steps-warm)
    return peak * (0.1+0.9*0.5*(1+math.cos(math.pi*progress)))


def chosen_coefficients(project, storage, config, device, microbatch):
    method, ratio, stage = (config[k] for k in ("method","ratio","stage"))
    if method in {"ce","initial","unigram"}:
        return {}
    if method == "combined":
        selected = read_json(project/"results"/"selection"/f"{stage}.json")["ratios"]
        kinds = {"trace":selected["trace"], "third":selected["third"]}
    else:
        kinds = {"third" if method == "sham" else method: ratio}
    return {kind: scale*calibrate(project,storage,stage,kind,device,microbatch) for kind,scale in kinds.items()}


def save_state(path, model, optimizer, step, elapsed, config):
    """Atomically persist optimizer, trainable weights, all stochastic state and next data step."""
    state = {"weights":{n:p.detach() for n,p in model.named_parameters() if p.requires_grad},
             "optimizer":optimizer.state_dict(), "next_step":step, "train_seconds":elapsed,
             "config":config, "cpu_rng":torch.get_rng_state(),
             "cuda_rng":torch.cuda.get_rng_state() if next(model.parameters()).is_cuda else None}
    temp = path.with_suffix(".partial")
    torch.save(state, temp)
    os.replace(temp,path)


def restore_state(path, model, optimizer, config, recorder, device):
    """Recover the last committed checkpoint and ignore telemetry from interrupted later steps."""
    if not path.exists():
        return 0, 0.0
    state = torch.load(path, map_location="cpu", weights_only=True)
    if state["config"] != config:
        raise ValueError("Resume configuration differs from saved scientific settings")
    model.load_state_dict(state["weights"], strict=False)
    optimizer.load_state_dict(state["optimizer"])
    torch.set_rng_state(state["cpu_rng"])
    if state["cuda_rng"] is not None:
        torch.cuda.set_rng_state(state["cuda_rng"], device)
    step = state["next_step"]
    path = recorder.directory/"events.jsonl"
    if path.exists():
        import json
        rows = [r for r in json_lines(path) if r.get("step", 0) <= step]
        temp = path.with_suffix(".partial")
        temp.write_text("".join(json.dumps(r)+"\n" for r in rows), encoding="utf-8")
        temp.replace(path)
    return step, state["train_seconds"]


def run_one(project, storage, stage, method, phase, seed, ratio, device, microbatch=None):
    config = scientific_config(stage,method,phase,seed,ratio)
    microbatch = microbatch or (32 if stage == "stories" else 2)
    if microbatch < 1:
        raise ValueError("A physical batch must contain at least one window")
    recorder = Recorder(project, config["id"])
    locks = storage / "locks"
    locks.mkdir(parents=True, exist_ok=True)
    with FileLock(str(locks/(config["id"]+".lock"))):
        try:
            return _run(project, storage, config, recorder, device, microbatch)
        except Exception as exc:
            write_json(recorder.directory/"failure.json", {"timestamp":time_now(), "error":repr(exc)})
            raise


def _run(project, storage, config, recorder, device, microbatch):
    stage, method, seed, budget = (config[k] for k in ("stage","method","seed","token_budget"))
    data = storage/"data"/stage
    manifest = read_json(data/"manifest.json")
    config["data_manifest_sha256"] = sha256(data/"manifest.json")
    config["microbatch"] = microbatch
    config["coefficients"] = chosen_coefficients(project,storage,config,device,microbatch)
    output = recorder.directory
    if (output/"config.json").exists() and read_json(output/"config.json") != config:
        raise ValueError(f"Existing run configuration conflicts with {config['id']}")
    write_json(output/"config.json",config)
    summary_path = output/"summary.json"
    if summary_path.exists():
        return read_json(summary_path)
    ckpt = storage/"checkpoints"/config["id"]
    ckpt.mkdir(parents=True,exist_ok=True)
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
    model = None if method == "unigram" else build_model(stage,seed,device,storage)
    parameters = tuple(p for p in model.parameters() if p.requires_grad) if model is not None else ()
    summary = {**config, "device":str(device), "torch":str(torch.__version__), "platform":platform.platform(),
               "gpu":torch.cuda.get_device_name(device) if device.type=="cuda" else None,
               "git_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=project,text=True).strip(),
               "trainable_parameters":sum(p.numel() for p in parameters)}
    batch = BATCHES[stage]
    steps = budget//(batch*CONTEXT)
    elapsed = 0.0
    if budget:
        windows = TrainingWindows(data/"train.bin",seed,batch)
        groups = [{"params":[p for p in parameters if p.ndim>1],"weight_decay":0.1},
                  {"params":[p for p in parameters if p.ndim<=1],"weight_decay":0.0}]
        optimizer = torch.optim.AdamW(groups,lr=1e-4,betas=(0.9,0.95),fused=(device.type=="cuda"))
        start,elapsed = restore_state(ckpt/"latest.pt",model,optimizer,config,recorder,device)
        # Match elapsed-time comparisons with periodic fixed development windows in every arm.
        interval = min(128,max(1,steps//16))
        for step in range(start,steps):
            model.train()
            tic = time.perf_counter()
            inputs,targets = windows.get(step,device)
            optimizer.zero_grad(set_to_none=True)
            base,accuracy = ce_backward(model,inputs,targets,microbatch)
            active = bool(config["coefficients"]) and gate(seed,step)
            terms = add_penalty(model,parameters,inputs,targets,config["coefficients"],method,seed,step) if active else {}
            norm = torch.nn.utils.clip_grad_norm_(parameters,1.0,error_if_nonfinite=True)
            lr = learning_rate(stage,step,steps)
            for group in optimizer.param_groups:
                group["lr"] = lr
            optimizer.step()
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            elapsed += time.perf_counter()-tic
            done = step+1
            if done % 8 == 0 or active or done == 1 or done % interval == 0 or done == steps:
                row = {"step":done, "tokens":done*batch*CONTEXT, "train_seconds":elapsed, "loss":base.item(),
                       "accuracy":accuracy.item(), "lr":lr, "gradient_norm":norm.item(),"derivatives":terms}
                if terms:
                    row["penalty"] = sum(8*t["lambda"]*t["estimate"] for t in terms.values())
                if done%interval == 0 or done==steps:
                    metrics = score(model,data/"dev.bin",device,microbatch,limit_windows=64)
                    row.update(dev_nll=metrics["nll"],dev_accuracy=metrics["accuracy"])
                recorder.emit(row)
            if done%interval == 0 or done==steps:
                save_state(ckpt/"latest.pt",model,optimizer,done,elapsed,config)
        del optimizer
    dist = unigram_distribution(data/"train.bin",4096 if stage=="stories" else 50304) if method=="unigram" else None
    validation = score(model,data/"dev.bin",device,microbatch,unigram=dist)
    # A rerun after final-checkpoint interruption writes each documented sample exactly once.
    sample_path = output/"samples.jsonl"
    if sample_path.exists():
        sample_path.unlink()
    sample_outputs(model,data,manifest,device,recorder,unigram=dist)
    if budget:
        weights = export_weights(model,ckpt/"export")
        shutil.copy2(data/"tokenizer.json", ckpt/"export"/"tokenizer.json")
        summary.update(weights_sha256=sha256(weights),weights_name=weights.name)
        summary["matched_dev_nll"] = next(e["dev_nll"] for e in reversed(json_lines(output/"events.jsonl"))
                                          if "dev_nll" in e)
    summary.update(tokens=budget,steps=steps,train_seconds=elapsed,tokens_per_sec=budget/elapsed if elapsed else 0,
                   peak_vram_mb=torch.cuda.max_memory_allocated(device)/2**20 if device.type=="cuda" else 0,
                   dev_nll=validation["nll"],dev_accuracy=validation["accuracy"],dev_tokens=validation["tokens"],
                   finished_at=time_now(),status="complete")
    write_json(summary_path,summary)
    (output/"failure.json").unlink(missing_ok=True)
    print(f"Completed {config['id']}  development NLL {summary['dev_nll']:.6f}",flush=True)
    return summary
