#!/usr/bin/env python3
"""Package a verified build with provenance, excluding private device backups."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
version = (ROOT / "VERSION").read_text().strip()
dest = ROOT / "dist" / f"auto-os-{version}"
dest.mkdir(parents=True, exist_ok=True)
subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/check_upstream.py")], check=True)
subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/verify_firmware.py")], check=True)
files = [ROOT / "qmk_firmware/keychron_v1_ansi_encoder_auto_os.bin",
         ROOT / f"via/keychron-v1-auto-os-v{version}.json"]
for file in files:
    shutil.copy2(file, dest / file.name)


def capture(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


manifest = {
    "version": version,
    "source_commit": capture(["git", "rev-parse", "HEAD"]),
    "source_dirty": bool(capture(["git", "status", "--porcelain"])),
    "upstream": json.loads((ROOT / "data/upstream.lock.json").read_text()),
    "compiler": capture(["arm-none-eabi-gcc", "--version"]).splitlines()[0],
    "target": "keychron/v1/ansi_encoder:auto_os",
    "hardware_tested_this_build": False,
    "files": {file.name: {"bytes": file.stat().st_size,
                          "sha256": hashlib.sha256(file.read_bytes()).hexdigest()} for file in files},
}
(dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(f"Packaged {dest}; hardware-test status is intentionally false until tested")
