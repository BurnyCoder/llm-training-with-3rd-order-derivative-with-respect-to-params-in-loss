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
