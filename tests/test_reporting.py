"""Check that the public progress views, paper and live feed share the same real records."""

import json

from pypdf import PdfReader

from thirdloss.reporting import build_report, study_snapshot


def test_examples_label_an_eligible_run_and_preserve_the_fixed_sample_order():
    from thirdloss.report_records import example_runs
    fields = {"stage":"abstracts","method":"third","status":"complete","samples":[{"continuation":"example"}]}
    rows = [{**fields,"id":key,"phase":phase} for key,phase in
            [("a-archived","diagnostic"),("c-later","pilot"),("b-corrected","pilot")]]
    assert [r["id"] for r in example_runs(rows)] == ["b-corrected"]


def test_snapshot_keeps_full_score_and_trace_semantics(tmp_path):
    """Distinguish raw derivative size, weighted training contribution and full validation."""
    run = tmp_path / "results" / "stories-pilot-s00-third-r03"
    run.mkdir(parents=True)
    config = {"stage": "stories", "phase": "pilot", "seed": 0, "method": "third", "token_budget": 4096}
    (run / "config.json").write_text(json.dumps(config), encoding="utf-8")
    event = {"step": 1, "tokens": 4096, "loss": 3.2, "penalty": 0.03, "dev_nll": 4.0,
             "derivatives": {"third": {"estimate": 7.0}}, "train_seconds": 1.0}
    (run / "events.jsonl").write_bytes(json.dumps(event).encode() + b'\n{"step":')
    (run / "summary.json").write_text('{"dev_nll":3.9,"status":"complete"}', encoding="utf-8")
    record = study_snapshot(tmp_path)["runs"][0]
    assert record["dev_nll"] == 3.9
    assert record["target_tokens"] == record["tokens"] == 4096
    assert record["events"][0]["raw_third"] == 7.0
    assert record["events"][0]["penalty"] == 0.03
    assert record["events_total"] == 1


def test_report_before_first_run_keeps_readme_and_emits_protocol_paper(tmp_path):
    """A fresh checkout supports an explicit, illustrated preregistration-only publication."""
    readme = tmp_path / "README.md"
    readme.write_text("# Intro\n\nRelated work.\n\n<!-- RESULTS:START -->\n"
                      "<!-- RESULTS:END -->\n\n## Reproduction\n", encoding="utf-8")
    study = build_report(tmp_path)
    assert not study["runs"]
    assert (tmp_path / "docs" / "figures" / "architecture.png").is_file()
    # The geometry examples have exact formulas and can be drawn before any training run.
    assert (tmp_path / "docs" / "figures" / "penalty-directions.png").is_file()
    assert not (tmp_path / "docs" / "figures" / "paired.png").exists()
    assert "Related work." in readme.read_text(encoding="utf-8")
    assert "## Reproduction" in readme.read_text(encoding="utf-8")
    assert "AI statement" not in readme.read_text(encoding="utf-8")
    reader = PdfReader(tmp_path / "reports" / "paper.pdf")
    text = " ".join(page.extract_text() for page in reader.pages)
    assert "AI statement" in text
    assert "Awaiting paired test results" in text
    assert "Libor" in text
