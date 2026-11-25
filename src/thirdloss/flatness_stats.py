"""Order statistics for two-sided perturbation widths with finite bisection and open upper bounds."""

import math
from statistics import median


def width_statistics(rays):
    """The registered endpoint uses the medians of both crossing brackets, including open ends."""
    lows,highs=[],[]
    for ray in rays:
        bounds=(ray["positive"],ray["negative"])
        lows.append(sum(b["lower"] for b in bounds))
        highs.append(sum(b["upper"] if b["upper"] is not None else math.inf for b in bounds))
    lower,upper=median(lows),median(highs)
    return {"directions":rays,"width_lower":lower,"width_upper":upper if math.isfinite(upper) else None,
            "width":(lower+upper)/2 if math.isfinite(upper) else None,
            "censored_rays":sum(ray[s]["upper"] is None for ray in rays for s in ("positive","negative"))}


def _quantile(values, fraction):
    """Linear empirical quantile, including an unbounded upper endpoint when its weight is positive."""
    ordered=sorted(values)
    position=(len(ordered)-1)*fraction
    lower=math.floor(position)
    upper=math.ceil(position)
    if lower==upper or ordered[lower]==ordered[upper]:
        return ordered[lower]
    return ordered[lower]+(ordered[upper]-ordered[lower])*(position-lower)


def quantile_bounds(bounds,fraction):
    """Monotonicity transfers the brackets on the individual widths to the same order statistic."""
    low=_quantile([b[0] for b in bounds],fraction)
    high=_quantile([b[1] if b[1] is not None else math.inf for b in bounds],fraction)
    return [low,high if math.isfinite(high) else None]


def direction_summary(width):
    """Keep the per-direction middle half and denominator without copying raw rays into the dashboard."""
    bounds=[]
    for ray in width.get("directions",[]):
        pos,neg=ray["positive"],ray["negative"]
        upper=None if pos["upper"] is None or neg["upper"] is None else pos["upper"]+neg["upper"]
        bounds.append([pos["lower"]+neg["lower"],upper])
    if not bounds:
        return {}
    return {"direction_q1":quantile_bounds(bounds,.25),"direction_q3":quantile_bounds(bounds,.75),
            "ray_count":2*len(bounds)}


def compact_width(width):
    """Leave every individual ray in the linked raw file and retain summary statistics for rendering."""
    return {**{k:v for k,v in width.items() if k!="directions"},**direction_summary(width)}
