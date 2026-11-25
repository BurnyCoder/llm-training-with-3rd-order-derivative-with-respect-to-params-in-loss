"""Verify the registered schedules, branch pairing and geometric measurement on exact losses."""

import math
import pytest
import torch

from thirdloss.hybrid import HybridSchedule, donor_seed
from thirdloss.width import crossing, measure_width


def test_lagged_rms_latch_and_replay_survive_checkpoint():
    adaptive = HybridSchedule("adaptive", alpha=0.1, cap=0.3)
    for _ in range(8):
        adaptive.observe(4.0, 3.8)
    adaptive.fix_reference()
    assert adaptive.coefficients(2048) == {"trace": 0.1, "third": 0.0}
    for _ in range(8):
        adaptive.observe(1.0, 3.8)
    assert adaptive.coefficients(2064)["third"] == pytest.approx(0.15)
    restored = HybridSchedule("adaptive", alpha=0.1, cap=0.3)
    restored.load(adaptive.state())
    for _ in range(8):
        restored.observe(16., 5.)
    assert restored.coefficients(2080)["third"] == pytest.approx(0.15)
    replay = HybridSchedule("replay", alpha=0.1, cap=0.3, replay=restored.changes)
    assert replay.coefficients(2063)["third"] == 0
    assert replay.coefficients(2064)["third"] == pytest.approx(0.15)
    assert donor_seed(21) == 28 and donor_seed(22) == 21


def test_fixed_and_stronger_trace_apply_only_after_switch():
    fixed = HybridSchedule("late", alpha=2., cap=6.)
    strong = HybridSchedule("strong", alpha=2., cap=6., delta=4.)
    assert [fixed.coefficients(t)["third"] for t in (0,2048,2560,3072,4095)] == [0,0,3,6,6]
    assert strong.coefficients(2560) == {"trace":4., "third":0.}
    adaptive = HybridSchedule("adaptive",alpha=2.,cap=6.)
    for _ in range(8):
        adaptive.observe(4.,4.5)
    adaptive.fix_reference()
    for _ in range(8):
        adaptive.observe(1.,4.5)
    assert adaptive.coefficients(3072)["third"] == 0.


def test_width_exact_crossing_censor_and_bitwise_restoration():
    model = torch.nn.Linear(2,1,bias=False,dtype=torch.float64)
    original = model.weight.detach().clone()
    model.weight.grad = torch.ones_like(original)
    rng = torch.get_rng_state().clone()
    stats = measure_width(model, lambda: (model.weight-original).square().sum(), directions=3)
    assert stats["width"] == pytest.approx(2*math.sqrt(.1),abs=1e-4)
    assert stats["weights_restored"] and model.training and torch.equal(model.weight,original)
    assert torch.equal(model.weight.grad, torch.ones_like(original))
    assert torch.equal(torch.get_rng_state(),rng)
    assert crossing(lambda radius: 0.,.1) == {"lower":128.,"upper":None}
    unbounded = measure_width(model,lambda: model.weight.sum()*0.,directions=2)
    assert unbounded["width"] is None and unbounded["width_lower"] == 256.


def test_branch_restores_adam_moments_rng_cursor_and_monitor(tmp_path):
    from types import SimpleNamespace
    from thirdloss.records import sha256
    from thirdloss.train import restore_state, save_state
    model = torch.nn.Linear(2,1)
    optim = torch.optim.AdamW(model.parameters(),lr=.01)
    x = torch.tensor([[2.,-3.]])
    model(x).square().sum().backward()
    optim.step()
    parent = tmp_path/"parent.pt"
    cfg = dict(id="trunk",seed=21,stage="stories",data_manifest_sha256="data",context=128,batch_windows=32,
               microbatch=32,alpha=1.,cap=2.,schedule_steps=4096,protocol="hybrid-v1")
    schedule = HybridSchedule("trunk",1.,2.)
    for _ in range(8):
        schedule.observe(1.,3.2)
    schedule.fix_reference()
    save_state(parent,model,optim,2048,123.,cfg,SimpleNamespace(schedule=schedule))
    control = torch.rand(3)
    child = torch.nn.Linear(2,1)
    child_opt = torch.optim.AdamW(child.parameters(),lr=.001)
    child_protocol = SimpleNamespace(parent=parent,schedule=HybridSchedule("adaptive",1.,2.))
    child_cfg = {**cfg,"id":"adaptive","parent":"trunk","parent_restart_sha256":sha256(parent)}
    assert restore_state(parent,child,child_opt,child_cfg,SimpleNamespace(directory=tmp_path),
                         torch.device("cpu"),child_protocol)==(2048,123.)
    assert torch.equal(torch.rand(3),control) and child_protocol.schedule.reference==1.
    for net,optimizer in ((model,optim),(child,child_opt)):
        optimizer.zero_grad()
        net(x).square().sum().backward()
        optimizer.step()
    assert all(torch.equal(a,b) for a,b in zip(model.parameters(),child.parameters()))


def test_width_inference_requires_eight_pairs_and_keeps_censoring():
    from thirdloss.hybrid_results import hybrid_results
    records=[]
    for seed in range(21,29):
        for arm,w in (("adaptive",3.),("late",2.),("replay",1.)):
            base={"baseline_nll":2.,"weights_sha256":"same"}
            records.append(dict(seed=seed,method=arm,phase="hybrid",finished_at="today",tokens=2**24,dev_nll=3.,
                                initial_trainable_sha256=str(seed),parent_restart_sha256=str(seed),
                                data_manifest_sha256="data",widths={"2048":{**base,"width":1.},"4096":{**base,"width":w}}))
    evidence = hybrid_results(records)
    assert evidence["status"]=="both width comparisons passed"
    assert evidence["comparisons"]["late"]["p_holm"]==2/256
    records[-1]["widths"]["4096"]["width"]=None
    evidence = hybrid_results(records)
    assert "replay" not in evidence["comparisons"]
    assert len(evidence["pairs"])==16


def test_missing_parent_uses_pinned_hub_revision_and_checks_bytes(tmp_path,monkeypatch):
    from thirdloss import study
    from thirdloss.hub_archive import STUDY_HUB
    from thirdloss.records import sha256,write_json
    repo = study.STAGE_HUB["stories"]
    remote = tmp_path/"remote"
    remote.mkdir()
    payload = remote/"training_state.pt"
    payload.write_bytes(b"fixture checkpoint bytes")
    digest=sha256(payload)
    row=dict(id="trunk",stage="stories",steps=2048,data_manifest_sha256="data",weights_name="model.safetensors",weights_sha256="weights")
    write_json(remote/"restart.json",{"sha256":digest,"next_step":2048,"data_manifest_sha256":"data"})
    write_json(remote/"publication.json",{"repositories":{repo:{"revision":"pinned","files":{
        "runs/trunk/model.safetensors":{"sha256":"weights"},"runs/trunk/training_state.pt":{"sha256":digest}}}}})
    def download(repo_id,filename,**options):
        if repo_id!=STUDY_HUB:
            assert repo_id==repo and options["revision"]=="pinned"
        return str(remote/filename.split("/")[-1])
    monkeypatch.setattr(study,"hf_hub_download",download)
    assert study.parent_restart_file(tmp_path/"storage",row).read_bytes()==payload.read_bytes()
    payload.write_bytes(b"corrupt")
    with pytest.raises(ValueError,match="checksum"):
        study.parent_restart_file(tmp_path/"other",row)


def test_joint_week_forecast_counts_shared_prefix_once_and_all_eight_replays(tmp_path):
    from datetime import datetime, timedelta, timezone
    import json
    from thirdloss.progress import hybrid_schedule
    from thirdloss.records import write_json
    epoch=datetime(2026,1,1,tzinfo=timezone.utc)
    primary={"first_training_update_at":epoch.isoformat(),"projected_confirmation_and_scoring_hours":24.}
    assert hybrid_schedule(tmp_path,primary) is None
    for i,kind in enumerate(("trunk","adaptive","late","trace","strong","always"),1):
        run="stories-"+("branch" if kind=="trunk" else "hybrid")+f"-s21-{kind}-r01"
        folder=tmp_path/"results"/run
        write_json(folder/"summary.json",dict(id=run,finished_at=(epoch+timedelta(hours=i)).isoformat(),peak_vram_mb=i))
        if kind=="trunk":
            (folder/"events.jsonl").write_text(json.dumps({"timestamp":epoch.isoformat(),"train_seconds":0})+"\n")
    forecast=hybrid_schedule(tmp_path,primary)
    assert forecast["remaining_hybrid_hours"]==7*6+8*1
    assert forecast["combined_hours"]==74 and forecast["hours_left_in_week"]==162
    assert forecast["fits_measured_budget"]


def test_restart_timing_distinguishes_real_elapsed_time_from_repeated_outages(tmp_path):
    from thirdloss.progress import hybrid_uptime
    trunk="stories-branch-s21-trunk-r01"
    adaptive="stories-hybrid-s21-adaptive-r01"
    always="stories-hybrid-s21-always-r01"
    day="2026-11-25T"
    def at(hour):
        return f"{day}{hour:02d}:00:00+00:00"
    def gap(start,end):
        return {"source":"fixture.json","last_pre_restart_timestamp":at(start),"resume_observed_at":at(end)}
    forecast={"run_ids":[trunk,adaptive,always],"as_of":at(18),"remaining_hybrid_hours":80.,"combined_hours":100.}
    study={"runs":[{"id":trunk,"finished_at":at(9)},{"id":adaptive,"finished_at":at(13),"restart_audits":[gap(10,11)]},
                   {"id":always,"finished_at":at(18),"restart_audits":[gap(14,17)]}]}
    adjusted=hybrid_uptime(tmp_path,study,forecast)
    assert adjusted["observed_gap_hours"]==4. and adjusted["replay_proxy_gap_hours"]==1.
    assert adjusted["combined_hours"]==100-7*4-8
    assert forecast["combined_hours"]==100.


def test_restart_audit_replays_only_uncommitted_logged_updates(tmp_path):
    import json
    from thirdloss.records import write_json
    from thirdloss.verification import audit_restart
    data=tmp_path/"results"/"run"
    write_json(data/"config.json",{"id":"run"})
    logs=tmp_path/"logs"
    logs.mkdir()
    def row(step,minute,loss):
        return {"timestamp":f"2026-11-25T10:{minute:02d}:00+00:00","step":step,"loss":loss,"gradient_norm":1.}
    old=[row(8,0,2.),row(9,1,1.9),row(10,2,1.8)]
    new=[row(9,5,1.9),row(10,6,1.80001),row(11,7,1.7)]
    for path,rows in ((logs/"run-01.jsonl",old),(logs/"run-02.jsonl",new),(data/"events.jsonl",[old[0],*new])):
        path.write_text("".join(json.dumps(r)+"\n" for r in rows),encoding="utf-8")
    audit=audit_restart(tmp_path,"run")
    assert audit["resume_checkpoint_step"]==8 and audit["replayed_steps"]==2
    assert audit["advanced_past_prior_run"] and audit["previous_log"]=="run-01.jsonl"
    assert [r["same_measurements"] for r in audit["logged_replay_observations"]]==[True,False]
