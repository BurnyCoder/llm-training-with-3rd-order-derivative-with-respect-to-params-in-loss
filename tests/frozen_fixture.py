"""Construct a fixed synthetic preregistered matrix independently of the records under test."""

import hashlib
import json

from thirdloss.analysis import analyze_stage
from thirdloss.records import HORIZONS, run_name


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def inputs(stage):
    corpus = {"stage": stage, "splits": {"test": {"sha256": digest(stage), "tokens": 129}}}
    ratios = {"trace": .01, "third": .01}
    ids = [run_name(stage, method, "confirm", seed, ratios.get(method, 0))
           for seed in range(1, 9) for method in ("ce", "trace", "third")]
    seal = {"stage": stage, "ratios": ratios, "test_sha256": digest(stage),
            "runs": {key: digest(key) for key in ids},
            "initializations": {str(seed): digest(str(seed)) for seed in range(1, 9)}}
    seal["freeze_id"] = digest(json.dumps(seal, sort_keys=True))
    return seal, corpus


def bind(row):
    stage, seed, method = row["stage"], row["seed"], row["method"]
    seal, corpus = inputs(stage)
    ratio = seal["ratios"].get(method, 0)
    name = run_name(stage, method, "confirm", seed, ratio)
    return {**row, "id": name, "ratio": ratio, "status": "complete", "token_budget": HORIZONS[stage],
            "weights_sha256": seal["runs"][name], "initial_trainable_sha256": seal["initializations"][str(seed)],
            "data_manifest_sha256": digest(json.dumps(corpus, indent=2, sort_keys=True) + "\n"),
            "test_tokens": 128, "freeze_id": seal["freeze_id"], "test_manifest_sha256": seal["test_sha256"]}


def analyze(rows, stage):
    seal, corpus = inputs(stage)
    return analyze_stage(rows, stage, freeze=seal, dataset=corpus)
