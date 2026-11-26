"""Read the run ledger shared by the paper, live dashboard and static explorer."""

import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

from .analysis import analyze_stage
from .flatness_stats import compact_width
from .hybrid_results import hybrid_results
from .records import GITHUB as REPOSITORY, PAGES


STAGES = {"stories": "TinyStories", "abstracts": "Research abstracts"}
METHODS = {
    "ce": "Ordinary AdamW",
    "trace": "Hessian trace",
    "third": "Third derivative",
    "hessian_norm": "Squared Hessian norm",
    "sham": "Randomized gradient signs",
    "combined": "Trace + third derivative",
    "initial": "Initial checkpoint",
    "unigram": "Unigram",
    "trunk":"Shared trace checkpoint","adaptive":"Curvature-dependent hybrid","late":"Fixed late hybrid",
    "replay":"Cross-seed replay","strong":"Stronger trace","always":"Always-on hybrid",
}
COLORS = {
    "ce": "#374d67", "trace": "#ac582a", "third": "#007166",
    "hessian_norm": "#64569c", "sham": "#ac3c66", "combined": "#3974a2",
    "initial": "#674e35", "unigram": "#73736c",
    "trunk":"#705d43","adaptive":"#007361","late":"#405fa6","replay":"#9b486c","strong":"#a66f0c","always":"#594489",
}
FIELDS = (
    "id", "stage", "method", "phase", "seed", "ratio", "tokens", "steps",
    "train_seconds", "tokens_per_sec", "peak_vram_mb", "dev_nll", "dev_accuracy",
    "test_nll", "test_accuracy", "status", "target_tokens", "budget", "parameters",
    "trainable_parameters", "lambda", "coefficients", "device", "learning_rate",
    "batch_size", "architecture", "commit", "dataset_revision", "data_hash",
    "freeze_id", "test_manifest_sha256", "test_tokens", "data_manifest_sha256",
    "token_budget", "batch_windows", "microbatch", "context", "weights_sha256", "dev_tokens",
    "git_revision", "gpu", "torch", "matched_dev_nll", "finished_at", "initial_trainable_sha256",
    "derivative_dtype", "derivative_device", "host_probe_seconds", "training_seconds_excluding_host_probes", "cpu_threads",
    "process_peak_rss_mib", "evaluation_batch_windows", "test_seconds", "evaluated_at",
    "parent","parent_restart_sha256","donor","alpha","cap","delta","reference_rms","zero_steps","final_third_lambda",
    "inherited_tokens","inherited_train_seconds",
)
EVENT_FIELDS = (
    "step", "tokens", "train_seconds", "loss", "accuracy", "penalty", "dev_nll",
    "dev_accuracy", "timestamp", "status", "peak_vram_mb",
    "training_seconds_excluding_host_probes", "host_probe_seconds",
    "curvature_q","curvature_rms","trace_lambda","third_lambda","reference_rms","monitor_mean_nll","gradient_norm",
)


def atomic_text(path: Path, text: str) -> None:
    """Replace a complete UTF-8 artifact so a local dashboard never reads half a report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    with NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                            delete=False, suffix=".tmp") as handle:
        handle.write(text)
        name = handle.name
    try:
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def read_json(path: Path) -> dict:
    """Small summaries and configurations are atomically produced by the trainer."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def read_lines(path: Path) -> list[dict]:
    """Ignore a concurrent partial trailing write, but surface damaged complete records."""
    if not path.exists():
        return []
    records = []
    with path.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except (ValueError, UnicodeDecodeError) as exc:
                if not line.endswith(b"\n"):
                    break
                raise ValueError(f"Unreadable JSON record {path}:{number}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Expected a JSON object at {path}:{number}")
            records.append(record)
    return records


def finite(value) -> bool:
    """Exclude missing values, booleans and nonfinite numbers from graphs and summaries."""
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def fmt(value, digits: int = 3) -> str:
    """Use a visible missing-value marker instead of completing an unobserved measurement."""
    return f"{value:,.{digits}f}" if finite(value) else "—"


def markdown_cell(value):
    """Keep arbitrary labels and run identifiers inside one GitHub Markdown table cell."""
    return str(value).replace("|","\\|").replace("\n"," ")


def markdown_table(rows,headings):
    def row(values):
        return "| "+" | ".join(markdown_cell(value) for value in values)+" |"
    return "\n".join([row(headings),row(["---"]*len(headings)),*(row(values) for values in rows)])


def run_record(folder: Path) -> dict:
    """Join configuration, events and final summary with explicit completion state."""
    state = read_json(folder / "state.json")
    config = {**state,**read_json(folder / "config.json")}
    summary = read_json(folder / "summary.json")
    last_error = read_json(folder / "failure.json")
    events = read_lines(folder / "events.jsonl")
    if state.get("status") == "paused" and not summary:
        # The optimizer can replay later logged updates only from the last saved state.
        events = [event for event in events if event.get("step", 0) <= state["checkpoint_step"]]
    record = {key: config[key] for key in FIELDS if key in config}
    # Calibration can fail before the trainer writes the final configuration.
    identity = re.fullmatch(r"(stories|abstracts)-(\w+)-s(\d+)-(\w+)-r(\d+)(?:-fp64)?", folder.name)
    if identity and not config:
        stage, phase, seed, method, ratio = identity.groups()
        record.update(stage=stage, phase=phase, seed=int(seed), method=method, ratio=int(ratio) / 100)
    for event in events:
        for key in ("tokens", "train_seconds", "peak_vram_mb", "dev_nll", "dev_accuracy", "status"):
            if event.get(key) is not None:
                record[key] = event[key]
        if event.get("step") is not None:
            record["steps"] = event["step"]
    record.update({key: summary[key] for key in FIELDS if key in summary})
    # The completed summary contains the token-weighted full-split NLL. Live events use a smaller probe.
    # https://huggingface.co/docs/transformers/perplexity
    for split in ("dev", "test"):
        nll = summary.get(f"{split}_nll")
        if finite(nll) and 0 <= nll <= math.log(sys.float_info.max):
            record[f"{split}_perplexity"] = math.exp(nll)
    if "token_budget" in record:
        record["target_tokens"] = record["token_budget"]
    record["id"] = folder.name
    if "targets_scored" in state and not summary:
        record["evaluation_progress"] = state
    test_state = read_json(folder / "test_state.json")
    if test_state and "test_nll" not in summary:
        record["evaluation_progress"] = test_state
    failures = read_json(folder / "attempts.json").get("failures", [])
    if last_error and last_error not in failures:
        failures.append(last_error)
    if failures:
        record["failures"] = failures
    resumed = bool(last_error and events and events[-1].get("timestamp", "")>last_error.get("timestamp", ""))
    if state.get("status") == "paused" and not summary:
        record["status"] = "paused"
    elif last_error and not summary and not resumed:
        record["status"] = "failed"
        record["error"] = str(last_error.get("error", "Recorded failure"))
    elif resumed and not summary:
        record["status"] = "scoring development" if record.get("tokens")==record.get("token_budget") else "training"
    else:
        record.setdefault("status", "complete" if summary else "in progress" if events else "configured")
    record["events"] = []
    for event in events:
        row = {k: event[k] for k in EVENT_FIELDS if event.get(k) is not None}
        for kind, details in (event.get("derivatives") or {}).items():
            if isinstance(details, dict) and finite(details.get("estimate")):
                row["raw_" + kind] = details["estimate"]
        record["events"].append(row)
    if record.get("phase") in {"hybrid","branch"}:
        record["widths"] = {}
        for path in sorted(folder.glob("width-*.json")):
            width = read_json(path)
            point = compact_width(width)
            record["widths"][str(width["step"])] = point
            record["events"].append({"step":width["step"],"tokens":width["tokens"],
                                     "width":width["width"],"width_probe_nll":width["baseline_nll"]})
        record["events"].sort(key=lambda row:row.get("step",0))
    diagnostic=read_json(folder/"flatness.json")
    if diagnostic:
        if (diagnostic["run"]!=folder.name or diagnostic["checkpoint_file_sha256"]!=record.get("weights_sha256")
                or diagnostic["data_manifest_sha256"]!=record.get("data_manifest_sha256")
                or diagnostic["split"]!="train" or not diagnostic["width"]["weights_restored"]):
            raise ValueError(f"Checkpoint geometry provenance differs for {folder.name}")
        record["flatness"]={**compact_width(diagnostic["width"]),
                            **{k:diagnostic[k] for k in ("protocol","probe_windows_sha256","width_device")},
                            **{k:diagnostic["curvature"][k] for k in ("rms_curvature","trace_per_parameter")},
                            "hessian_device":diagnostic["curvature"]["device"],"hessian_dtype":diagnostic["curvature"]["dtype"],
                            "dimensions":diagnostic["curvature"]["dimensions"]}
        record["events"].append({"step":record["steps"],"tokens":record["tokens"],"train_seconds":record["train_seconds"],
                                 "width":diagnostic["width"]["width"],"checkpoint_rms":diagnostic["curvature"]["rms_curvature"],
                                 "checkpoint_signed_trace":diagnostic["curvature"]["trace_per_parameter"]})
    output=read_json(folder/"score-flatness.json")
    if output:
        if (output["run"]!=folder.name or output["checkpoint_file_sha256"]!=record.get("weights_sha256")
                or output["split"]!="train" or output["data_manifest_sha256"]!=record.get("data_manifest_sha256")):
            raise ValueError(f"Output-score geometry provenance differs for {folder.name}")
        record["score_flatness"]={**compact_width(output["score"]),"probe_windows_sha256":output["probe_windows_sha256"],
                                  "protocol":output["protocol"]}
        record["events"].append({"step":record["steps"],"tokens":record["tokens"],"train_seconds":record["train_seconds"],
                                 "score_width":output["score"]["width"],
                                 "score_curvature":output["score"]["mean_directional_curvature"]})
    record["samples"] = read_lines(folder / "samples.jsonl")
    return record


def display_events(events: list[dict], maximum: int = 240) -> list[dict]:
    """Thin evenly by log index for display, keeping both endpoints and every validation event."""
    if len(events) <= maximum:
        return events
    keep = {round(i * (len(events) - 1) / (maximum - 1)) for i in range(maximum)}
    keep.update(i for i, event in enumerate(events) if finite(event.get("dev_nll")) or "width" in event or "score_width" in event)
    return [events[i] for i in sorted(keep)]


def pilot_differences(runs: list[dict], stage: str, selection: dict) -> list[dict]:
    """Compare one reserved seed at an identical observed horizon; keep the tuning status explicit."""
    ratios = selection.get("ratios", {})
    desired = {"ce": 0.0, "trace": ratios.get("trace", 0.03), "third": ratios.get("third", 0.03),
               "hessian_norm": 0.03, "sham": ratios.get("third", 0.03), "combined": ratios.get("third", 0.03)}
    by_method = {r["method"]: r for r in runs if r.get("stage") == stage and r.get("phase") == "pilot"
                 and r.get("seed") == 0 and completed(r) and finite(r.get("dev_nll"))
                 and r.get("method") in desired and r.get("ratio") == desired[r["method"]]}
    third = by_method.get("third")
    if not third:
        return []
    return [{"method": method, "third_id": third["id"], "comparison_id": other["id"],
             "tokens": third["tokens"], "delta": third["dev_nll"] - other["dev_nll"],
             "third_nll": third["dev_nll"], "baseline_nll": other["dev_nll"],
             "strength_basis": "strengths selected on development" if ratios else "initial pilot strengths"}
            for method, other in by_method.items() if method != "third" and other.get("tokens") == third.get("tokens")]


def study_snapshot(root: Path = Path(".")) -> dict:
    """Return a JSON-ready live view. Inference uses full logs before display thinning."""
    directory = Path(root) / "results"
    runs = []
    for folder in sorted(directory.glob("*")):
        if folder.is_dir() and any((folder / f).is_file() for f in ("config.json", "summary.json", "failure.json", "state.json")):
            runs.append(run_record(folder))
    exclusions = read_json(directory/"verification"/"numerical-exclusions.json")
    restarts = {}
    for path in sorted((directory/"verification").glob("*-system-restart.json")):
        audit = read_json(path)
        restarts.setdefault(audit["run"],[]).append({**audit,"source":path.name})
    for run in runs:
        if run["id"] in exclusions:
            run.update(registered_phase=run["phase"], phase="diagnostic", precision_audit=exclusions[run["id"]])
        if run["id"] in restarts:
            run["restart_audits"] = restarts[run["id"]]
    stages = {stage: analyze_stage(runs, stage) for stage in STAGES}
    for run in runs:
        run["events_total"] = len(run["events"])
        run["events"] = display_events(run["events"])
    context = {stage: {key: read_json(directory / key / f"{stage}.json")
                       for key in ("datasets", "selection", "feasibility")} for stage in STAGES}
    pilots = {s: pilot_differences(runs, s, context[s]["selection"]) for s in STAGES}
    numerics = {key:read_json(directory/"verification"/(key+".json")) for key in
                ("pythia-joint-cuda","pythia-fp64-agreement","pythia-fp64-cpu","pythia-fp64-cuda","stories-full-gradient")}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runs": runs, "stages": stages, "method_names": METHODS, "stage_names": STAGES,
        "colors": COLORS, "context": context, "pilot_comparisons": pilots,"numerics":numerics,
        "frozen_stages": [stage for stage in STAGES if (directory/"freeze"/f"{stage}.json").is_file()],
        "seed_sensitivity": (read_json(directory / "analysis" / "seed-sensitivity.json")
                             if (directory / "freeze" / "seed-sensitivity.json").is_file() else None),
        "hybrid":hybrid_results(runs),
    }


def completed(run: dict) -> bool:
    return run.get("status", "").lower() in {"complete", "completed", "finished", "evaluated", "success"}


def example_runs(runs):
    """Choose one completed registered checkpoint per method independently of sample text or scores."""
    examples = {}
    for run in sorted(runs,key=lambda r:r["id"]):
        if completed(run) and run["phase"] in {"confirm","pilot","control","hybrid"} and run["samples"]:
            examples.setdefault((run["stage"],run["method"]),run)
    return list(examples.values())


def describe_difference(delta) -> str:
    if delta == 0:
        return "identical development NLL"
    direction = "lower" if delta < 0 else "higher"
    return f"{abs(delta):.5f} nats per target token {direction}"


def verdict_text(result: dict, *, paired=False) -> str:
    """Use the analysis contract to distinguish an incomplete matrix from an inconclusive trial."""
    status = result.get("status")
    count = result.get("n_complete_seeds", 0)
    goal = result.get("n_expected_seeds", 8)
    conclusions = {
        "confirmed": "Third-order training improved test NLL over both baselines under the registered decision rule.",
        "inconclusive": "The registered test of superiority over both baselines was inconclusive.",
        "adverse": "The median test-loss difference favored at least one baseline across its full uncertainty interval.",
    }
    if status in conclusions:
        sentence = conclusions[status]
        if paired:
            ce, trace = (result["comparisons"][m] for m in ("ce", "trace"))
            sentence += (f" Third order had lower test NLL in {ce['wins']}/{len(ce['pairs'])} pairs against AdamW "
                         f"(Holm p = {ce['p_holm']:.5f}) and {trace['wins']}/{len(trace['pairs'])} against "
                         f"Hessian trace (Holm p = {trace['p_holm']:.5f}).")
        return sentence
    if status == "invalid":
        return f"The stage records require review. {result.get('reason') or 'See the analysis ledger.'}"
    return f"Awaiting paired test results ({count} of {goal} full-horizon training triplets)."
