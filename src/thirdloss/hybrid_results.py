"""Summarize measured follow-up geometry independently of the two frozen test comparisons."""

import math

from .analysis import holm, paired_sign


def width_contrast(a0, a1, b0, b1, *, shared):
    """Bound (a1−a0)−(b1−b0) from the ray-search brackets. A shared trunk cancels exactly."""
    def endpoints(point):
        hi = point["width_upper"]
        return point["width_lower"], math.inf if hi is None else hi
    alo, ahi = endpoints(a1)
    blo, bhi = endpoints(b1)
    low, high = alo-bhi, ahi-blo
    if not shared:
        al0, ah0 = endpoints(a0)
        bl0, bh0 = endpoints(b0)
        low, high = low+bl0-ah0, high+bh0-al0
    delta = None
    if all(p["width"] is not None for p in (a0,a1,b0,b1)):
        delta = (a1["width"]-a0["width"])-(b1["width"]-b0["width"])
    sign = "wider" if low>0 else "narrower" if high<0 else "tie" if low==high==0 else "unresolved"
    return {"delta":delta, "delta_lower":low if math.isfinite(low) else None,
            "delta_upper":high if math.isfinite(high) else None, "sign":sign}


def attainable_p(losses, ties, planned):
    """Optimistic raw sign-test probability with every unclassified or remaining pair a win."""
    discordant = planned-ties
    return sum(math.comb(discordant, j) for j in range(losses+1))/2**discordant


def hybrid_bound_text(data):
    """Describe a completion bound separately from a test of the observations available so far."""
    fixed = data["attainability"]["late"]
    if fixed["best_raw_p"] <= .05:
        return ""
    return (f"Adaptive was narrower than the fixed ramp in {fixed['narrower']} bracket-resolved pairs. "
            f"Even the most favorable completion of the eight planned pairs gives raw p ≥ {fixed['best_raw_p']:.5f}. "
            "The registered joint width-superiority criterion is unreachable.")


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
            contrast = width_contrast(a0,a1,b0,b1,shared=baseline!="always")
            row = {"seed":seed,"comparator":baseline,**contrast,
                   "train_probe_nll_delta":a1["baseline_nll"]-b1["baseline_nll"],
                   "comparable_fit":abs(a1["baseline_nll"]-b1["baseline_nll"])<=.02,
                   "dev_nll_delta":adaptive["dev_nll"]-other["dev_nll"]}
            pairs.append(row)
            if row["delta"] is not None and math.isfinite(row["delta"]):
                finite_pairs.append(row)
        if baseline in {"late","replay"} and len(finite_pairs)==8:
            comparisons[baseline] = paired_sign(finite_pairs,larger=True)
            comparisons[baseline]["dependent_pairs"] = baseline=="replay"
            comparisons[baseline]["unresolved_signs"] = sum(p["sign"]=="unresolved" for p in finite_pairs)
    limits = {}
    for arm in ("late","replay"):
        observed = [p for p in pairs if p["comparator"]==arm]
        losses = sum(p["sign"]=="narrower" for p in observed)
        ties = sum(p["sign"]=="tie" for p in observed)
        limits[arm] = {"observed":len(observed),"narrower":losses,"resolved_ties":ties,
                       "best_raw_p":attainable_p(losses,ties,8)}
    if len(comparisons)==2:
        holm(comparisons)
        status = ("both nominal midpoint tests passed; replay dependence limits inference"
                  if all(c["p_holm"]<=.05 for c in comparisons.values()) else "registered midpoint criterion unmet")
    else:
        status = "width endpoint censored" if len(named)==48 else "awaiting eight paired width measurements"
    return {"completed_arms":len(named),"completed_trunks":len(trunks),"status":status,"pairs":pairs,"attainability":limits,
            "comparisons":comparisons,"shared_training_tokens_saved":sum(
                max(0,sum((s,m) in named for m in ("adaptive","late","trace","strong","replay"))-1)*r["tokens"]
                for s,r in trunks.items())}
