"""Rebuild the public study artifacts from raw results with one command."""

import json
import re
from pathlib import Path
from statistics import median
from urllib.parse import quote

from .report_figures import build_figures
from .report_paper import write_paper
from .report_records import (
    METHODS, PAGES, STAGES, atomic_text, completed, describe_difference, finite, fmt, study_snapshot,
    verdict_text,
)


def _cell(value) -> str:
    """Keep arbitrary run annotations and identifiers inside one Markdown table cell."""
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(rows: list[list], headings: list[str]) -> str:
    def row(values):
        return "| " + " | ".join(_cell(v) for v in values) + " |"
    return "\n".join([row(headings), row(["---"] * len(headings)), *(row(v) for v in rows)])


def _method(run: dict) -> str:
    return METHODS.get(run.get("method"), run.get("method", "Unknown"))


def _stage(run: dict) -> str:
    return STAGES.get(run.get("stage"), run.get("stage", "Unknown"))


def _ledger_row(run: dict) -> list:
    return [
        _stage(run), _method(run), run.get("phase", "—"), run.get("seed", "—"),
        fmt(run.get("ratio")), fmt(run.get("tokens"), 0), fmt(run.get("dev_nll"), 4),
        fmt(run.get("test_nll"), 4), fmt(run.get("tokens_per_sec"), 0), run["status"],
    ]


LEDGER_HEADERS = ["Stage", "Method", "Phase", "Seed", "Ratio", "Train tokens", "Dev NLL",
                  "Test NLL", "Tokens/s", "Status"]


def _stage_summary(study: dict) -> str:
    return "\n\n".join(
        f"**{STAGES[stage]}.** {verdict_text(outcome)}" for stage, outcome in study["stages"].items()
    )


def _pilot_summary(study):
    observed = []
    for stage, contrasts in study["pilot_comparisons"].items():
        if contrasts:
            numbers = ", ".join(f"{describe_difference(row['delta'])} against {METHODS[row['method']]}"
                                for row in contrasts)
            first = contrasts[0]
            observed.append(f"**{STAGES[stage]} development pilot.** At {first['tokens']:,} "
                            f"training targets, the third-order run recorded {numbers}. "
                            f"These are single-seed descriptions using {first['strength_basis']}.")
    return "\n\n".join(observed)


def _comparisons(study: dict) -> str:
    parts = []
    for stage, analysis in study["stages"].items():
        pairs = []
        summary = []
        for baseline, stats in analysis.get("comparisons", {}).items():
            name = METHODS.get(baseline, baseline)
            lo, hi = stats["median_ci"]
            summary.append([name, stats["wins"], stats["ties"], stats["losses"],
                            fmt(stats["median_delta"], 5), f"[{fmt(lo,5)}, {fmt(hi,5)}]",
                            fmt(stats["ci_coverage"], 4), fmt(stats["p_raw"], 5),
                            fmt(stats["p_holm"], 5)])
            for pair in stats["pairs"]:
                pairs.append([name, pair["seed"], fmt(pair["third_nll"], 5),
                              fmt(pair["baseline_nll"], 5), fmt(pair["delta"], 5)])
        if summary:
            parts.append(f"### {STAGES[stage]}\n\n" + _table(summary, [
                "Comparator", "Wins", "Ties", "Losses", "Median ΔNLL", "Median interval",
                "Coverage", "Sign-test p", "Holm p"]) + "\n\n" + _table(pairs, [
                    "Comparator", "Seed", "Third-order NLL", "Comparator NLL", "ΔNLL"]))
        times = [[t["seed"], fmt(t["cutoff_seconds"], 1), _method({"method": m}),
                  fmt(o.get("train_seconds"), 1), fmt(o.get("tokens"), 0), fmt(o.get("dev_nll"), 5)]
                 for t in analysis.get("matched_time", []) for m, o in t.get("by_method", {}).items()
                 if isinstance(o, dict)]
        if times:
            parts.append(f"### {STAGES[stage]} at equal training time\n\n" + _table(times, [
                "Seed", "Common cutoff (s)", "Method", "Recorded checkpoint (s)",
                "Training tokens", "Dev NLL"]))
    return "\n\n".join(parts)


def _run_learning(run: dict) -> str:
    """Use a trajectory only for a within-run observation; avoid causal attribution to a single run."""
    if run.get("error"):
        return f"The run recorded a failure. The run ledger contains the error and last metrics."
    series = [e for e in run["events"] if finite(e.get("dev_nll")) and finite(e.get("tokens"))]
    if len(series) >= 2 and series[0]["tokens"] < series[-1]["tokens"]:
        delta = series[-1]["dev_nll"] - series[0]["dev_nll"]
        return (f"Development NLL changed by {delta:+.4f} nats per target token from "
                f"{series[0]['tokens']:,} to {series[-1]['tokens']:,} training targets. "
                "Attribution to the regularizer uses matched comparisons across seeds.")
    if finite(run.get("dev_nll")):
        return f"The observed development NLL is {fmt(run['dev_nll'], 4)} nats per target token."
    return "A development observation is pending."


def _sample(sample: dict) -> str:
    """Indent whole text blocks verbatim so model-generated Markdown is never executed."""
    def block(value):
        lines = str(value).splitlines() or [""]
        return "\n".join("    " + line for line in lines)
    segments = [("Prompt", sample.get("prompt", ""))]
    if sample.get("reference") is not None:
        segments.append(("Reference continuation", sample["reference"]))
    segments.append(("Model continuation", sample.get("continuation", "")))
    return "\n\n".join(f"**{title}**\n\n{block(body)}" for title, body in segments)


def _experiments(root, study):
    """Write all runs and samples, with one navigable index and brief evidence-linked learnings."""
    base = root / "reports" / "experiments"
    index = ["# Experiment ledger", "NLL is negative log-likelihood in nats per target token. "
             "A smaller value assigns more probability to the observed next tokens. "
             "The ratio sets the pilot regularizer-gradient magnitude relative to cross-entropy.",
             "[Architecture, training algorithms, objectives and planned budgets](../planned-runs.md)"]
    learnings = ["# Experimental learnings", _stage_summary(study),
                 "Independent random signs include mixed weight derivatives in the expected "
                 "penalty. The trace implementation motivating the gradient check converted its "
                 "estimate to a Python number. [Derivation and references](../literature-review.md)"]
    if study["runs"]:
        rows = []
        for run in study["runs"]:
            key = run["id"]
            link = "./" + quote(key, safe="") + "/experiment.md"
            rows.append([f"[{_cell(key)}]({link})", *_ledger_row(run)])
            raw_link = "../../../results/" + quote(key, safe="") + "/"
            material = [
                f"# {_stage(run)} · {_method(run)}",
                f"Run `{key}` · [raw records]({raw_link}) · [registered design](../../preregistration.md)",
                _table([_ledger_row(run)], LEDGER_HEADERS),
                f"Training time is {fmt(run.get('train_seconds'), 1)} seconds. "
                f"Peak allocated GPU memory is {fmt(run.get('peak_vram_mb'), 1)} MiB. "
                f"Development token accuracy is {fmt(run.get('dev_accuracy'), 4)}. "
                f"Test token accuracy is {fmt(run.get('test_accuracy'), 4)}.",
                "[Design and hyperparameter rationale](../../planned-runs.md) · "
                f"[Saved configuration]({raw_link}config.json)",
            ]
            if run.get("failures"):
                material += ["## Recorded interruptions", _table(
                    [[failure["timestamp"],failure["error"]] for failure in run["failures"]],
                    ["Time (UTC)","Recorded exception"])]
            if run.get("precision_audit"):
                material += ["## Numerical diagnostic",run["precision_audit"]["reason"],
                             "[Precision amendment](../../amendments/adapter-precision.md)"]
            if finite(run.get("process_peak_rss_mib")):
                material.append(f"The process working-set high-water mark was {fmt(run['process_peak_rss_mib'],1)} MiB. "
                                "This OS measure includes earlier work in the same interpreter.")
            if run["samples"]:
                material += ["## Fixed-prompt generations",
                             *[_sample(sample) for sample in run["samples"]]]
            atomic_text(base / key / "experiment.md", "\n\n".join(material) + "\n")
            observation = _run_learning(run)
            if run.get("precision_audit"):
                observation = run["precision_audit"]["reason"]
            if run.get("failures"):
                observation += f" The run ledger records {len(run['failures'])} interrupted attempt(s)."
            atomic_text(base / key / "learnings.md", f"# Run learnings\n\n{observation}\n\n"
                        "[Experiment and source records](experiment.md)\n")
            learnings.append(f"- [{key}]({link}) — {observation}")
        index.append(_table(rows, ["Run", *LEDGER_HEADERS]))
    else:
        index.append("The first run record will populate this ledger.")
    atomic_text(base / "experiments.md", "\n\n".join(index) + "\n")
    atomic_text(base / "learnings.md", "\n\n".join(learnings) + "\n")


def _compact_table(study: dict) -> str:
    """Summarize like-for-like measured runs without selecting the strongest seed."""
    groups = {}
    for run in study["runs"]:
        if completed(run):
            key = (_stage(run), run.get("phase"), _method(run), run.get("ratio"), run.get("tokens"))
            groups.setdefault(key, []).append(run)
    rows = []
    for (stage, phase, method, ratio, tokens), runs in groups.items():
        def middle(metric):
            observed = [r[metric] for r in runs if finite(r.get(metric))]
            return fmt(median(observed), 4) if observed else "—"
        rows.append([stage, phase, method, fmt(ratio), fmt(tokens, 0), len(runs),
                     middle("dev_nll"), middle("test_nll")])
    return _table(rows, ["Stage", "Phase", "Method", "Ratio", "Tokens/run", "Runs",
                         "Median dev NLL", "Median test NLL"]) if rows else ""


def _update_readme(root: Path, body: str) -> None:
    """Preserve all hand-authored material, including edits made between report builds."""
    path = root / "README.md"
    if not path.exists():
        return
    before = path.read_text(encoding="utf-8-sig")
    pattern = r"<!-- RESULTS:START -->.*?<!-- RESULTS:END -->"
    if len(re.findall(pattern, before, re.DOTALL)) != 1:
        raise ValueError(f"{path} requires exactly one pair of results markers")
    replacement = "<!-- RESULTS:START -->\n" + body.strip() + "\n<!-- RESULTS:END -->"
    atomic_text(path, re.sub(pattern, lambda _: replacement, before, flags=re.DOTALL))


def build_report(root: Path = Path(".")) -> dict:
    """Regenerate README results, PDF, experiment ledger, figures and the static dashboard."""
    root = Path(root).resolve()
    study = study_snapshot(root)
    figures = build_figures(study, root / "docs" / "figures")
    study["figures"] = figures
    static = json.dumps(study, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    atomic_text(root / "docs" / "study.json", static + "\n")
    _experiments(root, study)
    compact = _compact_table(study)
    comparisons = _comparisons(study)
    counts = len(study["runs"])
    done = sum(completed(run) for run in study["runs"])
    overview = f"Recorded {counts} runs, including {done} with a completed summary."
    documents = [f"[Interactive explorer]({PAGES})", "[Per-run ledger](experiments/experiments.md)",
                 "[Preregistration](preregistration.md)", "[Paper](paper.pdf)"]
    summary = ["# Study summary", overview, _stage_summary(study), " · ".join(documents)]
    pilots = _pilot_summary(study)
    if pilots:
        summary.extend(["## Development observations", pilots])
    if compact:
        summary.extend(["## Measured scores", compact])
    if comparisons:
        summary.extend(["## Paired evidence", comparisons])
    for key, label in (("architecture", "Computation graph"), ("curves", "Development trajectories"),
                       ("paired", "Paired test differences")):
        if key in figures:
            summary.append(f"![{label}](../docs/figures/{figures[key]})")
    atomic_text(root / "reports" / "summary.md", "\n\n".join(summary) + "\n")
    badge = f"[Explore the results]({PAGES}) · [Paper](reports/paper.pdf) · [Run ledger](reports/experiments/experiments.md)"
    readme = [badge, overview, _stage_summary(study)]
    if pilots:
        readme.append(pilots)
    if compact:
        readme.extend(["### Measured scores", compact])
    readme.append("![Parameter-space computation graph](docs/figures/architecture.png)")
    for key in ("paired", "curves"):
        if key in figures:
            readme.append(f"![{'Paired test differences' if key == 'paired' else 'Development NLL'}](docs/figures/{figures[key]})")
    seen = set()
    panels = []
    for run in study["runs"]:
        key = (run.get("stage"), run.get("method"))
        if not run["samples"] or key in seen:
            continue
        seen.add(key)
        panels.append(f"<details><summary>{_stage(run)} · {_method(run)}</summary>\n\n"
                      + _sample(run["samples"][0]) + "\n\n</details>")
    if panels:
        readme += ["### Recorded predictions", "First archived sample in run-ID order per "
                   "stage and method. [All continuations](reports/experiments/experiments.md)", *panels]
    _update_readme(root, "\n\n".join(readme))
    write_paper(study, root / "reports" / "paper.pdf", root / "docs" / "figures", figures)
    return study
