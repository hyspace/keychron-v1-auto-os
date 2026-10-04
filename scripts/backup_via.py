#!/usr/bin/env python3
"""Back up V1 VIA data using read-only protocol commands, without keystroke capture."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import hid


READ_COMMANDS = {0x01, 0x02, 0x04, 0x0C, 0x0D, 0x0E, 0x11, 0x12, 0x14}


class ViaReader:
    def __init__(self):
        devices = [
            d for d in hid.enumerate(0x3434, 0x0311)
            if d["usage_page"] == 0xFF60 and d["usage"] == 0x61
        ]
        if len(devices) != 1:
            raise RuntimeError(f"Expected exactly one V1 Raw HID device; found {len(devices)}")
        self.info = devices[0]
        self.device = hid.Device(path=self.info["path"])

    def request(self, command, *args):
        if command not in READ_COMMANDS or (command == 0x02 and args[0] not in (0x02, 0x04, 0x06)):
            raise ValueError("Only configuration read requests are allowed")
        packet = bytes([command, *args]).ljust(32, b"\0")
        if len(packet) != 32:
            raise ValueError("Invalid packet size")
        self.device.write(b"\0" + packet)
        response = bytes(self.device.read(32, timeout=2000))
        if len(response) != 32 or response[0] != command:
            raise RuntimeError(f"Unsupported command or invalid reply: {command:#04x}")
        return response

    def optional(self, command, *args):
        try:
            return self.request(command, *args)
        except RuntimeError:
            return None

    def buffer(self, command, size):
        result = bytearray()
        for offset in range(0, size, 28):
            count = min(28, size - offset)
            reply = self.request(command, offset >> 8, offset & 255, count)
            if reply[1:4] != bytes([offset >> 8, offset & 255, count]):
                raise RuntimeError("Buffer response does not match request")
            result.extend(reply[4:4 + count])
        return bytes(result)

    def snapshot(self):
        protocol = int.from_bytes(self.request(0x01)[1:3], "big")
        layers = self.request(0x11)[1]
        if not 1 <= layers <= 16:
            raise RuntimeError(f"Unexpected layer count: {layers}")
        rows, cols = 6, 16
        keymap = self.buffer(0x12, layers * rows * cols * 2)
        macro_count = self.request(0x0C)[1]
        macro_size = int.from_bytes(self.request(0x0D)[1:3], "big")
        if macro_size > 16384:
            raise RuntimeError(f"Unexpected macro buffer size: {macro_size}")
        macros = self.buffer(0x0E, macro_size)
        encoders = []
        for layer in range(layers):
            directions = []
            for clockwise in (0, 1):
                reply = self.optional(0x14, layer, 0, clockwise)
                directions.append(int.from_bytes(reply[4:6], "big") if reply else None)
            encoders.append(directions)
        layout = self.request(0x02, 0x02)
        firmware = self.optional(0x02, 0x04)
        keycodes = self.optional(0x02, 0x06)
        return {
            "format": "keychron-v1-via-raw-backup-v1",
            "vid": "0x3434", "pid": "0x0311",
            "usb_release": self.info["release_number"],
            "via_protocol": protocol,
            "via_firmware_version": int.from_bytes(firmware[2:6], "big") if firmware else None,
            "keycodes_version": int.from_bytes(keycodes[2:6], "big") if keycodes else None,
            "layers": layers, "rows": rows, "cols": cols,
            "layout_options": int.from_bytes(layout[2:6], "big"),
            "keymap_hex": keymap.hex(),
            "keymap_sha256": hashlib.sha256(keymap).hexdigest(),
            "encoders_ccw_cw": encoders,
            "macro_count": macro_count,
            "macro_buffer_hex": macros.hex(),
            "macro_buffer_sha256": hashlib.sha256(macros).hexdigest(),
            "notes": [
                "Two identical reads verified before saving.",
                "Not a VIA UI export or a full firmware/EEPROM dump.",
                "Translate legacy keycodes before restoring into newer QMK.",
                "Contains macro contents; keep private. RGB settings are not included.",
            ],
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    reader = ViaReader()
    try:
        first = reader.snapshot()
        second = reader.snapshot()
        if first != second:
            raise RuntimeError("Configuration changed between reads; backup aborted")
    finally:
        reader.device.close()
    first["captured_at_utc"] = datetime.now(timezone.utc).isoformat()
    with args.output.open("x") as stream:
        json.dump(first, stream, indent=2)
        stream.write("\n")
    args.output.chmod(0o600)
    print(f"Verified backup: {args.output}")
    print(f"VIA protocol {first['via_protocol']}; {first['layers']} layers; "
          f"{first['macro_count']} macros; two reads match")


if __name__ == "__main__":
    main()
