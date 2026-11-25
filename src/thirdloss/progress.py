"""Compute study progress and throughput-based remaining confirmation time from result files."""

from .records import HORIZONS, read_json, time_now
from .report_records import atomic_text, study_snapshot


def progress(project):
    study = study_snapshot(project)
    runs = [r for r in study["runs"] if r.get("phase")!="smoke"]
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
    lines += ["## Monitoring","Inspect runs lasting over 10, 30 and 60 minutes at 5, 15 and 30 minute intervals "
              "respectively. The live dashboard refreshes between those checks. "
              "[Study design](plan.md) · [Run matrix](planned-runs.md) · [Experiment ledger](experiments/experiments.md)"]
    body = "\n\n".join(lines)+"\n"
    atomic_text(project/"reports"/"progress.md",body)
    return body
