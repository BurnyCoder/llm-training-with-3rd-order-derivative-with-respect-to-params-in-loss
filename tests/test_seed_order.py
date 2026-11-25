"""Verify the research queue and the numerical summary of sensitivity to the paired training seed."""

import pytest


def test_full_study_finishes_single_seed_work_before_replications_and_analyzes_seeds_last(tmp_path,monkeypatch):
    from thirdloss import checkpoint_flatness,hybrid,study
    from thirdloss import seed_sensitivity
    from thirdloss.records import write_json
    events=[]
    write_json(tmp_path/"results/verification/pythia-scoring-batches.json",{})
    monkeypatch.setattr(study,"prepare_stage",lambda *a:None)
    monkeypatch.setattr(study,"feasibility",lambda *a:None)
    monkeypatch.setattr(study,"select",lambda *a:{"trace":.01,"third":.01})
    def run(project,storage,stage,method,phase,seed,*unused):
        events.append((phase,stage,method,seed))
        return {"id":events[-1]}
    monkeypatch.setattr(study,"run_one",run)
    monkeypatch.setattr(study,"milestone",lambda *a:None)
    monkeypatch.setattr(study,"freeze",lambda p,s,stage:{"runs":[stage]})
    monkeypatch.setattr(study,"evaluate_one",lambda p,s,run,d:events.append(("test",run)) or {})
    monkeypatch.setattr(hybrid,"run_hybrids",lambda *a,cohort,**kw:events.append(("hybrid",cohort)))
    monkeypatch.setattr(checkpoint_flatness,"flatness_study",lambda p,s,st,phase,*a:events.append(("geometry",phase)))
    monkeypatch.setattr(seed_sensitivity,"finish_seed_sensitivity",lambda *a:events.append(("seed-sensitivity",)))
    study.run_study(tmp_path,tmp_path,["stories","abstracts"],"cpu",False,with_hybrid=True,with_flatness=True)
    single=[i for i,e in enumerate(events) if e[0] in {"pilot","control"}
            or e==("hybrid","example") or (e[0]=="confirm" and e[3]==1)]
    repeats=[i for i,e in enumerate(events) if e[0]=="confirm" and e[3]>1]
    assert max(single)<min(repeats)
    assert sum(e[0]=="confirm" for e in events)==48
    assert events.index(("test","abstracts"))<events.index(("hybrid","replications"))
    assert events[-2:]==[("geometry","all"),("seed-sensitivity",)]


def test_seed_sensitivity_is_unavailable_for_an_incomplete_study(tmp_path):
    from thirdloss.seed_sensitivity import seal_inputs
    from thirdloss.report_records import study_snapshot
    with pytest.raises(ValueError,match="final stage"):
        seal_inputs(tmp_path,study_snapshot(tmp_path))
    assert not (tmp_path/"results/freeze/seed-sensitivity.json").exists()


def test_leave_one_seed_out_uses_each_seed_once_and_keeps_censoring():
    from thirdloss.seed_sensitivity import sensitivity
    values=[-4.,-3.,-2.,-1.,1.,2.,3.,4.]
    result=sensitivity(values)
    assert result["median"]==0 and result["min"]==-4 and result["max"]==4
    assert result["leave_one_out_medians"]==[1.]*4+[-1.]*4
    assert result["sample_sd"]==pytest.approx((60/7)**.5)
    assert sensitivity([None]+values[1:])=={"n":8,"finite":7}


def test_final_report_requires_a_seal_and_rejects_changed_inputs(tmp_path):
    from thirdloss.records import HORIZONS,write_json
    from thirdloss.seed_sensitivity import _planned_ids,render_seed_sensitivity,seal_inputs
    root=tmp_path/"results"
    study={"context":{s:{"selection":{"ratios":{"trace":.01,"third":.03}}} for s in HORIZONS},
           "stages":{},"runs":[],"hybrid":{"pairs":[]}}
    for stage in HORIZONS:
        pairs=[{"seed":i,"delta":i/100} for i in range(1,9)]
        study["stages"][stage]={"complete":True,"comparisons":{m:{"pairs":pairs} for m in ("ce","trace")}}
    for seed in range(21,29):
        study["hybrid"]["pairs"].extend({"seed":seed,"comparator":m,"delta":-.02,"dev_nll_delta":.001}
                                        for m in ("late","replay"))
    weights={s:{} for s in HORIZONS}
    for run in sorted(_planned_ids(study)):
        stage,phase,seed,method,*_=run.split("-")
        seed=int(seed[1:])
        summary={"id":run,"stage":stage,"phase":phase,"seed":seed,"method":method,"status":"complete",
                 "tokens":HORIZONS[stage],"dev_nll":2+seed/1000}
        folder=root/run
        if phase=="confirm":
            summary.update(test_nll=2+seed/1000,weights_sha256=run,freeze_id=stage,test_manifest_sha256=stage)
            weights[stage][run]=run
        write_json(folder/"summary.json",summary)
        row={**summary,"score_flatness":{"width":1.}}
        write_json(folder/"score-flatness.json",row["score_flatness"])
        if method!="unigram":
            row["flatness"]={"width":3.}
            write_json(folder/"flatness.json",row["flatness"])
        if phase in ("branch","hybrid"):
            row["widths"]={}
            for step in ((2048,) if phase=="branch" else (2048,3072,4096)):
                row["widths"][str(step)]={"width":3.}
                write_json(folder/f"width-{step}.json",row["widths"][str(step)])
        study["runs"].append(row)
    for stage in HORIZONS:
        write_json(root/"freeze"/f"{stage}.json",{"runs":weights[stage],"freeze_id":stage,"test_sha256":stage})
    assert render_seed_sensitivity(tmp_path,study) is None
    assert not (root/"analysis/seed-sensitivity.json").exists()
    seal_inputs(tmp_path,study)
    result=render_seed_sensitivity(tmp_path,study)
    assert len(result["rows"])==32 and all(r["n"]==8 for r in result["rows"])
    assert "Leave-one-out median range" in (tmp_path/"reports/seed-sensitivity.md").read_text(encoding="utf-8")
    write_json(root/"stories-confirm-s01-ce-r00"/"score-flatness.json",{"width":9.})
    with pytest.raises(ValueError,match="inputs changed"):
        render_seed_sensitivity(tmp_path,study)
