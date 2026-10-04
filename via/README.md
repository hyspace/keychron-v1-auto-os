# VIA definition for Auto OS 1.1.1

Use `keychron-v1-auto-os-v1.1.1.json` with the matching custom firmware, not the
original factory firmware. This is a **VIA v3 definition**, not a saved keymap.
Version 1.1.1 selects the Windows base layer for Linux as well. The previous
1.1.0 definition remains available for keyboards still running that version.

After flashing and verifying the keyboard:

1. Open https://usevia.app/ in a WebHID-capable browser, such as Chrome or Edge.
2. Enable **Show Design tab** in VIA settings. In Design, turn **Use V2
   definitions** off if it is present, then load this JSON.
3. Connect/authorize the Keychron V1. Confirm the definition name includes
   **Auto OS 1.1.1**. This file is local, not submitted to VIA's public database.
4. The **Custom** section contains all 11 original Keychron items in their
   original order. Lighting keys use the current QMK RGB Matrix keycode group.

| Index | New ID | Custom item | Host sequence |
| --- | --- | --- | --- |
| 0 | 0x7E00 | Mission Control | Mission Control consumer usage |
| 1 | 0x7E01 | Launch Pad | Launchpad consumer usage |
| 2 | 0x7E02 | Left Option | Left Alt |
| 3 | 0x7E03 | Right Option | Right Alt |
| 4 | 0x7E04 | Left Cmd | Left GUI |
| 5 | 0x7E05 | Right Cmd | Right GUI |
| 6 | 0x7E06 | Siri | Command+Space for 500 ms |
| 7 | 0x7E07 | Task View | Win+Tab |
| 8 | 0x7E08 | File Explorer | Win+E |
| 9 | 0x7E09 | Screen Shot | Shift+Command+4 |
| 10 | 0x7E0A | Cortana | Win+C |

These reproduce Keychron's HID sequences. They cannot guarantee a particular OS
feature still exists or has the matching shortcut configured. In particular,
Siri needs the matching macOS shortcut; Launchpad and Win+C behavior vary with
OS version. The mapping does not automatically repurpose these named Custom
keys for a different OS; automatic selection chooses the Mac/Windows base layer.

Do not import the original raw VIA backup directly. It uses old `0x7F00` custom
IDs and old RGB IDs. The new firmware uses standard QMK `QK_KB_0..10` IDs so modern
VIA's `CUSTOM(0)..CUSTOM(10)` matches. Legacy IDs are converted in the build
script, not intercepted at runtime (they now overlap QMK's user keycode range).
All current user mappings are already included in the compiled defaults.

The RGB menu is generated from the target's enabled effects and QMK effect
ordering. Compile-time assertions check every ID and the firmware version.
The official VIA reader validates the definition, including all 82 matrix
positions. Browser connection, GUI remapping and physical key behavior still
require a post-flash test.
