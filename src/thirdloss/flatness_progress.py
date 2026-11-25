"""Count checkpoint coverage and project the additional serial geometry work from observed wall time."""

from datetime import datetime
from statistics import median

from .records import RATIOS,read_json,write_json


def published_pilot_timings(project):
    """Keep the original start, measurement-complete and publication-complete times for each pilot."""
    path=project/"results"/"feasibility"/"flatness-pilot-wall-time.json"
    if path.exists():
        return read_json(path)
    for log in sorted((project/"logs").glob("checkpoint-flatness-*Z.log")):
        rows=[]
        for line in log.read_text(encoding="utf-8-sig").splitlines():
            stamp,_,body=line.partition(" ")
            if body.startswith("Measuring checkpoint flatness for ") or body.startswith("Completed pilot flatness measurements"):
                if rows:
                    rows[-1]["published_by"]=stamp
                if body.startswith("Measuring"):
                    rows.append({"run":body.split()[-1],"started_at":stamp})
            elif rows and body.startswith(rows[-1]["run"]+" width="):
                rows[-1]["measured_at"]=stamp
        if not rows or any("published_by" not in row or "measured_at" not in row for row in rows):
            continue
        for row in rows:
            summary=read_json(project/"results"/row["run"]/"summary.json")
            row["stage"]=summary["stage"]
            start,measured,end=(datetime.fromisoformat(row[key]) for key in ("started_at","measured_at","published_by"))
            if not start<=measured<=end:
                raise ValueError(f"Unordered pilot geometry timings for {row['run']}")
            row["measurement_seconds"]=(measured-start).total_seconds()
            row["cycle_seconds"]=(end-start).total_seconds()
        if {r["stage"] for r in rows}=={"stories","abstracts"}:
            result={"source_log":log.name,"rows":rows,
                    "basis":"Elapsed time between consecutive native-probe starts, or until the last release. "
                            "Includes checkpoint loading, weight widths, Hessian estimates, report generation and publication. "
                            "The shared logit test was added subsequently."}
            write_json(path,result)
            return result
    return None


def geometry_coverage(study):
    """Count complete predictors separately from their individual weight and output probes."""
    counts={}
    for stage in ("stories","abstracts"):
        runs=[r for r in study["runs"] if r.get("stage")==stage]
        # Two untrained references, ordinary training, two strength sweeps, three controls, three paired arms.
        planned=2+1+2*len(RATIOS)+3+3*8
        if stage=="stories":
            planned+=8*(1+6)  # one trace trunk and six full follow-up arms per seed
        planned+=sum(r["phase"]=="diagnostic" for r in runs)
        weight=sum("flatness" in r for r in runs)
        score=sum("score_flatness" in r for r in runs)
        complete=sum("score_flatness" in r and ("flatness" in r or r["method"]=="unigram") for r in runs)
        counts[stage]={"planned":planned,"weight":weight,"score":score,"complete":complete}
    return counts


def geometry_progress(project,study):
    """Compute denominators from the registered number of arms, strengths and seeds in each cohort."""
    from .report_records import markdown_table
    timings=published_pilot_timings(project)
    rows=[]
    all_remaining=[]
    for stage,counts in geometry_coverage(study).items():
        planned=counts["planned"]
        coverage=[stage,f"{counts['weight']}/{planned-1}",f"{counts['score']}/{planned}"]
        if timings:
            cycles=[r["cycle_seconds"] for r in timings["rows"] if r["stage"]==stage]
            remaining=planned-counts["complete"]
            all_remaining.append((remaining*median(cycles)/3600,remaining*max(cycles)/3600))
            coverage+= [f"{median(cycles):.0f} s",f"{max(cycles):.0f} s"]
        rows.append(coverage)
    columns=["Stage","Weight geometry","Shared score geometry"]
    if timings:
        columns+=["Median pilot cycle","Longest pilot cycle"]
    parts=["## Flatness coverage",markdown_table(rows,columns),
           "Weight geometry covers every neural checkpoint. Score geometry also covers the two unigram references. "
           "[All arms and their measurements](flatness.md#every-variant-and-baseline)"]
    if timings:
        typical,slow=map(sum,zip(*all_remaining))
        parts.append(f"Giving each predictor still missing a measurement one complete native pilot cycle projects "
                     f"{typical:.2f} additional hours at each stage’s median or {slow:.2f} hours at its longest observed cycle. "
                     "These scenarios include the observed reporting and upload time. Existing hybrid widths can be reused. "
                     "The shared score calculation, archive growth and future interruptions can change the total. "
                     "[Timestamped pilot measurements](../results/feasibility/flatness-pilot-wall-time.json) · "
                     f"[Archived timing log](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/logs/{timings['source_log']})")
    return parts
