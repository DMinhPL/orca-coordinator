#!/usr/bin/env python3
"""Machine acceptance gate for Dev and QC worker_done payloads.

The validator checks the structured return envelope from runtime. It raises the
reporting floor; it does not require a durable role report, prove implementation
correctness, or replace QC.

Usage:
    Get-Content runtime-copy.json | python scripts/validate_worker_output.py --role dev -
    python scripts/validate_worker_output.py --role dev runtime-copy.json
    python scripts/validate_worker_output.py --role qc runtime-copy.json

Exit codes: 0 = valid, 1 = invalid report, 2 = usage/read error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


COMMON_FIELDS: dict[str, type] = {
    "task_id": str,
    "role": str,
    "workflow_mode": str,
    "status": str,
    "criteria_status": dict,
    "files_changed": list,
    "allowlist_violations": list,
    "evidence_levels": dict,
    "open_questions": list,
    "recommended_next_action": str,
}
STATUS_VALUES = {"complete", "partial", "blocked", "escalated"}
QC_VERDICTS = {
    "approve",
    "approve-with-nits",
    "request-changes",
    "reject-to-requirement",
}
UNSATISFIED = re.compile(
    r"\b(not[ _-]?satisfied|unsatisfied|failed|blocked|unknown|unverified)\b",
    re.IGNORECASE,
)
SATISFIED = re.compile(r"\bsatisfied\b", re.IGNORECASE)
EVIDENCE = re.compile(
    r"(\bexecuted\b|\bconfirmed\b|\bpassed\b|\bfailed\b|\bmanual\b|"
    r"\bcommand\s*:|\b(?:pytest|vitest|jest|npm test|pnpm test|cargo test|go test)\b|"
    r"(?:^|[\s`])[^\s`]+\.(?:py|js|jsx|ts|tsx|go|rs|cs|php|java|rb|spec|test)"
    r":\d+)",
    re.IGNORECASE | re.MULTILINE,
)
TEST_CLAIM = re.compile(
    r"\b(tested|verified|passes|passed|works as expected|confirmed working)\b",
    re.IGNORECASE,
)
PLACEHOLDER = re.compile(r"^(?:\.\.\.|tbd|todo|fill me|placeholder)$", re.IGNORECASE)
SELF_REVALIDATION_RESULTS = {"passed", "failed", "blocked"}


def read_artifact(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[usage] cannot read {path}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def extract_envelope(text: str) -> dict[str, Any]:
    stripped = text.strip()
    candidates: list[str] = []

    if stripped.startswith("{"):
        candidates.append(stripped)

    candidates.extend(
        match.group(1).strip()
        for match in re.finditer(r"```json\s*(.*?)\s*```", text, re.IGNORECASE | re.DOTALL)
    )

    parsed: list[dict[str, Any]] = []
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and {"task_id", "role", "status"} <= value.keys():
            parsed.append(value)

    if not parsed:
        raise ValueError(
            "missing valid JSON return envelope; provide raw JSON or one fenced ```json block"
        )
    if len(parsed) > 1:
        raise ValueError("multiple JSON return envelopes found; exactly one is allowed")
    return parsed[0]


def scalar_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def find_placeholders(value: Any, path: str = "return_envelope") -> list[str]:
    problems: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            problems.extend(find_placeholders(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(find_placeholders(child, f"{path}[{index}]"))
    elif isinstance(value, str) and PLACEHOLDER.fullmatch(value.strip()):
        problems.append(f"{path} contains placeholder value {value!r}")
    return problems


def check_claim_evidence(text: str) -> list[str]:
    problems: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not TEST_CLAIM.search(line):
            continue
        window = "\n".join(lines[max(0, index - 4) : index + 5])
        if not EVIDENCE.search(window):
            problems.append(
                f"line {index + 1} asserts testing/verification without nearby execution evidence"
            )
    return problems


def check_boundary_matrix(text: str) -> list[str]:
    match = re.search(r"boundary (?:equivalence )?matrix", text, re.IGNORECASE)
    if not match:
        return []

    problems: list[str] = []
    section = text[match.start() : match.start() + 2000]
    for index, line in enumerate(section.splitlines(), start=1):
        if not line.strip().startswith("|"):
            continue
        if re.fullmatch(r"[\s|:-]+", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if any(cell in {"", "-", "..."} for cell in cells[1:]):
            problems.append(
                f"boundary matrix row {index} has a blank or placeholder data cell"
            )
    return problems


def criterion_problems(criteria: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not criteria:
        return ["criteria_status must contain at least one acceptance criterion"]

    for criterion_id, result in criteria.items():
        if not isinstance(criterion_id, str) or not criterion_id.strip():
            problems.append("criteria_status contains an empty/non-string criterion id")
            continue
        result_text = scalar_text(result)
        if not result_text.strip():
            problems.append(f"criteria_status.{criterion_id} is empty")
        if SATISFIED.search(result_text) and not UNSATISFIED.search(result_text):
            if not EVIDENCE.search(result_text):
                problems.append(
                    f"criteria_status.{criterion_id} is satisfied without named evidence"
                )
    return problems


def self_revalidation_problems(value: Any, status: str) -> list[str]:
    if not isinstance(value, dict):
        return ["xs_self_check Dev report requires object field: self_revalidation"]

    problems: list[str] = []
    for field, expected_type in {
        "commands": list,
        "checks": list,
        "result": str,
        "evidence": list,
    }.items():
        if field not in value:
            problems.append(f"self_revalidation missing required field: {field}")
        elif not isinstance(value[field], expected_type):
            problems.append(
                f"self_revalidation.{field} must be {expected_type.__name__}"
            )
    if problems:
        return problems

    result = value["result"].strip().lower()
    if result not in SELF_REVALIDATION_RESULTS:
        problems.append(
            f"self_revalidation.result {result!r} is not one of "
            f"{sorted(SELF_REVALIDATION_RESULTS)}"
        )
    if status == "complete" and result != "passed":
        problems.append("complete xs_self_check report requires self_revalidation.result passed")

    if not value["commands"]:
        problems.append("self_revalidation.commands must contain an executed command")
    for index, command in enumerate(value["commands"]):
        if not isinstance(command, dict):
            problems.append(f"self_revalidation.commands[{index}] must be an object")
            continue
        if not isinstance(command.get("command"), str) or not command["command"].strip():
            problems.append(
                f"self_revalidation.commands[{index}].command must be non-empty"
            )
        if not isinstance(command.get("exit_code"), int):
            problems.append(
                f"self_revalidation.commands[{index}].exit_code must be an integer"
            )
        elif status == "complete" and command["exit_code"] != 0:
            problems.append(
                f"complete xs_self_check report has failing command at index {index}"
            )

    for field in ("checks", "evidence"):
        if not value[field]:
            problems.append(f"self_revalidation.{field} must not be empty")
        elif any(not isinstance(item, str) or not item.strip() for item in value[field]):
            problems.append(f"self_revalidation.{field} must contain non-empty strings")
    return problems


def validate(text: str, expected_role: str) -> list[str]:
    problems: list[str] = []
    try:
        envelope = extract_envelope(text)
    except ValueError as exc:
        return [str(exc)]

    for field, expected_type in COMMON_FIELDS.items():
        if field not in envelope:
            problems.append(f"missing required field: {field}")
            continue
        if not isinstance(envelope[field], expected_type):
            problems.append(
                f"{field} must be {expected_type.__name__}, got {type(envelope[field]).__name__}"
            )

    if problems:
        return problems

    role = envelope["role"].strip().lower()
    workflow_mode = envelope["workflow_mode"].strip().lower()
    status = envelope["status"].strip().lower()
    if role != expected_role:
        problems.append(f"role is {role!r}; expected {expected_role!r}")
    if status not in STATUS_VALUES:
        problems.append(f"status {status!r} is not one of {sorted(STATUS_VALUES)}")
    if not envelope["task_id"].strip():
        problems.append("task_id must not be empty")
    if not envelope["recommended_next_action"].strip():
        problems.append("recommended_next_action must not be empty")

    problems.extend(criterion_problems(envelope["criteria_status"]))
    problems.extend(find_placeholders(envelope))
    problems.extend(check_claim_evidence(text))
    problems.extend(check_boundary_matrix(text))

    if expected_role == "dev" and workflow_mode == "xs_self_check":
        problems.extend(
            self_revalidation_problems(envelope.get("self_revalidation"), status)
        )

    if status == "complete":
        if envelope["allowlist_violations"]:
            problems.append("complete report has non-empty allowlist_violations")
        for criterion_id, result in envelope["criteria_status"].items():
            if UNSATISFIED.search(scalar_text(result)):
                problems.append(
                    f"complete report contains unresolved criterion {criterion_id}"
                )

    if expected_role == "qc":
        verdict = envelope.get("verdict")
        if not isinstance(verdict, str) or not verdict.strip():
            problems.append("QC return envelope requires non-empty field: verdict")
        else:
            normalized_verdict = verdict.strip().lower()
            if normalized_verdict not in QC_VERDICTS:
                problems.append(
                    f"QC verdict {normalized_verdict!r} is not one of {sorted(QC_VERDICTS)}"
                )
            if normalized_verdict in {"approve", "approve-with-nits"}:
                if status != "complete":
                    problems.append(f"QC verdict {normalized_verdict} requires status complete")
                if envelope["allowlist_violations"]:
                    problems.append(
                        f"QC verdict {normalized_verdict} cannot coexist with allowlist violations"
                    )
                if not EVIDENCE.search(text):
                    problems.append(
                        f"QC verdict {normalized_verdict} requires execution/static evidence"
                    )

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", required=True, choices=["dev", "qc"])
    parser.add_argument("artifact", help="report path, raw JSON path, or - for stdin")
    args = parser.parse_args()

    text = read_artifact(args.artifact)
    problems = validate(text, args.role)
    if problems:
        print(f"INVALID [{args.role}] {args.artifact}")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(f"VALID (machine floor met) [{args.role}] {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
