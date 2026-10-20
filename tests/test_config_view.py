import subprocess
import sys
import unittest
from pathlib import Path

import yaml


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


class DocumentationEconomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load(
            (ROOT / "references" / "agents-models.yaml").read_text(encoding="utf-8")
        )

    def test_docs_scale_by_band(self):
        documentation = self.config["documentation"]
        files = documentation["files_by_band"]
        self.assertEqual([], files["XS"])
        self.assertEqual(["summary.md"], files["S"])
        self.assertEqual(["summary.md"], files["M"])
        self.assertEqual(["summary.md"], files["L"])
        self.assertEqual(["summary.md"], files["XL"])
        self.assertTrue(
            documentation["folder_naming"][
                "evaluate_only_when_band_requires_durable_documentation"
            ]
        )
        self.assertFalse(documentation["supplemental_artifacts"]["create_automatically"])
        summary = documentation["summary"]
        self.assertIn("what_changed", summary["required_sections"])
        self.assertIn("verification", summary["required_sections"])
        self.assertIn("process_narrative", summary["exclude"])

    def test_runtime_artifacts_are_forbidden_in_repo(self):
        runtime = self.config["orchestration"]["runtime_artifacts"]
        self.assertEqual("forbidden", runtime["persist_inside_project_repository"])
        self.assertIn("**/dispatch.json", runtime["forbidden_repo_artifacts"])

    def test_decision_log_excludes_normal_events(self):
        decision_log = self.config["documentation"]["decision_log"]
        self.assertEqual("orca_runtime", decision_log["storage"])
        excluded = decision_log[
            "never_record_as_durable_decisions"
        ]
        self.assertIn("ordinary_classification", excluded)
        self.assertIn("dispatch_started", excluded)


if __name__ == "__main__":
    unittest.main()
