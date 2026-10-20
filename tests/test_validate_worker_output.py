import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_worker_output", ROOT / "scripts" / "validate_worker_output.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def xs_report():
    return {
        "task_id": "T1",
        "role": "dev",
        "workflow_mode": "xs_self_check",
        "status": "complete",
        "criteria_status": {"AC-01": "satisfied — command: npm test"},
        "files_changed": ["src/todo.js"],
        "allowlist_violations": [],
        "evidence_levels": {"AC-01": "confirmed"},
        "open_questions": [],
        "recommended_next_action": "close as Dev self-revalidated",
        "self_revalidation": {
            "commands": [{"command": "npm test", "exit_code": 0}],
            "checks": ["diff matches allowlist", "AC-01 satisfied"],
            "result": "passed",
            "evidence": ["test/todo.test.js:12"],
        },
    }


class WorkerOutputTests(unittest.TestCase):
    def test_accepts_structured_xs_self_revalidation(self):
        problems = MODULE.validate(json.dumps(xs_report()), "dev")
        self.assertEqual([], problems)

    def test_rejects_xs_without_self_revalidation(self):
        report = xs_report()
        del report["self_revalidation"]
        problems = MODULE.validate(json.dumps(report), "dev")
        self.assertTrue(any("self_revalidation" in problem for problem in problems))

    def test_rejects_complete_xs_with_failing_command(self):
        report = xs_report()
        report["self_revalidation"]["commands"][0]["exit_code"] = 1
        problems = MODULE.validate(json.dumps(report), "dev")
        self.assertTrue(any("failing command" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
