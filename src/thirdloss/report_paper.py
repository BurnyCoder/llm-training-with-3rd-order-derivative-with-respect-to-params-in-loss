"""Typeset the preregistered study and current evidence using ReportLab Platypus.

Flowables permit a protocol-only manuscript to expand as complete seed pairs appear.
Renderer reference: https://docs.reportlab.com/reportlab/userguide/ch5_platypus/
"""

import os
from datetime import datetime
from pathlib import Path
from statistics import median
from tempfile import NamedTemporaryFile
from xml.sax.saxutils import escape, quoteattr
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from matplotlib import get_data_path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, LongTable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, TableStyle,
)

from .report_records import METHODS, REPOSITORY, STAGES, completed, describe_difference, example_runs, finite, fmt, verdict_text

REFERENCES = {
    "flat": ("Hochreiter and Schmidhuber (1994), Simplifying neural nets by discovering flat minima",
             "https://proceedings.neurips.cc/paper/1994/hash/01882513d5fa7c329e940dda99b12147-Abstract.html"),
    "flat_mdl": ("Hochreiter and Schmidhuber (1997), Flat Minima",
                 "https://people.idsia.ch/~juergen/fm/node1.html"),
    "gpt_trace": ("Zhang, Li and Ju, Noise Stability Optimization for Finding Flat Minima: A Hessian-based Regularization Approach",
                  "https://arxiv.org/pdf/2306.08553#page=12"),
    "roughness": ("Duchon, Splines minimizing rotation-invariant semi-norms in Sobolev spaces",
                  "https://doi.org/10.1007/BFb0086566"),
    "trace": ("Liu, Yu and Lin, Regularizing deep neural networks with stochastic estimators of Hessian trace",
              "https://arxiv.org/pdf/2208.05924"),
    "sketch": ("Bujanović and Kressner, Norm and trace estimation with random rank-one vectors",
               "https://arxiv.org/pdf/2004.06433"),
    "fut": ("Yang et al., Estimating the effects of sample training orders for large language models without retraining",
            "https://arxiv.org/pdf/2505.22042#page=16"),
    "stories": ("Eldan and Li, TinyStories", "https://arxiv.org/pdf/2305.07759"),
    "pythia": ("Biderman et al., Pythia", "https://arxiv.org/pdf/2304.01373"),
    "lora": ("Hu et al., Low-rank adaptation of large language models", "https://arxiv.org/pdf/2106.09685"),
    "abstracts": ("Common Pile, Filtered arXiv abstracts", "https://huggingface.co/datasets/common-pile/arxiv_abstracts_filtered"),
    "seeds": ("Bouthillier et al., Accounting for variance in machine learning benchmarks",
              "https://proceedings.mlsys.org/paper_files/paper/2021/hash/0184b0cd3cfb185989f858a1d9f5c1eb-Abstract.html"),
    "coordinates": ("Dinh et al., Sharp minima can generalize for deep nets",
                    "https://proceedings.mlr.press/v70/dinh17b.html"),
}
TEAL = "#006c60"
INK = "#263735"
MUTED = "#4b5e59"


def _link(url, label):
    return f"<link href={quoteattr(url)} color='{TEAL}'><u>{escape(str(label))}</u></link>"


def _cite(key):
    label, url = REFERENCES[key]
    return _link(url, label.rsplit(", ",1)[0])


def _styles():
    """Use embedded Unicode fonts shipped with Matplotlib on every supported machine."""
    fonts = Path(get_data_path()) / "fonts" / "ttf"
    for name, file in (("PaperSans", "DejaVuSans.ttf"), ("PaperBold", "DejaVuSans-Bold.ttf"),
                       ("PaperSerif", "DejaVuSerif.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
    pdfmetrics.registerFontFamily("PaperSans", normal="PaperSans", bold="PaperBold",
                                 italic="PaperSans", boldItalic="PaperBold")
    base = dict(fontName="PaperSans", fontSize=9.0, leading=14, textColor=colors.HexColor(INK),
                alignment=TA_LEFT, spaceAfter=7, splitLongWords=True)
    styles = {"body": ParagraphStyle("body", **base)}
    for name, changes in {
        "title": dict(fontName="PaperSerif", fontSize=25, leading=30, spaceAfter=9, keepWithNext=True),
        "heading": dict(fontName="PaperSerif", fontSize=15, leading=20, spaceBefore=8, spaceAfter=6, keepWithNext=True),
        "subheading": dict(fontName="PaperBold", fontSize=10.4, leading=14, spaceBefore=6, keepWithNext=True),
        "byline": dict(fontSize=9.5, leading=15, textColor=colors.HexColor(TEAL), spaceAfter=13),
        "caption": dict(fontSize=7.8, leading=11.2, textColor=colors.HexColor(MUTED), spaceAfter=7),
        "cell": dict(fontSize=7.45, leading=10.4, spaceAfter=0),
        "headcell": dict(fontName="PaperBold", fontSize=7.3, leading=10.4, textColor=colors.white, spaceAfter=0),
        "equation": dict(fontName="PaperSerif", fontSize=12.4, leading=19, leftIndent=9,
                         spaceBefore=3, spaceAfter=9),
    }.items():
        styles[name] = ParagraphStyle(name, parent=styles["body"], **changes)
    return styles


def _grid(styles, headers, rows, widths):
    """Repeat the column labels if the growing experiment table spans multiple pages."""
    def line(cells, style):
        return [Paragraph(escape(str(cell)), styles[style]) for cell in cells]
    table = LongTable([line(headers, "headcell"), *[line(r, "cell") for r in rows]],
                      colWidths=widths, repeatRows=1, hAlign="LEFT", splitByRow=True)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34504a")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f5f2")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    return table


def _figure(path, max_width=477, max_height=240):
    image = Image(str(path))
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    image.hAlign = "LEFT"
    return image


def _result_tables(study):
    """Group scores at equal token horizons and compare resource use on like hardware."""
    groups = {}
    for run in study["runs"]:
        if completed(run):
            key = (run.get("stage"), run.get("phase"), run.get("method"),
                   run.get("ratio"), run.get("tokens"))
            groups.setdefault(key, []).append(run)
    scores, resources = {}, {}

    def middle(runs, key, digits):
        values = [r[key] for r in runs if finite(r.get(key))]
        return fmt(median(values), digits) if values else "—"

    for (stage, phase, method, ratio, tokens), runs in groups.items():
        arm = [STAGES.get(stage, stage), phase, METHODS.get(method, method), fmt(ratio)]
        scores.setdefault(stage, []).append([*arm[1:], len(runs), fmt(tokens, 0), middle(runs, "dev_nll", 6),
                                            middle(runs, "dev_perplexity", 4), middle(runs, "test_nll", 6),
                                            middle(runs, "test_perplexity", 4)])
        devices = {}
        for run in runs:
            hardware = run.get("gpu") or run.get("device") or "Hardware unrecorded"
            devices.setdefault(hardware, []).append(run)
        for device, subset in devices.items():
            timed = [r for r in subset if finite(r.get("train_seconds")) and r["train_seconds"] > 0]
            gpu = [r for r in subset if r.get("gpu") or str(r.get("device", "")).startswith("cuda")]
            resources.setdefault(device, []).append([
                *arm, len(subset), fmt(tokens, 0), middle(timed, "train_seconds", 1),
                middle(timed, "tokens_per_sec", 0), middle(gpu, "peak_vram_mb", 1),
            ])
    return scores, resources


def _matched_rows(study,key="matched_time"):
    """Print every matched seed, including each arm's distance from the shared cutoff."""
    rows = []
    for stage, outcome in study["stages"].items():
        for entry in outcome.get(key, []):
            cutoff = entry["cutoff_seconds"]
            losses = []
            for method in ("ce", "trace", "third"):
                point = entry["by_method"][method]
                lag = point["staleness_seconds"]
                losses.append(f"{fmt(point['dev_nll'], 4)} ({fmt(lag, 1)})")
            rows.append([STAGES[stage], entry["seed"], fmt(cutoff, 1), *losses])
    return rows


def write_paper(study: dict, output: Path, figure_dir: Path, figures: dict) -> None:
    """Create the dated paper, with pretraining and adaptation interpreted separately."""
    styles = _styles()
    flow = []

    def p(markup, style="body"):
        flow.append(Paragraph(markup, styles[style]))

    try:
        local_time = datetime.fromisoformat(study["generated_at"]).astimezone(ZoneInfo("Europe/Berlin"))
    except ZoneInfoNotFoundError:
        local_time = datetime.fromisoformat(study["generated_at"]).astimezone()
    rendered = local_time.strftime("%d %B %Y")
    p("Third-derivative regularization for causal language models", "title")
    p(f"Libor “Burny” Burian &nbsp;·&nbsp; {rendered}", "byline")
    p("Abstract", "heading")
    p("We study whether a language model improves its predictions when training penalizes "
      "variation in the curvature of its next-token loss. Independent random signs produce "
      "a differentiable estimate of the squared norm of all third partial derivatives in "
      "the trainable coordinates. Two matched interventions compare this objective with "
      "ordinary AdamW and a signed Hessian-trace penalty. " +
      " ".join(f"<b>{STAGES[s]}.</b> {escape(verdict_text(outcome,paired=True))}" for s, outcome in study["stages"].items()))
    p("Motivation and related work", "heading")
    p("Hochreiter and Schmidhuber proposed that flatter minima may generalize better at comparable "
      "training error. Coarser weights can preserve the fit, so fewer bits can describe it. Their "
      "minimum-description-length argument predicts less expected overfitting. Rescaling can alter "
      "sharpness while preserving predictions, so we measure held-out token loss. "
      f"{_cite('flat')} · {_cite('flat_mdl')} · {_cite('coordinates')}")
    p("The Hessian can change at constant trace. Squared third partials penalize this variation, "
      "adapting an order-three spline roughness measure. Earlier work studied trace regularization "
      "in recurrent language models and a symmetric perturbation approximation in GPT-2 fine-tuning. "
      f"{_cite('roughness')} · {_cite('trace')} · {_cite('gpt_trace')}, Table 5")
    p("FUT++ uses differences between Hessian estimates at consecutive checkpoints to approximate "
      "third weight derivatives and predict the effect of reordering training batches. Here the "
      "squared norm enters the loss and changes the optimizer update. "
      f"{_cite('fut')}, Appendix A.1, equations 14–15.")
    p("The estimator and its update", "heading")
    p("J(θ) = L(θ) + λ · ‖D³L(θ)‖²<sub>F</sub>", "equation")
    p("For independent Rademacher vectors u and v, form r = ∇(uᵀHv). Squaring and summing "
      "its coordinates, then averaging over probes, cancels every cross term with unmatched "
      "indices. The expectation is the squared Frobenius norm of the minibatch third derivative. "
      "The gradient through r supplies a fourth-derivative contraction to AdamW. The "
      "derivative minibatch contains two windows. A Bernoulli gate samples one eighth of "
      "updates and multiplies the active contribution by eight. "
      f"{_cite('sketch')} · {_link(REPOSITORY + '/blob/main/reports/preregistration.md', 'Preregistration')}")
    flow.append(KeepTogether([_figure(figure_dir / figures["architecture"], max_height=140),
                              Paragraph("Figure 1. Trainable coordinate sets and the stochastic "
                                        "regularization path.", styles["caption"])]))
    flow.append(PageBreak())
    p("Experimental design", "heading")
    p("Full-weight pretraining uses a four-block causal Transformer with width 192, four heads, "
      "a gated 512-wide MLP, tied embeddings and 128 targets per window. Stories use a "
      "train-only vocabulary of 4,096 tokens. The adapter stage freezes Pythia-410M and trains "
      "rank-eight attention QKV adapters with scale alpha 16. The first-submission timestamp "
      "sets the split within 2024, grouping versions by base arXiv identifier. January through April supply training text, May supplies "
      "development text, and June supplies the held-out test. "
      f"{_cite('stories')} · {_cite('pythia')} · {_cite('lora')} · {_cite('abstracts')}")
    p("The confirmatory horizons are 16,777,216 target tokens for stories and 524,288 for "
      "abstracts. Within a stage, each seed pairs starting weights, text order and optimizer "
      "schedule. The pilot calibrates penalty gradients on training data and selects strength "
      "at equal development horizons. The squared-Hessian, sign-randomized and combined arms "
      "test derivative order, gradient direction and incremental benefit. Initial checkpoints "
      "and token unigrams supply untrained references. "
      f"{_link(REPOSITORY + '/blob/main/reports/planned-runs.md', 'Run matrix')}")
    p("Each update averages 32 windows for stories or eight for adapters. AdamW uses β₁ = 0.9, "
      "β₂ = 0.95, matrix weight decay 0.1 and gradient norm clipping at one. Peak learning "
      "rates are 0.0003 and 0.0001, respectively, with 5% warmup and cosine decay to 10% of peak. "
      "Across 16 batches at the shared pilot initialization, the median ordinary-to-penalty "
      "gradient-norm ratio sets the scale. Both regularizers try 1%, 3% and 10% of this scale. "
      f"{_link(REPOSITORY + '/blob/main/reports/preregistration.md', 'Training and selection protocol')}")
    p("Normalize and deduplicate whole documents before fitting the stories tokenizer. Prioritize "
      "evaluation records when removing overlaps, and audit word-shingle similarity between "
      "splits. Pack documents with an end-of-sequence token. Full evaluation counts each valid "
      "target once. During training, the development curve uses a fixed subset of windows. "
      f"{_link(REPOSITORY + '/blob/main/docs/data.md', 'Data preparation and overlap audit')}")
    data_rows = [[STAGES[stage], name, fmt(split.get("documents"), 0), fmt(split.get("tokens"), 0)]
                 for stage, context in study["context"].items()
                 for name, split in context["datasets"].get("splits", {}).items()]
    if data_rows:
        flow.append(_grid(styles, ["Corpus", "Split", "Retained documents", "Packed tokens"],
                          data_rows, [112, 90, 132, 141]))
        p("Packed-token counts include document separators. The number of valid next-token "
          "targets is recorded separately during evaluation.", "caption")
    p("Statistical analysis", "heading")
    p("Corpus negative log-likelihood sums token losses and divides by the valid target count. "
      "For each baseline, paired differences subtract baseline NLL from third-order NLL at the "
      "same token budget. The registered stage decision requires both one-sided exact paired "
      "sign tests to pass Holm correction at 0.05 across eight seed pairs. Ties are removed "
      "from sign-test denominators. A distribution-free order-statistic interval quantifies "
      "uncertainty in the median paired difference. Equal-time analyses use the latest logged "
      "development checkpoint within the shortest final training time of that seed triple. "
      f"{_cite('seeds')} · {_link(REPOSITORY + '/blob/main/reports/preregistration.md', 'Decision rule')}")
    p("Results", "heading")
    numerical = study.get("numerics",{})
    single = numerical.get("pythia-joint-cuda",{})
    double = numerical.get("pythia-fp64-agreement",{})
    if single and double:
        p("Numerical accuracy on the pretrained checkpoint", "subheading")
        p(f"For identical Pythia weights and probe signs, changing the FP32 CUDA batching gave a "
          f"{100*single['relative_gradient_difference']:.1f}% relative discrepancy in the training gradient. "
          f"In FP64 the CPU and GPU gradients agreed to relative error {double['relative_gradient_difference']:.2g}. "
          "The initial FP32 pilot is retained as a diagnostic. The amended adapter arms compute their "
          "penalties in FP64 on the CPU and use CUDA for the ordinary loss and optimizer updates. "
          f"{_link(REPOSITORY + '/blob/main/reports/amendments/adapter-precision.md','Pre-test amendment and raw checks')}")
    run_count = len(study["runs"])
    done_count = sum(completed(run) for run in study["runs"])
    p(f"The ledger contains {run_count} runs and {done_count} completed summaries. "
      f"{_link(REPOSITORY + '/tree/main/results', 'Raw records')} · "
      f"{_link(REPOSITORY + '/blob/main/reports/experiments/experiments.md', 'Per-run ledger')}")
    plan = study["run_inventory"]
    p("Completed, active and planned experiments", "subheading")
    activity = " / ".join(plan["activity"]) or "Between recorded training and scoring updates"
    p(f"At {escape(study['generated_at'])}, {plan['done']} of {plan['total']} experimental milestones were complete. "
      f"Recorded activity · {escape(activity)}. Next scheduled work · {escape(plan['next'])}.")
    if "forecast" in study:
        low, high = study["forecast"]
        p(f"Measured remaining-time scenarios span {low:.2f}–{high:.2f} machine-hours. "
          f"{_link(REPOSITORY+'/blob/main/results/feasibility/remaining-work.json','Timing inputs and assumptions')}")
    flow.append(_grid(styles, ["Experiment or evaluation","Completed","Remaining","Planned"],
                      [[g["label"],g["done"],g["total"]-g["done"],g["total"]] for g in plan["groups"]],
                      [268,72,72,65]))
    p("The seed-sensitivity analysis is the final stage. The run matrix identifies every scheduled method, seed, "
      "token budget, test evaluation and checkpoint geometry measurement. "
      f"{_link(REPOSITORY+'/blob/main/reports/planned-runs.md#current-evidence-and-remaining-runs','Full execution matrix')}", "caption")
    for stage, outcome in study["stages"].items():
        p(f"<b>{STAGES[stage]}.</b> {escape(verdict_text(outcome))}")
        context = study["context"][stage]
        selected = context["selection"].get("ratios", {})
        if selected:
            p(f"Development selected trace ratio {fmt(selected.get('trace'))} and third-order "
              f"ratio {fmt(selected.get('third'))}. "
              f"{_link(REPOSITORY + '/blob/main/results/selection/' + stage + '.json', 'All candidate scores')}")
        hours = context["feasibility"].get("projected_confirm_training_hours")
        if finite(hours):
            p(f"The selected-arm pilot speeds project {hours:.2f} training hours for this full "
              "confirmatory stage. This estimate covers optimization time. "
              f"{_link(REPOSITORY + '/blob/main/results/feasibility/' + stage + '.json', 'Measured timing basis')}")
        pilots = study["pilot_comparisons"][stage]
        if pilots:
            changes = ", ".join(f"{describe_difference(row['delta'])} against "
                                f"{METHODS[row['method']]}" for row in pilots)
            p(f"In the development pilot at {pilots[0]['tokens']:,} training targets, third-order "
              f"training recorded {changes}. The comparison uses one seed and "
              f"{pilots[0]['strength_basis']}.")
    evaluated, resources = _result_tables(study)
    if evaluated:
        for stage, name in STAGES.items():
            if stage in evaluated:
                p(f"Scores across methods · {name}", "subheading")
                flow.append(_grid(styles, ["Phase", "Method", "Ratio", "Runs", "Tokens/run", "Dev NLL", "Dev PPL", "Test NLL", "Test PPL"],
                                  evaluated[stage], [50, 93, 35, 32, 57, 52, 53, 52, 53]))
        p("Table 1. Medians over available completed runs sharing corpus, method, development "
          "strength and token horizon. NLL is in nats per target token. Perplexity (PPL) is the exponential "
          "of each run’s full-split NLL. Lower values are better for both metrics. Dashes mark missing "
          "observations. The paired seed analyses use individual final test scores.", "caption")
    for key, caption in (("curves", "Development NLL by logged token count. Each line is a run; "
                                    "panels separate training stages and phases."),
                         ("paired", "Individual differences in test NLL. Diamonds mark median "
                                    "differences and horizontal segments show their registered intervals.")):
        if key in figures:
            flow.append(KeepTogether([_figure(figure_dir / figures[key]),
                                      Paragraph(caption, styles["caption"])]))
    p("Discussion and limitations", "heading")
    p("A wide minimum permits large weight displacements at a fixed loss increase. If curvature "
      "starts small and changes slowly over the displacement, the loss stays low. For the loss "
      "w<super>4</super>, the squared third derivative grows quadratically with distance from the bottom, so "
      "a small descent step can pull displaced weights back. A steep quadratic has constant curvature "
      "and receives zero third-derivative penalty everywhere. Finding wider basins remains a "
      "geometric hypothesis. "
      f"{_cite('coordinates')} · {_link(REPOSITORY + '/blob/main/docs/third-derivative-penalty.md#when-can-the-penalty-favor-a-wider-minimum', 'Derivation and examples')}")
    p("Predictive utility requires lower held-out loss against both baselines. A reduction in "
      "the derivative estimate alone describes local geometry. Parameterization changes its "
      "magnitude, including the low-rank factorization used for abstracts. The estimate targets "
      "expected two-window minibatch roughness. The small datasets, limited seed count and "
      "two tokenization schemes bound the interpretation. More tokens per GPU hour can change "
      "the practical ranking. "
      f"{_cite('coordinates')} · {_link(REPOSITORY + '/blob/main/reports/preregistration.md', 'Scope of inference')}")
    p("Registered curvature-dependent schedule", "subheading")
    p("The TinyStories follow-up keeps the trace active and increases the weight on squared third "
      "derivatives once training loss and measured curvature are low. Retaining the highest weight reached "
      "could oppose later drift if curvature changes faster at the edge. Direct division can reverse "
      "the incentive. For the quartic loss above, the squared ratio of third to second derivative "
      "is 4/w<super>2</super> away from zero and grows toward the flat bottom. The final appendix "
      "specifies both schedules and the width test. "
      f"{_link(REPOSITORY + '/blob/main/reports/hybrid/preregistration.md', 'Frozen follow-up design')}")
    from .flatness_tables import hybrid_flatness_rows
    hybrid = study["hybrid"]
    if "hybrid_width" in figures:
        flow.append(_figure(figure_dir/figures["hybrid_width"],max_height=605))
    p(f"{hybrid['completed_arms']} of 48 full hybrid arms and {hybrid['completed_trunks']} of 8 shared "
      f"checkpoints have completed. Geometric endpoint: {hybrid['status']}. "
      f"{_link(REPOSITORY + '/blob/main/reports/hybrid/results.md', 'All observed widths, development scores and fit differences')}")
    geometry=hybrid_flatness_rows(study["runs"])
    if geometry:
        p("Flatness at trained checkpoints","subheading")
        p("Switch and final widths are medians over the listed seeds. Larger widths tolerate greater weight "
          "displacement before the eight-window training loss rises by 0.1 nats. The directional interval "
          "summarizes the middle half of the 16 two-sided distances within each seed. The last column "
          "counts final rays whose crossing exceeded the search radius.")
        flow.append(_grid(styles,["Hybrid arm","Seeds","Switch width","Final width","Middle 50% of directions","Rays at limit"],
                          [[r[i] for i in (0,1,2,3,5,6)] for r in geometry],[104,71,65,65,93,66]))
    p("Secondary diagnostics compare the fitted primary checkpoints within each trainable parameterization. "
      "The checkpoint ledger gives their finite widths, signed trace per parameter, RMS curvature and raw probes. "
      f"{_link(REPOSITORY + '/blob/main/reports/flatness.md','Flatness measurements')} · "
      f"{_link(REPOSITORY + '/blob/main/reports/amendments/checkpoint-flatness.md','Secondary protocol')}")
    from .readme_comparisons import primary_geometry
    for stage in STAGES:
        caption,statistics=primary_geometry(study,stage)
        if statistics:
            p(caption,"subheading")
            flow.append(_grid(styles,["Flatness statistic","AdamW","Hessian trace","Third order"],
                              [[row[0].split("<br>")[0],*row[1:]] for row in statistics],[164,100,100,100]))
    for comparator,s in hybrid["comparisons"].items():
        lo,hi = s["median_ci"]
        p(f"Adaptive minus {METHODS[comparator]} median width gain {fmt(s['median_delta'],5)} "
          f"[{fmt(lo,5)}, {fmt(hi,5)}]. One-sided sign p = {fmt(s['p_raw'],5)}, Holm p = {fmt(s.get('p_holm'),5)}. "
          "Cross-seed replay shares schedule information across pairs, limiting the independent-sign approximation.","caption")
    p("Conclusion", "heading")
    if all(outcome.get("complete") for outcome in study["stages"].values()):
        confirmed = [STAGES[s] for s, outcome in study["stages"].items() if outcome.get("success")]
        if confirmed:
            p("The registered dual-baseline criterion was met in " + " and ".join(confirmed) +
              ". The observed gain applies to the reported data, trainable coordinates and token horizons.")
        else:
            p("Neither stage established the registered dual-baseline improvement. The paired "
              "effects and uncertainty intervals quantify the range compatible with these data.")
    else:
        p("The outstanding paired evaluations determine which claims can be made about prediction quality "
          "at the registered horizons. The run ledger preserves every available observation and implementation failure.")
    p("Appendix · Computational cost", "heading")
    if resources:
        for device, rows in resources.items():
            p(escape(str(device)), "subheading")
            flow.append(_grid(styles, ["Corpus", "Phase", "Method", "Ratio", "Runs", "Targets/run",
                                       "Train (s)", "Targets/s", "Peak GPU (MiB)"],
                              rows, [56, 49, 78, 35, 34, 64, 48, 57, 54]))
        p("Times and rates are per-run medians within each hardware, method, phase, strength and "
          "target budget. The clock sums synchronized training steps, including batch transfer and "
          "the optimizer update and any host FP64 probe while the GPU is reserved. Evaluation, checkpointing and uploads take additional time. Peak "
          "memory is PyTorch’s recorded maximum allocated GPU tensor memory during the run, including "
          "evaluation. Untrained controls have no training speed.", "caption")
    else:
        p("Hardware, training speed and peak allocated memory will appear with the first completed run.")
    p("Development NLL at matched GPU training time", "subheading")
    p("For each seed the cutoff is the shortest completed training time across AdamW, trace and "
      "third-order training. Fixed-window development evaluations occur at discrete checkpoints. "
      "We take the latest checkpoint at or before the cutoff. Each cell gives NLL in nats per target "
      "token, followed by its lag behind the cutoff in seconds. Larger lags make the time comparison "
      "coarser. The archived per-seed table also records the token count at each checkpoint. "
      f"{_link(REPOSITORY + '/blob/main/reports/summary.md', 'Per-seed timing records')}", "caption")
    matched = _matched_rows(study)
    if matched:
        flow.append(_grid(styles, ["Corpus", "Seed", "Cutoff (s)", "AdamW NLL (lag s)",
                                   "Trace NLL (lag s)", "Third NLL (lag s)"],
                          matched, [82, 34, 65, 98, 98, 98]))
    else:
        p("Awaiting a complete, timed three-method confirmatory seed with eligible development checkpoints.", "caption")
    nonhost = _matched_rows(study,"matched_nonhost_time")
    if nonhost:
        p("Adapter timing after subtracting host derivative calls", "subheading")
        p("This supplementary clock removes the observed duration of host derivative calls including their "
          "transfers. The table uses the same fixed development windows and reports checkpoint lags in seconds. "
          "Individual CUDA kernel durations were not profiled.", "caption")
        flow.append(_grid(styles,["Corpus","Seed","Cutoff (s)","AdamW NLL (lag s)",
                                  "Trace NLL (lag s)","Third NLL (lag s)"],nonhost,[82,34,65,98,98,98]))
    from .flatness_tables import all_arm_groups
    p("Appendix · Flatness by model and reference","heading")
    p("Each entry gives a median and the measured/planned seed count. A wider interval of permitted weight or "
      "score displacement is flatter under its corresponding perturbation. Smaller RMS Hessian curvature indicates "
      "less local bending. Common score width uses identical token-level logit biases for every predictor within a "
      "stage, including the unigram. The retained strength-search and diagnostic measurements follow each stage. "
      f"{_link(REPOSITORY + '/blob/main/reports/amendments/all-model-flatness.md','Common measurement protocol')} · "
      f"{_link(REPOSITORY + '/blob/main/reports/flatness.md','Per-run evidence')}")
    for name,main_arms,other_arms in all_arm_groups(study):
        p(name,"subheading")
        flow.append(_grid(styles,["Variant","Training targets","Seeds","Weight width ↑","RMS curvature ↓","Score width ↑"],
                          main_arms+other_arms,[124,71,45,79,79,78]))
    pair_rows = [[STAGES[stage], METHODS.get(base, base), pair["seed"],
                  fmt(pair["third_nll"], 5), fmt(pair["baseline_nll"], 5), fmt(pair["delta"], 5)]
                 for stage, outcome in study["stages"].items()
                 for base, stats in outcome.get("comparisons", {}).items() for pair in stats["pairs"]]
    if pair_rows:
        p("Appendix · Paired effects", "heading")
        flow.append(_grid(styles, ["Corpus", "Baseline", "Seed", "Third NLL", "Baseline NLL", "ΔNLL"],
                          pair_rows, [85, 110, 40, 78, 82, 80]))
        for stage, outcome in study["stages"].items():
            for base, stats in outcome.get("comparisons", {}).items():
                lo, hi = stats["median_ci"]
                p(f"{STAGES[stage]} / {METHODS[base]}: median ΔNLL {fmt(stats['median_delta'], 5)}, "
                  f"interval [{fmt(lo,5)}, {fmt(hi,5)}] at achieved coverage {fmt(stats['ci_coverage'],4)}. "
                  f"Holm-adjusted p = {fmt(stats['p_holm'], 5)}.", "caption")
    examples = example_runs(study["runs"])
    if examples:
        p("Appendix · Output examples", "heading")
        p("For each stage and method, the first registered checkpoint and sample in run-ID order is shown in excerpt. "
          "The experiment ledger contains every full saved continuation and its corresponding "
          f"reference when recorded. {_link(REPOSITORY + '/tree/main/reports/experiments', 'All outputs')}")
        for run in examples:
            sample = run["samples"][0]
            label = f"{STAGES[run['stage']]} · {METHODS[run['method']]} · {run['phase']}, seed {run['seed']}"
            url = REPOSITORY + "/blob/main/results/" + run["id"] + "/samples.jsonl"
            example = [Paragraph(_link(url,label), styles["subheading"])]
            for field, name in (("prompt", "Prompt"), ("reference", "Reference"), ("continuation", "Prediction")):
                if sample.get(field) is not None:
                    value = str(sample[field])
                    excerpt = value[:420] + (" […]" if len(value) > 420 else "")
                    example.append(Paragraph(f"<b>{name}.</b> {escape(excerpt)}", styles["caption"]))
            flow.append(KeepTogether(example))
    p("References and reproducibility", "heading")
    for title, url in REFERENCES.values():
        p(_link(url, title), "caption")
    p(f"Rebuild tables, figures, the explorer and this paper with <b>uv run thirdloss report</b>. "
      f"{_link(REPOSITORY, 'Code and versioned protocol')}", "caption")
    flow.append(PageBreak())
    p("Appendix · Registered TinyStories schedules", "heading")
    p("The follow-up asks whether changing the third-derivative coefficient in response to low curvature "
      "helps retain a wider low-loss neighborhood. Eight paired seeds compare six arms at equal training tokens.")
    p("Shared training objective", "subheading")
    p("J<sub>t</sub> = L<sub>t</sub> + (I<sub>t</sub>/p) [α<sub>t</sub> h<sub>t</sub> + λ<sub>t</sub> P<sub>3,t</sub>]", "equation")
    p("h<sub>t</sub> = a<super>T</super>H<sub>t</sub>a, &nbsp;&nbsp; "
      "P<sub>3,t</sub> = ‖T<sub>t</sub>[u, v, ·]‖²", "equation")
    p("L<sub>t</sub> is the full update’s next-token loss. H<sub>t</sub> and T<sub>t</sub> are the Hessian "
      "and third derivative of the unregularized two-window loss in the trainable weights. The trace probe "
      "a and the two independent third-derivative probes u, v have random sign entries. I<sub>t</sub> is "
      "the Bernoulli gate with activation probability p = 1/8. Both coefficients are held fixed in each weight update.")
    p("Fixed-token ramp and controls", "subheading")
    p("s<sub>t</sub> = min(1, max(0, (n<sub>t</sub> − n<sub>0</sub>)/R)), &nbsp;&nbsp; "
      "λ<sub>t</sub> = λ<sub>max</sub> s<sub>t</sub>", "equation")
    p("Here n<sub>t</sub> counts training targets before update t, n<sub>0</sub> is the switch point, "
      "and R is the positive ramp length in tokens. The trace coefficient stays at α. Trace alone sets "
      "λ<sub>t</sub> = 0. Stronger trace sets λ<sub>t</sub> = 0 and α<sub>t</sub> = α + Δα s<sub>t</sub>, "
      "with Δα calibrated to the added penalty-gradient norm. The always-on comparison sets "
      "λ<sub>t</sub> = λ<sub>max</sub> from the start.")
    p("Curvature-dependent coefficient", "subheading")
    p("c<sub>t</sub> = [(1/(md)) ∑<sub>j∈S(t)</sub> ‖H<sub>j</sub>z<sub>j</sub>‖²]<super>1/2</super>", "equation")
    p("λ<sub>t</sub> = max(λ<sub>t−1</sub>, λ<sub>max</sub> max(0, 1 − c<sub>t</sub>/c<sub>*</sub>))", "equation")
    p("S(t) contains the last m training-only measurements before the update. Each z<sub>j</sub> is a random "
      "sign probe and d is the number of trainable weights. Start λ at zero. Enable this rule after warm-up "
      "once the loss criterion is met and the window is full. Below the fixed positive threshold c<sub>*</sub>, "
      "smaller curvature can raise λ up to λ<sub>max</sub>. Retaining the peak keeps the penalty active "
      "when curvature rebounds. A control replays other seeds’ coefficient histories in a prespecified permutation.")
    p("Directional width", "subheading")
    p("r<sub>±</sub>(θ, e) = inf { r &gt; 0 | L<sub>probe</sub>(θ ± re) − L<sub>probe</sub>(θ) ≥ δ }", "equation")
    p("W<sub>δ</sub>(θ) = median<sub>e</sub> [r<sub>+</sub>(θ, e) + r<sub>−</sub>(θ, e)]", "equation")
    p("Use fixed unit directions e, fixed training examples, unregularized loss L<sub>probe</sub>, and a "
      "positive loss tolerance δ. Compare changes in W<sub>δ</sub> from a common trace-trained checkpoint "
      "at matched token counts. Held-out development loss tests prediction separately. "
      f"{_link(REPOSITORY + '/blob/main/docs/third-derivative-penalty.md#weighting-the-penalty-by-curvature', 'Derivation')} · "
      f"{_link(REPOSITORY + '/blob/main/reports/plan.md#curvature-dependent-penalty-weight', 'Controls and readouts')}")
    p("Final seed sensitivity", "subheading")
    sensitivity=study.get("seed_sensitivity")
    if sensitivity:
        rows=[]
        for r in sensitivity["rows"]:
            if r["metric"] in {"Δtest NLL","Δwidth retained"}:
                loo=r.get("leave_one_out_medians")
                rows.append([STAGES[r["stage"]],r["arm"],r["metric"],f"{r['sample_sd']:.5g}" if loo else "Censored",
                             f"{min(loo):.5g} to {max(loo):.5g}" if loo else "Censored"])
        flow.append(_grid(styles,["Corpus","Paired contrast","Metric","Seed SD","Leave-one-out median range"],
                          rows,[83,130,68,67,116]))
    else:
        p("The final seed analysis follows the original frozen test evaluations, hybrid replications and checkpoint geometry.", "caption")
    p(f"{_link(REPOSITORY+'/blob/main/reports/seed-sensitivity.md','Full seed results and execution order')}", "caption")
    p("AI statement", "subheading")
    p("Codex wrote the codebase and paper from the exact specification provided by a human. "
      "Human cleanup and rewriting are in progress.", "caption")

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#ccd8d3"))
        canvas.line(doc.leftMargin, 40, A4[0] - doc.rightMargin, 40)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.setFont("PaperSans", 7.4)
        canvas.drawString(doc.leftMargin, 27, "THIRD-DERIVATIVE REGULARIZATION")
        canvas.drawRightString(A4[0] - doc.rightMargin, 27, str(doc.page))
        canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=output.parent, suffix=".pdf", delete=False) as handle:
        tmp = Path(handle.name)
    try:
        document = SimpleDocTemplate(str(tmp), pagesize=A4, leftMargin=49, rightMargin=49,
                                     topMargin=43, bottomMargin=54,
                                     title="Third-derivative regularization for causal language models",
                                     author="Libor “Burny” Burian")
        document.build(flow, onFirstPage=footer, onLaterPages=footer)
        os.replace(tmp, output)
    finally:
        tmp.unlink(missing_ok=True)
