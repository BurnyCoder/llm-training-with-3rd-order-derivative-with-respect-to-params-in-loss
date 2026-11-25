"""Publish lightweight active-run updates while the durable collection keeps each completed run."""

import json
import threading
from contextlib import contextmanager

from filelock import FileLock, Timeout
from huggingface_hub import HfApi

from .hub_archive import STUDY_HUB
from .report_records import completed, read_json, study_snapshot


def live_snapshot(project,storage):
    """Include partial train-only calibration as well as recorded scores, targets and examples."""
    snapshot = study_snapshot(project)
    for run in snapshot["runs"]:
        if run.get("status")=="initializing":
            method = run.get("method")
            kinds = {"combined":("trace","third"),"sham":("third",)}.get(method,(method,))
            suffix = "-fp64" if run["stage"]=="abstracts" else ""
            for kind in kinds:
                path = storage/"calibration"/f"{run['stage']}-{kind}{suffix}-draws.json"
                draws = read_json(path).get("draws",[])
                if draws:
                    run["status"]=f"calibrating ({len(draws)}/16)"
                    run["calibration_progress"]={"draws_completed":len(draws),"last_draw":draws[-1]}
    return snapshot


def overlay(snapshot):
    """Send changing rows and the latest completions between static publications."""
    recent = {}
    for run in snapshot["runs"]:
        if completed(run):
            recent[run["stage"]] = max((run,recent.get(run["stage"],{})),
                                      key=lambda r:r.get("evaluated_at") or r.get("finished_at",""))
    active = [r for r in snapshot["runs"] if not completed(r) or "evaluation_progress" in r]
    rows = {r["id"]:r for r in (*recent.values(),*active)}
    return {"runs":list(rows.values()),"active":bool(active),"stages":snapshot["stages"],
            "pilot_comparisons":snapshot["pilot_comparisons"]}


@contextmanager
def publish_live(project,storage):
    """Telemetry retries separately from optimization, using the same lock as full releases."""
    stop = threading.Event()
    def update():
        api = HfApi()
        prior = None
        while not stop.is_set():
            try:
                with FileLock(str(project/".cache"/"publication.lock"),timeout=0):
                    snapshot = live_snapshot(project,storage)
                    changes = overlay(snapshot)
                    if changes!=prior:
                        body = json.dumps({**changes,"generated_at":snapshot["generated_at"]},
                                          separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
                        api.upload_file(repo_id=STUDY_HUB,path_in_repo="live.json",path_or_fileobj=body,
                                        commit_message="Update public training telemetry")
                        prior = changes
            except Timeout:
                pass
            except Exception as exc:
                print(f"Live Hub update will retry after {type(exc).__name__}",flush=True)
            stop.wait(120)
    (project/".cache").mkdir(exist_ok=True)
    thread = threading.Thread(target=update,name="Hub training metrics",daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=5)
