"""Persist a portable verification record from pytest's machine-readable JUnit output."""

import subprocess
import sys
import xml.etree.ElementTree as ET

from .records import time_now, write_json


def verify(project):
    directory = project/"tmp"/"verification"
    directory.mkdir(parents=True,exist_ok=True)
    xml = directory/"pytest.xml"
    completed = subprocess.run([sys.executable,"-m","pytest","-q","--junitxml",str(xml)],cwd=project)
    records = []
    for case in ET.parse(xml).iter("testcase"):
        outcome = next((name for name in ("error","failure","skipped") if case.find(name) is not None),"passed")
        records.append({"test":f"{case.get('classname')}.{case.get('name')}",
                        "seconds":float(case.get("time","0")),"outcome":outcome})
    write_json(project/"results"/"verification"/"tests.json",{
        "checked_at":time_now(), "git_revision":subprocess.check_output(
            ["git","rev-parse","HEAD"],cwd=project,text=True).strip(),
        "exit_code":completed.returncode,"cases":records})
    if completed.returncode:
        raise SystemExit(completed.returncode)
