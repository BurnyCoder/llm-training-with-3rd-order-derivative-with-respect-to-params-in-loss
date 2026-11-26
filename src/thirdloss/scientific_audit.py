"""Reproduce the scientific audit from archives. No model or optimizer is imported here."""

import json
import math
import subprocess
from pathlib import Path
from statistics import median

import numpy as np
from scipy.stats import binom, binomtest

from .analysis import analyze_stage
from .audit_overlap import exposure, matching_passages, presented
from .audit_records import calibration_and_selection, corpus_records, require, run_evidence
from .records import CONTEXT, HORIZONS, json_lines, read_json, sha256, write_json


def _git(project, *args):
    return subprocess.check_output(["git",*args],cwd=project)


def _primary(project, stage, records, corpus):
    """Independently recompute the binomial tails and order-statistic intervals from individual NLLs."""
    root = project/"results"
    records = [r for r in records if r["stage"]==stage and r["phase"]=="confirm"]
    seal_file = root/"freeze"/f"{stage}.json"
    seeds = sorted({r["seed"] for r in records if all(any(
        p["seed"]==r["seed"] and p["method"]==m for p in records) for m in ("ce","trace","third"))})
    result = {"completed_triplets":seeds,"scores":sum("test_nll" in r for r in records),"comparisons":{}}
    if not seal_file.exists():
        require(result["scores"]==0, f"{stage}: archived test scores without a freeze")
        return result
    seal = read_json(seal_file)
    if result["scores"] != len(seal["runs"]):
        return result
    verified = analyze_stage(records,stage,freeze=seal,dataset=corpus)
    require(verified["complete"],verified["reason"])
    commit = _git(project,"log","--diff-filter=A","--format=%H","-1","--",seal_file.relative_to(project).as_posix()).decode().strip()
    require(bool(commit), f"{stage}: missing pre-score Git freeze")
    result.update(freeze_id=seal["freeze_id"],freeze_commit=commit,test_targets=corpus["splits"]["test"]["tokens"]-1)
    result["unique_initializations"] = len(set(seal["initializations"].values()))
    history = _git(project,"log","--reverse","--format=%H","-G",'"test_nll"', "--",
                   f"results/{stage}-confirm-*/summary.json").decode().splitlines()
    require(bool(history) and history[0]!=commit, f"{stage}: missing distinct first scored commit")
    _git(project,"merge-base","--is-ancestor",commit,history[0])
    result["first_scored_commit"] = history[0]
    for row in records:
        before = json.loads(_git(project,"show",f"{commit}:results/{row['id']}/summary.json"))
        require("test_nll" not in before and before["weights_sha256"]==row["weights_sha256"] and
                before["tokens"]==HORIZONS[stage], f"{row['id']}: Git chronology")
    by_seed = {(r["seed"],r["method"]):r["test_nll"] for r in records}
    for baseline in ("ce","trace"):
        deltas = [by_seed[s,"third"]-by_seed[s,baseline] for s in seeds]
        wins,losses = sum(x<0 for x in deltas),sum(x>0 for x in deltas)
        p = binomtest(wins,wins+losses,alternative="greater").pvalue if wins+losses else 1.
        n = len(deltas)
        k = max(i for i in range(1,n//2+1) if 1-2*binom.cdf(i-1,n,.5)>=.95)
        ordered = sorted(deltas)
        result["comparisons"][baseline] = {"deltas":deltas,"wins":wins,"losses":losses,"ties":n-wins-losses,
            "median_delta":median(deltas),"median_ci":[ordered[k-1],ordered[-k]],"coverage":1-2*binom.cdf(k-1,n,.5),"p_raw":p}
    small,large = sorted(result["comparisons"].values(),key=lambda entry:entry["p_raw"])
    small["p_holm"]=min(1.,2*small["p_raw"])
    large["p_holm"]=max(small["p_holm"],large["p_raw"])
    for method,stats in result["comparisons"].items():
        actual = verified["comparisons"][method]
        for key in ("median_ci","median_delta","p_raw","p_holm","wins","losses","ties"):
            require(actual[key]==stats[key], f"{stage}/{method}: {key}")
        require(actual["ci_coverage"]==stats["coverage"],"Order-statistic interval")
    return result


def _hybrid_pairs(root, rows, hybrid):
    """Reconstruct shared-trunk contrasts directly from raw ray files, including partial seed blocks."""
    completed = {(r["seed"],r["method"]):r for r in rows if r["phase"]=="hybrid"}
    for pair in hybrid["pairs"]:
        seed, method = pair["seed"],pair["comparator"]
        if method not in {"late","replay"}:
            continue
        arms = [completed[seed,key] for key in ("adaptive",method)]
        trunks = [read_json(root/r["id"]/"width-2048.json") for r in arms]
        require(trunks[0]["weights_sha256"] == trunks[1]["weights_sha256"] and
                arms[0]["parent_restart_sha256"] == arms[1]["parent_restart_sha256"],"Unpaired hybrid trunk")
        restored = []
        for r in arms:
            point = read_json(root/r["id"]/"width-4096.json")
            rays = [(ray["positive"],ray["negative"]) for ray in point["directions"]]
            lo = median(a["lower"]+b["lower"] for a,b in rays)
            hi = median(sum(math.inf if q["upper"] is None else q["upper"] for q in ends) for ends in rays)
            restored.append((lo,hi))
        (a,b),(c,d) = restored
        bounds = [x if math.isfinite(x) else None for x in (a-d,b-c)]
        require(bounds==[pair["delta_lower"],pair["delta_upper"]],f"Independent hybrid bounds for seed {seed}")
    fixed = hybrid["attainability"]["late"]
    n = 8-fixed["resolved_ties"]
    require(fixed["best_raw_p"] == float(binom.cdf(fixed["narrower"],n,.5)), "Independent width completion bound")


def _clocks(project,rows):
    """Choose real fixed-window observations before the shortest optimizer clock, directly from JSONL."""
    output = []
    for stage in HORIZONS:
        runs = [r for r in rows if r["stage"]==stage and r["phase"]=="confirm"]
        for seed in sorted({r["seed"] for r in runs}):
            triplet = [r for r in runs if r["seed"]==seed]
            if len(triplet)!=3:
                continue
            for clock in ("train_seconds","training_seconds_excluding_host_probes"):
                if clock!="train_seconds" and stage!="abstracts":
                    continue
                cutoff = min(r[clock] for r in triplet)
                for r in triplet:
                    events = json_lines(project/"results"/r["id"]/"events.jsonl")
                    chosen = max((e for e in events if "dev_nll" in e and e[clock]<=cutoff),key=lambda e:e[clock])
                    output.append({"stage":stage,"seed":seed,"method":r["method"],"clock":clock,"cutoff":cutoff,
                                   "seconds":chosen[clock],"targets":chosen["tokens"],"nll":chosen["dev_nll"]})
    return output


def scientific_audit(project, storage):
    project = Path(project).resolve()
    root = project/"results"
    rows = [read_json(p) for p in sorted(root.glob("*/summary.json"))]
    revision = _git(project,"log","-1","--format=%H","--","results/*/summary.json","results/*/events.jsonl",
                    "results/*/state.json","results/*/width-*.json","results/*/flatness.json",
                    "results/*/score-flatness.json","results/freeze","results/verification/*-pause.json").decode().strip()
    output = {"evidence_revision":revision,"corpora":{},"primary":{}}
    for stage in HORIZONS:
        corpus,ends = corpus_records(root,storage,stage)
        output["corpora"][stage] = corpus
        manifest = read_json(root/"datasets"/f"{stage}.json")
        outcome = _primary(project,stage,rows,manifest)
        output["primary"][stage] = outcome
        if stage=="stories" and outcome["comparisons"]:
            folder = storage/"data"/stage
            train,test = (np.memmap(folder/(s+".bin"),dtype="<u2",mode="r") for s in ("train","test"))
            matches = matching_passages(train,test,eos=manifest["eos_id"])
            output["passages"] = {"minimum":50,"maximal_pairs":len(matches),
                "distinct_test_starts":len({b+i for _,b,n in matches for i in range(n-50+1)}),
                "longest":max((n for _,_,n in matches),default=0),"pool":exposure(matches,ends),
                "pairs":[{"train_start":a,"test_start":b,"tokens":n} for a,b,n in matches],
                "by_seed":{str(s):exposure(presented(matches,len(train),s,HORIZONS[stage],CONTEXT),ends)
                           for s in outcome["completed_triplets"]}}
    output["calibration"] = calibration_and_selection(root)
    for row in rows:
        if row["phase"]!="confirm":
            continue
        method, stage = row["method"],row["stage"]
        selected = output["calibration"]["selected_ratios"][stage]
        require(row["ratio"]==selected.get(method,0), f"{row['id']}: confirmatory strength")
        for term,weight in row["coefficients"].items():
            name = f"{stage}-{term}" + ("-fp64" if stage=="abstracts" else "")
            unit = output["calibration"]["unit_coefficients"][name]
            require(math.isclose(weight,unit*row["ratio"],rel_tol=1e-14,abs_tol=0), f"{row['id']}: scaled coefficient")
    output["secondary"] = run_evidence(root,storage,output["corpora"])
    output["matched_time"] = _clocks(project,rows)
    from .report_records import study_snapshot
    snapshot = study_snapshot(project)
    output["hybrid"] = snapshot["hybrid"]
    _hybrid_pairs(root,rows,output["hybrid"])
    output["pauses"] = []
    for path in sorted((root/"verification").glob("*-pause.json")):
        pause = read_json(path)
        state = read_json(root/pause["run"]/"config.json")
        require(state["data_manifest_sha256"]==pause["training_manifest_sha256"] and
                pause["checkpoint_step"]*state["context"]*state["batch_windows"]==pause["checkpoint_targets"],
                f"Paused checkpoint receipt for {pause['run']}")
        output["pauses"].append({k:pause[k] for k in ("run","checkpoint_step","checkpoint_targets","last_logged_step",
                                                      "checkpoint_sha256","hub_checkpoint")})
    for entry in output["matched_time"]:
        field = "matched_time" if entry["clock"]=="train_seconds" else "matched_nonhost_time"
        report = next(x for x in snapshot["stages"][entry["stage"]][field] if x["seed"]==entry["seed"])
        point = report["by_method"][entry["method"]]
        require((point["clock_seconds"],point["dev_nll"],point["tokens"])==
                (entry["seconds"],entry["nll"],entry["targets"]), "Matched-clock observation differs")
    bench = read_json(root/"verification"/"pythia-scoring-batches.json")
    ref,batch = bench["records"][0],next(r for r in bench["records"] if r["batch"]==bench["selected_batch"])
    output["scoring_benchmark"] = {"reference_batch":ref["batch"],"selected_batch":batch["batch"],"targets":ref["tokens"],
        "reference_correct":round(ref["accuracy"]*ref["tokens"]),"selected_correct":round(batch["accuracy"]*batch["tokens"]),
        "delta_nll":batch["nll"]-ref["nll"],"per_token_ids_archived":False}
    if "top1_mismatches" in batch:
        output["scoring_benchmark"]["top1_mismatches"] = batch["top1_mismatches"]
    output["precision"] = _precision(root,storage)
    path = root/"analysis"/"scientific-audit.json"
    write_json(path,output)
    return path


def _precision(root,storage):
    """Compare archived FP64 derivative arrays as numbers. Safetensors' NumPy reader executes no network."""
    from safetensors.numpy import load_file
    files = [storage/"diagnostics"/f"pythia-reference-{device}.safetensors" for device in ("cpu","cuda")]
    cpu,gpu = [load_file(str(p)) for p in files]
    require(cpu.keys()==gpu.keys(),"Gradient tensor names differ")
    dot,sq_cpu,sq_gpu,dsq = 0.,0.,0.,0.
    for key in sorted(cpu):
        a,b = cpu[key].astype(np.float64).ravel(),gpu[key].astype(np.float64).ravel()
        require(a.shape==b.shape, f"Derivative shape: {key}")
        dot += float(a@b)
        sq_cpu += float(a@a)
        sq_gpu += float(b@b)
        diff = a-b
        dsq += float(diff@diff)
    relative = math.sqrt(dsq/sq_cpu)
    cosine = dot/math.sqrt(sq_cpu*sq_gpu)
    saved = read_json(root/"verification"/"pythia-fp64-agreement.json")
    require(math.isclose(relative,saved["relative_gradient_difference"],rel_tol=1e-8) and
            math.isclose(cosine,saved["cosine"],abs_tol=1e-12),"Archived precision comparison")
    return {"relative_gradient_difference":relative,"cosine":cosine,"reference_files":{p.name:sha256(p) for p in files}}
