"""Secondary training-window geometry of saved language-model checkpoints, outside timed training."""

import hashlib
import json
import math
import subprocess
import sys
from statistics import mean

import torch
from filelock import FileLock

from .evaluation import unigram_distribution
from .models import build_model,logits_of,token_loss,trainable_digest,widen_pythia
from .penalties import inner,partials,random_signs
from .records import read_json,sha256,time_now,write_json
from .score_flatness import score_width
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


def _initial_model(project,storage,corpus,row,device):
    """Reconstruct zero-update weights, with an independent forward check for the earliest seed."""
    model=build_model(row["stage"],row["seed"],device,storage).eval()
    digest=trainable_digest(model)
    if row.get("initial_trainable_sha256"):
        if digest!=row["initial_trainable_sha256"]:
            raise ValueError("Reconstructed initial weights differ from their saved digest")
        return model,{"initial_trainable_sha256":digest,"verification":"recorded initial weight digest"}
    if row["stage"]!="stories" or row["seed"]!=0:
        raise ValueError("Missing initialization provenance for this reference")
    source="stories-pilot-s00-ce-r00"
    with (project/"results"/source/"events.jsonl").open(encoding="utf-8") as f:
        first=json.loads(next(f))
    inputs,targets=TrainingWindows(corpus/"train.bin",0,row["batch_windows"]).get(0,device)
    with torch.no_grad():
        logits=logits_of(model,inputs)
        loss=float(token_loss(logits,targets))
        accuracy=float((logits.argmax(-1)==targets).double().mean())
    if (first["step"]!=1 or targets.numel()!=first["tokens"] or abs(loss-first["loss"])>1e-5
            or abs(accuracy-first["accuracy"])>1e-8):
        raise ValueError("Reconstructed scratch reference differs on its recorded first training batch")
    return model,{"initial_trainable_sha256":digest,"first_update_source":source,"nll":loss,"accuracy":accuracy}


def _native_geometry(model,row,folder,inputs,targets):
    """Reuse registered widths with the same weights and direction backend, then measure local curvature."""
    registered=folder/f"width-{row['steps']}.json"
    width=None
    if row["phase"] in {"hybrid","branch"}:
        prior=read_json(registered)
        if prior["weights_sha256"]!=trainable_digest(model) or not prior["weights_restored"]:
            raise ValueError("Registered width belongs to different trained weights")
        if torch.device(row["device"]).type==inputs.device.type:
            width=prior
    if width is None:
        width=measure_width(model,lambda:token_loss(logits_of(model,inputs),targets))
    if row["stage"]=="abstracts":
        model=widen_pythia(model.cpu())
    else:
        model=model.double()
    hessian_device=next(model.parameters()).device
    loss=token_loss(logits_of(model,inputs[:2].to(hessian_device)),targets[:2].to(hessian_device))
    statistics=hessian_statistics(loss,tuple(p for p in model.parameters() if p.requires_grad))
    return {"width_windows":8,"curvature_windows":2,"width":width,"curvature":statistics}


def measure_checkpoint(project,storage,row,device):
    """Use shared output-score coordinates for every predictor and native coordinates where they exist."""
    folder=project/"results"/row["id"]
    corpus=storage/"data"/row["stage"]
    native,score=folder/"flatness.json",folder/"score-flatness.json"
    unigram=row["method"]=="unigram"
    if unigram:
        # A single frequency vector needs no network forward pass or GPU memory.
        device=torch.device("cpu")
    paths=[score] if unigram else [native,score]
    identity={"run":row["id"],"checkpoint_file_sha256":row.get("weights_sha256"),
              "data_manifest_sha256":sha256(corpus/"manifest.json"),"width_device":device.type}
    if identity["data_manifest_sha256"]!=row["data_manifest_sha256"]:
        raise ValueError(f"Training manifest changed for {row['id']}")
    for path in paths:
        if path.exists():
            saved=read_json(path)
            expected={**identity,"protocol":PROTOCOL if path==native else "shared-logit-width-v1"}
            if any(saved.get(k)!=v for k,v in expected.items()):
                raise ValueError(f"Saved flatness provenance differs for {row['id']}")
    if all(path.exists() for path in paths):
        return paths
    print(f"{time_now()} Measuring flatness for {row['id']}",flush=True)
    inputs,targets=TrainingWindows(corpus/"train.bin",88731,8).get(0,device)
    windows=hashlib.sha256(inputs.cpu().numpy().tobytes()+targets.cpu().numpy().tobytes()).hexdigest()
    common={**identity,"split":"train","probe_windows_sha256":windows,"timestamp":time_now()}
    if row["method"]=="initial":
        model,common["reference"]=_initial_model(project,storage,corpus,row,device)
    elif not unigram:
        model=load_trained_model(storage,row,device).eval()
    if not score.exists():
        with torch.no_grad():
            if unigram:
                distribution=unigram_distribution(corpus/"train.bin",read_json(corpus/"manifest.json")["model_vocab_size"])
                common["reference"]={"distribution_sha256":hashlib.sha256(distribution.tobytes()).hexdigest()}
                logits=torch.as_tensor(distribution,device=device).log()[None,:]
            else:
                logits=logits_of(model,inputs)
            output=score_width(logits,targets)
            del logits
        write_json(score,{**common,"protocol":"shared-logit-width-v1","score":output})
    if not unigram and not native.exists():
        data=_native_geometry(model,row,folder,inputs,targets)
        write_json(native,{**common,"protocol":PROTOCOL,**data})
    return paths


def flatness_study(project,storage,stages,phase,device,publish,run_id=None):
    """Visit saved study runs deterministically, including zero-update references and all strengths."""
    from .release import publish_snapshot
    phases={"pilot":{"pilot","control"},"confirm":{"confirm"},"hybrid":{"branch","hybrid"},
            "all":{"pilot","control","confirm","branch","hybrid"}}[phase]
    candidates=[read_json(p) for p in (project/"results").glob("*/summary.json")]
    rows=[r for r in candidates if r.get("stage") in stages and r.get("phase") in phases and
          r.get("status")=="complete" and (run_id is None or r["id"]==run_id)]
    if run_id is not None and not rows:
        raise ValueError(f"No completed study checkpoint matches {run_id}")
    for stage in {r["stage"] for r in rows}:
        data=storage/"data"/stage
        if sha256(data/"train.bin")!=read_json(data/"manifest.json")["artifacts"]["train.bin"]["sha256"]:
            raise ValueError(f"Training tokens differ from their registered digest for {stage}")
    # Show each kind of model early; the ordering is independent of every performance measurement.
    by_kind={}
    for r in sorted(rows,key=lambda r:(r["seed"],r["ratio"],r["id"])):
        by_kind.setdefault((r["stage"],r["phase"],r["method"]),[]).append(r)
    ordered=[items[i] for i in range(max(map(len,by_kind.values()),default=0)) for items in by_kind.values() if i<len(items)]
    for row in ordered:
        run=row["id"]
        if row["tokens"]!=row["token_budget"]:
            raise ValueError(f"Flatness comparison requires the complete registered horizon: {run}")
        with FileLock(str(storage/"locks"/(run+"-flatness.lock"))):
            paths=measure_checkpoint(project,storage,row,device)
            artifacts={p.name:sha256(p) for p in paths}
            marker=storage/"releases"/("flatness-"+run+".json")
            if publish and (not marker.exists() or read_json(marker).get("artifacts")!=artifacts):
                subprocess.run([sys.executable,"-m","thirdloss.cli","--project",str(project),"report"],cwd=project,check=True)
                revision=publish_snapshot(project,f"Measure comparable flatness for {run}")
                write_json(marker,{"artifacts":artifacts,"git_revision":revision})
    if rows and not publish:
        subprocess.run([sys.executable,"-m","thirdloss.cli","--project",str(project),"report"],cwd=project,check=True)


def geometry_milestone(project,storage,row,device,publish):
    """Keep checkpoint evaluation isolated from timed training and recover each missing publication."""
    run=row["id"]
    folder=project/"results"/run
    paths=[folder/"score-flatness.json"]
    if row["method"]!="unigram":
        paths.append(folder/"flatness.json")
    marker=storage/"releases"/("flatness-"+run+".json")
    if all(p.is_file() for p in paths) and (not publish or (marker.is_file() and
            read_json(marker).get("artifacts")=={p.name:sha256(p) for p in paths})):
        return
    cmd=[sys.executable,"-m","thirdloss.cli","--project",str(project),"flatness","--run-id",run,
         "--stage",row["stage"],"--device",str(device)]
    subprocess.run(cmd+(["--publish"] if publish else []),cwd=project,check=True)
