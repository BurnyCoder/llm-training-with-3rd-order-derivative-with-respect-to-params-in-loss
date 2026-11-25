"""Verify geometry statistics, censoring and a Hessian known exactly in the chosen coordinates."""

import math

import pytest
import torch


def test_curvature_keeps_trace_signs_and_counts_negative_eigenvalues_in_rms():
    from thirdloss.checkpoint_flatness import hessian_statistics
    p=torch.tensor([1.,2.,3.],dtype=torch.float64,requires_grad=True)
    diagonal=torch.tensor([-2.,0.,5.],dtype=torch.float64)
    result=hessian_statistics((diagonal*p.square()).sum()/2,(p,))
    assert result["trace_per_parameter"]==pytest.approx(1.)
    assert result["rms_curvature"]==pytest.approx(math.sqrt(29/3))
    assert len(result["draws"])==8 and result["dimensions"]==3


def test_direction_quantiles_propagate_open_bounds_without_dropping_rays():
    from thirdloss.flatness_stats import direction_summary,quantile_bounds
    def direction(i,upper):
        return {"direction":i,"negative":{"lower":0.,"upper":0.},"positive":{"lower":float(i),"upper":upper}}
    data=direction_summary({"directions":[direction(1,1.),direction(2,2.),direction(3,3.),direction(4,None)]})
    assert data["ray_count"]==8 and data["direction_q1"]==pytest.approx([1.75,1.75])
    assert data["direction_q3"]==[3.25,None]
    assert quantile_bounds([[2.,None]],.5)==[2.,None]


def test_flatness_table_preserves_seed_count_and_geometry_units():
    from thirdloss.flatness_tables import hybrid_flatness_table
    rows=[]
    for seed,method,initial,end in ((21,"adaptive",10.,8.),(22,"adaptive",11.,9.),(21,"late",10.,7.)):
        point={"width":end,"width_lower":end,"width_upper":end,"direction_q1":[5.,5.],
               "direction_q3":[9.,9.],"ray_count":32,"censored_rays":0,"baseline_nll":2.}
        rows.append({"stage":"stories","phase":"hybrid","method":method,"seed":seed,"status":"complete",
                     "tokens":2**24,"widths":{"2048":{**point,"width":initial,"width_lower":initial,"width_upper":initial},
                                              "4096":point}})
    table=hybrid_flatness_table(rows)
    assert "21, 22" in table and "8.500" in table and "8.000–9.000" in table and "0/64" in table
    assert "5.000–9.000" in table and "21 |" in table


def test_primary_flatness_summary_compares_only_common_probe_provenance():
    from thirdloss.flatness_tables import primary_flatness_rows
    r={"protocol":"v1","probe_windows_sha256":"same","width_device":"cuda","hessian_device":"cpu",
       "width":7.,"width_lower":6.99,"width_upper":7.01,"ray_count":32,"censored_rays":0,
       "baseline_nll":2.,"rms_curvature":.1,"trace_per_parameter":-.01}
    pairs=[{m:{"flatness":dict(r)} for m in ("ce","trace","third")} for _ in range(2)]
    stats=primary_flatness_rows(pairs)
    assert stats[0][1:]==["7.000"]*3 and stats[3][1:]==["0/64"]*3
    for arm in pairs[1].values():
        arm["flatness"]["probe_windows_sha256"]="different"
    with pytest.raises(ValueError,match="same probes"):
        primary_flatness_rows(pairs)


def test_geometry_forecast_counts_the_unigram_and_preserves_observed_publication_time(tmp_path):
    from thirdloss.flatness_progress import geometry_progress,published_pilot_timings
    from thirdloss.records import write_json
    logs=tmp_path/"logs"
    logs.mkdir()
    (logs/"checkpoint-flatness-fixtureZ.log").write_text(
        "2026-01-01T10:00:00+00:00 Measuring checkpoint flatness for run-a\n"
        "2026-01-01T10:00:05+00:00 run-a width=1.5 RMS curvature=2\n"
        "2026-01-01T10:00:20+00:00 Measuring checkpoint flatness for run-b\n"
        "2026-01-01T10:01:20+00:00 run-b width=3 RMS curvature=1\n"
        "2026-01-01T10:02:00+00:00 Completed pilot flatness measurements; releasing the training interval\n")
    for run,stage in (("run-a","stories"),("run-b","abstracts")):
        write_json(tmp_path/"results"/run/"summary.json",{"stage":stage})
    data=published_pilot_timings(tmp_path)
    assert [r["cycle_seconds"] for r in data["rows"]]==[20,100]
    assert [r["measurement_seconds"] for r in data["rows"]]==[5,60]
    report="\n".join(geometry_progress(tmp_path,{"runs":[{"stage":"stories","phase":"control","method":"unigram","score_flatness":{}}]}))
    assert "0/91 | 1/92" in report and "0/35 | 0/36" in report
    assert f"{(91*20+36*100)/3600:.2f} additional hours" in report


def test_all_model_table_rejects_mismatched_weight_probes_in_secondary_arms(tmp_path):
    from thirdloss.flatness_tables import all_arm_tables
    from thirdloss.report_records import study_snapshot
    study=study_snapshot(tmp_path)
    sample={"stage":"stories","phase":"pilot","seed":0,"tokens":2**21,"ratio":.01,"status":"complete"}
    probed={"protocol":"native","probe_windows_sha256":"same","width_device":"cuda",
            "hessian_device":"cuda:0","dimensions":100,"rms_curvature":.4}
    study["runs"]=[{**sample,"method":"sham","flatness":probed},
                   {**sample,"method":"combined","flatness":{**probed,"width_device":"cpu"}}]
    with pytest.raises(ValueError,match="weight-space"):
        all_arm_tables(study)


def test_hybrid_width_reuse_distinguishes_cpu_and_cuda_random_direction_streams(tmp_path,monkeypatch):
    from thirdloss import checkpoint_flatness as geometry
    from thirdloss.records import write_json
    model=torch.nn.Linear(2,3).double()
    inputs=torch.zeros(2,2,2,dtype=torch.float64)
    targets=torch.zeros(2,2,dtype=torch.long)
    row={"phase":"hybrid","steps":1,"stage":"stories","device":"cpu"}
    prior={"weights_sha256":geometry.trainable_digest(model),"weights_restored":True,"width":7.}
    write_json(tmp_path/"width-1.json",prior)
    monkeypatch.setattr(geometry,"measure_width",lambda model,loss:{"width":11.})
    assert geometry._native_geometry(model,row,tmp_path,inputs,targets)["width"]["width"]==7.
    row["device"]="cuda"
    assert geometry._native_geometry(model,row,tmp_path,inputs,targets)["width"]["width"]==11.


def test_common_logit_probe_matches_direct_softmax_and_its_second_derivative():
    from thirdloss.score_flatness import bias_response
    logits=torch.tensor([[.1,.2,-.3,1.],[-1.,2.,.7,-.3]],dtype=torch.float64)
    target=torch.tensor([1,0])
    signs=torch.tensor([1.,-1.,-1.,1.],dtype=torch.float64)
    plus=logits.softmax(-1)[:,signs>0].sum(-1).numpy()
    loss=torch.nn.functional.cross_entropy(logits,target)
    delta,curvature=bias_response(plus,float(signs[target].mean()))
    for r in (-1.,.5):
        assert delta(r)==pytest.approx(float(torch.nn.functional.cross_entropy(logits+r*signs,target)-loss))
    radius=torch.tensor(0.,dtype=torch.float64,requires_grad=True)
    derivative=torch.autograd.grad(torch.nn.functional.cross_entropy(logits+radius*signs,target),radius,create_graph=True)[0]
    assert curvature==pytest.approx(float(torch.autograd.grad(derivative,radius)[0]))


def test_unigram_uses_identical_score_coordinates_to_a_constant_neural_predictor():
    from thirdloss.score_flatness import score_width
    logits=torch.tensor([[0.,.25,.5,-.5]],dtype=torch.float64)
    targets=torch.tensor([3,1,3,2,1])
    table=score_width(logits,targets)
    network=score_width(logits.expand(targets.numel(),-1)+13,targets)
    assert table["width"]==network["width"] and table["direction_sha256"]==network["direction_sha256"]
    assert table["mean_directional_curvature"]==pytest.approx(network["mean_directional_curvature"])


def test_all_arm_table_keeps_weightless_reference_and_every_control(tmp_path):
    from thirdloss.flatness_tables import all_arm_tables
    from thirdloss.report_records import study_snapshot
    study=study_snapshot(tmp_path)
    for stage in study["context"].values():
        stage["selection"]={"ratios":{"trace":.01,"third":.03}}
    point={"width":.9,"width_lower":.8999,"width_upper":.9001,"direction_sha256":"same","protocol":"scores",
           "probe_windows_sha256":"same","vocab":4096}
    study["runs"]=[{"stage":"stories","phase":"control","method":"unigram","status":"complete",
                    "ratio":0.,"seed":0,"tokens":0,"score_flatness":point}]
    text="\n".join(all_arm_tables(study))
    assert "| Unigram | 0 | 0 | N/A · no weights | N/A · no weights | 0.9000 (1/1) |" in text
    assert all(name in text for name in ("Squared Hessian norm","Randomized gradient signs","Trace + third derivative",
                                         "Cross-seed replay","Shared trace checkpoint","Always-on hybrid"))
    assert "Hessian trace (10%)" in text and "Third derivative (1%)" in text


def test_score_card_keeps_small_width_differences_and_outward_bisection_bounds():
    from thirdloss.flatness_tables import checkpoint_table
    score={"width":1.0928345,"width_lower":1.0927429,"width_upper":1.0929261}
    text=checkpoint_table("third",None,score)
    assert "1.0928" in text and "[1.09274, 1.09293]" in text
    censored=checkpoint_table("unigram",None,{"width":None,"width_lower":128.125687,"width_upper":None})
    assert "≥128.12568" in censored


def test_geometry_milestone_retries_missing_receipt_and_skips_a_verified_unigram(tmp_path,monkeypatch):
    from thirdloss import checkpoint_flatness as geometry
    from thirdloss.records import sha256,write_json
    row={"id":"control","stage":"stories","method":"unigram"}
    score=tmp_path/"results/control/score-flatness.json"
    write_json(score,{"example":True})
    calls=[]
    monkeypatch.setattr(geometry.subprocess,"run",lambda cmd,**kw:calls.append(cmd))
    geometry.geometry_milestone(tmp_path,tmp_path,row,"cpu",True)
    assert len(calls)==1 and "--publish" in calls[0] and "control" in calls[0]
    write_json(tmp_path/"releases/flatness-control.json",{"artifacts":{score.name:sha256(score)}})
    geometry.geometry_milestone(tmp_path,tmp_path,row,"cpu",True)
    assert len(calls)==1
