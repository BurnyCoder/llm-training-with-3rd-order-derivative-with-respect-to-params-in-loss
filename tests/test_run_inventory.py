"""Reconcile the declared training schedule, reported evidence and live activities."""

from thirdloss.records import HORIZONS, run_name
from thirdloss.report_records import study_snapshot


def test_inventory_distinguishes_full_training_development_and_frozen_test(tmp_path):
    from thirdloss.run_inventory import inventory
    study = study_snapshot(tmp_path)
    for stage in HORIZONS:
        study["context"][stage]["selection"] = {"ratios": {"trace": .01, "third": .01}}
    run = run_name("abstracts", "ce", "confirm", 2, 0)
    row = {"id": run, "stage": "abstracts", "phase": "confirm", "method": "ce", "seed": 2, "ratio": 0.,
           "tokens": HORIZONS["abstracts"], "status": "scoring development", "evaluation_progress": {
               "split": "dev", "targets_scored": 37, "targets_to_score": 101}}
    study["runs"] = [row]
    plan = inventory(study)
    item = next(job for job in plan["fits"] if job["id"] == run)
    assert item["fit"] == "Scoring development" and item["test"] == "Awaiting freeze"
    assert "37/101" in plan["activity"][0]
    assert len(plan["fits"]) == 128 and plan["total"] == 304 and plan["done"] == 0
    row.update(status="complete", dev_nll=3.0, flatness={}, score_flatness={})
    row["evaluation_progress"] = {"split": "test", "targets_scored": 10, "targets_to_score": 27}
    study["frozen_stages"] = ["abstracts"]
    plan = inventory(study)
    item = next(job for job in plan["fits"] if job["id"] == run)
    assert item["fit"] == "Complete" and item["test"] == "Scoring test" and item["geometry"] == "Complete"
    assert plan["done"] == 2 and "10/27" in plan["activity"][0]
    row.pop("evaluation_progress")
    row.update(test_nll=3.1)
    study["runs"].append({**row, "id": "early-fp32", "phase": "diagnostic", "method": "third"})
    plan = inventory(study)
    assert plan["done"] == 4 and plan["total"] == 305
    assert sum(job["phase"] == "diagnostic" for job in plan["fits"]) == 1
    assert not plan["activity"]


def test_queue_keeps_unknown_strength_explicit_and_defers_the_cyclic_replay(tmp_path):
    from thirdloss.run_inventory import inventory
    study = study_snapshot(tmp_path)
    plan = inventory(study)
    assert plan["next"] == "TinyStories · Third derivative · pilot seed 0 (3%)"
    unselected = next(j for j in plan["fits"] if j["stage"] == "abstracts" and j["phase"] == "confirm"
                      and j["method"] == "third" and j["seed"] == 1)
    assert unselected["id"] is None and unselected["ratio"] is None
    hybrid = [j for j in plan["fits"] if j["phase"] == "hybrid"]
    assert (hybrid[-1]["seed"], hybrid[-1]["method"]) == (21, "replay")


def test_standalone_status_reads_the_sealed_final_analysis(tmp_path):
    """A fresh progress process recognizes the same final milestone as the published report."""
    from thirdloss.records import write_json
    from thirdloss.run_inventory import inventory

    root = tmp_path / "results"
    write_json(root / "analysis" / "seed-sensitivity.json", {"sealed_at": "final", "rows": []})
    assert not inventory(study_snapshot(tmp_path))["final"]
    write_json(root / "freeze" / "seed-sensitivity.json", {"sealed_at": "final"})
    assert inventory(study_snapshot(tmp_path))["final"]


def test_pause_uses_durable_progress_and_leaves_the_queue_idle(tmp_path):
    """Uncommitted log entries remain available in the raw interrupted attempt."""
    from thirdloss.live_hub import overlay
    from thirdloss.records import write_json
    from thirdloss.run_inventory import inventory

    run = run_name("stories", "third", "pilot", 0, .03)
    folder = tmp_path / "results" / run
    write_json(folder / "config.json", {"stage": "stories", "method": "third", "phase": "pilot", "seed": 0, "ratio": .03})
    write_json(folder / "state.json", {"status": "paused", "checkpoint_step": 2})
    (folder / "events.jsonl").write_text('{"step":2,"tokens":4}\n{"step":3,"tokens":6}\n', encoding="utf-8")
    study = study_snapshot(tmp_path)
    row = study["runs"][0]
    assert (row["status"], row["steps"], row["tokens"]) == ("paused", 2, 4)
    plan = inventory(study)
    assert plan["paused"] and not plan["activity"] and run == plan["fits"][0]["id"]
    assert "Third derivative" in plan["next"] and plan["done"] == 0
    update = overlay(study)
    assert not update["active"] and update["runs"][0]["status"] == "paused"
