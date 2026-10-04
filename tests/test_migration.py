import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("generate_keymap", ROOT / "scripts/generate_keymap.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MigrationTests(unittest.TestCase):
    def test_basic_keycodes_unchanged(self):
        for value in range(256):
            self.assertEqual(int(module.translate(value), 16), value)

    def test_vendor_codes(self):
        expected_codes = ["KCH_MISSION_CONTROL", "KCH_LAUNCHPAD", "KCH_LEFT_OPTION",
                          "KCH_RIGHT_OPTION", "KCH_LEFT_COMMAND", "KCH_RIGHT_COMMAND",
                          "KCH_SIRI", "KCH_TASK_VIEW", "KCH_FILE_EXPLORER",
                          "KCH_SCREENSHOT", "KCH_CORTANA"]
        for value, expected in enumerate(expected_codes, start=0x7F00):
            self.assertEqual(module.translate(value), expected)

    def test_unknown_code_fails_closed(self):
        with self.assertRaises(ValueError):
            module.translate(0x7F0B)

    def test_every_backed_up_key_and_encoder_is_supported(self):
        backup = json.loads(module.BACKUP.read_text())
        data = bytes.fromhex(backup["keymap_hex"])
        self.assertEqual(len(data), 768)
        for i in range(0, len(data), 2):
            module.translate(int.from_bytes(data[i:i + 2], "big"))
        for ccw, cw in backup["encoders_ccw_cw"]:
            module.translate(ccw)
            module.translate(cw)


if __name__ == "__main__":
    unittest.main()
