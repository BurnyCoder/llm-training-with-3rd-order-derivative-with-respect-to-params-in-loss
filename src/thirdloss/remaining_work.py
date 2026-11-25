"""Project outstanding study time from measured pilot, restart, geometry and publication records."""

from datetime import datetime,timezone
from math import ceil
from statistics import median

from .flatness_progress import geometry_coverage,published_pilot_timings
from .records import HORIZONS,read_json,sha256,storage_root,time_now,write_json
from .report_records import completed


def primary_work(arms,runs):
    """Only unscored frozen checkpoints retain a test cost after their training is complete."""
    hours=0.
    publications=0
    for arm in arms:
        stage,method=arm["stage"],arm["method"]
        fitted=[r for r in runs if r["stage"]==stage and r["method"]==method and r["phase"]=="confirm"
                and completed(r) and r["tokens"]==HORIZONS[stage]]
        train_left=8-len(fitted)
        test_left=8-sum("test_nll" in r for r in fitted)
        test_hours=arm["projected_test_seconds_per_run"]/3600
        hours+=train_left*(arm["projected_hours_all_seeds"]/8-test_hours)+test_left*test_hours
        publications+=train_left+test_left
    return hours,publications


def _release_benchmark(project,runs):
    """Freeze twelve recent end-to-end release intervals from checksum-matched completion receipts."""
    path=project/"results"/"feasibility"/"checkpoint-publication-time.json"
    if path.exists():
        return read_json(path)
    receipts=storage_root(project)/"releases"
    observations=[]
    for row in sorted(runs,key=lambda r:r["finished_at"],reverse=True):
        run=row["id"]
        record=receipts/(run+".json")
        if not record.is_file():
            continue
        receipt=read_json(record)
        if receipt["summary_sha256"]!=sha256(project/"results"/run/"summary.json"):
            continue
        end=datetime.fromtimestamp(record.stat().st_mtime,timezone.utc)
        seconds=(end-datetime.fromisoformat(row["finished_at"])).total_seconds()
        if seconds<0:
            raise ValueError(f"Publication receipt precedes {run}")
        observations.append({"run":run,"finished_training_at":row["finished_at"],"receipt_written_at":end.isoformat(),
                             "git_revision":receipt["git_revision"],"seconds":seconds})
        if len(observations)==12:
            result={"observations":observations,"basis":"Wall time between model completion and the local verified "
                    "Git and Hugging Face release receipt, sampled from the twelve latest published hybrid checkpoints."}
            write_json(path,result)
            return result
    return None


def remaining_work(project,study,primary,followup,uptime,original_done,original_total):
    """Separate the timing scenarios from statistical uncertainty about prediction and basin width."""
    counts=geometry_coverage(study)
    runs=[r for r in study["runs"] if completed(r)]
    hybrids=[r for r in runs if r["phase"] in {"hybrid","branch"}]
    covered=original_done+len(hybrids)+sum(c["complete"] for c in counts.values())
    total=original_total+8*(6+1)+sum(c["planned"] for c in counts.values())
    text=[f"Across training, references, final tests, hybrid runs and flatness evaluations, "
          f"**{covered}/{total} milestones are complete ({covered/total:.1%})** and {total-covered} remain. "
          "Each milestone has equal weight in this count. Data preparation, software and publications are recorded separately."]
    timing=published_pilot_timings(project)
    if not (timing and primary and followup):
        return text
    releases=_release_benchmark(project,hybrids)
    if not releases:
        return text
    arms=primary["arms"]
    confirm_hours,publications=primary_work(arms,runs)
    auxiliary_hours=0.
    for stage in HORIZONS:
        missing=sum(not any(r["stage"]==stage and r["phase"]=="pilot" and r["method"]==m for r in runs)
                    for m in ("hessian_norm","sham","combined"))
        seconds=max(a["pilot_loop_seconds"]+a["pilot_finalizing_seconds"] for a in arms if a["stage"]==stage)
        auxiliary_hours+=missing*seconds/3600
        publications+=missing
    # Charge a whole six-job block for a partly trained seed. The replay has its own measured proxy.
    finished={(r["seed"],r["method"]) for r in hybrids}
    blocks=sum(any((seed,m) not in finished for m in ("trunk","adaptive","late","trace","strong","always")) for seed in range(21,29))
    replays=sum((seed,"replay") not in finished for seed in range(21,29))
    hybrid_hours=blocks*(followup["observed_six_jobs_hours"]-(uptime or {}).get("observed_gap_hours",0.))
    hybrid_hours+=replays*(followup["estimated_one_replay_hours"]-(uptime or {}).get("replay_proxy_gap_hours",0.))
    release_times=sorted(obs["seconds"] for obs in releases["observations"])
    scenarios={}
    for name,estimate,release in (("typical",median,median(release_times)),
                                  ("slower",max,release_times[ceil(.9*len(release_times))-1])):
        geometry_hours=sum((c["planned"]-c["complete"])*estimate(r["cycle_seconds"] for r in timing["rows"]
                           if r["stage"]==stage)/3600 for stage,c in counts.items())
        costs={"confirmatory_training_and_test":confirm_hours,"hybrid_training_and_widths":hybrid_hours,
               "secondary_pilots":auxiliary_hours,"flatness_and_its_publication":geometry_hours,
               "original_model_publications":publications*release/3600}
        scenarios[name]={**costs,"total_hours":sum(costs.values())}
    now=time_now()
    available=168-(datetime.fromisoformat(now)-datetime.fromisoformat(primary["first_training_update_at"])).total_seconds()/3600
    write_json(project/"results"/"feasibility"/"remaining-work.json",
               {"as_of":now,"completed":covered,"planned":total,"remaining":total-covered,"remaining_hours_in_week":available,
                "hybrid_blocks_left_including_partial":blocks,"replays_left":replays,"remaining_primary_publications":publications,
                "geometry":counts,"scenarios":scenarios})
    low,high=(scenarios[k]["total_hours"] for k in ("typical","slower"))
    text.append(f"Projected remaining machine time is **{low:.2f}–{high:.2f} hours**, including model publication and "
                f"geometry. There are {available:.2f} hours left in the original week. These are two timing scenarios. "
                "They use the recorded pilot rates, whole remaining hybrid seed blocks, the longest primary pilot as a proxy "
                "for each remaining secondary pilot, and median or slower diagnostic and release cycles. Machine or network "
                "interruptions can extend them. [Cost by task](../results/feasibility/remaining-work.json) · "
                "[Observed release times](../results/feasibility/checkpoint-publication-time.json)")
    return text
