import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QMK = ROOT / "qmk_firmware"


class DefinitionTests(unittest.TestCase):
    def setUp(self):
        self.version = (ROOT / "VERSION").read_text().strip()
        self.definition = json.loads((ROOT / f"via/keychron-v1-auto-os-v{self.version}.json").read_text())
        self.official = json.loads((ROOT / "data/keychron-v1-official-via.json").read_text())

    def test_custom_order_and_layout_match_official(self):
        self.assertEqual(self.definition["layouts"], self.official["layouts"])
        self.assertEqual(self.definition["matrix"], self.official["matrix"])
        for field in ("name", "shortName"):
            self.assertEqual([x[field] for x in self.definition["customKeycodes"]],
                             [x[field] for x in self.official["customKeycodes"]])

    def test_via_protocol13_custom_ids_match_firmware(self):
        # Reviewed VIA protocol-13 contract; provenance is in docs/architecture.md.
        base = 0x7E00
        qmk_header = (QMK / "quantum/keycodes.h").read_text()
        for index in range(11):
            qmk_id = int(re.search(rf"\bQK_KB_{index}\s*=\s*(0x[0-9A-F]+)", qmk_header)[1], 16)
            self.assertEqual(base + index, qmk_id)

    def test_version_and_lighting(self):
        major, minor, patch = map(int, self.version.split('.'))
        self.assertEqual(self.definition["firmwareVersion"], (major << 16) | (minor << 8) | patch)
        self.assertEqual(self.definition["keycodes"], ["qmk_rgb_matrix_keycodes"])
        controls = self.definition["menus"][0]["content"][0]["content"]
        options = next(c["options"] for c in controls if c.get("label") == "Effect")
        self.assertEqual([i for _, i in options], list(range(23)))
        config = (ROOT / "keyboards/keychron/v1/ansi_encoder/keymaps/auto_os/via_effects_check.h").read_text()
        for name, index in options:
            effect = name.split(". ", 1)[1]
            self.assertIn(f"RGB_MATRIX_{effect} == {index}", config)


if __name__ == "__main__":
    unittest.main()
