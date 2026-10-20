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

    def test_process_cost_from_orca_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(orca_snapshot()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "retro_report.py"),
                    "--json",
                    "--orca-json",
                    str(path),
                    "missing-docs-directory",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        cost = json.loads(result.stdout)["process_cost"]
        xs = cost["by_mode"]["xs_self_check"]
        self.assertEqual(2.0, xs["dispatches_per_run"])
        self.assertEqual(0, xs["repeat_dispatches"])
        self.assertEqual(1, xs["ceremony_dispatches"])
        self.assertEqual(0, xs["inferred_dispatches"])
        standard = cost["by_mode"]["standard"]
        self.assertEqual(4, standard["inferred_dispatches"])
        self.assertEqual(1, standard["repeat_dispatches"])
        self.assertEqual(0, standard["ceremony_dispatches"])
        self.assertEqual(1, cost["reasons"]["retry_unclassified"])
        self.assertTrue(any(flag.startswith("xs_self_check") for flag in cost["flags"]))


def dispatch(dispatch_id, task_id, start, end, comment=None, retry_of=None):
    start_options = {"launch": {"effective": {"model": "gpt-5.6-luna"}}}
    if comment:
        start_options["comment"] = comment
    return {
        "dispatch": {
            "id": dispatch_id,
            "taskId": task_id,
            "dispatchedAt": start,
            "completedAt": end,
            "retryOfDispatchId": retry_of,
            "failureCount": 0,
        },
        "worker": {"dispatchId": dispatch_id, "startOptions": start_options},
    }


def task(task_id, title, spec, result=""):
    return {"id": task_id, "task_title": title, "spec": spec, "result": result}


def orca_snapshot():
    tagged_run = {
        "run": {"id": "run_xs", "created_at": "2026-10-20 03:25:10"},
        "tasks": [
            task("t1", "Gantt filters", "You are the Dev worker."),
            task(
                "t2",
                "Gantt filters again",
                "orca-tag role=dev band=XS mode=xs_self_check reason=report_correction\n"
                "You are the Dev worker.",
            ),
        ],
        "dispatches": [
            dispatch(
                "d1", "t1", "2026-10-20 03:25:32", "2026-10-20T03:27:36Z",
                comment="orca-tag role=dev band=XS mode=xs_self_check reason=initial",
            ),
            dispatch("d2", "t2", "2026-10-20 03:29:47", "2026-10-20T03:31:07Z", retry_of="d1"),
        ],
    }
    untagged_run = {
        "run": {"id": "run_std", "created_at": "2026-10-20 01:56:22"},
        "tasks": [
            task("b1", "BA: login requirement", "mode standard · band M"),
            task("v1", "Dev: login UI", "mode standard · band M"),
            task("q1", "QC: verify login", "mode standard · band M"),
            task("q2", "QC retry: verify login", "mode standard · band M"),
        ],
        "dispatches": [
            dispatch("e1", "b1", "2026-10-20 01:56:46", "2026-10-20T01:59:23Z"),
            dispatch("e2", "v1", "2026-10-20 01:59:57", "2026-10-20T02:03:44Z"),
            dispatch("e3", "q1", "2026-10-20 02:04:19", "2026-10-20T02:13:11Z"),
            dispatch(
                "e4", "q1", "2026-10-20 02:14:10", "2026-10-20T02:25:53Z",
                retry_of="e3",
            ),
        ],
    }
    return {"source": "orca", "runs": [tagged_run, untagged_run]}


if __name__ == "__main__":
    unittest.main()
