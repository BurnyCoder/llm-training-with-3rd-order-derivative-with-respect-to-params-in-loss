"""Publish the explicitly requested study artifacts using existing Git and Hugging Face logins."""

import subprocess
import re
import time

from filelock import FileLock
from huggingface_hub import HfApi

from .hub_archive import COLLECTION, STAGE_HUB, publish_archive,run_card
from .records import read_json, sha256, storage_root, time_now, write_json


def publish_snapshot(project, message):
    """Commit only curated public study outputs, then mirror tracked research files to the Hub."""
    cache = project/".cache"
    cache.mkdir(exist_ok=True)
    with FileLock(str(cache/"publication.lock")):
        return _publish_snapshot(project,message)


def push_main(project):
    """Preserve concurrent upstream commits when a completed run has a local release commit."""
    def run(*args,check=True):
        return subprocess.run(["git",*args],cwd=project,check=check,capture_output=True,text=True)

    def remote(*args):
        """A transient server rejection can arrive even over a successful HTTP connection."""
        for delay in (2,4,8,16,30,60,60,60,60,60,0):
            result=run(*args,check=False)
            temporary=re.search(r"internal server error|bad gateway|service unavailable|gateway timeout|"
                                r"(?:http |returned error: )(?:408|429|500|502|503|504)\b|connection (?:reset|timed out)",
                                result.stderr,re.IGNORECASE)
            if not result.returncode or not temporary or not delay:
                return result
            # Retrying the identical non-forced push preserves Git's fast-forward checks.
            # https://git-scm.com/docs/git-push#_note_about_fast_forwards
            print(f"{time_now()} Git {args[0]} returned {temporary.group()}. Retrying in {delay}s.",flush=True)
            time.sleep(delay)

    for attempt in range(4):
        pushed = remote("push","origin","main")
        if pushed.returncode==0:
            return
        error = pushed.stderr.lower()
        if attempt==3 or ("fetch first" not in error and "non-fast-forward" not in error):
            raise RuntimeError(f"Git release push failed: {pushed.stderr.strip()}")
        remote("fetch","origin","main").check_returncode()
        merged=run("merge","--no-edit","FETCH_HEAD",check=False)
        if merged.returncode:
            conflicts=run("diff","--name-only","--diff-filter=U").stdout.strip()
            if conflicts:
                # Preserve both original commits for review when edits overlap.
                run("merge","--abort")
            raise RuntimeError(f"Git release needs a merge review: {conflicts or merged.stderr.strip()}")


def _publish_snapshot(project,message):
    """Keep the Git revision and all verified collection receipts together across concurrent releases."""
    def git(*args):
        return subprocess.run(["git",*args],cwd=project,check=True,capture_output=True,text=True).stdout.strip()
    if git("branch","--show-current") != "main":
        raise ValueError("Publish study snapshots from the merged main branch")
    public = [name for name in ("README.md","reports","docs","results") if (project/name).exists()]
    git("add","--",*public)
    if git("diff","--cached","--name-only"):
        git("commit","-m",message,"--",*public)
    push_main(project)
    revision = git("rev-parse","HEAD")
    publish_archive(project,storage_root(project),revision,message)
    return revision


def publish_weights(project, storage, summary):
    """Store each fitted checkpoint in a distinct reproducible run directory in the collection."""
    if "weights_sha256" not in summary:
        return
    stage, run_id = summary["stage"], summary["id"]
    repo = STAGE_HUB[stage]
    api = HfApi()
    api.create_repo(repo,exist_ok=True)
    api.add_collection_item(COLLECTION,repo,"model",exists_ok=True)
    folder = storage/"checkpoints"/run_id/"export"
    if sha256(folder/summary["weights_name"]) != summary["weights_sha256"]:
        raise ValueError(f"Checkpoint integrity failure for {run_id}")
    # Keep exports directly loadable for inference and publish the restart payload alongside
    # them. The original state includes AdamW moments, RNGs and the next deterministic data step.
    import torch
    restart = folder.parent/"latest.pt"
    state = torch.load(restart,map_location="cpu",weights_only=True)
    if (state["next_step"]!=summary["steps"] or state["config"]["id"]!=run_id
            or state["config"]["data_manifest_sha256"]!=summary["data_manifest_sha256"]):
        raise ValueError(f"Restart state differs from the completed run {run_id}")
    write_json(folder/"restart.json",{"filename":"training_state.pt","sha256":sha256(restart),
                                    "next_step":state["next_step"],"data_manifest_sha256":summary["data_manifest_sha256"]})
    del state
    api.upload_file(repo_id=repo,path_or_fileobj=restart,path_in_repo=f"runs/{run_id}/training_state.pt",
                    commit_message=f"Archive optimizer, data cursor and random state for {run_id}")
    exclusions = project/"results"/"verification"/"numerical-exclusions.json"
    diagnostic = read_json(exclusions).get(run_id) if exclusions.exists() else None
    results=project/"results"/run_id
    raw=read_json(results/"flatness.json") if (results/"flatness.json").exists() else {}
    weight={**raw.get("width",{}),**raw.get("curvature",{})}
    score=read_json(results/"score-flatness.json")["score"] if (results/"score-flatness.json").exists() else {}
    (folder/"README.md").write_text(run_card(summary,repo,weight,score,diagnostic),encoding="utf-8")
    write_json(folder/"training_summary.json",summary)
    api.upload_folder(repo_id=repo,folder_path=folder,path_in_repo="runs/"+run_id,
                      commit_message=f"Publish {run_id} training and evaluation artifacts")
