"""Persist a portable verification record from pytest's machine-readable JUnit output."""

import subprocess
import sys
import xml.etree.ElementTree as ET

from .records import json_lines, read_json, time_now, write_json


def verify(project):
    directory = project/"tmp"/"verification"
    directory.mkdir(parents=True,exist_ok=True)
    xml = directory/"pytest.xml"
    completed = subprocess.run([sys.executable,"-m","pytest","-q","--junitxml",str(xml)],cwd=project)
    records = []
    for case in ET.parse(xml).iter("testcase"):
        outcome = next((name for name in ("error","failure","skipped") if case.find(name) is not None),"passed")
        row = {"test":f"{case.get('classname')}.{case.get('name')}",
               "seconds":float(case.get("time","0")),"outcome":outcome}
        properties = {p.get("name"):p.get("value") for p in case.findall("./properties/property")}
        if properties:
            row["measurements"] = properties
        records.append(row)
    write_json(project/"results"/"verification"/"tests.json",{
        "checked_at":time_now(), "git_revision":subprocess.check_output(
            ["git","rev-parse","HEAD"],cwd=project,text=True).strip(),
        "exit_code":completed.returncode,"cases":records})
    if completed.returncode:
        raise SystemExit(completed.returncode)


def audit_restart(project,run_id):
    """Compare the last two training attempts using the unabridged per-attempt logs."""
    from pathlib import Path
    if Path(run_id).name!=run_id or not (project/"results"/run_id/"config.json").is_file():
        raise ValueError("Select an existing training run ID")
    attempts=[]
    for path in sorted((project/"logs").glob(run_id+"-*.jsonl")):
        rows=[r for r in json_lines(path) if "step" in r and "loss" in r]
        if rows:
            attempts.append((path,rows))
    if len(attempts)<2:
        raise ValueError("Two training attempts with recorded optimizer updates are required")
    (previous,old),(resumed,new)=attempts[-2:]
    first=new[0]
    canonical=json_lines(project/"results"/run_id/"events.jsonl")
    prefix=[r for r in canonical if "step" in r and r["timestamp"]<first["timestamp"]]
    checkpoint=max((r["step"] for r in prefix),default=0)
    old_by_step={r["step"]:r for r in old if r["step"]>checkpoint}
    fields=("loss","accuracy","lr","gradient_norm","trace_lambda","third_lambda","curvature_q","curvature_rms")
    def estimates(row):
        return {k:v["estimate"] for k,v in row.get("derivatives",{}).items()}
    overlap=[]
    for row in new:
        if row["step"] in old_by_step:
            original=old_by_step[row["step"]]
            overlap.append({"step":row["step"],"same_measurements":all(original.get(k)==row.get(k) for k in fields)
                            and estimates(row)==estimates(original),
                            "absolute_loss_delta":abs(original["loss"]-row["loss"]),
                            "absolute_gradient_norm_delta":abs(original["gradient_norm"]-row["gradient_norm"])})
    if not overlap:
        raise ValueError("The two recorded attempts have no overlapping optimizer measurements")
    directory=project/"results"/"verification"
    path=directory/(run_id+"-"+resumed.stem.rsplit("-",1)[-1]+"-system-restart.json")
    for candidate in directory.glob("*-system-restart.json"):
        prior=read_json(candidate)
        if prior["run"]==run_id and prior["resume_observed_at"]==first["timestamp"]:
            path=candidate
            break
    result={"run":run_id,"verified_at":time_now(),"resume_checkpoint_step":checkpoint,
            "last_observed_pre_restart_step":old[-1]["step"],"first_observed_restart_step":first["step"],
            "resume_observed_at":first["timestamp"],"advanced_past_prior_run":new[-1]["step"]>old[-1]["step"],
            "replayed_steps":old[-1]["step"]-checkpoint,"last_pre_restart_timestamp":old[-1]["timestamp"],
            "telemetry_fields":[*fields,"raw_penalty_estimates"],"logged_replay_observations":overlap,
            "previous_log":previous.name,"resumed_log":resumed.name}
    write_json(path,result)
    return result
