"""Summarize measured follow-up geometry independently of the two frozen test comparisons."""

import math

from .analysis import holm, paired_sign


def hybrid_results(runs):
    """Keep every arm, all horizon-matched pairs and right-censored outcomes in the record."""
    named = {(r["seed"],r["method"]):r for r in runs if r.get("phase")=="hybrid" and r.get("finished_at")}
    trunks = {r["seed"]:r for r in runs if r.get("phase")=="branch" and r.get("finished_at")}
    comparisons,pairs = {},[]
    for baseline in ("late","replay","trace","strong","always"):
        finite_pairs = []
        for seed in range(21,29):
            adaptive,other = named.get((seed,"adaptive")),named.get((seed,baseline))
            if not (adaptive and other):
                continue
            if adaptive["tokens"]!=other["tokens"] or adaptive["tokens"]!=2**24:
                raise ValueError("Hybrid comparisons require full, equal token budgets")
            if (adaptive["initial_trainable_sha256"]!=other["initial_trainable_sha256"] or
                adaptive["data_manifest_sha256"]!=other["data_manifest_sha256"]):
                raise ValueError("Hybrid comparisons require paired initialization and the same corpus")
            values = [r["widths"][str(step)] for r in (adaptive,other) for step in (2048,4096)]
            a0,a1,b0,b1 = values
            if baseline!="always" and (adaptive["parent_restart_sha256"]!=other["parent_restart_sha256"]
                                      or a0["weights_sha256"]!=b0["weights_sha256"]):
                raise ValueError("Hybrid branches do not share the same AdamW checkpoint and width baseline")
            delta = None if any(v["width"] is None for v in values) else (a1["width"]-a0["width"])-(b1["width"]-b0["width"])
            row = {"seed":seed,"comparator":baseline,"delta":delta,
                   "train_probe_nll_delta":a1["baseline_nll"]-b1["baseline_nll"],
                   "comparable_fit":abs(a1["baseline_nll"]-b1["baseline_nll"])<=.02,
                   "dev_nll_delta":adaptive["dev_nll"]-other["dev_nll"]}
            pairs.append(row)
            if delta is not None and math.isfinite(delta):
                finite_pairs.append(row)
        if baseline in {"late","replay"} and len(finite_pairs)==8:
            comparisons[baseline] = paired_sign(finite_pairs,larger=True)
    if len(comparisons)==2:
        holm(comparisons)
        status = "both width comparisons passed" if all(c["p_holm"]<=.05 for c in comparisons.values()) else "width advantage inconclusive"
    else:
        status = "width endpoint censored" if len(named)==48 else "awaiting eight paired width measurements"
    return {"completed_arms":len(named),"completed_trunks":len(trunks),"status":status,"pairs":pairs,
            "comparisons":comparisons,"shared_training_tokens_saved":sum(
                max(0,sum((s,m) in named for m in ("adaptive","late","trace","strong","replay"))-1)*r["tokens"]
                for s,r in trunks.items())}
