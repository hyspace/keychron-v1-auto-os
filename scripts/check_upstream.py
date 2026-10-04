#!/usr/bin/env python3
"""Fail before building if QMK or one of its initialized submodules was changed."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "data/upstream.lock.json").read_text())


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT / "qmk_firmware"), *args], text=True).strip()


assert git("rev-parse", "HEAD") == lock["commit"], "QMK does not match upstream.lock.json"
assert not git("status", "--porcelain"), "QMK checkout is dirty; keep custom work in external userspace"
for entry in git("submodule", "status", *lock["submodules"]).splitlines():
    # strip() removes the first line's normal leading space, not '-' or '+'.
    assert entry[0] not in "-+U", f"Submodule not pinned/initialized: {entry}"
print(f"PASS: clean QMK {lock['tag']} and pinned build submodules")
