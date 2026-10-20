#!/usr/bin/env python3
"""Aggregate Orca decisions.jsonl files into a batch retrospective.

Usage:
    python scripts/retro_report.py
    python scripts/retro_report.py .docs/features other/task/decisions.jsonl
    python scripts/retro_report.py --json --strict .docs/features

Directories are searched recursively for decisions.jsonl. Malformed records are
reported and skipped unless --strict is supplied.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


BAND_ORDER = {band: index for index, band in enumerate(("XS", "S", "M", "L", "XL"))}


def decision_files(inputs: Iterable[str]) -> list[Path]:
    found: set[Path] = set()
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            found.update(candidate.resolve() for candidate in path.rglob("decisions.jsonl"))
        elif path.is_file():
            found.add(path.resolve())
    return sorted(found)


def band(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("band") or value.get("name")
    if not isinstance(value, str):
        return None
    candidate = value.strip().upper().split()[0].strip("():")
    return candidate if candidate in BAND_ORDER else None


def load_records(paths: list[Path]) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append(f"{path}: {exc}")
            continue
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{number}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(record, dict):
                errors.append(f"{path}:{number}: record must be an object")
                continue
            record.setdefault("_source", f"{path}:{number}")
            records.append(record)
    return records, errors


def summarize(records: list[dict[str, Any]], files: list[Path]) -> dict[str, Any]:
    events = Counter(str(record.get("event", "unknown")) for record in records)
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, record in enumerate(records, 1):
        task_id = str(record.get("task_id") or f"unknown:{index}")
        by_task[task_id].append(record)

    escalation_tasks: set[str] = set()
    qc_independence_failures: set[str] = set()
    intake_bands: Counter[str] = Counter()
    final_bands: Counter[str] = Counter()
    change_request_origins: Counter[str] = Counter()
    allowlist_amendments = 0
    requirement_gaps = 0
    upward_rescores = 0

    for task_id, task_records in by_task.items():
        task_intake = None
        task_final = None
        for record in task_records:
            event = str(record.get("event", ""))
            haystack = json.dumps(record, ensure_ascii=False).lower()
            if event == "escalation_triggered":
                escalation_tasks.add(task_id)
            if event == "allowlist_amended":
                allowlist_amendments += 1
            if event == "change_request_disposition":
                origin = str(record.get("actor") or record.get("origin") or "unknown").lower()
                change_request_origins[origin] += 1
                if "requirement_gap" in haystack or "scope_addition" in haystack or "new_requirement" in haystack:
                    requirement_gaps += 1
            if "qc_independence" in haystack and any(word in haystack for word in ("failed", "false", "lost", "violated")):
                qc_independence_failures.add(task_id)

            if event == "complexity_score":
                task_intake = task_intake or band(record.get("to")) or band(record.get("band"))
                task_final = band(record.get("to")) or band(record.get("band")) or task_final
            elif event == "complexity_rescore":
                before = band(record.get("from")) or task_final
                after = band(record.get("to")) or band(record.get("band_final"))
                if before and after and BAND_ORDER[after] > BAND_ORDER[before]:
                    upward_rescores += 1
                task_intake = task_intake or before
                task_final = after or task_final

        if task_intake:
            intake_bands[task_intake] += 1
        if task_final or task_intake:
            final_bands[task_final or task_intake] += 1

    task_count = len(by_task)
    return {
        "files": len(files),
        "records": len(records),
        "tasks": task_count,
        "events": dict(sorted(events.items())),
        "escalation": {
            "tasks": len(escalation_tasks),
            "rate": round(len(escalation_tasks) / task_count, 4) if task_count else 0.0,
        },
        "allowlist_amendments": allowlist_amendments,
        "requirement_gap_change_requests": requirement_gaps,
        "upward_rescores": upward_rescores,
        "band_at_intake": dict(sorted(intake_bands.items(), key=lambda item: BAND_ORDER[item[0]])),
        "band_final": dict(sorted(final_bands.items(), key=lambda item: BAND_ORDER[item[0]])),
        "change_request_origins": dict(sorted(change_request_origins.items())),
        "qc_independence_failure_tasks": len(qc_independence_failures),
    }


def print_human(summary: dict[str, Any], errors: list[str]) -> None:
    print("Orca batch retrospective")
    print(f"files: {summary['files']}  records: {summary['records']}  tasks: {summary['tasks']}")
    escalation = summary["escalation"]
    print(f"escalation rate: {escalation['tasks']}/{summary['tasks']} ({escalation['rate']:.1%})")
    print(f"allowlist amendments: {summary['allowlist_amendments']}")
    print(f"requirement-gap change requests: {summary['requirement_gap_change_requests']}")
    print(f"upward rescores: {summary['upward_rescores']}")
    print(f"QC independence failures: {summary['qc_independence_failure_tasks']}")
    print(f"bands at intake: {summary['band_at_intake']}")
    print(f"bands final: {summary['band_final']}")
    print(f"change-request origins: {summary['change_request_origins']}")
    if errors:
        print(f"warnings: {len(errors)}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", default=[".docs/features"])
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    files = decision_files(args.inputs)
    if not files:
        print("retro-report: no decisions.jsonl files found", file=sys.stderr)
        return 2
    records, errors = load_records(files)
    if args.strict and errors:
        for error in errors:
            print(f"retro-report: {error}", file=sys.stderr)
        return 1

    summary = summarize(records, files)
    if args.as_json:
        print(json.dumps({**summary, "warnings": errors}, ensure_ascii=False, indent=2))
    else:
        print_human(summary, errors)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
