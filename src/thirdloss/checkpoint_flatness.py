"""Secondary training-window geometry of saved language-model checkpoints, outside timed training."""

import hashlib
import math
import subprocess
import sys
from statistics import mean

import torch
from filelock import FileLock

from .models import logits_of,token_loss,widen_pythia
from .penalties import inner,partials,random_signs
from .records import HORIZONS,read_json,run_name,sha256,time_now,write_json
from .study import load_trained_model
from .width import measure_width
from .windows import TrainingWindows,generator


PROTOCOL="checkpoint-flatness-v1"


def hessian_statistics(loss,parameters):
    """Estimate tr(H)/d and ||H||F/√d on one fixed loss; the signed trace can cancel."""
    gradient=partials(loss,parameters)
    dimensions=sum(p.numel() for p in parameters)
    device=parameters[0].device
    draws=[]
    for index in range(8):
        z=random_signs(parameters,generator(device,88731,index,983))
        hz=partials(inner(gradient,z),parameters,create_graph=False)
        signed=float(inner(z,hz))/dimensions
        square=float(inner(hz,hz))/dimensions
        if not math.isfinite(signed) or not math.isfinite(square):
            raise FloatingPointError("Nonfinite checkpoint Hessian product")
        draws.append({"index":index,"trace_per_parameter":signed,"squared_rms":square})
    return {"dimensions":dimensions,"draws":draws,"device":str(device),"dtype":str(parameters[0].dtype),
            "trace_per_parameter":mean(r["trace_per_parameter"] for r in draws),
            "rms_curvature":math.sqrt(mean(r["squared_rms"] for r in draws))}


def measure_checkpoint(project,storage,row,device):
    """Restore one verified export and compute both local curvature and finite-radius width."""
    corpus=storage/"data"/row["stage"]
    path=project/"results"/row["id"]/"flatness.json"
    identity={"protocol":PROTOCOL,"run":row["id"],"checkpoint_file_sha256":row["weights_sha256"],
              "data_manifest_sha256":sha256(corpus/"manifest.json"),"width_device":device.type}
    if identity["data_manifest_sha256"]!=row["data_manifest_sha256"]:
        raise ValueError(f"Training manifest changed for {row['id']}")
    if path.exists():
        existing=read_json(path)
        if any(existing.get(k)!=v for k,v in identity.items()):
            raise ValueError(f"Saved flatness provenance differs for {row['id']}")
        return path
    print(f"{time_now()} Measuring checkpoint flatness for {row['id']}",flush=True)
    model=load_trained_model(storage,row,device).eval()
    inputs,targets=TrainingWindows(corpus/"train.bin",88731,8).get(0,device)
    fingerprint=hashlib.sha256(inputs.cpu().numpy().tobytes()+targets.cpu().numpy().tobytes()).hexdigest()
    width=measure_width(model,lambda:token_loss(logits_of(model,inputs),targets))
    if row["stage"]=="abstracts":
        model=widen_pythia(model.cpu())
    else:
        model=model.double()
    hessian_device=next(model.parameters()).device
    loss=token_loss(logits_of(model,inputs[:2].to(hessian_device)),targets[:2].to(hessian_device))
    statistics=hessian_statistics(loss,tuple(p for p in model.parameters() if p.requires_grad))
    write_json(path,{**identity,"timestamp":time_now(),"split":"train","probe_windows_sha256":fingerprint,
                     "width_windows":8,"curvature_windows":2,"width":width,"curvature":statistics})
    print(f"{time_now()} {row['id']} width={width['width']} RMS curvature={statistics['rms_curvature']:.6g}",flush=True)
    return path


def flatness_study(project,storage,stages,phase,device,publish):
    """Measure all available prespecified matches; resume from independently verified per-run records."""
    from .release import publish_snapshot
    for stage in stages:
        data=storage/"data"/stage
        if (project/"results"/"selection"/f"{stage}.json").exists():
            if sha256(data/"train.bin")!=read_json(data/"manifest.json")["artifacts"]["train.bin"]["sha256"]:
                raise ValueError(f"Training tokens differ from their registered digest for {stage}")
    for group in (("ce","trace","third"),("hessian_norm","sham","combined")):
        for stage in stages:
            selection=project/"results"/"selection"/f"{stage}.json"
            if not selection.exists():
                continue
            ratios=read_json(selection)["ratios"]
            strength={"ce":0.,"hessian_norm":.03,"sham":ratios["third"],"combined":ratios["third"],**ratios}
            for kind in (("pilot","confirm") if phase=="all" else (phase,)):
                if kind=="confirm" and "ce" not in group:
                    continue
                for seed in ((0,) if kind=="pilot" else range(1,9)):
                    for method in group:
                        run=run_name(stage,method,kind,seed,strength[method])
                        summary=project/"results"/run/"summary.json"
                        if not summary.exists():
                            continue
                        row=read_json(summary)
                        if row["tokens"]!=(HORIZONS[stage]//8 if kind=="pilot" else HORIZONS[stage]):
                            raise ValueError(f"Flatness comparison requires the complete registered horizon: {run}")
                        with FileLock(str(storage/"locks"/(run+"-flatness.lock"))):
                            measured=measure_checkpoint(project,storage,row,device)
                            marker=storage/"releases"/("flatness-"+run+".json")
                            digest=sha256(measured)
                            if publish and (not marker.exists() or read_json(marker)["sha256"]!=digest):
                                subprocess.run([sys.executable,"-m","thirdloss.cli","--project",str(project),"report"],
                                               cwd=project,check=True)
                                revision=publish_snapshot(project,f"Measure training-window flatness for {run}")
                                write_json(marker,{"sha256":digest,"git_revision":revision})
