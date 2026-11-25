"""Build README head-to-head tables from matched, completed runs and their raw scores."""

from dataclasses import dataclass
from html import escape
from statistics import median

from .analysis import _time_match
from .flatness_tables import all_arm_tables,hybrid_flatness_table,primary_flatness_rows
from .records import HORIZONS
from .report_records import METHODS, completed, finite, markdown_table, verdict_text


@dataclass(frozen=True)
class Metric:
    key: str
    title: str
    digits: int
    larger: bool = False
    scale: float = 1.
    suffix: str = ""

    @property
    def direction(self):
        """State the objective beside each score, including the narrower meaning of geometric width."""
        if self.key=="width_gain":
            return "↑ More retained is better for the width test"
        return "↑ Higher is better" if self.larger else "↓ Lower is better"


NLL = Metric("dev_nll","Development NLL",6)
ACCURACY = Metric("dev_accuracy","Dev top-1 accuracy",3,True,100.,"%")
SPEED = Metric("tokens_per_sec","Training speed (targets/s)",0,True)
MEMORY = Metric("peak_vram_mb","Peak GPU allocation (MiB)",1)
WIDTH = Metric("width_gain","Width change after switch",4,True)
EQUAL_TIME = Metric("equal_time_nll","Equal-time probe NLL",5)
TEST = Metric("test_nll","Final test NLL",6)
TEST_ACC = Metric("test_accuracy","Final test accuracy",3,True,100.,"%")
STAGES = {"stories":"TinyStories pretraining","abstracts":"Pythia-410M adapters"}
PRIMARY = ("ce","trace","third")
SHORT = {"ce":"AdamW","trace":"Hessian trace","third":"Third order","hessian_norm":"Squared Hessian",
         "sham":"Scrambled signs","combined":"Trace + third","adaptive":"Adaptive","late":"Fixed ramp"}


def _effect(pairs,metric,method,baseline):
    """Use paired changes, including within-seed speed ratios and percentage-point accuracy changes."""
    changes=[]
    for pair in pairs:
        value=pair[method].get(metric.key)
        reference=pair[baseline].get(metric.key)
        if finite(value) and finite(reference):
            if metric==SPEED:
                if reference>0:
                    changes.append(100*(value/reference-1))
            else:
                changes.append((value-reference)*metric.scale)
    if not changes:
        return "—"
    change=median(changes)
    digits=1 if metric==SPEED else metric.digits
    if round(abs(change),digits)==0:
        return "Tie"
    amount=f"{abs(change):,.{digits}f}"
    if metric==SPEED:
        return amount+("% faster" if change>0 else "% slower")
    if metric==WIDTH:
        return amount+(" more retained" if change>0 else " less retained")
    if metric==MEMORY:
        return amount+(" MiB more" if change>0 else " MiB less")
    if metric.scale==100:
        amount+=" pp"
    return amount+(" higher" if change>0 else " lower")


def _score_table(pairs,methods,metrics,comparisons=()):
    """Rank the displayed medians. A row uses the same finite observations for every method."""
    rows=[]
    for metric in metrics:
        eligible=[p for p in pairs if all(finite(p[m].get(metric.key)) for m in methods)]
        if not eligible:
            continue
        values=[median(p[m][metric.key] for p in eligible)*metric.scale for m in methods]
        formatted=[f"{v:,.{metric.digits}f}{metric.suffix}" for v in values]
        best=formatted[values.index((max if metric.larger else min)(values))]
        cells=[f"**{v}**" if v==best and len(set(formatted))>1 else v for v in formatted]
        label=metric.title if len(eligible)==len(pairs) else f"{metric.title} ({len(eligible)} paired)"
        rows.append([label+"<br>"+metric.direction,*cells,*[_effect(eligible,metric,m,b) for m,b in comparisons]])
    return markdown_table(rows,["Metric",*[SHORT.get(m,METHODS.get(m,m)) for m in methods],
                                *["vs "+SHORT.get(b,b) for _,b in comparisons]])


def _paired_runs(study,stage,phase,methods):
    """Choose one registered run per method/seed with equal targets, initialization and corpus."""
    ratios=study["context"][stage]["selection"].get("ratios",{})
    strengths={"ce":0.,"trace":ratios.get("trace",.03),"third":ratios.get("third",.03),
               "hessian_norm":.03,"sham":ratios.get("third",.03),"combined":ratios.get("third",.03)}
    budget=HORIZONS[stage] if phase=="confirm" else HORIZONS[stage]//8
    groups={}
    for r in study["runs"]:
        m=r.get("method")
        if (r.get("stage")==stage and r.get("phase")==phase and m in methods and completed(r)
                and r.get("tokens")==budget and r.get("ratio")==strengths[m] and finite(r.get("dev_nll"))):
            groups.setdefault((r["seed"],m),[]).append(r)
    pairs=[]
    for seed in range(1,9) if phase=="confirm" else (0,):
        if any(len(groups.get((seed,m),[]))!=1 for m in methods):
            continue
        pair={m:dict(groups[seed,m][0]) for m in methods}
        provenance=("data_manifest_sha256","dev_tokens")
        if any(not all(r.get(key) for r in pair.values()) or len({r[key] for r in pair.values()})!=1
               for key in provenance):
            continue
        hashes={r.get("initial_trainable_sha256") for r in pair.values()}
        if hashes=={None} and (stage,phase)==("stories","pilot"):
            # Early scratch pilots recorded the seed and first ordinary update before weight digests existed.
            first=[next((e for e in r.get("events",[]) if e.get("step")==1),{}) for r in pair.values()]
            fields=("tokens","loss","accuracy","gradient_norm")
            if any(not all(finite(e.get(k)) for e in first) or len({e[k] for e in first})!=1 for k in fields):
                continue
        elif len(hashes)!=1 or not all(hashes):
            continue
        if methods==PRIMARY:
            timed=_time_match(seed,{(seed,m):r for m,r in pair.items()})
            if timed:
                for m,r in pair.items():
                    r["equal_time_nll"]=timed["by_method"][m]["dev_nll"]
                    r["equal_time_cutoff"]=timed["cutoff_seconds"]
                    r["equal_time_lag"]=timed["by_method"][m]["staleness_seconds"]
        pairs.append(pair)
    return pairs


def _hybrid_pairs(study,baseline):
    """Use the validated comparator-specific seeds and the width change from each arm's switch."""
    runs={(r["seed"],r["method"]):r for r in study["runs"] if r.get("phase")=="hybrid" and completed(r)}
    pairs=[]
    for test in study["hybrid"]["pairs"]:
        if test["comparator"]!=baseline:
            continue
        pair={}
        for m in ("adaptive",baseline):
            r=runs[test["seed"],m]
            start=r["widths"]["2048"]["width"]
            end=r["widths"]["4096"]["width"]
            pair[m]={**r,"width_gain":end-start if finite(start) and finite(end) else None}
        pairs.append(pair)
    return pairs


def _controls(study,stage):
    """Show every available pilot control alongside the selected third-order reference."""
    available=tuple(m for m in ("third","hessian_norm","sham","combined") if _paired_runs(study,stage,"pilot",(m,)))
    if "third" not in available or len(available)<2:
        return f"**{STAGES[stage]}** · Secondary pilot comparisons are pending."
    pairs=_paired_runs(study,stage,"pilot",available)
    if not pairs:
        return f"**{STAGES[stage]}** · Awaiting controls with matched provenance."
    return f"**{STAGES[stage]}** · Pilot seed, {pairs[0]['third']['tokens']:,} training targets.\n\n"+_score_table(
        pairs,available,(NLL,ACCURACY,SPEED,MEMORY))


def _sample_panel(pairs,methods,title):
    """Compare the first recorded prompt of the lowest paired seed, independent of the generated text."""
    first=pairs[0]
    samples=[first[m].get("samples",[]) for m in methods]
    if any(not items for items in samples):
        return ""
    saved=[items[0] for items in samples]
    if (len({s.get("prompt") for s in saved})!=1 or not isinstance(saved[0].get("prompt"),str)
            or any("continuation" not in s for s in saved)):
        return ""
    def literal(text):
        return "<samp>"+escape(str(text)).replace("\n","<br>")+"</samp>"
    headers=[f"[{SHORT[m]}](results/{first[m]['id']}/samples.jsonl)" for m in methods]
    return (f"<details><summary>{title} · same prompt, seed {first[methods[0]]['seed']}</summary>\n\n"
            f"**Prompt** {literal(saved[0]['prompt'])}\n\n"+
            markdown_table([[literal(s["continuation"]) for s in saved]],headers)+"\n\n</details>")


def primary_geometry(study,stage):
    """Choose the furthest common horizon whose three geometry records are actually available."""
    for horizon in ("confirm","pilot"):
        pairs=[p for p in _paired_runs(study,stage,horizon,PRIMARY) if all("flatness" in p[m] for m in PRIMARY)]
        if pairs:
            scope="full-budget checkpoints" if horizon=="confirm" else "development pilots"
            seeds=", ".join(str(p["ce"]["seed"]) for p in pairs)
            return f"{STAGES[stage]} · {scope} · seeds {seeds} · {pairs[0]['ce']['tokens']:,} training targets",primary_flatness_rows(pairs)
    return "",[]


def comparison_sections(study):
    """Return a short opening scorecard and the detailed, regenerable comparisons for the README."""
    top=[]
    samples=[]
    geometry_tables=[]
    detail=["## Side-by-side comparisons","Each row states which direction is better for that metric. "
            "Bold highlights the best observed value at the displayed precision. A tie means the paired difference rounds to zero. "
            "NLL is negative log-likelihood in nats per target. Accuracy differences use percentage points (pp)."]
    for stage,name in STAGES.items():
        caption,geometry_rows=primary_geometry(study,stage)
        if geometry_rows:
            geometry_tables.append(f"**{caption}**\n\n"+markdown_table(geometry_rows,["Flatness statistic","AdamW","Hessian trace","Third order"]))
        pairs=_paired_runs(study,stage,"confirm",PRIMARY)
        confirm=bool(pairs)
        if not confirm:
            pairs=_paired_runs(study,stage,"pilot",PRIMARY)
        detail.append("### "+name)
        if not pairs:
            detail.append("Awaiting matched checkpoints for AdamW, Hessian trace and third order.")
            continue
        outcome=study["stages"][stage]
        final=confirm and len(pairs)==8 and outcome.get("complete",False)
        metric=TEST if final else NLL
        n=len(pairs)
        cohort=(f"{n}/8 full-budget seeds" if confirm else "one development pilot seed")
        evidence="Final test" if final else "Full development split"
        detail.append(f"**{evidence} · {cohort} · {pairs[0]['ce']['tokens']:,} training targets per run.** "
                      "Method columns show medians over the same seeds. The two right columns give the median "
                      "paired change for third order against each baseline. "
                      +("The pilot also selected the derivative strengths. " if not confirm else "")
                      +f"[Strength selection](results/selection/{stage}.json) · [Experiment ledger](reports/experiments/experiments.md)")
        metrics=((TEST,TEST_ACC) if final else ())+ (NLL,ACCURACY,EQUAL_TIME,SPEED,MEMORY)
        detail.append(_score_table(pairs,PRIMARY,metrics,(("third","ce"),("third","trace"))))
        if not pairs[0]["ce"].get("initial_trainable_sha256"):
            detail.append("These early TinyStories pilots share the initialization seed and identical "
                          "first-update token count, loss, accuracy and gradient norm. Initial weight digests "
                          "were first recorded in later runs. [First-update records](reports/experiments/experiments.md)")
        samples.append(_sample_panel(pairs,PRIMARY,name))
        timed=[p for p in pairs if "equal_time_cutoff" in p["ce"]]
        if timed:
            cutoff=median(p["ce"]["equal_time_cutoff"] for p in timed)
            lag=max(p[m]["equal_time_lag"] for p in timed for m in PRIMARY)
            detail.append(f"The common training-time cutoff had a median of {cutoff:.1f} seconds. "
                          f"The furthest checkpoint used for this row was {lag:.1f} seconds before its cutoff.")
        else:
            detail.append("An equal-time NLL comparison is pending because at least one arm lacks a recorded "
                          "development checkpoint at or before the shared cutoff.")
        if stage=="abstracts" and all(finite(p[m].get("process_peak_rss_mib")) for p in pairs for m in PRIMARY):
            highwater=", ".join(f"{SHORT[m]} {median(p[m]['process_peak_rss_mib'] for p in pairs)/1024:.2f} GiB" for m in PRIMARY)
            detail.append("Peak host memory (lower uses less RAM) was "+highwater+
                          ". This measure includes earlier work in each interpreter.")
        detail.append(verdict_text(outcome))
        if final:
            rows=[]
            for m,stats in outcome["comparisons"].items():
                lo,hi=stats["median_ci"]
                rows.append([SHORT[m],f"{stats['median_delta']:+.6f}",f"[{lo:+.6f}, {hi:+.6f}]",
                             f"{stats['wins']}/{stats['ties']}/{stats['losses']}",f"{stats['p_holm']:.5f}"])
            detail.append(markdown_table(rows,["Against","Paired Δtest NLL","Median interval","Wins/ties/losses","Holm p"]))
            detail.append("A negative difference favors third order. A positive difference favors the named baseline. "
                          "The interval shows uncertainty in the median difference. A smaller Holm-adjusted p-value "
                          "gives stronger evidence for the registered improvement. [Test decision rule](reports/preregistration.md)")
        top.append([name+" · "+("test" if final else "dev"),cohort,_effect(pairs,metric,"third","ce"),
                    _effect(pairs,metric,"third","trace"),_effect(pairs,SPEED,"third","ce")])
    quick=["## Results at a glance","**Lower next-token loss (NLL) is better** because the model assigns more probability "
           "to the tokens that actually came next. **Higher top-1 accuracy is better** because the model’s first guess is correct "
           "more often. Higher speed means more training targets per second. Lower peak memory uses fewer resources."]
    if top:
        quick.append(markdown_table(top,["Model and split","Matched evidence","Third-order NLL vs AdamW<br>"+NLL.direction,
                                        "Third-order NLL vs trace<br>"+NLL.direction,"Speed vs AdamW<br>"+SPEED.direction]))
    detail.append("The equal-time row uses the last available fixed-window development score at or before "
                  "the fastest run’s finish time in each seed. Full-split NLL uses every development target. "
                  "Training speed includes regularizer probes. Adapter derivatives use CPU float64 with one GPU reserved. "
                  "[Timing definitions and checkpoint lags](reports/summary.md)")
    detail.extend(["### Flatness of the trained checkpoints",
                   "How far can the weights move before next-token loss rises by 0.1 nats on eight fixed training windows? "
                   "We add the crossing distances on both sides of each of 16 unit directions, then take their median. "
                   "**Wider is flatter** in these coordinates. Establishing a local minimum would also require a stationarity test. "
                   "[Flat-minima paper](https://people.idsia.ch/~juergen/fm/node1.html) · "
                   "[Coordinate dependence](https://proceedings.mlr.press/v70/dinh17b/dinh17b.pdf#page=2)",
                   "**TinyStories hybrids** · Each row names the completed seeds. Switch and final widths are medians over those seeds. "
                   "The final seed range shows the smallest and largest seed widths. The middle 50% column gives the medians of "
                   "the within-seed directional quartiles. Spread has no preferred direction. A ray at the search limit supplies a lower bound.",
                   hybrid_flatness_table(study["runs"])])
    detail.extend(["#### All variants and baselines",
                   "Each row uses the same fixed training windows and probe directions within its stage. "
                   "Parentheses give measured / planned seeds for that cell. Targets count next-token examples used for optimizer updates in this study. "
                   "The unigram uses counts from the full training split, and initial Pythia retains its pretrained backbone. "
                   "Compare rows with matching targets and seeds. "
                   "Larger **weight width** means greater tolerance to moving the model’s trainable parameters. "
                   "Larger **common score width** means that all token scores can tolerate a larger shared bias before NLL rises "
                   "by 0.1 nats, measured in RMS logit units. The unigram has zero trainable model weights and shares the score test "
                   "with every neural predictor. Both widths have an unknown relationship to better held-out prediction. "
                   "[All-model measurement design](reports/amendments/all-model-flatness.md)",*all_arm_tables(study)])
    if geometry_tables:
        detail.extend(geometry_tables)
    else:
        detail.append("Matched finite-width and Hessian measurements for the primary AdamW, trace and third-order checkpoints are pending.")
    detail.append("For the primary comparison, TinyStories uses all weights and Pythia uses the LoRA factors. "
                  "Compare widths within each model. The link gives every run, directional bracket and Hessian probe. "
                  "[Flatness statistics and raw files](reports/flatness.md) · [Secondary measurement design](reports/amendments/checkpoint-flatness.md)")
    fixed=_hybrid_pairs(study,"late")
    detail.append("### TinyStories hybrid schedules")
    if fixed:
        n=len(fixed)
        width_change=_effect(fixed,WIDTH,"adaptive","late")
        if width_change=="—":
            geometry="Its paired width difference is unidentifiable within the measured radii."
        elif width_change=="Tie":
            geometry="The two schedules retained equal width at the displayed precision."
        else:
            geometry=f"It retained {width_change.removesuffix(' retained')} directional width after the switch."
        finals=[[pair[m]["widths"]["4096"]["width"] for pair in fixed] for m in ("adaptive","late")]
        if all(finite(w) for group in finals for w in group):
            geometry+=f" Median final widths were {median(finals[0]):.3f} (adaptive) and {median(finals[1]):.3f} (fixed)."
        loss_change=_effect(fixed,NLL,"adaptive","late")
        prediction=("The two schedules had equal development NLL at the displayed precision." if loss_change=="Tie"
                    else f"Adaptive development NLL was {loss_change}.")
        quick.append(f"**Adaptive vs fixed-ramp hybrid** · {n}/8 paired seeds. {prediction} {geometry} "
                     "More width is better for the registered geometry test. Whether more width improves prediction is unknown.")
        detail.append(f"**Adaptive vs fixed ramp · {n}/8 paired seeds · {fixed[0]['adaptive']['tokens']:,} targets per run.** "
                      "Both arms resume the same trace-trained checkpoint. Width change is final width minus width at "
                      "the switch. A larger change means more width retained at the fixed loss tolerance. "
                      "For two negative changes, the one closer to zero lost less width.")
        detail.append(_score_table(fixed,("adaptive","late"),(NLL,ACCURACY,WIDTH,SPEED,MEMORY),(("adaptive","late"),)))
        samples.append(_sample_panel(fixed,("adaptive","late"),"TinyStories hybrid schedules"))
    else:
        detail.append("The adaptive and fixed-ramp comparison is awaiting its first matched pair.")
    rows=[]
    for m in ("replay","trace","strong","always"):
        pairs=_hybrid_pairs(study,m)
        rows.append([METHODS[m],f"{len(pairs)}/8",
                     *([_effect(pairs,k,"adaptive",m) for k in (NLL,WIDTH,SPEED)] if pairs else ["Pending","—","—"])])
    detail.append("The remaining controls are paired independently. Each row uses only seeds that finished both arms. "
                  "The always-on arm has its own measured width at the switch.")
    detail.append(markdown_table(rows,["Adaptive versus","Paired seeds","Adaptive NLL<br>"+NLL.direction,
                                      "Adaptive width change<br>"+WIDTH.direction,"Adaptive speed<br>"+SPEED.direction]))
    detail.append(f"**Registered width decision** · {study['hybrid']['status'].capitalize()}. Width probes use fixed training windows. "
                  "[Every width, training-fit flag, replay and paired difference](reports/hybrid/results.md)")
    detail.append("**Training diagnostics have no established better direction for held-out prediction.** "
                  "A smaller derivative penalty meets its training objective more closely. The raw Hessian trace, "
                  "third-derivative estimate, gradient norm and penalty strength describe the training process. "
                  "Their predictive value is assessed separately by held-out NLL. [Objectives and endpoints](reports/preregistration.md)")
    controls=[_controls(study,stage) for stage in STAGES]
    zero=[]
    for stage,name in STAGES.items():
        runs={r["method"]:r for r in study["runs"] if r.get("stage")==stage and r.get("phase")=="control"
              and r.get("tokens")==0 and completed(r) and finite(r.get("dev_nll"))}
        if {"initial","unigram"}<=runs.keys():
            zero.append([name,*[f"{runs[m]['dev_nll']:.6f}" for m in ("initial","unigram")],
                         *[f"{100*runs[m]['dev_accuracy']:.3f}%" for m in ("initial","unigram")]])
    if zero:
        controls+=["**Zero-update references** · The unigram uses training-split frequencies. Initial Pythia uses its pretrained weights.",
                   markdown_table(zero,["Stage","Initial NLL<br>"+NLL.direction,"Unigram NLL<br>"+NLL.direction,
                                        "Initial accuracy<br>"+ACCURACY.direction,"Unigram accuracy<br>"+ACCURACY.direction])]
    detail.append("<details><summary>Squared-Hessian, scrambled-gradient, combined and untrained controls</summary>\n\n"
                  +"\n\n".join(controls)+"\n\n</details>")
    if any(samples):
        detail.extend(["### Same-prompt continuations","Each panel shows the first saved prompt and full continuations "
                       "from the lowest matched seed. These examples have no quality rating. The method names link to the raw generations.",
                       *(panel for panel in samples if panel)])
    quick.append("[Side-by-side scores, accuracy, speed and memory](#side-by-side-comparisons) · "
                 "[Flatness statistics](#flatness-of-the-trained-checkpoints) · "
                 "[Live explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · "
                 "[Paired tests and intervals](reports/summary.md)")
    if not any(o.get("complete") for o in study["stages"].values()):
        quick.insert(-1,"Both primary test decisions are pending. Each stage requires eight paired test seeds "
                     "and superiority over both baselines under Holm correction.")
    else:
        quick.insert(-1," ".join(f"**{name}** · {verdict_text(study['stages'][stage])}"
                                 for stage,name in STAGES.items()))
    return "\n\n".join(quick),"\n\n".join(detail)
