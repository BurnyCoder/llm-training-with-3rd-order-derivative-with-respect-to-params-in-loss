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
