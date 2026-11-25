"""Use deliberately synthetic summaries to test the registered inference and visibility rules."""

import math

import pytest

from thirdloss.analysis import analyze_stage


METHODS = ("ce", "trace", "third")
STORY_TOKENS = 16_777_216


def complete_matrix():
    """Every registered seed has the same tiny improvement in this artificial fixture."""
    return [
        {
            "id": f"stories-{method}-{seed}", "stage": "stories", "phase": "confirm",
            "seed": seed, "method": method, "tokens": STORY_TOKENS,
            "test_nll": 1.0 if method == "third" else 1.5,
            "freeze_id": "fixture-matrix", "test_manifest_sha256": "fixture-test-corpus",
        }
        for seed in range(1, 9)
        for method in METHODS
    ]


def test_wins_require_both_registered_exact_sign_tests():
    """The two equally small p-values have the same adjusted p-value under step-down Holm."""
    result = analyze_stage(complete_matrix(), "stories")
    assert result["complete"] and result["success"]
    assert result["n_complete_seeds"] == 8
    for stats in result["comparisons"].values():
        assert [p["seed"] for p in stats["pairs"]] == list(range(1, 9))
        assert stats["wins"] == 8 and stats["ties"] == 0 and stats["losses"] == 0
        assert stats["median_delta"] == -0.5
        assert stats["median_ci"] == [-0.5, -0.5]
        assert stats["ci_coverage"] == 254 / 256
        assert stats["p_raw"] == 1 / 256
        assert stats["p_holm"] == 2 / 256


def test_second_comparator_failure_and_ties_count_separately():
    """Declaring a win against ordinary AdamW alone would violate the registered conjunction."""
    rows = complete_matrix()
    for row in rows:
        if row["method"] == "trace":
            row["test_nll"] = 1.0 if row["seed"] % 2 else 0.5
    result = analyze_stage(rows, "stories")
    assert result["complete"] and result["success"] is False
    trace = result["comparisons"]["trace"]
    assert trace["wins"] == 0 and trace["ties"] == 4 and trace["losses"] == 4
    assert trace["p_raw"] == 1
    assert result["comparisons"]["ce"]["p_holm"] == 2 / 256


def test_holm_step_down_tie_handling_and_exact_boundary():
    """Seven wins can pass the second Holm threshold once the first comparator passes."""
    rows = complete_matrix()
    for row in rows:
        if row["seed"] == 8 and row["method"] == "trace":
            row["test_nll"] = 0.5
    result = analyze_stage(rows, "stories")
    assert result["success"] is True
    assert result["comparisons"]["trace"]["p_holm"] == 9 / 256


def test_all_ties_are_reported_with_unit_p_value():
    """A zero number of discordant pairs supplies no direction for a sign test."""
    rows = complete_matrix()
    for row in rows:
        row["test_nll"] = 1.0
    result = analyze_stage(rows, "stories")
    assert result["success"] is False
    assert result["comparisons"]["ce"]["p_raw"] == 1
    assert result["comparisons"]["trace"]["ties"] == 8


@pytest.mark.parametrize("defect", ["missing", "no score", "duplicate", "unequal tokens",
                                   "all short", "wrong configured budget", "nonfinite",
                                   "mixed freeze", "mixed corpus"])
def test_partial_or_mismatched_results_never_unlock_primary_inference(defect):
    """In particular, identical truncated budgets cannot form a full-budget confirmation."""
    rows = complete_matrix()
    if defect == "missing":
        rows.pop()
    elif defect == "no score":
        rows[-1].pop("test_nll")
    elif defect == "duplicate":
        rows.append(dict(rows[-1], id="another-checkpoint-for-same-seed"))
    elif defect == "unequal tokens":
        rows[-1]["tokens"] -= 128
    elif defect == "all short":
        for row in rows:
            row["tokens"] //= 8
    elif defect == "wrong configured budget":
        rows[0]["target_tokens"] = STORY_TOKENS * 2
    elif defect == "nonfinite":
        rows[-1]["test_nll"] = math.nan
    elif defect == "mixed freeze":
        rows[-1]["freeze_id"] = "another-set"
    elif defect == "mixed corpus":
        rows[-1]["test_manifest_sha256"] = "another-corpus"
    result = analyze_stage(rows, "stories")
    assert result["success"] is None and not result["complete"]
    assert result["comparisons"] == {}
    assert result["status"] in {"invalid", "incomplete"}


def test_adverse_effect_reported_separately_from_uncertainty():
    """A strictly positive exact interval favors the comparison in the stated sign convention."""
    rows = complete_matrix()
    for row in rows:
        if row["method"] == "trace":
            row["test_nll"] = 0.25
    result = analyze_stage(rows, "stories")
    assert result["status"] == "adverse"
    assert result["comparisons"]["trace"]["interpretation"] == "adverse"


def test_exploratory_arms_and_other_stages_do_not_enter_paired_matrix():
    """Unrelated validation sweeps cannot increase the number of independent seeds."""
    rows = complete_matrix()
    extras = [
        dict(rows[0], phase="pilot", test_nll=0.1),
        dict(rows[0], stage="abstracts", tokens=524_288),
        dict(rows[0], method="hessian_norm", test_nll=0.1),
    ]
    assert analyze_stage(rows + extras, "stories") == analyze_stage(rows, "stories")
    assert analyze_stage([], "stories")["status"] == "pending"


def test_elapsed_time_uses_latest_actual_validation_before_shared_cutoff():
    """Faster methods can process more tokens within the common time allowance."""
    rows = complete_matrix()
    for row in rows:
        seconds = {"ce": 10.0, "trace": 15.0, "third": 20.0}[row["method"]]
        row.update(train_seconds=seconds, dev_nll=1.0)
        row["events"] = [
            {"train_seconds": 9.0, "tokens": 80, "dev_nll": 2.2},
            {"train_seconds": 5.0, "tokens": 48, "dev_nll": 2.8},
            {"train_seconds": 9.9, "tokens": 96, "loss": 1.8},  # training-only record
            {"train_seconds": 12.0, "tokens": 120, "dev_nll": 1.6},
        ]
    groups = analyze_stage(rows, "stories")["matched_time"]
    assert [g["seed"] for g in groups] == list(range(1, 9))
    first = groups[0]
    assert first["cutoff_seconds"] == 10.0
    assert first["by_method"]["ce"]["dev_nll"] == 1.0  # eligible final checkpoint
    assert first["by_method"]["trace"]["dev_nll"] == 2.2
    assert first["by_method"]["third"]["tokens"] == 80


def test_time_matched_comparison_uses_one_validation_population_across_methods():
    """Whole-split NLL cannot replace a fixed-window diagnostic in another run."""
    rows = complete_matrix()
    for row in rows:
        row.update(train_seconds=10.0, dev_nll=90.0)
        row["events"] = [{"train_seconds": 5.0, "tokens": 48, "dev_nll": 8.0}]
        if row["method"] == "ce":
            # The actual diagnostic at the final clock takes priority over a summary.
            row["matched_dev_nll"] = 3.0
            row["events"].append({"train_seconds": 10.0, "tokens": 96, "dev_nll": 2.0})
        elif row["method"] == "third":
            row["matched_dev_nll"] = 5.0
    by_method = analyze_stage(rows, "stories")["matched_time"][0]["by_method"]
    assert by_method["ce"]["dev_nll"] == 2.0
    assert by_method["ce"]["tokens"] == 96
    assert by_method["trace"]["dev_nll"] == 8.0
    assert by_method["trace"]["staleness_seconds"] == 5.0
    assert by_method["third"]["dev_nll"] == 5.0
