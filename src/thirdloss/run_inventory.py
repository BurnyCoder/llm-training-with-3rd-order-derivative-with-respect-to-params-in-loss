"""Reconcile the registered queue with observed training, evaluation and checkpoint geometry."""

from .records import HORIZONS, RATIOS, run_name
from .report_records import METHODS, STAGES, completed, finite, markdown_table


def scheduled_jobs(study):
    """Yield the coordinator's training and test order. Strengths become known at development selection."""
    def job(stage, phase, method, seed, ratio, action="fit"):
        return action, stage, phase, method, seed, ratio

    def selected(stage, method):
        return study["context"][stage]["selection"].get("ratios", {}).get(method)

    def full(stage, seed, method, action="fit"):
        return job(stage, "confirm", method, seed, 0. if method == "ce" else selected(stage, method), action)

    def hybrid(seed, method):
        return job("stories", "branch" if method == "trunk" else "hybrid", method, seed, .01)

    for stage in STAGES:
        yield job(stage, "pilot", "third", 0, .03)
        for method in ("initial", "unigram"):
            yield job(stage, "control", method, 0, 0.)
        yield job(stage, "pilot", "ce", 0, 0.)
        for method in ("trace", "third"):
            for ratio in RATIOS:
                if (method, ratio) != ("third", .03):
                    yield job(stage, "pilot", method, 0, ratio)
        for method in ("hessian_norm", "sham", "combined"):
            yield job(stage, "pilot", method, 0, .03 if method == "hessian_norm" else selected(stage, "third"))
    arms = ("trunk", "adaptive", "late", "trace", "strong", "always")
    for method in arms:
        yield hybrid(21, method)
    for stage in STAGES:
        for method in ("third", "ce", "trace"):
            yield full(stage, 1, method)
    for stage in STAGES:
        for seed in range(2, 9):
            for method in ("third", "ce", "trace"):
                yield full(stage, seed, method)
        for seed in range(1, 9):
            for method in ("ce", "trace", "third"):
                yield full(stage, seed, method, "test")
    for seed in range(22, 29):
        for method in (*arms, "replay"):
            yield hybrid(seed, method)
    yield hybrid(21, "replay")


def _entry(study, observed, stage, phase, method, seed, ratio, run_id):
    """A full token count still awaits its development summary. Test scoring has a separate state."""
    row = observed.get(run_id, {})
    evaluation = row.get("evaluation_progress", {})
    done = completed(row)
    status = row.get("status", "planned")
    fit = "Complete" if done else status.capitalize()
    if not done and evaluation.get("split") == "dev":
        fit = "Scoring development"
    test = "—"
    if phase == "confirm":
        frozen = stage in study.get("frozen_stages", ()) or bool(row.get("freeze_id"))
        test = "Queued" if frozen else "Awaiting freeze"
        if frozen and finite(row.get("test_nll")):
            test = "Complete"
        elif frozen and evaluation.get("split") == "test":
            test = "Scoring test"
    geometry = "Pending"
    if "score_flatness" in row and ("flatness" in row or method == "unigram"):
        geometry = "Complete"
    elif "score_flatness" in row or "flatness" in row:
        geometry = "Partial"
    target = HORIZONS[stage]
    budget = {"control": 0, "pilot": target//8, "branch": target//2,
              "diagnostic": row.get("tokens", 0)}.get(phase, target)
    strength = f" ({ratio:.0%})" if ratio else ""
    title = f"{STAGES[stage]} · {METHODS[method]} · {phase} seed {seed}{strength}"
    activity = ""
    if test == "Scoring test" or (row and not done and status not in {"queued", "planned", "failed", "paused"}):
        label = "Scoring test" if test == "Scoring test" else fit
        if evaluation.get("targets_to_score"):
            detail = f"{evaluation['targets_scored']:,}/{evaluation['targets_to_score']:,} targets scored"
        else:
            detail = f"{row.get('tokens', 0):,}/{budget:,} training targets"
        activity = f"{title} · {label} · {detail}"
    return {"id": run_id, "stage": stage, "phase": phase, "method": method, "seed": seed,
            "ratio": ratio, "targets": budget, "title": title, "fit": fit, "test": test,
            "geometry": geometry, "activity": activity}


def inventory(study):
    """Summarize every scheduled fit and score, including untrained references and the archived diagnostic."""
    observed = {r["id"]: r for r in study["runs"]}
    fits = {}
    order = []
    next_job = None
    for action, stage, phase, method, seed, ratio in scheduled_jobs(study):
        key = stage, phase, method, seed, ratio
        if action == "fit":
            name = run_name(stage, method, phase, seed, ratio) if ratio is not None else None
            fits[key] = _entry(study, observed, *key, name)
        item = fits[key]
        order.append((key, action))
        if next_job is None and item[action] != "Complete" and not item["activity"]:
            next_job = item["title"] + (" · frozen test" if action == "test" else "")
    rows = list(fits.values())
    for r in observed.values():
        if r["phase"] == "diagnostic":
            rows.append(_entry(study, observed, r["stage"], r["phase"], r["method"], r["seed"], r["ratio"], r["id"]))
    groups = []
    positions = {id(row): i for i, row in enumerate(rows)}
    def group(title, subset, field):
        groups.append({"label": title, "done": sum(r[field] == "Complete" for r in subset), "total": len(subset),
                       "field":field, "members":[positions[id(r)] for r in subset]})
    for stage, name in STAGES.items():
        selected = [r for r in rows if r["stage"] == stage]
        primary = [r for r in selected if r["phase"] == "confirm"]
        group(name+" · development and controls", [r for r in selected if r["phase"] in {"pilot", "control"}], "fit")
        group(name+" · full-budget primary runs", primary, "fit")
        group(name+" · frozen tests", primary, "test")
        group(name+" · checkpoint flatness", selected, "geometry")
    group("TinyStories · shared hybrid checkpoints", [r for r in rows if r["phase"] == "branch"], "fit")
    group("TinyStories · full hybrid runs", [r for r in rows if r["phase"] == "hybrid"], "fit")
    final = bool(study.get("seed_sensitivity"))
    if next_job is None:
        next_job = ("Complete remaining checkpoint flatness" if any(r["geometry"] != "Complete" for r in rows)
                    else "Study complete" if final else "Final seed-sensitivity analysis")
    paused = any(r["fit"] == "Paused" for r in rows)
    return {"groups": groups, "fits": rows, "done": sum(g["done"] for g in groups),
            "total": sum(g["total"] for g in groups), "activity": [r["activity"] for r in rows if r["activity"]],
            "paused": paused, "next": next_job, "final": final, "order":[[positions[id(fits[key])],action] for key,action in order]}


def activity_labels(plan):
    """Keep the current status and conditional resumption wording consistent across publications."""
    if plan["paused"]:
        return "Experiments paused by request. The remaining runs have no scheduled start date", "First run on resumption"
    return " / ".join(plan["activity"]) or "Between recorded training and scoring updates", "Next scheduled work"


def status_lines(study):
    """Label the publication time and distinguish observed activity from the next scheduled job."""
    plan = study["run_inventory"]
    active, next_label = activity_labels(plan)
    lines = [f"**Snapshot at {study['generated_at']}** · {plan['done']}/{plan['total']} experimental milestones complete.",
             f"**Recorded activity** · {active}.", f"**{next_label}** · {plan['next']}."]
    if "forecast" in study:
        low, high = study["forecast"]
        lines.append(f"The measured remaining-time scenarios are {low:.2f}–{high:.2f} machine-hours.")
    return lines


def matrix_markdown(study):
    """List observed and future runs, their separate evaluations, and the source of each completed result."""
    plan = study["run_inventory"]
    lines = ["## Current evidence and remaining runs", *status_lines(study),
             markdown_table([[g["label"],g["done"],g["total"]-g["done"],g["total"]] for g in plan["groups"]],
                            ["Work", "Complete", "Remaining", "Planned"]),
             "The final seed-sensitivity analysis follows every model, frozen test and flatness measurement. "
             "[Final analysis](seed-sensitivity.md) · [Measured time remaining](progress.md)"]
    for stage, name in STAGES.items():
        rows = []
        for r in plan["fits"]:
            if r["stage"] != stage:
                continue
            method = METHODS[r["method"]]
            if r["id"] and r["fit"] != "Planned":
                method = f"[{method}](../results/{r['id']}/)"
            ratio = "After selection" if r["ratio"] is None else f"{r['ratio']:.0%}"
            rows.append([r["phase"],r["seed"],method,ratio,f"{r['targets']:,}",r["fit"],r["test"],r["geometry"]])
        lines += [f"<details><summary>{name} · every planned run</summary>",
                  markdown_table(rows, ["Phase", "Seed", "Arm", "Strength", "Training targets",
                                        "Training and development", "Frozen test", "Flatness"]), "</details>"]
    return "\n\n".join(lines)
