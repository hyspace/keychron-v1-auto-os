#!/usr/bin/env python3
"""Fetch only the locked QMK revision; never reset or overwrite an existing checkout."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "data/upstream.lock.json").read_text())
dest = ROOT / "qmk_firmware"
if not dest.exists():
    subprocess.run(["git", "clone", "--depth", "1", "--branch", lock["tag"], lock["repository"], str(dest)], check=True)
actual = subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"], text=True).strip()
if actual != lock["commit"]:
    raise SystemExit(f"QMK checkout is {actual}, expected {lock['commit']}. Resolve manually; no reset performed.")
subprocess.run(["git", "-C", str(dest), "submodule", "update", "--init", "--depth", "1", *lock["submodules"]], check=True)
print(f"QMK {lock['tag']} verified at {actual}")
