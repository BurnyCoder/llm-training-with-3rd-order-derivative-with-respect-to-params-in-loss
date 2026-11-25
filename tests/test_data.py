"""Offline corpus fixtures exercise the split and tokenizer logic through its public API."""

import gzip
import json
import random

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from tokenizers import Tokenizer

from thirdloss import data
from thirdloss.overlap import Document, ShingleIndex, clean_splits, content_hash, shingles


def test_exact_and_edited_documents_respect_split_priority():
    original = " ".join(f"w{i}" for i in range(75))
    changed = original.replace("w39", "revised")
    raw = {
        "test": [Document.make("t", original)],
        "dev": [Document.make("d", changed), Document.make("d2", "Development only.")],
        "train": [Document.make("a", " \t" + original.upper()), Document.make("b", changed),
                  Document.make("c", "Development   only."), Document.make("d", "Fresh words."),
                  Document.make("empty", " \t\n")],
    }
    clean, counts, rejected = clean_splits(raw, lambda _: None)
    assert [doc.source_id for doc in clean["train"]] == ["d"]
    assert [doc.source_id for doc in clean["dev"]] == ["d2"]
    assert counts["train"] == dict(input=5, kept=1, exact=2, cross_split_near=1, empty=1)
    assert [(row["source_id"], row["reference_split"]) for row in rejected if row["reason"] == "near"] == [
        ("d", "test"), ("b", "test")
    ]


def test_prefix_candidates_match_exhaustive_jaccard_including_boundary():
    # A short exact-threshold pair exercises integer rounding in both the length and prefix filters.
    prefix = "one two three four five six seven eight"
    docs = [Document.make("boundary", prefix + " nine")]
    assert ShingleIndex(docs).match(shingles(prefix)) == docs[0]
    generator = random.Random(1903)
    queries = []
    for i in range(24):
        words = [f"w{j}" for j in generator.sample(range(800), 85)]
        docs.append(Document.make(str(i), " ".join(words)))
        for edits in range(0, 7):
            probe = words.copy()
            for idx in generator.sample(range(len(words)), edits):
                probe[idx] = "changed"
            queries.append(shingles(" ".join(probe)))
    index = ShingleIndex(docs)
    references = [(doc, shingles(doc.text)) for doc in docs]
    for query in queries:
        brute = next((doc for doc, terms in references
                      if 5 * len(terms & query) >= 4 * len(terms | query)), None)
        assert index.match(query) == brute


def test_abstract_submission_month_and_base_id_grouping(monkeypatch, tmp_path):
    rows = [
        [("2312.12345", "2023-12-31", "old"), ("2405.00001v1", "2024-04-30", "April"),
         ("2405.00002", "2024-05-01", "May")],
        [("2405.00001v2", "2024-04-30", "same ID revised"), ("2407.00001", "2024-06-30", "June"),
         ("2407.00002", "2024-07-01", "July")],
    ]
    for i, batch in enumerate(rows):
        with gzip.open(tmp_path / str(i), "wt", encoding="utf-8") as writer:
            for identifier, submitted, text in batch:
                writer.write(json.dumps(dict(id=identifier, created=submitted, added="2025-01-01", text=text)) + "\n")
    def source(root, repo, revision, key):
        return tmp_path / key[-1], {"file": key}
    monkeypatch.setattr(data, "_source", source)
    docs, sources, audit = data._abstract_documents(tmp_path)
    assert {split: [doc.text for doc in entries] for split, entries in docs.items()} == {
        "train": ["April"], "dev": ["May"], "test": ["June"],
    }
    assert [doc.source_id for doc in docs["train"]] == ["2405.00001"]
    assert audit["repeated_base_id"] == 1
    assert audit["identifier_month_differs_from_created"] == 2
    assert len(sources) == 2


def test_prepare_from_parquet_proves_train_only_fit_packing_and_repair(monkeypatch, tmp_path):
    # Each document uses its own words. Both retained splits therefore survive the overlap audit.
    texts = []
    train_count = dev_count = 0
    while train_count < 30 or dev_count < 2:
        i = len(texts)
        text = " ".join(f"document{i}word{j}" for j in range(12))
        texts.append(text)
        if int(content_hash(text)[:16], 16) % 50:
            train_count += 1
        else:
            dev_count += 1
    heldout = " ".join(f"heldout{j}" for j in range(30))
    pq.write_table(pa.table({"text": texts}), tmp_path / "source-train.parquet")
    pq.write_table(pa.table({"text": [heldout]}), tmp_path / "source-test.parquet")
    def source(root, repo, revision, key):
        path = tmp_path / f"source-{key.split('_')[1]}.parquet"
        return path, {"file": path.name}
    monkeypatch.setattr(data, "_source", source)
    monkeypatch.setattr(data, "STORY_LIMIT", len(texts))
    monkeypatch.setattr(data, "STORY_VOCAB", 280)
    original = data._tokenizer
    observed = []
    def find_training_docs(stage, train, root, output, sources):
        observed.extend(doc.text for doc in train)
        return original(stage, train, root, output, sources)
    monkeypatch.setattr(data, "_tokenizer", find_training_docs)
    manifest = data.prepare("stories", tmp_path)
    assert set(observed) == {text for text in texts if int(content_hash(text)[:16], 16) % 50}
    assert manifest["vocab_size"] == 280
    folder = tmp_path / "stories"
    tokenizer = Tokenizer.from_file(str(folder / "tokenizer.json"))
    assert tokenizer.decode(tokenizer.encode("Hello, café 🦉").ids) == "Hello, café 🦉"
    streams = {s: np.fromfile(folder / f"{s}.bin", dtype="<u2") for s in ("train", "dev", "test")}
    for line in (folder / "documents.jsonl").read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        row = int(entry["id"].split(":")[1])
        text = heldout if entry["split"] == "test" else texts[row]
        start = entry["start_token"]
        end = start + entry["tokens"]
        expected = tokenizer.encode(text, add_special_tokens=False).ids + [manifest["eos_id"]]
        assert streams[entry["split"]][start:end].tolist() == expected
    assert data.prepare("stories", tmp_path) == manifest
    (folder / "test.bin").write_bytes(b"corrupt")
    repaired = data.prepare("stories", tmp_path)
    assert repaired["artifacts"]["test.bin"]["sha256"] == manifest["artifacts"]["test.bin"]["sha256"]
    assert repaired["token_counts"] == {s: len(ids) for s, ids in streams.items()}
