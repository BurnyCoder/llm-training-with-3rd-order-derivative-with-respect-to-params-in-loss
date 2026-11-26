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
