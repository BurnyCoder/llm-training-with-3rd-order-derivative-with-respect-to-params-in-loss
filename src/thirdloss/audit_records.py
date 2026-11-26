"""Reconcile archives using scalar arithmetic, token metadata and file digests, without loading a model."""

import math
from collections import Counter, defaultdict
from itertools import combinations
from statistics import median

from .records import json_lines, read_json, sha256


def require(condition, message):
    """Keep provenance checks active even when Python runs with optimizations."""
    if not condition:
        raise ValueError(message)


def corpus_records(results, storage, stage):
    directory = storage/"data"/stage
    corpus = read_json(results/"datasets"/f"{stage}.json")
    require(corpus == read_json(directory/"manifest.json"), f"{stage}: published corpus differs")
    sealed = not (results/"freeze"/f"{stage}.json").exists()
    checked = {}
    for name, spec in corpus["artifacts"].items():
        if name == "test.bin" and sealed:
            continue
        path = directory/name
        checked[name] = sha256(path)
        require(checked[name] == spec["sha256"] and path.stat().st_size==spec["bytes"], f"{stage}/{name}")
    offsets, hashes, ids = Counter(), defaultdict(set), defaultdict(set)
    test_ends = []
    for doc in json_lines(directory/"documents.jsonl"):
        split, identity = doc["split"],doc["id"]
        require(offsets[split]==doc["start_token"], f"{stage}: discontinuous document offsets")
        require(doc["sha256"] not in hashes[split] and identity not in ids[split], f"{stage}: duplicate {identity}")
        hashes[split].add(doc["sha256"])
        ids[split].add(identity)
        offsets[split] += doc["tokens"]
        if split=="test":
            test_ends.append(offsets[split])
        if stage=="stories" and split!="test":
            require((int(doc["sha256"][:16],16)%50==0)==(split=="dev"), "Story split assignment")
        if stage=="abstracts":
            month = doc["submitted"][:7]
            allowed = {"train":"2024-01"<=month<="2024-04","dev":month=="2024-05","test":month=="2024-06"}
            require(allowed[split], "Abstract month assignment")
    overlap = {}
    for x,y in combinations(("train","dev","test"),2):
        overlap[f"{x}/{y}"] = {"normalized_hashes":len(hashes[x]&hashes[y]),"source_ids":len(ids[x]&ids[y])}
    for split,r in corpus["splits"].items():
        require((r["tokens"],r["documents"])==(offsets[split],len(ids[split])), f"{stage}/{split}: counts")
    rejected = Counter((d["split"], d["reason"]) for d in json_lines(directory/"rejections.jsonl"))
    for split, totals in corpus["audit"].items():
        for field, reason in (("exact","exact"),("empty","empty"),("cross_split_near","near")):
            require(totals[field]==rejected[split,reason], f"{stage}/{split}: {reason}")
    return {"manifest_sha256":sha256(directory/"manifest.json"),"verified_files":checked,"exact_overlap":overlap,
            "splits":corpus["splits"],"test_content_sealed":sealed}, test_ends


def width_from_rays(point):
    """Reconstruct the median and its numerical bracket from both rays of each direction."""
    lows,highs = [],[]
    for index,ray in enumerate(point["directions"]):
        require(ray["direction"]==index, "Direction index mismatch")
        ends = [ray[key] for key in ("positive","negative")]
        lower = [r["lower"] for r in ends]
        upper = [math.inf if r["upper"] is None else r["upper"] for r in ends]
        require(all(0<=a<=b for a,b in zip(lower,upper)), "Invalid radius bracket")
        lows.append(sum(lower))
        highs.append(sum(upper))
    require(len(lows)==16, "Unexpected number of directions")
    low,high = median(lows),median(highs)
    expected = (low, high if math.isfinite(high) else None, (low+high)/2 if math.isfinite(high) else None)
    require(expected==(point["width_lower"],point["width_upper"],point["width"]), "Median width mismatch")
    return expected


def calibration_and_selection(results):
    units, selected = {},{}
    for path in sorted((results/"calibration").glob("*.json")):
        record = read_json(path)
        draws = record["draws"]
        require([d["draw"] for d in draws]==list(range(16)), f"Calibration draws: {path.name}")
        ratios = [d["ce_grad_norm"]/d["penalty_grad_norm"] for d in draws]
        require(ratios==[d["norm_ratio"] for d in draws] and median(ratios)==record["unit_lambda"], path.name)
        units[path.stem] = median(ratios)
    for path in sorted((results/"selection").glob("*.json")):
        record = read_json(path)
        selected[path.stem] = {}
        for method, candidates in record["candidates"].items():
            require(sorted(c["ratio"] for c in candidates)==[.01,.03,.10], "Pilot grid differs")
            values = []
            for candidate in candidates:
                row = read_json(results/candidate["run"]/"summary.json")
                require(row["dev_nll"]==candidate["nll"] and row["method"]==method and
                        row["seed"]==0 and row["phase"]=="pilot" and row["ratio"]==candidate["ratio"], "Pilot identity")
                values.append((row["dev_nll"],row["ratio"]))
            chosen = min(values)[1]
            require(chosen==record["ratios"][method], "Published ratio is not the development minimizer")
            selected[path.stem][method] = chosen
    return {"unit_coefficients":units, "selected_ratios":selected}


def run_evidence(results, storage, corpora):
    """Reconstruct run-level full-split metrics, checkpoint geometry and measured resource accounting."""
    rows, flags = [],Counter()
    groups = defaultdict(list)
    exclusions = read_json(results/"verification"/"numerical-exclusions.json")
    for path in sorted(results.glob("*/summary.json")):
        row = read_json(path)
        name,folder = row["id"],path.parent
        stage,method = row["stage"],row["method"]
        require(folder.name==name and row["status"]=="complete",name)
        require(all(row.get(k)==v for k,v in read_json(folder/"config.json").items()), f"{name}: config")
        require(row["data_manifest_sha256"]==corpora[stage]["manifest_sha256"], f"{name}: corpus")
        require(row["tokens"]==row["steps"]*row["context"]*row["batch_windows"]==row["token_budget"], f"{name}: budget")
        check = {"run":name,"targets":row["tokens"]}
        if row.get("weights_name"):
            require(sha256(storage/"checkpoints"/name/"export"/row["weights_name"])==row["weights_sha256"],f"{name}: weights")
            flags["checkpoint_files"] += 1
        for split in ("dev","test"):
            if split+"_nll" not in row:
                continue
            n = row[split+"_tokens"]
            nll,accuracy = row[split+"_nll"],row[split+"_accuracy"]
            require(n==corpora[stage]["splits"][split]["tokens"]-1 and math.isfinite(nll) and nll>=0, f"{name}/{split}: NLL or tokens")
            require(0<=accuracy<=1 and math.isclose(accuracy*n,round(accuracy*n),rel_tol=0,abs_tol=1e-7),f"{name}: accuracy")
            check[split] = {"targets":n,"correct_from_accuracy":round(accuracy*n),"nll":nll,"ppl":math.exp(nll)}
        devlog = json_lines(folder/"evaluation.jsonl")
        if devlog:
            last = devlog[-1]
            require((last["targets_scored"],last["nll_so_far"],last["accuracy_so_far"])==
                    (row["dev_tokens"],row["dev_nll"],row["dev_accuracy"]), f"{name}: full development log")
            flags["full_dev_logs"] += 1
        if "test" in check:
            progress = json_lines(folder/"test_progress.jsonl")
            require(progress[-1]["targets_scored"]==progress[-1]["targets_to_score"]==row["test_tokens"],f"{name}: test coverage")
            flags["full_test_coverage_logs"] += 1
        if row["tokens"]:
            require(math.isclose(row["tokens"]/row["train_seconds"],row["tokens_per_sec"]),f"{name}: throughput")
        check.update(optimizer_seconds=row["train_seconds"],peak_gpu_mib=row["peak_vram_mb"])
        for f in sorted(folder.glob("width-*.json")):
            width_from_rays(read_json(f))
            flags["hybrid_width_files"] += 1
        for filename in ("flatness.json","score-flatness.json"):
            if not (folder/filename).is_file():
                continue
            geom = read_json(folder/filename)
            require(geom["run"]==name and geom["split"]=="train" and geom["data_manifest_sha256"]==row["data_manifest_sha256"]
                    and geom["checkpoint_file_sha256"]==row.get("weights_sha256"), f"{name}/{filename}: provenance")
            if filename=="flatness.json":
                point,curv = geom["width"],geom["curvature"]
                draws = curv["draws"]
                require(len(draws)==8 and point["weights_restored"],f"{name}: curvature provenance")
                rms = math.sqrt(sum(d["squared_rms"] for d in draws)/len(draws))
                trace = sum(d["trace_per_parameter"] for d in draws)/len(draws)
                require(math.isclose(rms,curv["rms_curvature"]) and math.isclose(trace,curv["trace_per_parameter"],abs_tol=1e-14),name)
            else:
                point = geom["score"]
                require(math.isclose(sum(d["curvature"] for d in point["directions"])/len(point["directions"]),
                                     point["mean_directional_curvature"]),f"{name}: score curvature")
            check[filename] = width_from_rays(point)
            flags[filename] += 1
        if method=="replay":
            donor = results/row["donor"]/"schedule.json"
            donor_run = read_json(donor.parent/"summary.json")
            require(donor_run["method"] == "adaptive" and donor_run["seed"] == 21+(row["seed"]-22)%8,
                    f"{name}: donor violates the registered cyclic permutation")
            require(read_json(donor)["changes"]==read_json(folder/"schedule.json")["changes"],f"{name}: replay coefficients")
            flags["replayed_schedules"] += 1
        phase = "diagnostic" if name in exclusions else row["phase"]
        groups[(stage,phase,method,row["ratio"],row["tokens"])].append(check)
        rows.append(check)
    cohorts = []
    for (stage,phase,method,ratio,budget), records in sorted(groups.items()):
        group = {"stage":stage,"phase":phase,"method":method,"ratio":ratio,"budget":budget,"n":len(records)}
        for split in ("dev","test"):
            scores = [r[split] for r in records if split in r]
            if scores:
                group[split] = {m:median(s[m] for s in scores) for m in ("nll","ppl")}
        cohorts.append(group)
    return {"counts":dict(flags),"runs":rows,"cohorts":cohorts}
