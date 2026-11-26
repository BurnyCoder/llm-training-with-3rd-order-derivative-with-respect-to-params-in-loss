"""Compare both fourth-order implementations on identical pretrained weights and probes."""

import hashlib
import time

import numpy as np
import torch

from .models import build_model, logits_of, token_loss, trainable_digest
from .objectives import ce_backward, probe_gradient, two_window_third_gradient
from .penalties import estimate, partials, random_signs
from .records import BATCHES, storage_root, time_now, write_json
from .windows import TrainingWindows, generator, probe_rows


def verify_pretrained(project,device):
    """Use training calibration draw zero. The full joint GPU graph can exceed 10 GiB."""
    storage = storage_root(project)
    model = build_model("abstracts",0,device,storage).eval()
    parameters = tuple(p for p in model.parameters() if p.requires_grad)
    seed,step = 6247,0
    batch_x,batch_y = TrainingWindows(storage/"data"/"abstracts"/"train.bin",seed,BATCHES["abstracts"]).get(step,device)
    rows = probe_rows(seed,step,len(batch_x))
    x,y = batch_x[rows],batch_y[rows]
    rng = generator(device,seed,step,827)
    u,v = random_signs(parameters,rng),random_signs(parameters,rng)
    def digest(tensors):
        h = hashlib.sha256()
        for tensor in tensors:
            h.update(tensor.detach().contiguous().cpu().numpy().tobytes())
        return h.hexdigest()
    result = {"timestamp":time_now(),"device":str(device),"seed":0,"calibration_seed":seed,"draw":step,
              "initial_trainable_sha256":trainable_digest(model),"input_sha256":digest((x,y)),
              "probes_sha256":digest((*u,*v))}
    with torch.no_grad():
        single = torch.cat([logits_of(model,t[None,:]) for t in x])
        together = logits_of(model,x)
        result["max_logit_abs_difference"] = (together-single).abs().max().item()
        result["two_window_cross_entropy"] = token_loss(together,y).item()
        del single,together
    def calculate(implementation):
        if device.type=="cuda":
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats(device)
        start = time.perf_counter()
        if implementation=="joint":
            loss = token_loss(logits_of(model,x),y)
            value = estimate(loss,parameters,"third",u=u,v=v)
            gradient = partials(value,parameters,create_graph=False)
        else:
            value,gradient = two_window_third_gradient(model,parameters,x,y,u,v)
        flat = torch.cat([g.detach().reshape(-1).cpu().double() for g in gradient])
        result[implementation] = {"penalty":value.item(),"gradient_norm":flat.norm().item(),
                                  "seconds":time.perf_counter()-start,"finite":bool(flat.isfinite().all()),
                                  "peak_allocated_mib":torch.cuda.max_memory_allocated(device)/2**20 if device.type=="cuda" else None}
        return flat
    joint = calculate("joint")
    split = calculate("sequential")
    result["relative_gradient_difference"] = ((joint-split).norm()/joint.norm()).item()
    result["gradient_cosine"] = torch.nn.functional.cosine_similarity(joint,split,dim=0).item()
    result["relative_penalty_difference"] = abs(result["joint"]["penalty"]-result["sequential"]["penalty"])/result["joint"]["penalty"]
    # Repeat the actual production calibration path from a fresh model, including its
    # preceding ordinary-gradient pass and independent regeneration of both probes.
    del parameters,model
    if device.type=="cuda":
        torch.cuda.empty_cache()
    fresh = build_model("abstracts",0,device,storage)
    fresh_parameters = tuple(p for p in fresh.parameters() if p.requires_grad)
    fresh_rng = generator(device,seed,step,827)
    result["repeat_initial_trainable_sha256"] = trainable_digest(fresh)
    result["repeat_probes_sha256"] = digest((*random_signs(fresh_parameters,fresh_rng),*random_signs(fresh_parameters,fresh_rng)))
    ce_backward(fresh,batch_x,batch_y,2)
    fresh.zero_grad(set_to_none=True)
    value,gradient = probe_gradient(fresh,fresh_parameters,batch_x,batch_y,"third",seed,step)
    flat = torch.cat([g.detach().reshape(-1).cpu().double() for g in gradient])
    result["repeat_production_penalty"] = value.item()
    result["repeat_production_gradient_norm"] = flat.norm().item()
    result["repeat_relative_gradient_difference"] = ((flat-split).norm()/split.norm()).item()
    write_json(project/"results"/"verification"/f"pythia-joint-{device.type}.json",result)
    print(result,flush=True)
    return result


def choose_scoring_batch(records):
    """Apply the registered speed, NLL, predicted-ID and memory limits to aligned training windows."""
    reference = records[0]
    qualified = [r for r in records[1:] if r["tokens"] == reference["tokens"]
                 and abs(r["nll"]-reference["nll"]) <= 2e-6 and r["top1_mismatches"] <= 1
                 and r["targets_per_second"] >= 1.1*reference["targets_per_second"]
                 and (r["peak_allocated_mib"] is None or r["peak_allocated_mib"] <= 7*1024)]
    return max(qualified,key=lambda r:r["targets_per_second"]) if qualified else reference


def benchmark_scoring(project,device):
    """Measure physical inference batch sizes on the same spaced *training* windows."""
    from .evaluation import score
    storage=storage_root(project)
    model=build_model("abstracts",0,device,storage).eval()
    path=storage/"data"/"abstracts"/"train.bin"
    records=[]
    for batch in (2,8,16,32):
        score(model,path,device,batch,limit_windows=16)
        if device.type=="cuda":
            torch.cuda.reset_peak_memory_stats(device)
        start=time.perf_counter()
        metrics=score(model,path,device,batch,limit_windows=256)
        seconds=time.perf_counter()-start
        records.append(dict(batch=batch,seconds=seconds,targets_per_second=metrics["tokens"]/seconds,
                            peak_allocated_mib=torch.cuda.max_memory_allocated(device)/2**20 if device.type=="cuda" else None,**metrics))
    # Collect aligned token IDs outside the timed benchmark, using the identical fixed windows.
    reference_ids = None
    for row in records:
        chunks = []
        score(model,path,device,row["batch"],limit_windows=256,top1_sink=chunks.append)
        ids = np.concatenate(chunks).astype("<i8",copy=False)
        if reference_ids is None:
            reference_ids = ids
        if len(ids) != row["tokens"] or ids.shape != reference_ids.shape:
            raise ValueError("Scoring batches must cover identical ordered target positions")
        row["top1_mismatches"] = int(np.count_nonzero(ids != reference_ids))
        row["top1_sha256"] = hashlib.sha256(ids.tobytes()).hexdigest()
    chosen=choose_scoring_batch(records)
    result={"timestamp":time_now(),"split":"train","device":str(device),"initial_trainable_sha256":trainable_digest(model),
            "records":records,"selected_batch":chosen["batch"]}
    path = project/"results"/"verification"/"pythia-scoring-batches.json"
    if path.exists():
        # Downstream runs cite the original selection. A subsequent benchmark is a new observation.
        path = path.with_name("pythia-scoring-batches-tokenwise.json")
    write_json(path,result)
    print(result,flush=True)
    return result
