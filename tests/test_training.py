"""Verify paired data, sham updates, and exact restart of the actual training loop."""

import subprocess

import numpy as np
import torch
from safetensors.torch import load_file

from thirdloss import train
from thirdloss.models import StoryConfig, StoryTransformer
from thirdloss.objectives import add_penalty
from thirdloss.records import write_json
from thirdloss.windows import gate


def small_model(stage, seed, device, storage):
    torch.manual_seed(seed)
    return StoryTransformer(StoryConfig(vocab_size=7,width=8,heads=2,layers=1,hidden=12)).to(device)


def test_randomized_control_preserves_coordinate_magnitudes_and_zero_is_noop():
    model = small_model("stories",0,"cpu",None)
    params = tuple(model.parameters())
    x = torch.tensor([[2,3,4,0],[1,3,2,1],[4,2,5,0]])
    y = (x+1)%7
    for p in params:
        p.grad = torch.zeros_like(p)
    add_penalty(model,params,x,y,{"third":0.0},"third",3,1)
    assert all(p.grad.count_nonzero()==0 for p in params)
    add_penalty(model,params,x,y,{"third":0.01},"third",3,1)
    actual = torch.cat([p.grad.flatten() for p in params])
    model.zero_grad(set_to_none=True)
    add_penalty(model,params,x,y,{"third":0.01},"sham",3,1)
    sham = torch.cat([p.grad.flatten() for p in params])
    torch.testing.assert_close(actual.abs(),sham.abs(),rtol=0,atol=0)
    assert torch.any(actual*sham < 0)


def test_step_recovery_matches_uninterrupted_weights(tmp_path,monkeypatch):
    """Crash just after a committed checkpoint, then restart through the public runner."""
    project = tmp_path/"project"
    project.mkdir()
    subprocess.run(["git","init","-q"],cwd=project,check=True)
    subprocess.run(["git","-c","user.name=Test","-c","user.email=test@example.invalid",
                    "commit","--allow-empty","-qm","fixture"],cwd=project,check=True)
    root = tmp_path/"store"
    directory = root/"data"/"stories"
    directory.mkdir(parents=True)
    rng = np.random.default_rng(42)
    for split in ("train","dev"):
        rng.integers(0,7,size=7000,dtype=np.uint16).tofile(directory/f"{split}.bin")
    write_json(directory/"manifest.json",{"eos_id":0})
    (directory/"tokenizer.json").write_text("{}",encoding="utf-8")
    monkeypatch.setattr(train,"build_model",small_model)
    monkeypatch.setattr(train,"sample_outputs",lambda *a,**k:None)
    monkeypatch.setattr(train,"chosen_coefficients",lambda *a:{"third":1e-13})
    saved = train.save_state
    seed = next(s for s in range(100) if any(gate(s,i) for i in range(2,8)))

    def interrupt(*args):
        saved(*args)
        if args[3] == 2:
            raise RuntimeError("intentional restart fixture")

    prior_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        monkeypatch.setattr(train,"save_state",interrupt)
        import pytest
        with pytest.raises(RuntimeError,match="intentional restart"):
            train.run_one(project,root,"stories","third","smoke",seed,0.03,torch.device("cpu"))
        monkeypatch.setattr(train,"save_state",saved)
        resumed = train.run_one(project,root,"stories","third","smoke",seed,0.03,torch.device("cpu"))
        history = train.read_json(project/"results"/resumed["id"]/"attempts.json")["failures"]
        assert len(history) == 1 and "intentional restart fixture" in history[0]["error"]
        import shutil
        reference = tmp_path/"reference"
        shutil.copytree(project/".git",reference/".git")
        store2 = tmp_path/"store2"
        shutil.copytree(root/"data",store2/"data")
        normal = train.run_one(reference,store2,"stories","third","smoke",seed,0.03,torch.device("cpu"))
        assert normal["initial_trainable_sha256"] == resumed["initial_trainable_sha256"]
        rel = f"checkpoints/{normal['id']}/export/model.safetensors"
        first, second = load_file(str(root/rel)),load_file(str(store2/rel))
        for name in first:
            torch.testing.assert_close(first[name],second[name],rtol=0,atol=0)
        assert normal["dev_nll"]==resumed["dev_nll"]
    finally:
        torch.set_num_threads(prior_threads)


def test_adapter_confirmation_observes_early_matched_time_checkpoints():
    """A slow host probe can span the baseline's whole time cutoff before a routine validation."""
    from thirdloss.train import validation_due
    expected = [0, 4, 8, 12, 16, 20, 24, 28, 32, 64]
    assert [step for step in range(65) if validation_due("abstracts","confirm",step,32)] == expected
    assert [step for step in range(65) if validation_due("stories","confirm",step,32)] == [32,64]
    assert [step for step in range(17) if validation_due("abstracts","pilot",step,4)] == [4,8,12,16]


def test_evaluator_requires_measured_schedule_before_test_reads(tmp_path):
    """Exercise the standalone entry point without placing any test token bytes on disk."""
    import pytest
    from thirdloss.study import evaluate_one
    run_id = "stories-confirm-s01-ce-r00"
    write_json(tmp_path/"results"/run_id/"summary.json",{"stage":"stories","id":run_id,"weights_sha256":"abc"})
    write_json(tmp_path/"results"/"freeze"/"stories.json",{"runs":{run_id:"abc"},"freeze_id":"fixture"})
    with pytest.raises(ValueError,match="one-week"):
        evaluate_one(tmp_path,tmp_path/"storage",run_id,torch.device("cpu"))
