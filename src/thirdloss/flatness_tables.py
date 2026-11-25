"""Describe checkpoint widths, directional variation and local curvature without treating rays as seeds."""

from statistics import median

from .flatness_stats import quantile_bounds
from .records import HORIZONS,RATIOS
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


def checkpoint_table(method,weight,score):
    """Use the same labels, coordinates and censoring in the experiment report and model card."""
    weight=weight or {}
    score=score or {}
    missing="N/A · no trainable weights" if method=="unigram" else "Pending"
    def width(point,absent):
        return _width_stat([point],.5) if "width" in point else absent
    def number(point,key,absent):
        return f"{point[key]:.6g}" if key in point else absent
    rows=[
        ["Weight width",width(weight,missing),"↑ Wider is flatter in these weight coordinates"],
        ["RMS weight curvature",number(weight,"rms_curvature",missing),"↓ Lower means less local bending"],
        ["Signed Hessian trace / parameter",number(weight,"trace_per_parameter",missing),"No general better direction"],
        ["Common score width",width(score,"Pending"),"↑ Wider tolerates larger changes in token scores"],
        ["Mean directional score curvature",number(score,"mean_directional_curvature","Pending"),
         "↓ Lower means less local bending in score space"],
    ]
    return markdown_table(rows,["Training-window measurement","Value","Interpretation"])


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


def all_arm_groups(study):
    """Include every registered predictor, hyperparameter and control with explicit coverage denominators."""
    groups=[]
    for stage,name in (("stories","TinyStories · all model weights"),("abstracts","Pythia-410M · adapter weights")):
        ratios=study["context"][stage]["selection"].get("ratios",{})
        target=HORIZONS[stage]
        stage_runs=[r for r in study["runs"] if r.get("stage")==stage and completed(r)]
        measured=[r["score_flatness"] for r in stage_runs if "score_flatness" in r]
        if len({(p["protocol"],p["probe_windows_sha256"],p["direction_sha256"],p["vocab"]) for p in measured})>1:
            raise ValueError(f"The output-space comparison for {stage} mixes probes or vocabularies")
        def line(phase,method,ratio,budget,seeds,label=None):
            runs=[r for r in stage_runs if r["phase"]==phase and r["method"]==method and r["seed"] in seeds
                  and r["tokens"]==budget and (ratio is None or r["ratio"]==ratio)]
            widths=[];curvature=[];scores=[]
            for r in runs:
                w=r.get("flatness") or r.get("widths",{}).get(str(r.get("steps")))
                if w and "width" in w:
                    widths.append(w)
                if "flatness" in r:
                    curvature.append(r["flatness"]["rms_curvature"])
                if "score_flatness" in r:
                    scores.append(r["score_flatness"])
            def value(points,formatter):
                return (formatter(points)+f" ({len(points)}/{len(seeds)})") if points else "Pending"
            cohort=str(seeds[0]) if len(seeds)==1 else f"{seeds[0]}–{seeds[-1]}"
            native=value(widths,lambda items:_width_stat(items,.5)) if method!="unigram" else "N/A · no weights"
            rms=value(curvature,lambda items:f"{median(items):.5g}") if method!="unigram" else "N/A · no weights"
            return [label or METHODS[method],f"{budget:,}",cohort,native,rms,value(scores,lambda items:_width_stat(items,.5))]
        one=(0,); confirm=range(1,9); follow=range(21,29)
        rows=[line("control",m,0.,0,one) for m in ("initial","unigram")]
        arms={"ce":0.,"trace":ratios.get("trace"),"third":ratios.get("third"),"hessian_norm":.03,
              "sham":ratios.get("third"),"combined":ratios.get("third")}
        for m,r in arms.items():
            if r is not None:
                rows.append(line("pilot",m,r,target//8,one,METHODS[m]+(f" ({r:.0%})" if r else "")))
        for m in ("ce","trace","third"):
            rows.append(line("confirm",m,arms[m],target,confirm,METHODS[m]+" · confirmation"))
        if stage=="stories":
            rows.append(line("branch","trunk",.01,target//2,follow))
            for m in ("adaptive","late","trace","strong","replay","always"):
                rows.append(line("hybrid",m,.01,target,follow,METHODS[m]+" · hybrid study"))
        extra=[line("pilot",m,r,target//8,one,f"{METHODS[m]} ({r:.0%})") for m in ("trace","third")
               for r in RATIOS if r!=arms[m]]
        for row in stage_runs:
            if row["phase"]=="diagnostic":
                extra.append(line("diagnostic",row["method"],row["ratio"],row["tokens"],(row["seed"],),
                                  f"{METHODS[row['method']]} ({row['ratio']:.0%}) · excluded precision diagnostic"))
        groups.append((name,rows,extra))
    return groups


def all_arm_tables(study):
    headers=["Variant","Training targets","Seed cohort","Weight width<br>↑ Wider is flatter",
             "RMS weight curvature<br>↓ Less local bending","Common score width<br>↑ More score tolerance"]
    tables=[]
    for name,rows,extra in all_arm_groups(study):
        tables.extend([f"**{name}**",markdown_table(rows,headers)])
        tables.append(f"<details><summary>{name} · other pilot strengths and precision diagnostics</summary>\n\n"
                      +markdown_table(extra,headers)+"\n\n</details>")
    return tables


def flatness_ledger(study):
    """Provide one evidence link per measured checkpoint, including secondary controls and censored rays."""
    rows=[]
    for r in study["runs"]:
        p=r.get("flatness")
        s=r.get("score_flatness")
        if p or s:
            base=f"../results/{r['id']}/"
            links=([f"[Weight probes]({base}flatness.json)"] if p else [])+([f"[Score probes]({base}score-flatness.json)"] if s else [])
            rows.append([r["stage"],r["phase"],r["seed"],METHODS[r["method"]],f"{r['ratio']:.0%}",
                         *([_width_stat([p],.5),_spread([p]),_ray_count([p]),f"{p['rms_curvature']:.6g}",
                            f"{p['trace_per_parameter']:+.6g}"] if p else ["N/A" if r["method"]=="unigram" else "Pending"]*5),
                         *([_width_stat([s],.5),_spread([s]),_ray_count([s]),f"{s['mean_directional_curvature']:.6g}"] if s else ["Pending"]*4),
                         " · ".join(links)])
    text=["# Flatness at saved checkpoints",
          "Widths are measured in each model’s trainable coordinates. A larger width is flatter at the specified "
          "training-loss tolerance. A smaller RMS curvature means less local bending. Opposite curvature signs "
          "can cancel in the normalized trace. [Measurement design](amendments/checkpoint-flatness.md)",
          "## Registered TinyStories hybrids",hybrid_flatness_table(study["runs"]),
          "The seed range and directional spread describe variability. The rays at the limit give measurement coverage. "
          "Compare matching seeds for differences between arms. [Every crossing and paired comparison](hybrid/results.md)",
          "## Every variant and baseline","Parentheses give measured / planned seeds. A unigram has only the common score-space measurement. "
          "[Shared score perturbations](amendments/all-model-flatness.md)",*all_arm_tables(study),
          "## Per-run checkpoint measurements"]
    text.append(markdown_table(rows,["Stage","Horizon","Seed","Arm","Strength","Weight width ↑","Weight middle 50%",
                                    "Weight rays at limit","RMS curvature ↓","Signed trace / parameter","Score width ↑",
                                    "Score middle 50%","Score rays at limit","Mean score curvature","Evidence"])
                if rows else "Awaiting the first saved primary-checkpoint measurement.")
    return "\n\n".join(text)+"\n"
