import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RetroReportTests(unittest.TestCase):
    def test_aggregates_decision_events(self):
        records = [
            {"task_id": "T1", "event": "complexity_score", "to": "XS"},
            {"task_id": "T1", "event": "complexity_rescore", "from": "XS", "to": "S"},
            {"task_id": "T1", "event": "escalation_triggered"},
            {"task_id": "T1", "event": "allowlist_amended"},
            {
                "task_id": "T1",
                "event": "change_request_disposition",
                "actor": "dev",
                "reason": "requirement_gap",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "decisions.jsonl"
            path.write_text(
                "".join(json.dumps(record) + "\n" for record in records),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "retro_report.py"),
                    "--json",
                    str(path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )

        report = json.loads(result.stdout)
        self.assertEqual(1, report["tasks"])
        self.assertEqual(1, report["upward_rescores"])
        self.assertEqual(1, report["allowlist_amendments"])
        self.assertEqual(1, report["requirement_gap_change_requests"])
        self.assertEqual(1.0, report["escalation"]["rate"])

    def test_missing_inputs_return_usage_error(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "retro_report.py"), "missing"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)

    def test_accepts_explicit_runtime_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orca-runtime.jsonl"
            path.write_text(
                json.dumps({"task_id": "T2", "event": "complexity_score", "to": "S"}) + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "retro_report.py"),
                    "--json",
                    "--runtime-export",
                    str(path),
                    "missing-docs-directory",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        self.assertEqual(1, json.loads(result.stdout)["tasks"])


if __name__ == "__main__":
    unittest.main()
