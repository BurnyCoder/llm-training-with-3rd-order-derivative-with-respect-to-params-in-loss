"""Seal the complete research inputs and measure between-seed variation as the final stage."""

import hashlib
import json
import math
import subprocess
import sys
from statistics import median,stdev

from .records import HORIZONS,read_json,run_name,time_now,write_json
from .run_inventory import scheduled_jobs
from .report_records import METHODS,STAGES,atomic_text,completed,markdown_table,study_snapshot


def _planned_ids(study):
    """Use the registered IDs, including the cyclic replay and the available precision diagnostic."""
    ids={r["id"] for r in study["runs"] if r["phase"]=="diagnostic"}
    for action,stage,phase,method,seed,ratio in scheduled_jobs(study):
        if ratio is None:
            raise ValueError(f"The final analysis awaits the selected {stage} strength")
        if action=="fit":
            ids.add(run_name(stage,method,phase,seed,ratio))
    return ids


def _input_digests(project,study):
    """Bind the final analysis to both stage freezes and all scheduled model and geometry records."""
    if not all(study["stages"][stage]["complete"] for stage in STAGES):
        raise ValueError("The final stage requires both frozen eight-seed primary test matrices")
    root=project/"results"
    indexed={r["id"]:r for r in study["runs"] if completed(r)}
    files=[]
    for stage in STAGES:
        path=root/"freeze"/f"{stage}.json"
        frozen=read_json(path)
        for method in ("ce","trace","third"):
            for seed in range(1,9):
                matched=[r for r in indexed.values() if r["stage"]==stage and r["phase"]=="confirm"
                         and r["method"]==method and r["seed"]==seed]
                if len(matched)!=1:
                    raise ValueError(f"The final stage requires each registered {stage} seed and arm")
                row=matched[0]
                if (frozen["runs"].get(row["id"])!=row["weights_sha256"] or row["freeze_id"]!=frozen["freeze_id"]
                        or row["tokens"]!=HORIZONS[stage] or row["test_manifest_sha256"]!=frozen["test_sha256"]):
                    raise ValueError(f"Frozen test provenance differs for {row['id']}")
        files.append(path)
    for run in sorted(_planned_ids(study)):
        r=indexed.get(run)
        if not r or "score_flatness" not in r or (r["method"]!="unigram" and "flatness" not in r):
            raise ValueError(f"The final stage awaits the completed checkpoint and flatness probes for {run}")
        folder=root/run
        files.extend([folder/"summary.json",folder/"score-flatness.json"])
        if r["method"]!="unigram":
            files.append(folder/"flatness.json")
        if r["phase"] in {"hybrid","branch"}:
            files.extend(folder/f"width-{step}.json" for step in ((2048,) if r["phase"]=="branch" else (2048,3072,4096)))
    # Canonical JSON hashes survive a clone with different Git line-ending settings.
    return {p.relative_to(root).as_posix():hashlib.sha256(json.dumps(read_json(p),sort_keys=True,allow_nan=False,
                        ensure_ascii=False,separators=(",",":")).encode()).hexdigest() for p in files}


def seal_inputs(project,study):
    """Only the final command creates this seal. Subsequent reports verify every input before reuse."""
    path=project/"results"/"freeze"/"seed-sensitivity.json"
    digests=_input_digests(project,study)
    if path.exists():
        seal=read_json(path)
        if seal["inputs"]!=digests:
            raise ValueError("The final seed analysis inputs changed after sealing")
        return seal
    seal={"sealed_at":time_now(),"protocol":"final-seed-sensitivity-v1","inputs":digests}
    write_json(path,seal)
    return seal


def sensitivity(values):
    """Leave one whole paired seed out in turn. Preserve an unidentified endpoint when a width is censored."""
    observed=[v for v in values if v is not None and math.isfinite(v)]
    result={"n":len(values),"finite":len(observed)}
    if len(observed)==len(values):
        result.update(median=median(values),min=min(values),max=max(values),sample_sd=stdev(values),
                      leave_one_out_medians=[median(values[:i]+values[i+1:]) for i in range(len(values))])
    return result


def _rows(study):
    rows=[]
    def add(stage,arm,metric,seeds,values):
        rows.append({"stage":stage,"arm":arm,"metric":metric,"seeds":list(seeds),"values":values,**sensitivity(values)})
    confirm=range(1,9)
    for stage in STAGES:
        for method in ("ce","trace","third"):
            runs=sorted((r for r in study["runs"] if r["stage"]==stage and r["phase"]=="confirm" and r["method"]==method and r["seed"] in confirm),
                        key=lambda r:r["seed"])
            add(stage,METHODS[method],"Test NLL",confirm,[r["test_nll"] for r in runs])
            add(stage,METHODS[method],"Weight width",confirm,[r["flatness"]["width"] for r in runs])
        for comparator,result in study["stages"][stage]["comparisons"].items():
            pairs=sorted(result["pairs"],key=lambda p:p["seed"])
            add(stage,"Third order − "+METHODS[comparator],"Δtest NLL",confirm,[p["delta"] for p in pairs])
    follow=range(21,29)
    for method in ("adaptive","late","trace","strong","replay","always"):
        runs=sorted((r for r in study["runs"] if r["phase"]=="hybrid" and r["method"]==method and r["seed"] in follow),key=lambda r:r["seed"])
        add("stories",METHODS[method]+" · hybrid","Dev NLL",follow,[r["dev_nll"] for r in runs])
        add("stories",METHODS[method]+" · hybrid","Final weight width",follow,[r["widths"]["4096"]["width"] for r in runs])
    for comparator in ("late","replay"):
        pairs=sorted((p for p in study["hybrid"]["pairs"] if p["comparator"]==comparator),key=lambda p:p["seed"])
        arm="Adaptive − "+METHODS[comparator]
        add("stories",arm,"Δwidth retained",follow,[p["delta"] for p in pairs])
        add("stories",arm,"Δdev NLL",follow,[p["dev_nll_delta"] for p in pairs])
    return rows


def render_seed_sensitivity(project,study):
    """The ordinary reporting command can regenerate the final results only from the sealed inputs."""
    body=["# Final seed-sensitivity analysis",
          "[Execution order and descriptive analysis](amendments/seed-sensitivity-last.md) · "
          "[Timestamped study progress](progress.md)"]
    seal=project/"results"/"freeze"/"seed-sensitivity.json"
    if not seal.is_file():
        body.append("Scheduled last, after both primary test matrices, the complete hybrid follow-up and all checkpoint geometry.")
        atomic_text(project/"reports"/"seed-sensitivity.md","\n\n".join(body)+"\n")
        return None
    frozen=seal_inputs(project,study)
    rows=_rows(study)
    result={"sealed_at":frozen["sealed_at"],"protocol":frozen["protocol"],"rows":rows}
    write_json(project/"results"/"analysis"/"seed-sensitivity.json",result)
    body+=["The unit of replication is one training seed, including its initialization, document order and probes. "
           "For each paired contrast, omit one complete seed pair at a time and recompute the median. Lower NLL is better. "
           "A positive width-retention difference favors the adaptive schedule. Dispersion measures have no general better direction. "
           "The strength and training-control pilots use one seed and do not estimate across-seed variation.",
           "[Sealed input hashes](../results/freeze/seed-sensitivity.json) · "
           "[Every seed value and leave-one-out median](../results/analysis/seed-sensitivity.json)"]
    for stage,name in STAGES.items():
        table=[]
        for r in rows:
            if r["stage"]!=stage:
                continue
            data=["Censored"]*4
            if "median" in r:
                loo=r["leave_one_out_medians"]
                data=[f"{r['median']:.6g}",f"{r['sample_sd']:.6g}",f"{r['min']:.6g} to {r['max']:.6g}",
                      f"{min(loo):.6g} to {max(loo):.6g}"]
            table.append([r["arm"],r["metric"],f"{r['finite']}/{r['n']}",*data])
        body.extend([f"## {name}",markdown_table(table,["Arm or paired contrast","Metric","Finite seeds","Median",
                     "Sample SD","Across-seed range","Leave-one-out median range"])])
    atomic_text(project/"reports"/"seed-sensitivity.md","\n\n".join(body)+"\n")
    return result


def finish_seed_sensitivity(project,publish):
    """The full study reaches this entry point after all training, evaluation and geometry milestones."""
    seal_inputs(project,study_snapshot(project))
    subprocess.run([sys.executable,"-m","thirdloss.cli","--project",str(project),"report"],cwd=project,check=True)
    if publish:
        from .release import publish_snapshot
        publish_snapshot(project,"Publish the final seed-sensitivity analysis")
