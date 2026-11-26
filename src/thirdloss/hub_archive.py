"""Publish exact Git blobs and verify ordinary Git and large-file objects on the Hub."""

import hashlib
import io
import json
import re
import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from huggingface_hub import CommitOperationAdd, CommitOperationDelete, HfApi, hf_hub_download, snapshot_download

from .records import GITHUB, read_json, time_now, write_json

OWNER = "BurnyCoder"
STUDY_HUB = f"{OWNER}/thirdloss-study"
STAGE_HUB = {"stories":f"{OWNER}/thirdloss-stories","abstracts":f"{OWNER}/thirdloss-pythia-410m-adapters"}
DATA_HUB = {"stories":f"{OWNER}/thirdloss-tinystories-tokens","abstracts":f"{OWNER}/thirdloss-arxiv-abstracts-2024"}
SPACE = f"{OWNER}/thirdloss-explorer"
COLLECTION = f"{OWNER}/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378"
HUB = "https://huggingface.co/"


def committed_files(project,revision):
    """Read the exact public commit, including dotfiles, independent of the working tree and CRLF settings."""
    def git(*args,inputs=None):
        return subprocess.check_output(["git",*args],cwd=project,input=inputs)
    entries = []
    for row in git("ls-tree","-rz",revision).split(b"\0"):
        if row:
            attributes,name = row.split(b"\t",1)
            _,kind,oid = attributes.split()
            if kind!=b"blob":
                raise ValueError(f"Unarchived Git object {name!r} of type {kind!r}")
            entries.append((name.decode(),oid))
    stream = io.BytesIO(git("cat-file","--batch",inputs=b"".join(oid+b"\n" for _,oid in entries)))
    files = {}
    for name,oid in entries:
        actual,kind,size = stream.readline().split()
        if actual!=oid or kind!=b"blob":
            raise ValueError(f"Git object mismatch for {name}")
        files[name] = stream.read(int(size))
        if stream.read(1)!=b"\n":
            raise ValueError(f"Incomplete Git blob for {name}")
    return files


def fingerprint(payload,cache=None):
    """SHA-256 verifies LFS content. Git SHA-1 also includes the header with its byte length."""
    path = payload if isinstance(payload,Path) else None
    size = path.stat().st_size if path else len(payload)
    key = str(path.resolve()) if path else None
    stamp = path.stat().st_mtime_ns if path else 0
    if path and cache and cache.get(key,{}).get("mtime_ns")==stamp and cache[key]["digest"]["size"]==size:
        return cache[key]["digest"]
    blob = hashlib.sha1(f"blob {size}\0".encode())
    digest = hashlib.sha256()
    with (path.open("rb") if path else io.BytesIO(payload)) as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            blob.update(chunk)
            digest.update(chunk)
    result = {"size":size,"sha256":digest.hexdigest(),"git_blob":blob.hexdigest()}
    if path and cache is not None:
        cache[key] = {"mtime_ns":stamp,"digest":result}
    return result


def agrees(digest,remote):
    """Use the content digest for large files, whose Git object contains only a pointer."""
    return bool(remote and remote.size==digest["size"] and (
        remote.lfs.sha256==digest["sha256"] if remote.lfs else remote.blob_id==digest["git_blob"]))


def matches(payload,remote):
    return agrees(fingerprint(payload),remote)


def console_log(raw,project,storage):
    """Retain operator output while removing local account paths and transport credentials."""
    encoding = "utf-16" if raw.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig"
    value = raw.decode(encoding,errors="replace")
    for local,label in ((project,"[project]"),(storage,"[storage]"),(Path.home(),"[user]")):
        value = value.replace(str(local),label).replace(local.as_posix(),label)
    value = re.sub(r"(?i)(authorization\s*[:=]\s*)(?:bearer\s+|basic\s+)?[^\s,}\]]+",
                   r"\1[redacted]",value)
    value = re.sub(r"\b(?:hf_|gh[pousr]_|github_pat_|sk-)[A-Za-z0-9_-]{20,}","[redacted]",value)
    value = re.sub(r"(?i)(https?://[^\s?'\"]+)\?[^\s'\"]*(?:x-amz-|x-goog-|signature=|token=)[^\s'\"]*",
                   r"\1?[redacted]",value)
    return value.encode("utf-8")


def remote_files(api,repo,kind,revision=None):
    return {entry.path:entry for entry in api.list_repo_tree(repo,repo_type=kind,revision=revision,recursive=True)
            if hasattr(entry,"blob_id")}


def sync(api,repo,kind,files,cache,message,prune=()):
    """Compare both sides, repair missing or changed content, then verify the committed remote tree."""
    api.create_repo(repo,repo_type=kind,space_sdk="static" if kind=="space" else None,exist_ok=True)
    api.add_collection_item(COLLECTION,repo,kind,exists_ok=True)
    hashes = {name:fingerprint(value,cache) for name,value in files.items()}
    revision = api.repo_info(repo,repo_type=kind).sha
    remote = remote_files(api,repo,kind,revision)
    ops = [CommitOperationAdd(path_in_repo=name,path_or_fileobj=files[name])
           for name,digest in hashes.items() if not agrees(digest,remote.get(name))]
    ops.extend(CommitOperationDelete(path_in_repo=name) for name in remote.keys()-files.keys()
               if name.startswith(prune))
    if ops:
        commit = api.create_commit(repo,repo_type=kind,operations=ops,commit_message=message)
        revision = commit.oid
        remote = remote_files(api,repo,kind,revision)
    bad = [name for name,digest in hashes.items() if not agrees(digest,remote.get(name))]
    if bad:
        raise ValueError(f"Hub content differs in {repo} for {bad[:5]}")
    return {"type":kind,"revision":revision,"files":hashes}


def dataset_files(storage,stage,tree,cache):
    """Package the actual packed corpus and its audit. Release test bytes after the recorded stage freeze."""
    base = storage/"data"/stage
    record_name = f"results/datasets/{stage}.json"
    if record_name not in tree:
        return {}
    if not (base/"manifest.json").exists():
        from .data import prepare
        prepare(stage,storage/"data")
    manifest = read_json(base/"manifest.json")
    if manifest!=json.loads(tree[record_name]):
        raise ValueError(f"Prepared corpus differs from the committed {stage} manifest")
    sealed = f"results/freeze/{stage}.json" in tree and "results/feasibility/one-week.json" in tree
    files = {"manifest.json":base/"manifest.json"}
    for name,record in manifest["artifacts"].items():
        if name=="test.bin" and not sealed:
            continue
        path = base/name
        local = fingerprint(path,cache)
        if local["size"]!=record["bytes"] or local["sha256"]!=record["sha256"]:
            raise ValueError(f"Prepared corpus differs from its manifest for {stage}/{name}")
        files[name] = path
    license_name = "CDLA-Sharing-1.0.txt" if stage=="stories" else "Apache-2.0.txt"
    files[license_name] = tree["docs/hub/"+license_name]
    card = tree[f"docs/hub/{stage}.md"].decode()
    availability = ("The frozen test stream is available as `test.bin`." if sealed else
                    "The manifest records the test digest. Its token stream is released when the stage checkpoints are frozen.")
    files["README.md"] = (card+"\n"+availability+"\n").encode()
    return files


def run_card(run,repo,weight=None,score=None,diagnostic=None):
    """Render a fitted checkpoint or zero-update reference from its committed measurements."""
    from .flatness_tables import checkpoint_table
    from .report_records import METHODS,STAGES
    study=HUB+STUDY_HUB
    docs=study+"/blob/main/research"
    prefix=f"{HUB}{repo}/blob/main/runs/{run['id']}"
    kind=METHODS.get(run["method"],run["method"])
    lines=["---\nlanguage: [en]\npipeline_tag: text-generation\n---",f"# {kind} · {STAGES[run['stage']]}",
           f"Run `{run['id']}` used seed {run['seed']} and {run['tokens']:,} optimizer targets. "
           f"Full development NLL was {run['dev_nll']:.6f} nats per target. Lower NLL is better."]
    if "test_nll" in run:
        lines.append(f"Frozen-checkpoint test NLL was {run['test_nll']:.6f} nats per target.")
        if run["stage"]=="stories":
            lines.append("Some held-out stories share exact passages with sampled training windows. "
                         f"The saved score covers the whole split. [Overlap by seed]({docs}/reports/reviews/independent-scientific-audit.md)")
    if run["method"]=="unigram":
        lines.append("This predictor uses add-one-smoothed training token counts. Its common score width "
                     "can be compared with the neural predictors on the same corpus.")
    elif run["method"]=="initial":
        lines.append("The registered initialization gives this zero-update neural reference. "
                     "The probe record identifies the reconstructed weights used for measurement.")
    else:
        base="EleutherAI/pythia-410m with attention QKV LoRA" if run["stage"]=="abstracts" else "Randomly initialized TinyStories decoder"
        lines.append(f"{base}. The restart manifest identifies the weights' optimizer state, data cursor and random state. "
                     f"[Restart manifest]({prefix}/restart.json) · [Reload instructions]({docs}/docs/runbook.md)")
    if diagnostic:
        lines.append(f"{diagnostic['reason']} [Numerical audit]({docs}/reports/amendments/adapter-precision.md)")
    if run["phase"] in {"branch","hybrid"}:
        lines.append(f"[Hybrid protocol]({docs}/reports/hybrid/preregistration.md) · "
                     f"[Paired width differences, numerical bounds and donor dependence]({docs}/reports/hybrid/results.md)")
    lines.extend(["## Flatness",checkpoint_table(run["method"],weight,score),
                  "Compare weight measurements within the same parameterization and token horizon. The shared "
                  "score probes use the same token-level perturbations within each corpus. Their value for predicting "
                  f"held-out performance is unknown. [Compare every variant and baseline]({study}#all-variants-and-baselines) · "
                  f"[Per-run statistics and raw probes]({docs}/reports/flatness.md) · [Training scores]({prefix}/training_summary.json)"])
    probes=[]
    if weight and "rms_curvature" in weight:
        probes.append(f"[Weight perturbations and Hessian probes]({prefix}/flatness.json)")
    if score:
        probes.append(f"[Shared score perturbations]({prefix}/score-flatness.json)")
    if probes:
        lines.append(" · ".join(probes))
    return "\n\n".join(lines)+"\n"


def _fitted_files(storage,repo,run,cache):
    """Verify local or Hub-recovered weights and the optimizer state against the published fingerprints."""
    prefix="runs/"+run["id"]+"/"
    folder=storage/"checkpoints"/run["id"]
    export=folder/"export"
    state=folder/"latest.pt"
    if not (export/"restart.json").exists() or not state.exists():
        saved=snapshot_download(repo,allow_patterns=[prefix+"*"],cache_dir=storage/"hub")
        export=Path(saved)/prefix
        state=export/"training_state.pt"
    restart=read_json(export/"restart.json")
    if (fingerprint(export/run["weights_name"],cache)["sha256"]!=run["weights_sha256"]
            or fingerprint(state,cache)["sha256"]!=restart["sha256"]
            or restart["next_step"]!=run["steps"] or restart["data_manifest_sha256"]!=run["data_manifest_sha256"]):
        raise ValueError(f"Weight or optimizer receipt differs for {run['id']}")
    files={prefix+file.name:file for file in export.iterdir() if file.is_file()}
    if prefix+"tokenizer.json" not in files:
        raise ValueError(f"Missing publication artifact {run['id']}/tokenizer.json")
    files[prefix+"training_state.pt"]=state
    return files


def model_files(storage,stage,repo,tree,cache):
    """Place every fitted run and both untrained references alongside comparable, digest-verified probes."""
    files = {}
    exclusions=json.loads(tree.get("results/verification/numerical-exclusions.json",b"{}"))
    for name,content in tree.items():
        if not (name.startswith("results/") and name.endswith("/summary.json")):
            continue
        run = json.loads(content)
        if run.get("stage")!=stage:
            continue
        prefix = "runs/"+run["id"]+"/"
        if run.get("weights_sha256"):
            files.update(_fitted_files(storage,repo,run,cache))
        elif run["method"] not in {"initial","unigram"}:
            raise ValueError(f"Missing fitted weights for {run['id']}")
        source=name.removesuffix("summary.json")
        weight,score={},{}
        for filename in ("flatness.json","score-flatness.json"):
            if source+filename in tree:
                data=tree[source+filename]
                probe=json.loads(data)
                files[prefix+filename]=data
                if filename=="flatness.json":
                    weight={**probe["width"],**probe["curvature"]}
                else:
                    score=probe["score"]
        final_width=source+f"width-{run['steps']}.json"
        if not weight and final_width in tree:
            weight=json.loads(tree[final_width])
        files[prefix+"README.md"]=run_card(run,repo,weight,score,exclusions.get(run["id"])).encode()
        files[prefix+"training_summary.json"] = content
    if files:
        title = "Full-weight TinyStories models" if stage=="stories" else "Pythia-410M QKV LoRA adapters"
        header = "library_name: pytorch" if stage=="stories" else "library_name: peft\nbase_model: EleutherAI/pythia-410m"
        files["README.md"] = (f"---\nlanguage: [en]\npipeline_tag: text-generation\n{header}\n---\n"
            f"# {title}\n\nEach run has a card with its prediction scores and available flatness measurements. "
            f"Fitted models also include weights, tokenizer and restartable training state. "
            f"[Browse models and controls]({HUB}{repo}/tree/main/runs) · "
            f"[Compare flatness across variants and baselines]({HUB}{STUDY_HUB}#all-variants-and-baselines) · "
            f"[Prepared corpus]({HUB}datasets/{DATA_HUB[stage]}) · [Explorer]({HUB}spaces/{SPACE})\n").encode()
    return files


def space_files(tree):
    """Serve the same figures, JavaScript and result records, using Hub-native research links."""
    files = {path.removeprefix("docs/"):content for path,content in tree.items() if
             path.startswith("docs/figures/") or path in {"docs/index.html","docs/explorer.js","docs/explorer.css","docs/study.json"}}
    study = HUB+STUDY_HUB
    root = study+"/tree/main/research"
    html = files["index.html"].decode().replace(GITHUB+"/blob/main/",study+"/blob/main/research/")
    html = html.replace('class="source" href="'+GITHUB+'"',
                        'class="source" data-runs="'+root+'/results/" href="'+root+'"')
    files["index.html"] = html.encode()
    files["README.md"] = tree["docs/hub/space.md"]
    return files


def publish_archive(project,storage,revision,message):
    """Reconcile the public study, runnable Space, prepared datasets, exported models and restart files."""
    api = HfApi()
    tree = committed_files(project,revision)
    cache_path = project/".cache"/"hub-object-hashes.json"
    cache = read_json(cache_path) if cache_path.exists() else {}
    repositories = {SPACE:sync(api,SPACE,"space",space_files(tree),cache,message,("figures/",))}
    for stage,repo in DATA_HUB.items():
        files = dataset_files(storage,stage,tree,cache)
        if files:
            repositories[repo] = sync(api,repo,"dataset",files,cache,message)
    for stage,repo in STAGE_HUB.items():
        files = model_files(storage,stage,repo,tree,cache)
        if files:
            repositories[repo] = sync(api,repo,"model",files,cache,message)
    files = {"research/"+name:value for name,value in tree.items()}
    evidence = json.loads(tree.get("results/analysis/scientific-audit.json", b"{}"))
    for name,digest in evidence.get("precision",{}).get("reference_files",{}).items():
        path = storage/"diagnostics"/name
        if fingerprint(path,cache)["sha256"] != digest:
            raise ValueError(f"FP64 reference digest differs for {name}")
        files["diagnostics/"+name] = path
    for path in sorted((project/"logs").glob("*")):
        if path.is_file() and path.suffix in {".jsonl",".log"}:
            raw = path.read_bytes()
            files["logs/"+path.name] = console_log(raw,project,storage) if path.suffix==".log" else raw
    files["README.md"] = tree["docs/hub/archive.md"]
    repositories[STUDY_HUB] = {"type":"model","files":{name:fingerprint(value,cache) for name,value in files.items()}}
    receipt = {"git_revision":revision,"verified_at":time_now(),"collection":COLLECTION,"repositories":repositories}
    files["publication.json"] = (json.dumps(receipt,indent=2,sort_keys=True)+"\n").encode()
    sync(api,STUDY_HUB,"model",files,cache,message,("research/",))
    write_json(cache_path,cache)
    return receipt


def audit_archive(project):
    """Fetch the public receipt, compare every remote object digest, then compare the exact local Git tree."""
    api = HfApi()
    current = api.repo_info(STUDY_HUB).sha
    receipt_file = Path(hf_hub_download(STUDY_HUB,"publication.json",revision=current))
    receipt = read_json(receipt_file)
    collection = {x.item_id for x in api.get_collection(COLLECTION).items}
    for repo,record in receipt["repositories"].items():
        remote = remote_files(api,repo,record["type"],record.get("revision",current))
        if repo==STUDY_HUB and not matches(receipt_file,remote.get("publication.json")):
            raise ValueError("The downloaded publication receipt differs from its Hub object")
        if repo not in collection:
            raise ValueError(f"Missing collection item {repo}")
        for name,digest in record["files"].items():
            if not agrees(digest,remote.get(name)):
                raise ValueError(f"Publication audit failed for {repo}/{name}")
    commit = subprocess.check_output(["git","rev-parse","HEAD"],cwd=project,text=True).strip()
    if commit!=receipt["git_revision"]:
        raise ValueError(f"Published Git commit {receipt['git_revision']} differs from current HEAD {commit}")
    tree = committed_files(project,commit)
    expected = {"research/"+n:fingerprint(data) for n,data in tree.items()}
    archived = receipt["repositories"][STUDY_HUB]["files"]
    if expected!={n:d for n,d in archived.items() if n.startswith("research/")}:
        raise ValueError("The published research tree differs from the committed Git blobs")
    return {"git_revision":commit,"git_files":len(tree),"archive_revision":current,
            "verified_files":{repo:len(r["files"]) for repo,r in receipt["repositories"].items()}}


def restore_audit_inputs(project,storage,revision=None):
    """Fetch missing numeric evidence from one publication receipt. No model is instantiated."""
    snapshot = HfApi().repo_info(STUDY_HUB,revision=revision).sha
    receipt = read_json(hf_hub_download(STUDY_HUB,"publication.json",revision=snapshot))

    def restore(repo, name, destination):
        record = receipt["repositories"][repo]
        expected = record["files"][name]["sha256"]
        if destination.exists() and fingerprint(destination)["sha256"]==expected:
            return
        cached = Path(hf_hub_download(repo,name,repo_type=record["type"],
                                      revision=record.get("revision",snapshot)))
        if fingerprint(cached)["sha256"]!=expected:
            raise ValueError(f"Unexpected archived digest for {repo}/{name}")
        destination.parent.mkdir(parents=True,exist_ok=True)
        with NamedTemporaryFile(dir=destination.parent,delete=False) as handle:
            temporary = Path(handle.name)
        try:
            shutil.copyfile(cached,temporary)
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)

    results = project/"results"
    for stage,repo in DATA_HUB.items():
        manifest = read_json(results/"datasets"/f"{stage}.json")
        for name in ("manifest.json", *manifest["artifacts"]):
            if name!="test.bin" or (results/"freeze"/f"{stage}.json").exists():
                restore(repo,name,storage/"data"/stage/name)
    for path in results.glob("*/summary.json"):
        row = read_json(path)
        if row.get("weights_name"):
            name,run = row["weights_name"],row["id"]
            restore(STAGE_HUB[row["stage"]],f"runs/{run}/{name}",storage/"checkpoints"/run/"export"/name)
    for device in ("cpu","cuda"):
        name = f"pythia-reference-{device}.safetensors"
        restore(STUDY_HUB,"diagnostics/"+name,storage/"diagnostics"/name)
