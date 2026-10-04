#!/usr/bin/env python3
"""Check the linked keymap bytes against the original VIA backup and migration."""

import hashlib
import json
import re
import struct
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QMK = ROOT / "qmk_firmware"
NAME = "keychron_v1_ansi_encoder_auto_os"
ELF = QMK / ".build" / f"{NAME}.elf"
RAW = QMK / ".build" / f"{NAME}.bin"
BIN = QMK / f"{NAME}.bin"
NM = shutil.which("arm-none-eabi-nm") or "/opt/homebrew/opt/arm-none-eabi-binutils/bin/arm-none-eabi-nm"


def main():
    baseline = json.loads((ROOT / "data/expected-keymap.json").read_text())
    keymap_bytes = bytes.fromhex(baseline["keymap_hex"])
    expected = struct.unpack(f">{len(keymap_bytes) // 2}H", keymap_bytes)
    encoder_expected = [v for pair in baseline["encoders_ccw_cw"] for v in pair]
    # VIA queries use CCW/CW, but QMK's flash array is CW/CCW.
    enc_header = (QMK / "quantum/encoder.h").read_text()
    assert "ENCODER_CCW_CW(ccw, cw) {(cw), (ccw)}" in enc_header
    encoder_flash = [v for i in range(0, len(encoder_expected), 2)
                     for v in (encoder_expected[i + 1], encoder_expected[i])]
    assert BIN.read_bytes() == RAW.read_bytes()
    subprocess.run(["dfu-suffix", "--check", str(BIN)], check=True, capture_output=True)
    raw = RAW.read_bytes()[:-16]
    symbols = subprocess.check_output([NM, "-S", str(ELF)], text=True)
    for function in ("process_record_user", "housekeeping_task_user", "process_detected_host_os_user", "via_command_kb"):
        assert re.search(rf"^[0-9a-f]+ [0-9a-f]+ T {function}$", symbols, re.M), function
    for symbol, values in [("keymaps", expected), ("encoder_map", encoder_flash)]:
        match = re.search(rf"^([0-9a-f]+) ([0-9a-f]+) \w {symbol}$", symbols, re.M)
        assert match, f"Missing {symbol}"
        offset, size = int(match[1], 16) - 0x08000000, int(match[2], 16)
        assert size == len(values) * 2
        assert raw[offset:offset + size] == struct.pack(f"<{len(values)}H", *values), symbol
    vector_sp, vector_reset = struct.unpack_from("<II", raw)
    assert 0x20000000 < vector_sp <= 0x20010000
    assert vector_reset & 1 and 0x08000000 <= (vector_reset & ~1) < 0x08000000 + len(raw)
    assert len(raw) < 256 * 1024 - 4096
    migrated = {
        "keymap_hex": struct.pack(f">{len(expected)}H", *expected).hex(),
        "encoders_ccw_cw": [encoder_expected[i:i + 2] for i in range(0, 8, 2)],
        "layers": 4, "rows": 6, "cols": 16,
    }
    (ROOT / "work/expected-migrated-keymap.json").write_text(json.dumps(migrated, indent=2) + "\n")
    print(f"PASS: all 384 matrix entries and 8 encoder entries match the reviewed baseline")
    print(f"PASS: STM32 vector table, {len(raw)}-byte payload, DFU suffix and memory bounds")
    print("PASS: linked custom-keycode, Siri timer, OS detection and diagnostic hooks")
    print(f"SHA256: {hashlib.sha256(BIN.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
