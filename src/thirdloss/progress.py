"""Compute study progress and pre-test schedule estimates from timestamped pilot records."""

from datetime import datetime

from .records import HORIZONS, json_lines, read_json, time_now, write_json
from .report_records import atomic_text, study_snapshot


def week_schedule(project):
    """Freeze a wall-time projection from both stages without reading either test token stream.

    Each timed pilot includes its training-loop diagnostics. The interval from the final
    step to the first saved sample also includes a checkpoint write and one generated text,
    so scaling that interval by the test/dev token ratio is a conservative scoring proxy.
    """
    root = project/"results"
    target = root/"feasibility"/"one-week.json"
    if target.exists():
        return read_json(target)
    if any(not (target.parent/f"{s}.json").exists() for s in HORIZONS):
        return None
    arms = []
    def stamp(value):
        return datetime.fromisoformat(value).timestamp()
    for stage, horizon in HORIZONS.items():
        splits = read_json(root/"datasets"/f"{stage}.json")["splits"]
        for arm in read_json(target.parent/f"{stage}.json")["arms"]:
            path = root/arm["pilot_run"]
            summary = read_json(path/"summary.json")
            events = json_lines(path/"events.jsonl")
            first, final = events[0], events[-1]
            sample = json_lines(path/"samples.jsonl")[0]
            full_dev = max(1, stamp(sample["timestamp"]) - stamp(final["timestamp"]) + 1)
            # Scale *all* in-loop wall time with targets. At confirmation the frequency
            # of diagnostic checkpoints per target is lower than or equal to that in pilots.
            loop = max(summary["train_seconds"], stamp(final["timestamp"])-stamp(first["timestamp"])
                       + first["train_seconds"] + 1)
            finalizing = max(full_dev, stamp(summary["finished_at"])-stamp(final["timestamp"]) + 1)
            test = full_dev * (splits["test"]["tokens"]-1)/(splits["dev"]["tokens"]-1)
            hours = 8*(horizon/summary["tokens"]*loop + finalizing + test)/3600
            arms.append({"stage":stage, "method":arm["method"], "pilot_run":arm["pilot_run"],
                         "pilot_tokens_per_second":arm["tokens_per_sec"], "peak_allocated_mib":arm["peak_vram_mb"],
                         "pilot_loop_seconds":loop, "pilot_finalizing_seconds":finalizing,
                         "projected_test_seconds_per_run":test, "projected_hours_all_seeds":hours})
    # Anchor the seven-day allowance at the first optimized training update, not at forecast time.
    first = json_lines(root/"stories-pilot-s00-third-r03"/"events.jsonl")[0]
    checked = time_now()
    hours_left = 7*24 - (stamp(checked)-stamp(first["timestamp"]))/3600
    projected = sum(a["projected_hours_all_seeds"] for a in arms)
    result = {"computed_at":checked,"first_training_update_at":first["timestamp"],"arms":arms,
              "hours_left_in_week":hours_left,"projected_confirmation_and_scoring_hours":projected,
              "hours_available_for_other_work":hours_left-projected,"fits_measured_budget":projected<=hours_left,
              "scope":"All 48 confirmations and test evaluations. Remaining secondary pilots, process startup, "
                      "publishing, downtime and retries use the reported headroom. Times are observational projections."}
    write_json(target,result)
    return result


def progress(project):
    study = study_snapshot(project)
    runs = [r for r in study["runs"] if r.get("phase") in {"control","pilot","confirm"}]
    done = [r for r in runs if r["status"] in {"complete","evaluated"}]
    tests = [r for r in done if "test_nll" in r]
    # Each stage has seven development candidates, two free controls, three ablations,
    # three arms times eight confirmed seeds and the same number of test evaluations.
    total = len(HORIZONS) * (7+2+3+2*3*8)
    lines = ["# Study progress",f"Updated {time_now()}.",f"{len(done)} training/control records and "
             f"{len(tests)} final evaluations are complete. This is {(len(done)+len(tests))/total:.1%} "
             f"of {total} planned model milestones.", "## Current record"]
    for stage,horizon in HORIZONS.items():
        rows = [r for r in done if r.get("stage")==stage]
        live = [r for r in runs if r.get("stage")==stage and r not in done]
        status = ", ".join(f"{r['id']} ({r['status']}, {r.get('tokens',0):,} targets)" for r in live)
        lines.append(f"**{stage}** has {len(rows)} completed runs. "
                     + (f"Current records: {status}." if live else "The next milestone is determined by the run matrix."))
        path = project/"results"/"feasibility"/f"{stage}.json"
        if path.exists():
            spec = read_json(path)
            remaining = 0.0
            for arm in spec["arms"]:
                completed = sum(r.get("tokens",0) for r in rows if r.get("phase")=="confirm" and r["method"]==arm["method"])
                remaining += max(0,8*horizon-completed)/arm["tokens_per_sec"]/3600
            lines.append(f"Pilot rates project {remaining:.2f} remaining confirmation GPU-hours, "
                         "excluding validation, exports and uploads.")
        outcome = study["stages"][stage]
        lines.append(f"Statistical status: {outcome['status']}. {outcome['reason']}")
    schedule = week_schedule(project)
    if schedule:
        lines += ["## One-week feasibility", f"At the pre-test check on {schedule['computed_at']}, pilot timings projected "
                  f"{schedule['projected_confirmation_and_scoring_hours']:.2f} hours for all confirmatory training and "
                  f"scoring, with {schedule['hours_available_for_other_work']:.2f} hours of the week available for "
                  "secondary pilots, setup, publication and interruptions. [Timing and GPU memory by method]"
                  "(../results/feasibility/one-week.json)"]
    followup = study["hybrid"]
    lines += ["## TinyStories hybrid follow-up",f"{followup['completed_arms']} of 48 full runs and "
              f"{followup['completed_trunks']} of 8 shared checkpoints complete. "
              f"{followup['status']}. [Per-seed widths and development scores](hybrid/results.md)"]
    extra = hybrid_schedule(project,schedule)
    if extra:
        lines.append(f"The first measured set of hybrid arms projects {extra['remaining_hybrid_hours']:.2f} "
                     f"further hours from that checkpoint, including the eight replays. With the original "
                     f"confirmations and final scoring, the projected remaining work at the check was "
                     f"{extra['combined_hours']:.2f} hours with {extra['hours_left_in_week']:.2f} hours left in the week. "
                     "[Wall-time assumptions, measured memory and inputs](../results/feasibility/hybrid-week.json)")
    lines += ["## Monitoring","Inspect runs lasting over 10, 30 and 60 minutes at 5, 15 and 30 minute intervals "
              "respectively. The live dashboard refreshes between those checks. "
              "[Study design](plan.md) · [Run matrix](planned-runs.md) · [Experiment ledger](experiments/experiments.md)"]
    body = "\n\n".join(lines)+"\n"
    atomic_text(project/"reports"/"progress.md",body)
    return body


def hybrid_schedule(project,primary):
    """Freeze a joint timing forecast from the first six real follow-up jobs before sealed scoring."""
    root = project/"results"
    out = root/"feasibility"/"hybrid-week.json"
    if out.exists():
        return read_json(out)
    if not primary:
        return None
    arms = {kind:root/("stories-"+("branch" if kind=="trunk" else "hybrid")+f"-s21-{kind}-r01")
            for kind in ("trunk","adaptive","late","trace","strong","always")}
    if any(not (folder/"summary.json").exists() for folder in arms.values()):
        return None
    summaries = {kind:read_json(folder/"summary.json") for kind,folder in arms.items()}
    def stamp(value):
        return datetime.fromisoformat(value).timestamp()
    first = json_lines(arms["trunk"]/"events.jsonl")[0]
    start = stamp(first["timestamp"])-first["train_seconds"]
    end = stamp(summaries["always"]["finished_at"])
    observed = (end-start)/3600
    replay = (stamp(summaries["adaptive"]["finished_at"])-stamp(summaries["trunk"]["finished_at"]))/3600
    if not (0<replay<observed):
        raise ValueError("Invalid hybrid wall-time observation order")
    remaining = 7*observed+8*replay
    combined = remaining+primary["projected_confirmation_and_scoring_hours"]
    left = 168-(end-stamp(primary["first_training_update_at"]))/3600
    record = {"computed_at":time_now(),"as_of":summaries["always"]["finished_at"],"seed":21,
              "run_ids":[s["id"] for s in summaries.values()],"observed_six_jobs_hours":observed,
              "estimated_one_replay_hours":replay,"remaining_hybrid_hours":remaining,
              "combined_hours":combined,"hours_left_in_week":left,"fits_measured_budget":combined<=left,
              "peak_allocated_mib":max(s["peak_vram_mb"] for s in summaries.values()),
              "basis":"Observed wall time includes shared training, calibration, widths, development scoring, "
                      "intervening publications and interruptions. Repeat the six jobs for seven more seeds. "
                      "Budget each replay as the elapsed trunk-completion to adaptive-completion interval. "
                      "Remaining adapter pilots and tool or network interruptions use the residual headroom."}
    write_json(out,record)
    return record
