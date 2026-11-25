"""Sequence prospective pilots, blinded model selection, sealed evaluation and releases."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

from .data import prepare
from .evaluation import score
from .models import build_model
from .records import HORIZONS, RATIOS, Recorder, read_json, run_name, sha256, time_now, write_json
from .release import STAGE_HUB, publish_snapshot, publish_weights
from .train import run_one


def prepare_stage(project, storage, stage):
    manifest = prepare(stage,storage/"data")
    write_json(project/"results"/"datasets"/f"{stage}.json",manifest)
    return manifest


def select(project, stage):
    """Lock selection using the six equal-horizon full-development scores."""
    candidates = {}
    for kind in ("trace","third"):
        candidates[kind] = []
        for ratio in RATIOS:
            path = project/"results"/run_name(stage,kind,"pilot",0,ratio)/"summary.json"
            row = read_json(path)
            if row["tokens"] != HORIZONS[stage]//8:
                raise ValueError("All pilot candidates must finish the same development horizon")
            candidates[kind].append({"ratio":ratio,"nll":row["dev_nll"],"run":row["id"]})
    result = {"stage":stage,"candidates":candidates,"ratios":{
        kind:min(rows,key=lambda x:(x["nll"],x["ratio"]))["ratio"] for kind,rows in candidates.items()}}
    path = project/"results"/"selection"/f"{stage}.json"
    if path.exists() and read_json(path)!=result:
        raise ValueError("Development scores changed after the stage selection was locked")
    write_json(path,result)
    return result["ratios"]


def weights_file(storage, summary):
    """Verify local snapshot or retrieve the same digest from the published collection."""
    run_id = summary["id"]
    filename = summary["weights_name"]
    path = storage/"checkpoints"/run_id/"export"/filename
    if not path.is_file():
        path = Path(hf_hub_download(STAGE_HUB[summary["stage"]],f"runs/{run_id}/{filename}",
                                    cache_dir=str(storage/"hub")))
    if sha256(path)!=summary["weights_sha256"]:
        raise ValueError(f"Weights for {run_id} differ from their registered checksum")
    return path


def freeze(project, storage, stage):
    """Bind all 24 finished checkpoints, split, and selected coefficients before opening test bytes."""
    selection = read_json(project/"results"/"selection"/f"{stage}.json")["ratios"]
    split = read_json(storage/"data"/stage/"manifest.json")["splits"]["test"]
    frozen = {"stage":stage,"ratios":selection,"test_sha256":split["sha256"],"runs":{}}
    for seed in range(1,9):
        initial = set()
        for method in ("ce","trace","third"):
            name = run_name(stage,method,"confirm",seed,selection.get(method,0))
            summary = read_json(project/"results"/name/"summary.json")
            if summary["tokens"]!=HORIZONS[stage] or summary["status"]!="complete":
                raise ValueError(f"Incomplete registered checkpoint {name}")
            if summary["data_manifest_sha256"]!=sha256(storage/"data"/stage/"manifest.json"):
                raise ValueError(f"Different corpus for {name}")
            weights_file(storage,summary)
            frozen["runs"][name] = summary["weights_sha256"]
            digest = summary.get("initial_trainable_sha256")
            if not digest:
                raise ValueError(f"Missing initial trainable-weight digest for {name}")
            initial.add(digest)
        if len(initial)!=1:
            raise ValueError(f"Initial trainable weights differ across {stage} seed {seed} arms")
        frozen.setdefault("initializations",{})[str(seed)] = initial.pop()
    frozen["freeze_id"] = hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()
    path = project/"results"/"freeze"/f"{stage}.json"
    if path.exists() and read_json(path)!=frozen:
        raise ValueError("A sealed checkpoint or dataset changed")
    write_json(path,frozen)
    return frozen


def evaluate_one(project, storage, run_id, device):
    from .progress import week_schedule
    path = project/"results"/run_id/"summary.json"
    summary = read_json(path)
    stage = summary["stage"]
    sealed = read_json(project/"results"/"freeze"/f"{stage}.json")
    data = storage/"data"/stage
    if sealed["runs"].get(run_id)!=summary.get("weights_sha256") or run_id not in sealed["runs"]:
        raise ValueError("Evaluation requires a checkpoint present in the stage freeze")
    if week_schedule(project) is None:
        raise ValueError("The one-week timing and memory projection requires selected pilots from both stages before test scoring")
    if "test_nll" in summary:
        if summary["freeze_id"]!=sealed["freeze_id"]:
            raise ValueError("Existing evaluation uses a different freeze")
        return summary
    weights = weights_file(storage,summary)
    if sha256(data/"test.bin") != sealed["test_sha256"]:
        raise ValueError("Test stream differs from the frozen manifest")
    model = build_model(stage,summary["seed"],device,storage)
    state = load_file(str(weights),device="cpu")
    if stage=="stories":
        model.load_state_dict(state,strict=True)
    else:
        from peft import get_peft_model_state_dict,set_peft_model_state_dict
        if set(state)!=set(get_peft_model_state_dict(model)):
            raise ValueError("Adapter payload does not match the pinned backbone and target modules")
        set_peft_model_state_dict(model,state)
    recorder = Recorder(project,run_id)
    state = path.parent/"test_state.json"
    def report_progress(row):
        # Publish elapsed time and coverage during a sealed evaluation. The full-corpus
        # NLL and accuracy enter the summary only after every target has been scored.
        coverage = {key:row[key] for key in ("targets_scored","targets_to_score","score_seconds")}
        write_json(state,{"split":"test","timestamp":time_now(),**coverage})
        recorder.emit({"split":"test",**coverage},"test_progress.jsonl")
    report_progress({"targets_scored":0,"targets_to_score":(data/"test.bin").stat().st_size//2-1,"score_seconds":0.0})
    stats = score(model,data/"test.bin",device,summary.get("evaluation_batch_windows",summary["microbatch"]),
                  progress=report_progress)
    summary.update(test_nll=stats["nll"],test_accuracy=stats["accuracy"],test_tokens=stats["tokens"],
                   test_manifest_sha256=sealed["test_sha256"],freeze_id=sealed["freeze_id"],
                   test_seconds=read_json(state)["score_seconds"],evaluated_at=time_now())
    write_json(path,summary)
    state.unlink(missing_ok=True)
    return summary


def milestone(project,storage,summary,publish):
    path = project/"results"/summary["id"]/"summary.json"
    marker = storage/"releases"/(summary["id"]+".json")
    fingerprint = sha256(path)
    if publish and marker.exists() and read_json(marker)["summary_sha256"]==fingerprint:
        return
    # A study can run for days. Render from the current checked-in reporting code so a
    # later milestone cannot replace an updated paper or explorer with an older template.
    subprocess.run([sys.executable,"-m","thirdloss.cli","--project",str(project),"report"],cwd=project,check=True)
    if publish:
        publish_weights(project,storage,summary)
        label = "evaluation" if "test_nll" in summary else "development"
        revision = publish_snapshot(project,f"Record {label} results for {summary['id']}")
        write_json(marker,{"summary_sha256":fingerprint,"git_revision":revision})


def feasibility(project, stage):
    """Project training-only cost from actual per-arm pilot timing before using test data."""
    selected = read_json(project/"results"/"selection"/f"{stage}.json")["ratios"]
    rows = []
    for method in ("third","ce","trace"):
        row = read_json(project/"results"/run_name(stage,method,"pilot",0,selected.get(method,0))/"summary.json")
        rows.append({"method":method,"pilot_run":row["id"],"tokens_per_sec":row["tokens_per_sec"],
                     "peak_vram_mb":row["peak_vram_mb"],"projected_confirm_hours":
                         8*HORIZONS[stage]/row["tokens_per_sec"]/3600})
    hours = sum(r["projected_confirm_hours"] for r in rows)
    result = {"stage":stage,"arms":rows,"projected_confirm_training_hours":hours,
              "basis":"Pilot training time. Data, calibration, evaluation, checkpoint and upload overhead are additional."}
    write_json(project/"results"/"feasibility"/f"{stage}.json",result)
    return result


def run_study(project,storage,stages,device,publish):
    """Retry-safe complete study. Cached milestones allow continuation after reboot or network loss."""
    def run(stage,method,phase,seed,ratio):
        row = run_one(project,storage,stage,method,phase,seed,ratio,device)
        milestone(project,storage,row,publish)
        return row
    for stage in stages:
        prepare_stage(project,storage,stage)
        if stage=="abstracts" and not (project/"results"/"verification"/"pythia-scoring-batches.json").exists():
            from .probe_check import benchmark_scoring
            benchmark_scoring(project,device)
        run(stage,"third","pilot",0,0.03)
        for method in ("initial","unigram"):
            run(stage,method,"control",0,0)
        run(stage,"ce","pilot",0,0)
        for method in ("trace","third"):
            for ratio in RATIOS:
                run(stage,method,"pilot",0,ratio)
        selected = select(project,stage)
        feasibility(project,stage)
        for method,ratio in (("hessian_norm",0.03),("sham",selected["third"]),("combined",selected["third"])):
            run(stage,method,"pilot",0,ratio)
    for stage in stages:
        selected = select(project,stage)
        for seed in range(1,9):
            for method in ("third","ce","trace"):
                run(stage,method,"confirm",seed,selected.get(method,0))
        sealed = freeze(project,storage,stage)
        if publish:
            publish_snapshot(project,f"Freeze all {stage} confirmatory checkpoints before test evaluation")
        for run_id in sealed["runs"]:
            row = evaluate_one(project,storage,run_id,device)
            milestone(project,storage,row,publish)
