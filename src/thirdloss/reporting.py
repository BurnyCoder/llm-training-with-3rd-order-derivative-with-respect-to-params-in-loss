"""Rebuild the public study artifacts from raw results with one command."""

import json
import re
from pathlib import Path
from statistics import median
from urllib.parse import quote

from .report_figures import build_figures
from .flatness_tables import checkpoint_table,flatness_ledger
from .readme_comparisons import comparison_sections
from .report_paper import write_paper
from .report_records import (
    METHODS, PAGES, STAGES, atomic_text, completed, describe_difference, example_runs, finite, fmt, study_snapshot,
    verdict_text,markdown_cell as _cell,markdown_table as _table,
)


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
        supplement = [[item["seed"],fmt(item["cutoff_seconds"],1),METHODS[m],fmt(point["clock_seconds"],1),
                       fmt(point["tokens"],0),fmt(point["dev_nll"],5)]
                      for item in analysis.get("matched_nonhost_time",[]) for m,point in item["by_method"].items()]
        if supplement:
            parts.append(f"### {STAGES[stage]} after subtracting host derivative calls\n\n"
                         "This supplementary clock excludes the measured host probe calls and their transfers. "
                         "The registered comparison above counts elapsed time with one GPU reserved.\n\n" +
                         _table(supplement,["Seed","Cutoff (s)","Method","Checkpoint (s)","Training tokens","Dev NLL"]))
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
            if run.get("flatness") or run.get("score_flatness"):
                material += ["## Checkpoint flatness",checkpoint_table(run["method"],run.get("flatness"),run.get("score_flatness")),
                             "The connection between width and better held-out prediction is unknown. "
                             "[Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline)."]
            if run.get("failures"):
                material += ["## Recorded interruptions", _table(
                    [[failure["timestamp"],failure["error"]] for failure in run["failures"]],
                    ["Time (UTC)","Recorded exception"])]
            restarts = []
            for audit in run.get("restart_audits",[]):
                samples = audit["logged_replay_observations"]
                loss_diff = max(row["absolute_loss_delta"] for row in samples)
                grad_diff = max(row["absolute_gradient_norm_delta"] for row in samples)
                restarts.append(f"After the system restart, training resumed from update {audit['resume_checkpoint_step']:,} "
                                f"and replayed {audit['replayed_steps']} updates. Across {len(samples)} logged overlaps, "
                                f"the maximum absolute training NLL difference was {loss_diff:.4g} nats per target "
                                f"and the maximum difference in the unclipped gradient norm was {grad_diff:.4g}. "
                                f"[Replay measurements](../../../results/verification/{audit['source']})")
            if restarts:
                material += ["## Restart verification",*restarts]
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
            if restarts:
                observation += " "+" ".join(restarts)
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


def _update_sections(path,sections):
    """Replace only the named report sections, preserving the author's surrounding text."""
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8-sig")
    for label,generated,required in sections:
        if not required and f"<!-- {label}:" not in content:
            continue
        pattern=f"<!-- {label}:START -->.*?<!-- {label}:END -->"
        if len(re.findall(pattern,content,re.DOTALL))!=1:
            raise ValueError(f"{path} requires exactly one pair of {label} markers")
        replacement=f"<!-- {label}:START -->\n\n"+generated.strip()+f"\n\n<!-- {label}:END -->"
        content=re.sub(pattern,lambda _:replacement,content,flags=re.DOTALL)
    atomic_text(path,content)


def _hybrid_report(root,study):
    """Report each observed width, censoring, matched fit and preregistered sign comparison."""
    data = study["hybrid"]
    headline = (f"TinyStories hybrid follow-up: {data['completed_arms']} of 48 full runs and "
                f"{data['completed_trunks']} of 8 shared checkpoints complete. "
                f"Geometric decision: {data['status']}.")
    material = ["# Hybrid schedules on TinyStories",headline,
                "[Frozen protocol and decision rule](preregistration.md) · "
                "[Interactive measurement and run selector](../../docs/index.html#curves)",
                "Two-sided directional width is measured in the original Euclidean weight coordinates at a "
                "fixed increase of 0.1 nats per target. Each linked JSON contains all 32 rays and their brackets. "
                "A missing upper bound means that the search reached its maximum radius before crossing. "
                "The five shared-checkpoint arms reuse the trunk’s switch measurement and its recorded probe time."]
    widths = []
    for r in study["runs"]:
        for w in r.get("widths",{}).values():
            path = f"../../results/{r['id']}/width-{w['step']}.json"
            widths.append([r["seed"],_method(r),f"[{w['step']}]({path})",fmt(w["width"],5),
                           fmt(w["width_lower"],5),fmt(w["width_upper"],5),w["censored_rays"],
                           fmt(w["baseline_nll"],5),fmt(w["seconds"],2)])
    if widths:
        material += ["## Width observations",_table(widths,["Seed","Arm","Step","Width","Lower","Upper",
                       "Censored rays","Training probe NLL","Probe seconds"])]
        if any(finite(w["width"]) for r in study["runs"] for w in r.get("widths",{}).values()):
            material.append("![Median directional width by seed and training arm](../../docs/figures/hybrid_width.png)")
    arms = []
    for r in study["runs"]:
        if r.get("phase") not in {"hybrid","branch"} or not completed(r):
            continue
        url = f"../../results/{r['id']}/schedule.json"
        arms.append([r["seed"],_method(r),fmt(r["dev_nll"],6),fmt(r["dev_accuracy"],5),fmt(r["reference_rms"],5),
                     f"[{r['zero_steps']}]({url})",f"{r['final_third_lambda']:.6g}",fmt(r["tokens_per_sec"],0),
                     fmt(r["peak_vram_mb"],1),fmt(r["process_peak_rss_mib"],1)])
    if arms:
        material += ["## Full development and resource measurements",_table(arms,["Seed","Arm","Dev NLL","Accuracy",
                     "Reference RMS","Steps at zero λ₃","Final λ₃","Targets/s","Allocated GPU MiB","Process peak MiB"])]
    calibrations=[]
    for path in sorted((root/"results"/"hybrid"/"calibration").glob("seed-*.json")):
        cal=json.loads(path.read_text(encoding="utf-8"))
        calibrations.append([cal["seed"],len(cal["draws"]),f"{cal['delta']:.7g}",fmt(cal["calibration_seconds"],2),
                             f"[Per-draw gradient norms](../../results/hybrid/calibration/{path.name})"])
    if calibrations:
        material += ["## Stronger trace at the common checkpoint",
                     _table(calibrations,["Seed","Draws","Additional trace coefficient","Seconds","Calibration record"])]
    if data["pairs"]:
        material += ["## Adaptive minus comparator per seed","Positive Δwidth favors the adaptive schedule. "
                     "Negative ΔNLL favors its prediction. Comparable fit uses the frozen 0.02-nat training threshold.",
                     _table([[p["seed"],METHODS[p["comparator"]],fmt(p["delta"],6),fmt(p["dev_nll_delta"],6),
                              fmt(p["train_probe_nll_delta"],6),"yes" if p["comparable_fit"] else "no"]
                             for p in data["pairs"]],["Seed","Comparator","Δwidth gain","Δdev NLL","Δtrain NLL","Comparable fit"])]
    for comparator,s in data["comparisons"].items():
        lo,hi = s["median_ci"]
        material.append(f"Against {METHODS[comparator]}, the median paired width difference is {fmt(s['median_delta'],6)}, "
                        f"interval [{fmt(lo,6)}, {fmt(hi,6)}], coverage {fmt(s['ci_coverage'],4)}. "
                        f"Wins/ties/losses: {s['wins']}/{s['ties']}/{s['losses']}. "
                        f"One-sided sign p = {fmt(s['p_raw'],5)}, Holm p = {fmt(s.get('p_holm'),5)}.")
    material += [f"The completed branches reused {data['shared_training_tokens_saved']:,} targets of optimization "
                 "compared with independently training each branch from initialization. The replay permutation "
                 "couples different seeds through their coefficient histories. The sign-test reference for this "
                 "comparison assumes exchangeable independent pair signs. Shared donor histories make that assumption approximate. "
                 "All raw pairs are reported for inspection."]
    atomic_text(root/"reports"/"hybrid"/"results.md","\n\n".join(material)+"\n")
    return headline


def build_report(root: Path = Path(".")) -> dict:
    """Regenerate README results, PDF, experiment ledger, figures and the static dashboard."""
    root = Path(root).resolve()
    study = study_snapshot(root)
    hybrid = _hybrid_report(root,study)
    atomic_text(root/"reports"/"flatness.md",flatness_ledger(study))
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
    summary = ["# Study summary", overview, _stage_summary(study), hybrid+" [Hybrid outcomes](hybrid/results.md)", " · ".join(documents)]
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
    badge = (f"[Explore the results]({PAGES}) · [Hugging Face explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · "
             "[Hugging Face collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378) · "
             "[Paper](reports/paper.pdf) · [Run ledger](reports/experiments/experiments.md)")
    opening,side_by_side=comparison_sections(study)
    readme = [side_by_side,badge,overview,hybrid+" [Width measurements, scores and controls](reports/hybrid/results.md)",
              "[Full score table, strength search and per-seed test differences](reports/summary.md)"]
    if "hybrid_width" in figures:
        readme.append("![Directional width by TinyStories arm and seed](docs/figures/hybrid_width.png)")
    readme.append("![Parameter-space computation graph](docs/figures/architecture.png)")
    for key in ("paired", "curves"):
        if key in figures:
            readme.append(f"![{'Paired test differences' if key == 'paired' else 'Development NLL'}](docs/figures/{figures[key]})")
    examples=example_runs(study["runs"])
    if examples:
        readme.append("### Full generations by method")
        for stage,name in STAGES.items():
            links=[f"[{_method(r)}](reports/experiments/{r['id']}/experiment.md#fixed-prompt-generations)"
                   for r in examples if r["stage"]==stage]
            if links:
                readme.append(f"**{name}** · "+" · ".join(links))
    _update_sections(root/"README.md",[("RESULTS","\n\n".join(readme),True),("READOUT",opening,False)])
    # The collection's landing card shows the same tables with native Hub evidence links.
    hub_base="https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/"
    hub_tables=re.sub(r"\]\(((?:reports|results)/)",lambda match:"]("+hub_base+match.group(1),
                      opening+"\n\n"+side_by_side)
    _update_sections(root/"docs"/"hub"/"archive.md",[("COMPARISONS",hub_tables,True)])
    write_paper(study, root / "reports" / "paper.pdf", root / "docs" / "figures", figures)
    return study
