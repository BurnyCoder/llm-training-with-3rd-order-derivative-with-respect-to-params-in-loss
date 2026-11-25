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
from .models import build_model, export_weights, trainable_digest
from .objectives import add_penalty, adapter_derivative_device, calibrate, ce_backward, derivative_replica
from .records import (BATCHES, CONTEXT, HORIZONS, RATIOS, Recorder, json_lines, read_json,
                      peak_process_mib, run_name, sha256, time_now, write_json)
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


def validation_due(stage, phase, step, interval):
    """Observe the early portion of every adapter confirmatory arm at common data positions."""
    initial_adapter = stage=="abstracts" and phase=="confirm" and step<interval
    return (step>0 and step%interval==0) or (initial_adapter and step%4==0)


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
        log = recorder.directory/"attempts.json"
        marker = recorder.directory/"failure.json"
        def remember(failure):
            """Keep the original timestamp and exception across successful or repeated retries."""
            history = read_json(log) if log.exists() else {"failures":[]}
            if failure not in history["failures"]:
                history["failures"].append(failure)
                write_json(log,history)
        if marker.exists():
            remember(read_json(marker))
            marker.unlink()
        try:
            return _run(project, storage, config, recorder, device, microbatch)
        except Exception as exc:
            failure = {"timestamp":time_now(), "error":repr(exc)}
            write_json(marker,failure)
            remember(failure)
            raise


def _run(project, storage, config, recorder, device, microbatch):
    stage, method, seed, budget = (config[k] for k in ("stage","method","seed","token_budget"))
    data = storage/"data"/stage
    manifest = read_json(data/"manifest.json")
    config["data_manifest_sha256"] = sha256(data/"manifest.json")
    config["microbatch"] = microbatch
    precise = stage=="abstracts" and method not in {"ce","initial","unigram"}
    if precise:
        config.update(derivative_dtype="float64",derivative_device=str(adapter_derivative_device()))
    output = recorder.directory
    state_path = output/"state.json"
    if not (output/"summary.json").exists():
        write_json(state_path,{**config,"status":"initializing","timestamp":time_now()})
    config["coefficients"] = chosen_coefficients(project,storage,config,device,microbatch)
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
    replica = derivative_replica(stage,seed,storage) if precise else None
    bench=project/"results"/"verification"/"pythia-scoring-batches.json"
    score_batch=read_json(bench)["selected_batch"] if stage=="abstracts" and bench.exists() else microbatch
    parameters = tuple(p for p in model.parameters() if p.requires_grad) if model is not None else ()
    summary = {**config, "device":str(device), "torch":str(torch.__version__), "platform":platform.platform(),
               "gpu":torch.cuda.get_device_name(device) if device.type=="cuda" else None,
               "initial_trainable_sha256":trainable_digest(model) if model is not None else None,
               "cpu_threads":torch.get_num_threads(),"evaluation_batch_windows":score_batch,
               "git_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=project,text=True).strip(),
               "trainable_parameters":sum(p.numel() for p in parameters)}
    batch = BATCHES[stage]
    steps = budget//(batch*CONTEXT)
    elapsed = 0.0
    if budget:
        write_json(state_path,{"status":"training","timestamp":time_now()})
        windows = TrainingWindows(data/"train.bin",seed,batch)
        groups = [{"params":[p for p in parameters if p.ndim>1],"weight_decay":0.1},
                  {"params":[p for p in parameters if p.ndim<=1],"weight_decay":0.0}]
        optimizer = torch.optim.AdamW(groups,lr=1e-4,betas=(0.9,0.95),fused=(device.type=="cuda"))
        # A restart during the first checkpoint interval must discard measurements from
        # updates whose weights and optimizer moments were never committed.
        if not (ckpt/"latest.pt").exists():
            save_state(ckpt/"latest.pt",model,optimizer,0,0.0,config)
        start,elapsed = restore_state(ckpt/"latest.pt",model,optimizer,config,recorder,device)
        history = json_lines(output/"events.jsonl")
        host_probes = sum(e.get("host_probe_seconds",0.0) for e in history)
        # Match elapsed-time comparisons with periodic fixed development windows in every arm.
        interval = min(128,max(1,steps//16))
        if start==0 and validation_due(stage,config["phase"],0,interval) and not history:
            metrics = score(model,data/"dev.bin",device,score_batch,limit_windows=64)
            recorder.emit({"step":0,"tokens":0,"train_seconds":0.0,"training_seconds_excluding_host_probes":0.0,
                           "dev_nll":metrics["nll"],"dev_accuracy":metrics["accuracy"]})
        for step in range(start,steps):
            model.train()
            tic = time.perf_counter()
            inputs,targets = windows.get(step,device)
            optimizer.zero_grad(set_to_none=True)
            base,accuracy = ce_backward(model,inputs,targets,microbatch)
            active = bool(config["coefficients"]) and gate(seed,step)
            terms = add_penalty(model,parameters,inputs,targets,config["coefficients"],method,seed,step,replica) if active else {}
            host_seconds = (sum(t["probe_seconds"] for t in terms.values())
                            if precise and config["derivative_device"]=="cpu" and device.type=="cuda" else 0.0)
            host_probes += host_seconds
            norm = torch.nn.utils.clip_grad_norm_(parameters,1.0,error_if_nonfinite=True)
            lr = learning_rate(stage,step,steps)
            for group in optimizer.param_groups:
                group["lr"] = lr
            optimizer.step()
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            elapsed += time.perf_counter()-tic
            done = step+1
            validate = validation_due(stage,config["phase"],done,interval) or done==steps
            if done % 8 == 0 or active or done == 1 or validate:
                row = {"step":done, "tokens":done*batch*CONTEXT, "train_seconds":elapsed, "loss":base.item(),
                       "accuracy":accuracy.item(), "lr":lr, "gradient_norm":norm.item(),"derivatives":terms,
                       "host_probe_seconds":host_seconds,"training_seconds_excluding_host_probes":max(0.0,elapsed-host_probes)}
                if terms:
                    row["penalty"] = sum(8*t["lambda"]*t["estimate"] for t in terms.values())
                if validate:
                    metrics = score(model,data/"dev.bin",device,score_batch,limit_windows=64)
                    row.update(dev_nll=metrics["nll"],dev_accuracy=metrics["accuracy"])
                recorder.emit(row)
            if done%interval == 0 or done==steps:
                save_state(ckpt/"latest.pt",model,optimizer,done,elapsed,config)
        del optimizer
        summary.update(host_probe_seconds=host_probes,training_seconds_excluding_host_probes=max(0.0,elapsed-host_probes))
    del replica
    dist = unigram_distribution(data/"train.bin",4096 if stage=="stories" else 50304) if method=="unigram" else None
    write_json(state_path,{"status":"scoring development","timestamp":time_now()})
    def evaluation_progress(row):
        write_json(state_path,{"status":"scoring development",**row})
        recorder.emit({"split":"dev",**row},"evaluation.jsonl")
    validation = score(model,data/"dev.bin",device,score_batch,unigram=dist,progress=evaluation_progress)
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
                   process_peak_rss_mib=peak_process_mib(),
                   peak_vram_mb=torch.cuda.max_memory_allocated(device)/2**20 if device.type=="cuda" else 0,
                   dev_nll=validation["nll"],dev_accuracy=validation["accuracy"],dev_tokens=validation["tokens"],
                   finished_at=time_now(),status="complete")
    write_json(summary_path,summary)
    state_path.unlink(missing_ok=True)
    (output/"failure.json").unlink(missing_ok=True)
    print(f"Completed {config['id']}  development NLL {summary['dev_nll']:.6f}",flush=True)
    return summary
