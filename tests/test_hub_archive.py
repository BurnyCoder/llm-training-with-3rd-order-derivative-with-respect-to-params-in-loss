"""Verify exact Git and Hub bytes without publishing fixtures to a remote service."""

import hashlib
import json
import subprocess
from types import SimpleNamespace

import pytest

from thirdloss.hub_archive import committed_files, console_log, dataset_files, matches


def test_archive_uses_committed_blobs_including_dotfiles(tmp_path):
    def git(*args):
        return subprocess.check_output(["git",*args],cwd=tmp_path)
    git("init","-q")
    git("config","core.autocrlf","true")
    (tmp_path/".gitignore").write_bytes(b".env\r\n")
    (tmp_path/".env").write_bytes(b"private=yes")
    (tmp_path/"README.md").write_bytes(b"published\r\n")
    git("add",".")
    git("-c","user.name=Test","-c","user.email=test@example.invalid","commit","-qm","fixture")
    (tmp_path/"README.md").write_bytes(b"uncommitted working copy")
    assert committed_files(tmp_path,"HEAD")=={".gitignore":b".env\n","README.md":b"published\n"}


def test_remote_sha_matches_git_and_large_file_storage(tmp_path):
    data=b"measured file\n"
    git_object=hashlib.sha1(b"blob 14\0"+data).hexdigest()
    normal=SimpleNamespace(size=14,blob_id=git_object,lfs=None)
    large=SimpleNamespace(size=14,blob_id="pointer",lfs=SimpleNamespace(sha256=hashlib.sha256(data).hexdigest()))
    path=tmp_path/"example"
    path.write_bytes(data)
    assert matches(data,normal) and matches(path,large)
    assert not matches(b"measured tile\n",normal)
    assert not matches(data,None)


def test_operational_logs_preserve_science_and_remove_auth_material(tmp_path):
    token="hf_"+"s"*35
    content=f"loss 3.25\nAuthorization: Bearer {token}\nhttps://host.test/obj?X-Amz-Signature=private\n"
    safe=console_log(content.encode(),tmp_path,tmp_path/"storage")
    assert b"loss 3.25" in safe and b"private" not in safe and token.encode() not in safe


def test_model_repository_compares_fitted_and_weightless_predictors_from_the_same_records(tmp_path):
    """The individual Hub cards, raw probe files and study-wide comparison must agree."""
    from thirdloss.hub_archive import model_files
    table={"id":"story-counts","method":"unigram","stage":"stories","phase":"control","seed":0,
           "tokens":0,"steps":0,"dev_nll":4.5,"data_manifest_sha256":"corpus"}
    fitted={**table,"id":"story-ce","method":"ce","phase":"pilot","steps":1,"tokens":4096,
            "weights_name":"model.safetensors","weights_sha256":hashlib.sha256(b"weights").hexdigest()}
    folder=tmp_path/"checkpoints"/"story-ce"/"export"
    folder.mkdir(parents=True)
    (folder/"model.safetensors").write_bytes(b"weights")
    (folder.parent/"latest.pt").write_bytes(b"state")
    (folder/"tokenizer.json").write_text("{}")
    (folder/"restart.json").write_text(json.dumps({"sha256":hashlib.sha256(b"state").hexdigest(),
                                                   "next_step":1,"data_manifest_sha256":"corpus"}))
    summary=lambda obj:json.dumps(obj).encode()
    score={"width":1.25,"width_lower":1.249,"width_upper":1.251,"mean_directional_curvature":.9,
           "directions":[],"censored_rays":0}
    native={"width":2.5,"width_lower":2.499,"width_upper":2.501,"censored_rays":0,"directions":[]}
    tree={f"results/{row['id']}/summary.json":summary(row) for row in (table,fitted)}
    for row in (table,fitted):
        tree[f"results/{row['id']}/score-flatness.json"]=summary({"score":score})
    tree["results/story-ce/flatness.json"]=summary({"width":native,"curvature":{"rms_curvature":.42,"trace_per_parameter":-.02}})
    files=model_files(tmp_path,"stories","account/test",tree,{})
    for run in ("story-counts","story-ce"):
        card=files[f"runs/{run}/README.md"].decode()
        assert "1.250" in card and "all-variants-and-baselines" in card
        assert files[f"runs/{run}/score-flatness.json"]==tree[f"results/{run}/score-flatness.json"]
    assert "N/A" in files["runs/story-counts/README.md"].decode() and "2.500" in files["runs/story-ce/README.md"].decode()
    assert "runs/story-counts/training_state.pt" not in files and "runs/story-ce/training_state.pt" in files
    assert b"all-variants-and-baselines" in files["README.md"]


def test_packed_files_match_manifest_and_release_test_only_after_both_gates(tmp_path):
    base=tmp_path/"data"/"stories"
    base.mkdir(parents=True)
    manifest={"artifacts":{}}
    for data in ("train.bin","dev.bin","test.bin"):
        payload=data.encode()
        (base/data).write_bytes(payload)
        manifest["artifacts"][data]={"bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest()}
    encoded=json.dumps(manifest).encode()
    (base/"manifest.json").write_bytes(encoded)
    tree={"docs/hub/stories.md":b"card","docs/hub/CDLA-Sharing-1.0.txt":b"terms","results/datasets/stories.json":encoded}
    assert "test.bin" not in dataset_files(tmp_path,"stories",tree,{})
    tree["results/freeze/stories.json"]=b"{}"
    assert "test.bin" not in dataset_files(tmp_path,"stories",tree,{})
    tree["results/feasibility/one-week.json"]=b"{}"
    assert "test.bin" in dataset_files(tmp_path,"stories",tree,{})
    (base/"train.bin").write_bytes(b"wrong.bin")
    with pytest.raises(ValueError,match="differs from its manifest"):
        dataset_files(tmp_path,"stories",tree,{})


def test_live_feed_retains_active_and_latest_completed_runs():
    from thirdloss.live_hub import overlay
    done={"stage":"abstracts","status":"complete"}
    runs=[{**done,"id":"earlier","finished_at":"01"},{**done,"id":"newer","finished_at":"02"},
          {"stage":"abstracts","status":"training","id":"current","events":[{"accuracy":0.4}]}]
    feed=overlay({"runs":runs,"stages":{},"pilot_comparisons":{}})
    assert feed["active"] and [r["id"] for r in feed["runs"]]==["newer","current"]
    assert feed["runs"][1]["events"]==[{"accuracy":0.4}]
def test_result_publisher_merges_concurrent_documentation_without_losing_either(tmp_path):
    """Reproduce a remote documentation commit landing while a local run report is being generated."""
    from thirdloss.release import push_main
    def git(folder,*args):
        return subprocess.run(["git",*args],cwd=folder,check=True,capture_output=True,text=True).stdout.strip()
    remote=tmp_path/"upstream.git"
    git(tmp_path,"init","--bare","--initial-branch=main",str(remote))
    owner=tmp_path/"study"
    git(tmp_path,"clone",str(remote),str(owner))
    git(owner,"config","user.name","Study fixture")
    git(owner,"config","user.email","study@example.invalid")
    (owner/"README.md").write_text("Study",encoding="utf-8")
    git(owner,"add",".")
    git(owner,"commit","-m","Register study")
    git(owner,"push","origin","main")
    writer=tmp_path/"writer"
    git(tmp_path,"clone",str(remote),str(writer))
    git(writer,"config","user.name","Review fixture")
    git(writer,"config","user.email","review@example.invalid")
    (writer/"worked-example.md").write_text("Derivation",encoding="utf-8")
    git(writer,"add",".")
    git(writer,"commit","-m","Explain the schedule")
    (owner/"width.json").write_text("{}",encoding="utf-8")
    git(owner,"add",".")
    git(owner,"commit","-m","Measure width")
    git(writer,"push","origin","main")
    push_main(owner)
    assert git(remote,"show","main:worked-example.md")=="Derivation"
    assert git(remote,"show","main:width.json")=="{}"
    assert git(owner,"rev-parse","HEAD")==git(remote,"rev-parse","main")


def test_result_publication_retries_outages_without_rewriting_history(monkeypatch,tmp_path):
    import subprocess
    from thirdloss import release
    failures=iter(["remote: Internal Server Error","The requested URL returned error: 503",""])
    calls=[]; delays=[]
    def once(args,**kwargs):
        calls.append(args)
        error=next(failures)
        return subprocess.CompletedProcess(args,int(bool(error)),stdout="",stderr=error)
    monkeypatch.setattr(release.subprocess,"run",once)
    monkeypatch.setattr(release.time,"sleep",delays.append)
    release.push_main(tmp_path)
    assert calls==[["git","push","origin","main"]]*3 and delays==[2,4]
    failures=iter(["permission denied"])
    with pytest.raises(RuntimeError,match="permission denied"):
        release.push_main(tmp_path)
    assert delays==[2,4]
