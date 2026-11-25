"""Prepare versioned, leakage-audited token streams for both causal LM experiments."""

import gzip
import hashlib
import json
import os
import re
import shutil
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from itertools import batched, islice
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
import numpy as np
import pyarrow.parquet as pq
from filelock import FileLock
from huggingface_hub import constants, hf_hub_download, hf_hub_url
from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

from .overlap import Document, clean_splits


STORY_REPO = "roneneldan/TinyStories"
STORY_REVISION = "f54c09fd23315a6f9c86f9dc80f725de7d8f9c64"
ABSTRACT_REPO = "common-pile/arxiv_abstracts_filtered"
ABSTRACT_REVISION = "dc1ceab4755eb037ec61e49cf1350dab7ceee6e7"
PYTHIA_REPO = "EleutherAI/pythia-410m"
PYTHIA_REVISION = "9879c9b5f8bea9051dcb0e68dff21493d67e9d4f"
STORY_LIMIT = 160_000
STORY_VOCAB = 4096
EOS = "<|endoftext|>"
FORMAT = "thirdloss-packed-v1"

# Object IDs and byte lengths come from the pinned HF tree APIs documented in docs/data.md.
# Large files use LFS SHA-256. The tokenizer uses the Git blob identifier at this release.
FILES = {
    "story_train": ("data/train-00000-of-00004-2d5a1467fff1081b.parquet", 248731111,
                    "77cf780cebe52b6e83e3a2ac84bc56d8059363113e41d17a023f1d8b2ed0fc0b"),
    "story_test": ("data/validation-00000-of-00001-869c898b519ad725.parquet", 9989127,
                   "33406a6206554cfc279c29c11f4df51528af487aa1a602b075566fc83c49dcab"),
    "abstract_0": ("arxiv-abstracts-dolma-0000.json.gz", 892766221,
                   "2aa4dba7c362a977853619239655f073205346978931d6ad070026c7dfa1c4d2"),
    "abstract_1": ("arxiv-abstracts-dolma-0001.json.gz", 235616002,
                   "451ff8bbc867360d66ddca2794459377d1cc56f91b2243587857f8ded982af36"),
    "pythia_tokenizer": ("tokenizer.json", 2113710, "f74dfbfab8f97770a87769c739fb080c21c8bacc"),
}


def _log(message: str) -> None:
    """Make long stream/audit phases visible to the command-line run log."""
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"{stamp} [prepare] {message}", flush=True)


def _sha256(path: Path) -> str:
    """Hash bytes incrementally to avoid holding upstream archives in memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _verify_source(path: Path, size: int, expected: str) -> str:
    """Authenticate each input against the immutable upstream object identifier."""
    if path.stat().st_size != size:
        raise ValueError(f"Unexpected byte count for {path.name}")
    sha = _sha256(path)
    if len(expected) == 40:
        git = hashlib.sha1(f"blob {size}\0".encode("ascii"), usedforsecurity=False)
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                git.update(block)
        actual = git.hexdigest()
    else:
        actual = sha
    if actual != expected:
        raise ValueError(f"Content hash differs from pinned revision for {path.name}")
    return sha


def _source(root: Path, repo: str, revision: str, key: str, kind: str = "dataset") -> tuple[Path, dict]:
    """Download from the pinned Hub revision, with a verified public HTTPS fallback."""
    name, size, oid = FILES[key]
    fallback = root / "_sources" / "https" / revision / name
    options = dict(repo_id=repo, filename=name, revision=revision, repo_type=kind)
    _log(f"resolving {repo}@{revision[:9]}/{name}")
    if fallback.is_file():
        try:
            digest = _verify_source(fallback, size, oid)
            return fallback, dict(repo=repo, revision=revision, file=name, bytes=size, sha256=digest)
        except ValueError:
            _log(f"refreshing damaged fallback for {name}")
    try:
        path = Path(hf_hub_download(**options, cache_dir=root / "_sources" / "hub"))
        digest = _verify_source(path, size, oid)
    except (OSError, RuntimeError, ValueError, httpx.HTTPError) as error:
        if constants.HF_HUB_OFFLINE:
            raise
        _log(f"Hub transport failed ({type(error).__name__}); verifying public HTTPS copy")
        # A nonce requests a fresh signed object URL on networks that cache stale redirects.
        url = hf_hub_url(**options) + f"?download=true&attempt={int(time.time())}"
        fallback.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=fallback.parent, prefix=".download-") as directory:
            partial = Path(directory) / "download"
            request = urllib.request.Request(url, headers={"User-Agent": "thirdloss-data/1"})
            with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as target:
                shutil.copyfileobj(response, target, length=4 * 1024 * 1024)
            digest = _verify_source(partial, size, oid)
            os.replace(partial, fallback)
        path = fallback
    return path, dict(repo=repo, revision=revision, file=name, bytes=size, sha256=digest)


def _texts(path: Path):
    """Stream Arrow record batches in physical row order and keep only the text column."""
    with pq.ParquetFile(path) as table:
        for batch in table.iter_batches(batch_size=2048, columns=["text"]):
            yield from batch.column(0).to_pylist()


def _story_documents(root: Path) -> tuple[dict, list, dict]:
    """Assign the first registered source rows before deduplication and tokenizer fitting."""
    train, train_meta = _source(root, STORY_REPO, STORY_REVISION, "story_train")
    test, test_meta = _source(root, STORY_REPO, STORY_REVISION, "story_test")
    docs = {"train": [], "dev": [], "test": []}
    for row, text in enumerate(islice(_texts(train), STORY_LIMIT)):
        doc = Document.make(f"train:{row}", text or "")
        # A content hash makes equivalent stories receive the same development assignment.
        split = "dev" if int(doc.digest[:16], 16) % 50 == 0 else "train"
        docs[split].append(doc)
    if len(docs["train"]) + len(docs["dev"]) != STORY_LIMIT:
        raise ValueError("Pinned first training shard does not cover the registered prefix")
    for row, text in enumerate(_texts(test)):
        docs["test"].append(Document.make(f"validation:{row}", text or ""))
    return docs, [train_meta, test_meta], dict(training_prefix=STORY_LIMIT, dev_hash_modulus=50)


def _abstract_id(value: str, submitted: str) -> tuple[str, str] | None:
    """Split by the source's creation timestamp, grouping all versions of a paper."""
    month = str(submitted)[:7]
    if not re.fullmatch(r"2024-0[1-6]", month):
        return None
    match = re.fullmatch(r"(?:arXiv:)?(\d{4}\.\d{5})(?:v[1-9]\d*)?", str(value).strip())
    if not match:
        raise ValueError(f"Unrecognized modern arXiv identifier {value!r} with submission date {submitted!r}")
    split = "train" if month <= "2024-04" else ("dev" if month == "2024-05" else "test")
    return match[1], split


def _abstract_documents(root: Path) -> tuple[dict, list, dict]:
    """Read both Common Pile shards, grouping versions of each base paper identifier."""
    docs = {"train": [], "dev": [], "test": []}
    seen_ids, sources = set(), []
    counts = Counter()
    for key in ("abstract_0", "abstract_1"):
        path, meta = _source(root, ABSTRACT_REPO, ABSTRACT_REVISION, key)
        sources.append(meta)
        with gzip.open(path, "rb") as stream:
            for line in stream:
                record = json.loads(line)
                counts["total_source_rows"] += 1
                parsed = _abstract_id(record["id"], record["created"])
                if parsed is None:
                    continue
                identifier, split = parsed
                if identifier in seen_ids:
                    counts["repeated_base_id"] += 1
                    continue
                seen_ids.add(identifier)
                submitted = str(record["created"])
                # arXiv assigns IDs at announcement; retain date-boundary disagreements for audit.
                if identifier[:4] != submitted[2:4] + submitted[5:7]:
                    counts["identifier_month_differs_from_created"] += 1
                docs[split].append(Document.make(identifier, record["text"] or "", submitted))
        _log(f"scanned {meta['file']}, {len(seen_ids):,} eligible paper IDs so far")
    return docs, sources, dict(counts)


def _tokenizer(stage: str, train: list[Document], root: Path, output: Path, sources: list) -> Tokenizer:
    """Only accepted training documents may fit the scratch BPE. Preserve the adapter tokenizer."""
    if stage == "abstracts":
        path, metadata = _source(root, PYTHIA_REPO, PYTHIA_REVISION, "pythia_tokenizer", "model")
        sources.append(metadata)
        shutil.copyfile(path, output)
        return Tokenizer.from_file(str(output))
    tokenizer = Tokenizer(models.BPE())
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(vocab_size=STORY_VOCAB, initial_alphabet=sorted(pre_tokenizers.ByteLevel.alphabet()),
                                  special_tokens=[EOS], show_progress=False)
    _log(f"fitting {STORY_VOCAB:,}-token byte BPE on {len(train):,} retained training documents")
    tokenizer.train_from_iterator((doc.text for doc in train), trainer=trainer, length=len(train))
    if tokenizer.get_vocab_size() != STORY_VOCAB:
        raise ValueError("Training text did not support the registered BPE vocabulary size")
    tokenizer.save(str(output))
    return tokenizer


def _write_line(stream, record: dict) -> None:
    """Use a stable machine-readable row for each document decision."""
    stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def _pack(directory: Path, splits: dict, tokenizer: Tokenizer, eos: int) -> dict:
    """Save little-endian IDs and byte-addressable membership records for reproducible slicing."""
    metadata = {}
    with (directory / "documents.jsonl").open("w", encoding="utf-8", newline="\n") as members:
        for split, documents in splits.items():
            path = directory / f"{split}.bin"
            offset = 0
            with path.open("wb") as stream:
                for block in batched(documents, 256):
                    encodings = tokenizer.encode_batch([doc.text for doc in block], add_special_tokens=False)
                    flat = []
                    for doc, encoding in zip(block, encodings, strict=True):
                        ids = encoding.ids
                        size = len(ids) + 1
                        member = dict(split=split, id=doc.source_id, sha256=doc.digest,
                                      start_token=offset, tokens=size)
                        if doc.submitted:
                            member["submitted"] = doc.submitted
                        _write_line(members, member)
                        flat.extend(ids)
                        flat.append(eos)
                        offset += size
                    np.asarray(flat, dtype="<u2").tofile(stream)
            metadata[split] = dict(documents=len(documents), tokens=offset, bytes=path.stat().st_size,
                                   sha256=_sha256(path))
            _log(f"packed {split}: {len(documents):,} documents, {offset:,} tokens")
    return metadata


def _existing(directory: Path) -> dict | None:
    """Only return a completed preparation if its byte-level evidence is still intact."""
    marker = directory / "manifest.json"
    if not marker.is_file():
        return None
    try:
        manifest = json.loads(marker.read_text(encoding="utf-8"))
        if manifest["format"] != FORMAT or manifest["stage"] != directory.name:
            return None
        for name in ("tokenizer.json", "train.bin", "dev.bin", "test.bin", "documents.jsonl", "rejections.jsonl"):
            path = directory / name
            if not path.is_file() or _sha256(path) != manifest["artifacts"][name]["sha256"]:
                return None
        return manifest
    except (KeyError, ValueError, TypeError):
        return None


def prepare(stage: str, root: Path) -> dict:
    """Create or verify an entire stage, publishing the manifest after all content checks pass."""
    if stage not in ("stories", "abstracts"):
        raise ValueError("stage must be 'stories' or 'abstracts'")
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    output = root / stage
    with FileLock(str(root / f".{stage}.prepare.lock")):
        existing = _existing(output)
        if existing is not None:
            return existing
        with TemporaryDirectory(dir=root, prefix=f".prepare-{stage}-") as directory:
            staged = Path(directory)
            load = _story_documents if stage == "stories" else _abstract_documents
            raw, sources, selection = load(root)
            splits, audit, rejected = clean_splits(raw, _log)
            if not all(splits.values()):
                raise ValueError(f"Empty split after {stage} corpus filtering: {audit}")
            with (staged / "rejections.jsonl").open("w", encoding="utf-8", newline="\n") as records:
                for item in rejected:
                    _write_line(records, item)
            tokenizer = _tokenizer(stage, splits["train"], root, staged / "tokenizer.json", sources)
            vocab = tokenizer.get_vocab(with_added_tokens=True)
            vocab_size = max(vocab.values()) + 1
            eos = tokenizer.token_to_id(EOS)
            if eos is None or vocab_size > 65536:
                raise ValueError("The tokenizer must have an EOS ID and fit in uint16")
            packed = _pack(staged, splits, tokenizer, eos)
            files = {f"{split}.bin": dict(bytes=values["bytes"], sha256=values["sha256"])
                     for split, values in packed.items()}
            for name in ("tokenizer.json", "documents.jsonl", "rejections.jsonl"):
                path = staged / name
                files[name] = dict(bytes=path.stat().st_size, sha256=_sha256(path))
            manifest = dict(format=FORMAT, stage=stage, sources=sources, selection=selection, audit=audit,
                            overlap=dict(words=5, jaccard_at_least="4/5", priority=["test", "dev", "train"],
                                         coverage="All retained cross-split document pairs at this threshold"),
                            dtype="<u2", packing="one appended EOS per document, no added BOS",
                            eos_id=eos, vocab_size=vocab_size, tokenizer_entries=len(vocab),
                            model_vocab_size=50304 if stage == "abstracts" else vocab_size,
                            token_counts={s: v["tokens"] for s, v in packed.items()},
                            splits=packed, artifacts=files)
            (staged / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                                  encoding="utf-8", newline="\n")
            output.mkdir(exist_ok=True)
            # Atomic per-file publication, with the manifest as the final commit marker.
            (output / "manifest.json").unlink(missing_ok=True)
            for name in (*files, "manifest.json"):
                os.replace(staged / name, output / name)
        return manifest
