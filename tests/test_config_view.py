import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ConfigViewTests(unittest.TestCase):
    def test_dev_view_is_smaller_and_role_scoped(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "config_view.py"), "--role", "dev"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("# --- agents.dev ---", result.stdout)
        self.assertIn("# --- workflow_modes.xs_self_check ---", result.stdout)
        self.assertNotIn("# --- agents.lead ---", result.stdout)
        self.assertLess(
            len(result.stdout),
            len((ROOT / "references" / "agents-models.yaml").read_text(encoding="utf-8")),
        )

    def test_unknown_path_fails(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "config_view.py"), "--path", "missing.path"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("path not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
