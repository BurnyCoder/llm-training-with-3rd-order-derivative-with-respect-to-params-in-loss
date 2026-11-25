"""Describe checkpoint widths, directional variation and local curvature without treating rays as seeds."""

from statistics import median

from .flatness_stats import quantile_bounds
from .report_records import METHODS,completed,markdown_table


def _bound_text(interval,censored=False):
    low,high=interval
    if high is None:
        return f"≥{low:.3f}"
    if censored and f"{low:.3f}"!=f"{high:.3f}":
        return f"[{low:.3f}, {high:.3f}]"
    return f"{(low+high)/2:.3f}"


def _width_stat(points,fraction):
    """Use each registered midpoint when available and keep the lower bound of every censored seed."""
    bounds=[[p["width"],p["width"]] if p["width"] is not None else [p["width_lower"],None] for p in points]
    return _bound_text(quantile_bounds(bounds,fraction),any(b[1] is None for b in bounds))


def _spread(points):
    if not all("direction_q1" in p for p in points):
        return "—"
    bounds=[quantile_bounds([p[key] for p in points],.5) for key in ("direction_q1","direction_q3")]
    return "–".join(_bound_text(b,any(p["censored_rays"] for p in points)) for b in bounds)


def _seed_range(points):
    return "One seed" if len(points)==1 else "–".join(_width_stat(points,q) for q in (0.,1.))


def _ray_count(points):
    if not all(p.get("ray_count") for p in points):
        return "—"
    return f"{sum(p['censored_rays'] for p in points)}/{sum(p['ray_count'] for p in points)}"


def hybrid_flatness_rows(runs):
    """Show which seeds contributed to each arm; their random directions are shared by design."""
    rows=[]
    for arm in ("adaptive","late","trace","strong","replay","always"):
        subset=sorted((r for r in runs if r.get("phase")=="hybrid" and completed(r) and r["method"]==arm
                       and all(str(step) in r.get("widths",{}) for step in (2048,4096))),key=lambda r:r["seed"])
        if not subset:
            continue
        initial=[r["widths"]["2048"] for r in subset]
        final=[r["widths"]["4096"] for r in subset]
        rows.append([METHODS[arm],", ".join(str(r["seed"]) for r in subset),_width_stat(initial,.5),
                     _width_stat(final,.5),_seed_range(final),_spread(final),_ray_count(final)])
    return rows


def hybrid_flatness_table(runs):
    rows=hybrid_flatness_rows(runs)
    if not rows:
        return "Awaiting completed hybrid checkpoints."
    return markdown_table(rows,["Hybrid arm","Seeds","Switch width<br>↑ Wider is flatter","Final width<br>↑ Wider is flatter","Final seed range",
                                "Middle 50% of final directions","Rays at limit / tested"])


def primary_flatness_rows(pairs):
    """Compare the same measured seeds, trainable parameterization, training windows and probe backend."""
    methods=("ce","trace","third")
    measured=[pair for pair in pairs if all("flatness" in pair[m] for m in methods)]
    if not measured:
        return []
    signatures={(pair[m]["flatness"]["protocol"],pair[m]["flatness"]["probe_windows_sha256"],
                 pair[m]["flatness"]["width_device"],pair[m]["flatness"]["hessian_device"]) for pair in measured for m in methods}
    if len(signatures)!=1:
        raise ValueError("Matched flatness statistics require the same probes and arithmetic")
    groups=[[pair[m]["flatness"] for pair in measured] for m in methods]
    return [
        ["Directional width<br>↑ Wider is flatter",*[_width_stat(g,.5) for g in groups]],
        ["Final width range across seeds<br>Descriptive spread",*[_seed_range(g) for g in groups]],
        ["Middle 50% of directions<br>Descriptive spread",*[_spread(g) for g in groups]],
        ["Rays at limit / tested<br>Measurement coverage",*[_ray_count(g) for g in groups]],
        ["Unperturbed probe NLL<br>↓ Lower fits these windows better",*[f"{median(p['baseline_nll'] for p in g):.5f}" for g in groups]],
        ["RMS Hessian curvature<br>↓ Lower means less local bending",*[f"{median(p['rms_curvature'] for p in g):.6g}" for g in groups]],
        ["Signed Hessian trace / parameter<br>No general better direction",*[f"{median(p['trace_per_parameter'] for p in g):+.6g}" for g in groups]],
    ]


def flatness_ledger(study):
    """Provide one evidence link per measured checkpoint, including secondary controls and censored rays."""
    rows=[]
    for r in study["runs"]:
        if "flatness" in r:
            p=r["flatness"]
            rows.append([r["stage"],r["phase"],r["seed"],METHODS[r["method"]],_width_stat([p],.5),
                         _spread([p]),_ray_count([p]),f"{p['rms_curvature']:.6g}",f"{p['trace_per_parameter']:+.6g}",
                         f"[All probes](../results/{r['id']}/flatness.json)"])
    text=["# Flatness at saved checkpoints",
          "Widths are measured in each model’s trainable coordinates. A larger width is flatter at the specified "
          "training-loss tolerance. A smaller RMS curvature means less local bending. Opposite curvature signs "
          "can cancel in the normalized trace. [Measurement design](amendments/checkpoint-flatness.md)",
          "## Registered TinyStories hybrids",hybrid_flatness_table(study["runs"]),
          "The seed range and directional spread describe variability. The rays at the limit give measurement coverage. "
          "Compare matching seeds for differences between arms. [Every crossing and paired comparison](hybrid/results.md)",
          "## Secondary checkpoint measurements"]
    text.append(markdown_table(rows,["Stage","Horizon","Seed","Arm","Width ↑","Middle 50% of directions",
                                    "Rays at limit / tested","RMS curvature ↓","Signed trace / parameter","Evidence"])
                if rows else "Awaiting the first saved primary-checkpoint measurement.")
    return "\n\n".join(text)+"\n"
