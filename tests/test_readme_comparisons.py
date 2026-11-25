"""Keep visual rankings tied to the same seeds, horizon, selection and evaluation split."""

from math import exp

from thirdloss.readme_comparisons import comparison_sections
from thirdloss.report_records import study_snapshot


def pilot(method,loss,rate,ratio,stage="stories"):
    return {"id":method+str(ratio),"stage":stage,"phase":"pilot","method":method,"seed":0,
            "ratio":ratio,"tokens":2**21 if stage=="stories" else 2**16,"status":"complete",
            "dev_nll":loss,"dev_perplexity":exp(loss),"dev_accuracy":.4,"tokens_per_sec":rate,"peak_vram_mb":600.,
            "initial_trainable_sha256":"same","data_manifest_sha256":"same","dev_tokens":256,"events":[]}


def test_pilot_comparison_excludes_unselected_runs_and_unsealed_scores(tmp_path):
    study=study_snapshot(tmp_path)
    study["context"]["stories"]["selection"]={"ratios":{"third":.01,"trace":.01}}
    rows=[pilot("ce",3.,100,0.),pilot("trace",2.5,80,.01),pilot("third",2.75,50,.01),
          pilot("third",.123456,5000,.1)]
    rows[2]["test_nll"]=98.765432
    study["runs"]=rows
    top,detail=comparison_sections(study)
    assert "0.250000 lower" in top and "0.250000 higher" in top and "50.0% slower" in top
    assert "**2.500000**" in detail and "50.0% slower" in detail
    assert "0.123456" not in detail and "98.765432" not in detail
    assert "| Dev top-1 accuracy<br>↑ Higher is better | 40.000% | 40.000% | 40.000%" in detail
    assert "Third-order NLL vs AdamW<br>↓ Lower is better" in top
    assert "Speed vs AdamW<br>↑ Higher is better" in top
    assert "Peak GPU allocation (MiB)<br>↓ Lower is better" in detail
    assert "| Development perplexity<br>↓ Lower is better | 20.0855 | **12.1825** | 15.6426 |" in detail
    assert "Final test perplexity<br>" not in detail
    rows[1]["tokens"]-=1
    _,detail=comparison_sections(study)
    assert "**2.500000**" not in detail


def test_hybrid_effects_use_each_comparators_own_pairs_and_width_gains(tmp_path):
    study=study_snapshot(tmp_path)
    for seed,method,nll,warm,final in ((21,"adaptive",2.,8.,7.),(21,"late",3.,8.,7.5),
                                     (21,"always",4.,11.,8.),(22,"adaptive",.123456,9.,8.)):
        r=pilot(method,nll,100,.01)
        r.update(id=f"{seed}-{method}",phase="hybrid",seed=seed,tokens=2**24,finished_at="today",
                 widths={"2048":{"width":warm},"4096":{"width":final}})
        study["runs"].append(r)
    study["hybrid"]["pairs"]=[{"seed":21,"comparator":"late","delta":-.5,"dev_nll_delta":-1.,"comparable_fit":True},
                              {"seed":21,"comparator":"always","delta":2.,"dev_nll_delta":-2.,"comparable_fit":True}]
    top,detail=comparison_sections(study)
    assert "0.5000 less directional width" in top and "1.000000 lower" in top
    assert "2.0000 more retained" in detail and "0.123456" not in detail
    assert "Cross-seed replay" in detail and "Pending" in detail
    assert "Width change after switch<br>↑ More retained is better for the width test" in detail
    assert "Whether more width improves prediction is unknown" in top
    assert "no established better direction for held-out prediction" in detail


def test_final_scorecard_uses_all_eight_seeds_and_shows_holm_and_median_interval(tmp_path):
    from thirdloss.analysis import analyze_stage
    study=study_snapshot(tmp_path)
    study["context"]["stories"]["selection"]={"ratios":{"third":.01,"trace":.01}}
    for seed in range(1,9):
        for i,m in enumerate(("ce","trace","third")):
            row=pilot(m,3.-i/10,100-i*15,.01 if i else 0.)
            row.update(id=f"{seed}-{m}",phase="confirm",seed=seed,tokens=2**24,test_nll=4.-i/10,
                       test_accuracy=.5+i/100,test_perplexity=exp(4.-i/10),freeze_id="frozen",test_manifest_sha256="split",test_tokens=128)
            study["runs"].append(row)
    study["stages"]["stories"]=analyze_stage(study["runs"],"stories")
    top,detail=comparison_sections(study)
    assert "TinyStories pretraining · test" in top and "8/8 full-budget seeds" in top
    assert "| Final test NLL<br>↓ Lower is better | 4.000000 | 3.900000 | **3.800000** |" in detail
    assert "| Final test perplexity<br>↓ Lower is better | 54.5982 | 49.4024 | **44.7012** |" in detail
    assert "Median interval" in detail and "Holm p" in detail and "0.00781" in detail
    assert "A negative difference favors third order" in detail


def test_output_panel_requires_identical_prompts_and_escapes_generated_markup(tmp_path):
    study=study_snapshot(tmp_path)
    study["runs"]=[pilot(m,3.,100,0. if m=="ce" else .03) for m in ("ce","trace","third")]
    for r in study["runs"]:
        r["samples"]=[{"prompt":"A small bird","continuation":"<bird> | sang"}]
    _,detail=comparison_sections(study)
    assert "same prompt, seed 0" in detail and "&lt;bird&gt; \\| sang" in detail
    study["runs"][1]["samples"][0]["prompt"]="A different bird"
    assert "same prompt, seed 0" not in comparison_sections(study)[1]


def test_legacy_stories_pilots_require_matching_first_update_when_initial_hash_is_absent(tmp_path):
    study=study_snapshot(tmp_path)
    for method in ("ce","trace","third"):
        row=pilot(method,3.,100,0. if method=="ce" else .03)
        del row["initial_trainable_sha256"]
        row["events"]=[{"step":1,"tokens":4096,"loss":8.35,"accuracy":.003,"gradient_norm":1.88}]
        study["runs"].append(row)
    top,detail=comparison_sections(study)
    assert "TinyStories pretraining · dev" in top and "first-update" in detail
    study["runs"][1]["events"][0]["gradient_norm"]+=.01
    assert "TinyStories pretraining · dev" not in comparison_sections(study)[0]
