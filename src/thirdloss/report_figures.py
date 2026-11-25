"""Publication figures from the same raw-run snapshot served by the interactive explorer."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

from .report_records import COLORS, METHODS, STAGES, finite

INK = "#263735"
GRID = "#dbe2df"


def _save(figure: Figure, path: Path) -> None:
    """Write a stable PNG atomically for Pages and the ReportLab paper."""
    FigureCanvasAgg(figure)
    with NamedTemporaryFile(dir=path.parent, suffix=".png", delete=False) as handle:
        temp = Path(handle.name)
    try:
        figure.savefig(temp, format="png", dpi=170, bbox_inches="tight", facecolor="white")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
        figure.clear()


def architecture(path: Path) -> None:
    """Draw the mathematical computation graph and the trainable coordinate choice."""
    fig = Figure(figsize=(10.2, 3.2))
    ax = fig.subplots()
    ax.set(xlim=(0, 10), ylim=(0, 3.25))
    ax.axis("off")

    def box(x, y, w, h, line1, line2, fill):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                   facecolor=fill, edgecolor="#afc7c0", linewidth=1.1))
        ax.text(x + w / 2, y + h * 0.63, line1, ha="center", va="center",
                color=INK, fontsize=9.6, fontweight="semibold")
        ax.text(x + w / 2, y + h * 0.29, line2, ha="center", va="center", color=INK, fontsize=8.5)

    def arrow(start, end):
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "-|>", "color": "#506c65",
                    "lw": 1.25, "shrinkA": 1, "shrinkB": 2})

    box(0.06, 2.12, 2.01, 0.77, "TinyStories", "all decoder weights", "#e7f2ef")
    box(0.06, 0.42, 2.01, 0.77, "Research abstracts", "Pythia QKV adapters", "#e7f2ef")
    box(2.65, 1.27, 1.85, 0.77, "Next-token loss", "cross-entropy L", "#f0f3f1")
    box(5.15, 2.12, 2.0, 0.77, "Hessian contraction", "independent signs u, v", "#f6ede6")
    box(7.84, 2.12, 2.0, 0.77, "Third derivative", "r = grad(uᵀ H v)", "#e7f2ef")
    box(7.84, 0.42, 2.0, 0.77, "Training objective", "L + weighted ‖r‖²", "#d9eee8")
    arrow((2.08, 2.48), (2.65, 1.83))
    arrow((2.08, 0.80), (2.65, 1.47))
    arrow((4.51, 1.84), (5.14, 2.47))
    arrow((7.17, 2.5), (7.82, 2.5))
    arrow((8.84, 2.08), (8.84, 1.2))
    arrow((4.51, 1.43), (7.80, 0.73))
    ax.text(5.8, 0.5, "AdamW differentiates the complete objective",
            fontsize=8, color="#526863", ha="center")
    _save(fig, path)


def _axes_style(ax, xlabel, ylabel):
    """Give each scale its units and never imply a zero baseline for a difference plot."""
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#91a09c")
    ax.tick_params(labelsize=8, color="#91a09c")


def _curves(study, path) -> bool:
    """Draw actual development measurements in stage/phase panels, preserving run identity."""
    groups = {}
    for run in study["runs"]:
        points = [(e["tokens"], e["dev_nll"]) for e in run["events"]
                  if finite(e.get("tokens")) and finite(e.get("dev_nll"))]
        if points:
            groups.setdefault((run.get("stage"), run.get("phase")), []).append((run, points))
    if not groups:
        return False
    fig = Figure(figsize=(8, 2.8 * len(groups)), layout="constrained")
    axes = fig.subplots(len(groups), 1, squeeze=False).ravel()
    for ax, ((stage, phase), series) in zip(axes, groups.items()):
        labels = set()
        for run, points in series:
            method = run.get("method")
            label = METHODS.get(method, method) if method not in labels else "_nolegend_"
            labels.add(method)
            tokens, losses = zip(*points)
            ax.plot(tokens, losses, color=COLORS.get(method, "#777"), marker=".",
                    markersize=3, linewidth=1, alpha=0.78, label=label)
        _axes_style(ax, "Training target tokens", "Development NLL (nats/token)")
        ax.set_title(f"{STAGES.get(stage, stage)}  /  {phase}", loc="left", fontsize=11, color=INK)
        ax.legend(loc="best", fontsize=7, frameon=False, ncol=2)
    _save(fig, path)
    return True


def _paired(study, path) -> bool:
    """Show every seed and the median interval for each registered comparison."""
    rows = [(stage, baseline, stats) for stage, outcome in study["stages"].items()
            for baseline, stats in outcome.get("comparisons", {}).items() if stats.get("pairs")]
    if not rows:
        return False
    fig = Figure(figsize=(8.5, 1.5 + 0.72 * len(rows)), layout="constrained")
    ax = fig.subplots()
    axis_labels = []
    for index, (stage, baseline, stats) in enumerate(rows):
        axis_labels.append(f"{STAGES[stage]} / {METHODS[baseline]}")
        pairs = stats["pairs"]
        y = [index + (k - (len(pairs) - 1) / 2) * 0.036 for k in range(len(pairs))]
        ax.scatter([pair["delta"] for pair in pairs], y, color=COLORS["third"], s=21, zorder=2)
        lo, hi = stats["median_ci"]
        if finite(lo) and finite(hi):
            ax.hlines(index + 0.22, lo, hi, color=INK, linewidth=1.5)
        ax.scatter([stats["median_delta"]], [index + 0.22], color=INK, marker="D", s=25, zorder=3)
    ax.axvline(0, color="#677572", linewidth=0.8, linestyle="--")
    ax.set_yticks(range(len(rows)), axis_labels)
    _axes_style(ax, "Test NLL difference, third-order minus baseline (nats/token)", "")
    ax.set_title("Paired seeds and median intervals", loc="left", fontsize=11, color=INK)
    _save(fig, path)
    return True


def build_figures(study: dict, directory: Path) -> dict:
    """Emit the architecture always and measured plots only when observations exist."""
    directory.mkdir(parents=True, exist_ok=True)
    architecture(directory / "architecture.png")
    products = {"architecture": "architecture.png"}
    for key, draw in (("curves", _curves), ("paired", _paired)):
        file = directory / f"{key}.png"
        if draw(study, file):
            products[key] = file.name
        else:
            file.unlink(missing_ok=True)
    return products
