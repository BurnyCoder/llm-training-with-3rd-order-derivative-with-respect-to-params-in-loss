"""Compare both fourth-order implementations on identical pretrained weights and probes."""

import hashlib
import time

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
