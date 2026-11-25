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

from .report_records import METHODS, REPOSITORY, STAGES, completed, describe_difference, finite, fmt, verdict_text

REFERENCES = {
    "roughness": ("Duchon, Splines minimizing rotation-invariant semi-norms in Sobolev spaces",
                  "https://doi.org/10.1007/BFb0086566"),
    "trace": ("Liu, Yu and Lin, Regularizing deep neural networks with stochastic estimators of Hessian trace",
              "https://arxiv.org/pdf/2208.05924"),
    "sketch": ("Bujanović and Kressner, Norm and trace estimation with random rank-one vectors",
               "https://arxiv.org/pdf/2004.06433"),
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
    return _link(url, label.split(",")[0] if key != "trace" else "Liu, Yu and Lin")


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


def _score_rows(study):
    """Separate tuning strengths and token horizons before any descriptive aggregation."""
    groups = {}
    for run in study["runs"]:
        if completed(run):
            key = (run.get("stage"), run.get("phase"), run.get("method"),
                   run.get("ratio"), run.get("tokens"))
            groups.setdefault(key, []).append(run)
    rows = []
    for (stage, phase, method, ratio, tokens), runs in groups.items():
        def middle(key):
            values = [r[key] for r in runs if finite(r.get(key))]
            return fmt(median(values), 4) if values else "—"
        rows.append([STAGES.get(stage, stage), phase, METHODS.get(method, method),
                     fmt(ratio), len(runs), fmt(tokens, 0), middle("dev_nll"), middle("test_nll")])
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
      " ".join(f"{STAGES[s]}: {escape(verdict_text(outcome))}" for s, outcome in study["stages"].items()))
    p("Motivation and related work", "heading")
    p("A Hessian gives a local quadratic description of loss. Two nearby sets of weights "
      "can share its trace while individual curvature components vary. Summing squared "
      "third partials assigns a nonnegative cost to that variation in the chosen coordinates. "
      "The proposed local density adapts an order-three spline roughness measure. The "
      "published signed-trace language experiments studied recurrent language models. "
      f"{_cite('roughness')} · {_cite('trace')} · {_cite('coordinates')}")
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
    run_count = len(study["runs"])
    done_count = sum(completed(run) for run in study["runs"])
    p(f"The ledger contains {run_count} runs and {done_count} completed summaries. "
      f"{_link(REPOSITORY + '/tree/main/results', 'Raw records')} · "
      f"{_link(REPOSITORY + '/blob/main/reports/experiments/experiments.md', 'Per-run ledger')}")
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
    evaluated = _score_rows(study)
    if evaluated:
        p("Scores across methods", "subheading")
        flow.append(_grid(styles, ["Corpus", "Phase", "Method", "Ratio", "Runs", "Tokens/run", "Dev NLL", "Test NLL"],
                          evaluated, [60, 53, 105, 36, 34, 69, 58, 60]))
        p("Table 1. Medians over available completed runs sharing corpus, method, development "
          "strength and token horizon. NLL is in nats per target token. Dashes mark missing "
          "observations. The paired seed analyses use individual final test scores.", "caption")
    for key, caption in (("curves", "Development NLL by logged token count. Each line is a run; "
                                    "panels separate training stages and phases."),
                         ("paired", "Individual differences in test NLL. Diamonds mark median "
                                    "differences and horizontal segments show their registered intervals.")):
        if key in figures:
            flow.append(KeepTogether([_figure(figure_dir / figures[key]),
                                      Paragraph(caption, styles["caption"])]))
    p("Discussion and limitations", "heading")
    p("Predictive utility requires lower held-out loss against both baselines. A reduction in "
      "the derivative estimate alone describes local geometry. Parameterization changes its "
      "magnitude, including the low-rank factorization used for abstracts. The estimate targets "
      "expected two-window minibatch roughness. The small datasets, limited seed count and "
      "two tokenization schemes bound the interpretation. More tokens per GPU hour can change "
      "the practical ranking. "
      f"{_cite('coordinates')} · {_link(REPOSITORY + '/blob/main/reports/preregistration.md', 'Scope of inference')}")
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
    has_examples = any(run["samples"] for run in study["runs"])
    if has_examples:
        p("Appendix · Output examples", "heading")
        p("For each stage and method, the first saved sample in run-ID order is shown in excerpt. "
          "The experiment ledger contains every full saved continuation and its corresponding "
          f"reference when recorded. {_link(REPOSITORY + '/tree/main/reports/experiments', 'All outputs')}")
        seen = set()
        for run in study["runs"]:
            key = (run.get("stage"), run.get("method"))
            if not run["samples"] or key in seen:
                continue
            seen.add(key)
            sample = run["samples"][0]
            p(f"{STAGES.get(key[0], key[0])} · {METHODS.get(key[1], key[1])}", "subheading")
            for field, name in (("prompt", "Prompt"), ("reference", "Reference"), ("continuation", "Prediction")):
                if sample.get(field) is not None:
                    value = str(sample[field])
                    excerpt = value[:420] + (" […]" if len(value) > 420 else "")
                    p(f"<b>{name}.</b> {escape(excerpt)}", "caption")
    p("References and reproducibility", "heading")
    for title, url in REFERENCES.values():
        p(_link(url, title), "caption")
    p(f"Rebuild tables, figures, the explorer and this paper with <b>uv run thirdloss report</b>. "
      f"{_link(REPOSITORY, 'Code and versioned protocol')}", "caption")
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
