"""Registered comparisons for third-derivative training on a fixed test corpus.

Seeds are independent experimental units. Positive deltas mean worse prediction for the
third-order method. The module consumes ordinary JSON-compatible result records so the
CLI, static report, and interactive explorer can share the same inference.
"""

from math import comb, isfinite
from statistics import median


_METHODS = ("ce", "trace", "third")
_SEEDS = range(1, 9)
_HORIZON = {"stories": 2**24, "abstracts": 2**19}


def _number(value):
    """Reject missing, boolean and nonfinite values before constructing measures or plots."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _comparison(records, baseline):
    """Apply the registered paired sign test and symmetric distribution-free median interval."""
    pairs = []
    for seed in _SEEDS:
        third = records[seed, "third"]["test_nll"]
        other = records[seed, baseline]["test_nll"]
        pairs.append({"seed": seed, "third_nll": third, "baseline_nll": other, "delta": third - other})

    ordered = sorted(pair["delta"] for pair in pairs)
    wins = sum(d < 0 for d in ordered)
    losses = sum(d > 0 for d in ordered)
    discordant = wins + losses
    # Exact upper binomial tail under fair signs conditional on discordant pairs.
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html
    p_raw = sum(comb(discordant, k) for k in range(wins, discordant + 1)) / 2**discordant

    # If m is a continuous population median, #{observations < m} has Bin(n, 1/2) law.
    # Choose the narrowest symmetric order-statistic interval meeting the registered level.
    # Equations 29–30: https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.2119.pdf
    n = len(ordered)
    rank = 0
    discarded = 0
    coverage = 1.0
    for k in range(n // 2):
        discarded += comb(n, k)
        candidate = 1 - 2 * discarded / 2**n
        if candidate < 0.95:
            break
        rank, coverage = k + 1, candidate
    # The registered eight pairs admit a finite interval; expose unbounded ends for small n.
    interval = [ordered[rank - 1], ordered[-rank]] if rank else [None, None]
    return {
        "pairs": pairs, "median_delta": median(ordered), "median_ci": interval,
        "ci_coverage": coverage, "wins": wins, "ties": n - discordant, "losses": losses,
        "p_raw": p_raw,
    }


def _time_match(seed, records):
    """Look backward from the shortest complete training run to actual validation evaluations."""
    runs = {method: records[seed, method] for method in _METHODS}
    if any(not _number(run.get("train_seconds")) or run["train_seconds"] <= 0 for run in runs.values()):
        return None
    cutoff = min(run["train_seconds"] for run in runs.values())
    # Production logs evaluate fixed windows at each diagnostic, including the final step.
    # Older homogeneous result files have a single dev_nll field for the same population.
    fixed_windows = any("matched_dev_nll" in run for run in runs.values())
    summary_field = "matched_dev_nll" if fixed_windows else "dev_nll"
    matched = {}
    for method, run in runs.items():
        events = list(run.get("events") or [])
        final = run.get("status") not in {"configured", "in progress", "training", "failed"}
        if final and _number(run.get(summary_field)):
            events.append({
                "tokens": run["tokens"], "train_seconds": run["train_seconds"],
                "dev_nll": run[summary_field],
            })
        eligible = [
            event for event in events
            if _number(event.get("train_seconds")) and 0 <= event["train_seconds"] <= cutoff
            and _number(event.get("dev_nll")) and event["dev_nll"] >= 0
            and _number(event.get("tokens")) and event["tokens"] >= 0
        ]
        if not eligible:
            return None
        # max() takes the first equal timestamp, giving a real event priority over its summary.
        event = max(eligible, key=lambda x: x["train_seconds"])
        matched[method] = {key: event[key] for key in ("tokens", "train_seconds", "dev_nll")}
        matched[method]["staleness_seconds"] = cutoff - event["train_seconds"]
    return {"seed": seed, "cutoff_seconds": cutoff, "by_method": matched}


def _inconsistency(records):
    """Check optional provenance as an all-or-none contract within a completed scored matrix."""
    for field in ("freeze_id", "test_manifest_sha256", "test_tokens"):
        values = {row.get(field) for row in records.values()}
        if len(values) > 1:
            return f"The stage has inconsistent {field} values across final checkpoints."
    for method in ("trace", "third"):
        ratios = {records[seed, method].get("ratio") for seed in _SEEDS}
        if len(ratios) > 1:
            return f"The frozen {method} regularization ratio changes across seeds."
    return None


def analyze_stage(summaries: list[dict], stage: str) -> dict:
    """Analyze the fixed three-arm matrix after every registered checkpoint has a final score.

    Partial matrices expose progress and eligible elapsed-time development comparisons.
    Duplicate rows or incompatible provenance invalidate inference for that stage.
    """
    horizon = _HORIZON[stage]
    result = {
        "stage": stage, "status": "pending", "complete": False, "success": None,
        "n_expected_seeds": len(_SEEDS), "n_complete_seeds": 0, "missing": [],
        "comparisons": {}, "matched_time": [], "reason": "Awaiting confirmatory runs.",
    }
    records = {}
    for row in summaries:
        seed, method = row.get("seed"), row.get("method")
        if (row.get("stage") != stage or row.get("phase") != "confirm" or method not in _METHODS
                or type(seed) is not int or seed not in _SEEDS):
            continue
        key = (seed, method)
        if key in records:
            result.update(status="invalid", reason=f"Duplicate final-run records for seed {seed}, {method}.")
            return result
        if row.get("target_tokens") is not None and row["target_tokens"] != horizon:
            result.update(status="invalid", reason=f"The configured {method} budget differs from registration.")
            return result
        records[key] = row
    if not records:
        return result

    for seed in _SEEDS:
        missing_methods = [
            method for method in _METHODS if records.get((seed, method), {}).get("tokens") != horizon
        ]
        if missing_methods:
            result["missing"].extend(f"Seed {seed} {method} full horizon" for method in missing_methods)
        else:
            result["n_complete_seeds"] += 1
            timing = _time_match(seed, records)
            if timing is not None:
                result["matched_time"].append(timing)
    if result["missing"]:
        result.update(status="incomplete", reason=f"All checkpoints must reach {horizon:,} target tokens.")
        return result

    # Inspect the test scores only after establishing complete training coverage.
    for (seed, method), row in records.items():
        score = row.get("test_nll")
        if score is None:
            result["missing"].append(f"Seed {seed} {method} final test score")
        elif not _number(score) or score < 0:
            result.update(status="invalid", reason=f"Invalid test NLL for seed {seed}, {method}.")
            return result
    if result["missing"]:
        result.update(status="incomplete", reason="Awaiting the complete frozen set of final test scores.")
        return result
    issue = _inconsistency(records)
    if issue:
        result.update(status="invalid", reason=issue)
        return result

    comparisons = {baseline: _comparison(records, baseline) for baseline in ("ce", "trace")}
    # Holm step-down: adjusted p-values are monotone in raw-p rank; ties receive equal values.
    # https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html
    running_max = 0.0
    for index, stats in enumerate(sorted(comparisons.values(), key=lambda item: item["p_raw"])):
        running_max = max(running_max, stats["p_raw"] * (len(comparisons) - index))
        stats["p_holm"] = min(1.0, running_max)
        if stats["p_holm"] <= 0.05:
            stats["interpretation"] = "improved"
        elif stats["median_ci"][0] > 0:
            stats["interpretation"] = "adverse"
        else:
            stats["interpretation"] = "inconclusive"
    success = all(stats["p_holm"] <= 0.05 for stats in comparisons.values())
    if success:
        status, reason = "confirmed", "Both registered superiority comparisons passed."
    elif any(stats["interpretation"] == "adverse" for stats in comparisons.values()):
        status, reason = "adverse", "A median-difference interval favors a baseline."
    else:
        status, reason = "inconclusive", "The registered two-comparison superiority criterion was unmet."
    result.update(status=status, complete=True, success=success, comparisons=comparisons, reason=reason)
    return result
