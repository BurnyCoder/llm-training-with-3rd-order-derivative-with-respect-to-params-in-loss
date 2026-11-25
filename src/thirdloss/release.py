"""Publish the explicitly requested study artifacts using existing Git and Hugging Face logins."""

import subprocess
from pathlib import Path

from filelock import FileLock
from huggingface_hub import HfApi

from .hub_archive import COLLECTION, STAGE_HUB, publish_archive
from .records import GITHUB, read_json, sha256, storage_root, write_json


def publish_snapshot(project, message):
    """Commit only curated public study outputs, then mirror tracked research files to the Hub."""
    cache = project/".cache"
    cache.mkdir(exist_ok=True)
    with FileLock(str(cache/"publication.lock")):
        return _publish_snapshot(project,message)


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
    git("push","origin","main")
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
    prior = "EleutherAI/pythia-410m" if stage=="abstracts" else "Random initialization"
    exclusions = project/"results"/"verification"/"numerical-exclusions.json"
    diagnostic = read_json(exclusions).get(run_id) if exclusions.exists() else None
    card = (f"# {run_id}\n\n"
            f"Research checkpoint for {stage} using the {summary['method']} objective. Base: {prior}. "
            f"The run processed {summary['tokens']:,} training targets. Full development NLL was "
            f"{summary['dev_nll']:.6f} nats per target. "
            + (f"Sealed test NLL was {summary['test_nll']:.6f}. " if "test_nll" in summary else "")
            + f"See the [protocol]({GITHUB}/blob/main/reports/preregistration.md) and "
            f"[machine-readable results]({GITHUB}/tree/main/results/{run_id}). "
            f"The [restart manifest](restart.json) identifies the saved optimizer, data cursor and RNG state. "
            f"Use the pinned base and loading instructions in [the guide]({GITHUB}/blob/main/docs/runbook.md).\n")
    if diagnostic:
        card += f"\n{diagnostic['reason']} [Numerical audit]({GITHUB}/blob/main/reports/amendments/adapter-precision.md)\n"
    if summary["phase"] in {"branch","hybrid"}:
        card += (f"\nThis checkpoint belongs to the [TinyStories hybrid follow-up]({GITHUB}/blob/main/reports/hybrid/preregistration.md). "
                 f"The [per-seed geometry and development outcomes]({GITHUB}/blob/main/reports/hybrid/results.md) "
                 "link to full schedules, crossing brackets and the matched controls.\n")
    card = "---\nlanguage: [en]\npipeline_tag: text-generation\n---\n" + card
    (folder/"README.md").write_text(card,encoding="utf-8")
    write_json(folder/"training_summary.json",summary)
    api.upload_folder(repo_id=repo,folder_path=folder,path_in_repo="runs/"+run_id,
                      commit_message=f"Publish {run_id} training and evaluation artifacts")
    description = ("Full-weight research checkpoints" if stage=="stories" else "LoRA adapters for EleutherAI/pythia-410m")
    index = (f"---\nlanguage: [en]\npipeline_tag: text-generation\n"
             + ("base_model: EleutherAI/pythia-410m\nlibrary_name: peft\n" if stage=="abstracts" else "library_name: pytorch\n")
             + f"---\n# Third-derivative study · {stage}\n\n{description} are stored under "
             f"[runs](https://huggingface.co/{repo}/tree/main/runs). Each directory includes its model card, "
             f"weights, restart state, tokenizer and machine-readable scores. [Study and reproduction guide]({GITHUB})\n")
    api.upload_file(repo_id=repo,path_or_fileobj=index.encode(),path_in_repo="README.md",
                    commit_message=f"Index {stage} checkpoint collection")
