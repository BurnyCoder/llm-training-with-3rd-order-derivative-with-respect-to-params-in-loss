"""A completed corpus score, training run or verified geometry removes only its own remaining cost."""

import pytest


def test_remaining_primary_work_keeps_frozen_tests_after_training_and_removes_scored_tests():
    from thirdloss.remaining_work import primary_work
    arms=[{"stage":"stories","method":"third","projected_hours_all_seeds":16.,"projected_test_seconds_per_run":1800.}]
    runs=[{"stage":"stories","phase":"confirm","method":"third","seed":s,"tokens":2**24,"status":"complete"}
          for s in range(1,9)]
    runs[0]["test_nll"]=2.
    cost,unpublished=primary_work(arms,runs)
    assert cost==pytest.approx(3.5) and unpublished==7
    assert primary_work(arms,[])==(16.,16)


def test_adapter_forecast_prices_the_registered_gates_and_only_the_unfinished_runs():
    from thirdloss.remaining_work import adapter_gate_timing
    arms = [{"stage": "abstracts", "method": "third", "pilot_run": "selected"}]
    pilot = {"id": "selected", "stage": "abstracts", "method": "third", "phase": "pilot", "seed": 0,
             "status": "complete", "steps": 64, "tokens": 65536, "host_probe_seconds": 50.}
    complete = {**pilot, "id": "full", "phase": "confirm", "seed": 1, "steps": 512, "tokens": 524288,
                "host_probe_seconds": 1160.}
    row = adapter_gate_timing(arms, [pilot, complete])["third"]
    # The seed-zero pilot has five active updates. The full seed-one run has 58.
    assert row["pilot_calls"] == 5 and row["observed_calls"] == 63
    assert row["remaining_seeds"] == list(range(2, 9))
    assert row["remaining_calls"] == 459 and row["extrapolated_pilot_calls"] == 280
    expected = (459 * (1210 / 63) - 280 * 10) / 3600
    assert row["adjustment_hours"] == pytest.approx(expected)
