#!/usr/bin/env python3
"""Read auto_os diagnostics without modifying the keyboard."""

import json
import hid

devices = [d for d in hid.enumerate(0x3434, 0x0311)
           if d["usage_page"] == 0xFF60 and d["usage"] == 0x61]
if len(devices) != 1:
    raise SystemExit(f"Expected one Keychron V1; found {len(devices)}")
device = hid.Device(path=devices[0]["path"])
try:
    device.write(b"\0" + bytes([0x02, 0x80]).ljust(32, b"\0"))
    reply = bytes(device.read(32, timeout=2000))
finally:
    device.close()
if len(reply) != 32 or reply[:6] != b"\x02\x80AOS1":
    raise SystemExit("No auto_os v1 diagnostic response (old firmware or USB issue)")
names = ["unsure", "linux", "windows", "macos", "ios"]
print(json.dumps({
    "applied_os": names[reply[6]] if reply[6] < len(names) else reply[6],
    "default_layer": reply[7],
    "detection_reported": bool(reply[8]),
    "current_guess": names[reply[9]] if reply[9] < len(names) else reply[9],
    "uptime_ms": int.from_bytes(reply[10:14], "big"),
}, indent=2))
