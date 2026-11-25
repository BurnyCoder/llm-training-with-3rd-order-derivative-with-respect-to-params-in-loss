"""Durable run identities, atomic JSON/checkpoint writes, and timestamped experiment records."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

GITHUB = "https://github.com/BurnyCoder/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss-with-derivative-of-hessian"
PAGES = "https://burnycoder.github.io/"+GITHUB.rsplit("/",1)[1]+"/"

HORIZONS = {"stories": 2**24, "abstracts": 2**19}
BATCHES = {"stories": 32, "abstracts": 8}
METHODS = ("ce", "trace", "third", "hessian_norm", "sham", "combined")
RATIOS = (0.01, 0.03, 0.10)
CONTEXT = 128


def time_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def peak_process_mib():
    """OS process working-set high-water mark, including earlier activity in this interpreter."""
    if os.name=="nt":
        import psutil
        return psutil.Process().memory_info().peak_wset/2**20
    import resource
    import sys
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return usage/(2**20 if sys.platform=="darwin" else 1024)


def storage_root(project):
    load_dotenv(project / ".env")
    root = Path(os.environ.get("THIRDLOSS_STORAGE", "storage")).expanduser()
    return (project / root).resolve()


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    """Atomic replacement leaves the preceding durable version intact after interruption."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def json_lines(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


class Recorder:
    """Mirror every metric and complete generation to the terminal and a timestamped log."""

    def __init__(self, project, run_id):
        self.directory = project / "results" / run_id
        self.directory.mkdir(parents=True, exist_ok=True)
        logs = project / "logs"
        logs.mkdir(exist_ok=True)
        self.log = logs / f"{run_id}-{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}.jsonl"

    def emit(self, record, filename="events.jsonl"):
        row = {"timestamp": time_now(), **record}
        line = json.dumps(row, ensure_ascii=True, allow_nan=False)
        for path in (self.directory / filename, self.log):
            with path.open("a", encoding="utf-8") as stream:
                stream.write(line + "\n")
        print(line, flush=True)


def run_name(stage, method, phase, seed, ratio):
    # Preserve the original FP32 adapter pilot under its published ID. Amended derivative
    # runs have distinct records, weights, RNG checkpoints and calibrated coefficients.
    suffix = "-fp64" if stage=="abstracts" and method in METHODS and method!="ce" else ""
    return f"{stage}-{phase}-s{seed:02d}-{method}-r{round(ratio * 100):02d}{suffix}"


def setup_device(requested):
    """Enable CUDA when available and keep the parameter differentiation path in FP32."""
    import torch
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("The requested CUDA device is unavailable in this PyTorch installation")
    if device.type == "cuda":
        torch.set_float32_matmul_precision("highest")
    return device
