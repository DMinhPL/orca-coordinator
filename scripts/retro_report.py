#!/usr/bin/env python3
"""Aggregate Orca runtime exports and compatible legacy decision logs.

Usage:
    python scripts/retro_report.py
    python scripts/retro_report.py .docs/features other/task/decisions.jsonl
    python scripts/retro_report.py --runtime-export orca-runtime.jsonl .docs/features
    python scripts/retro_report.py --json --strict .docs/features
    python scripts/retro_report.py --orca-runs                  # latest batch from Orca
    python scripts/retro_report.py --orca-runs run_abc run_def --orca-save snap.json
    python scripts/retro_report.py --orca-json snap.json

Directories are searched recursively for legacy decisions.jsonl files; runtime
exports are passed explicitly so the script never writes or copies them into the
project. Malformed records are reported and skipped unless --strict is supplied.

--orca-runs reads Orca orchestration state read-only (run-list, task-list,
worker-list, worker-show) and reports process cost by workflow mode: dispatches,
worker minutes, repeats, and ceremony dispatches that produced no new work. Orca
does not expose token counts; these are the proxies it does expose. Dispatch
vocabulary and flag thresholds come from agents-models.yaml
(orchestration.dispatch_tag, retrospective.process_cost).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_view import CONFIG, extract  # noqa: E402


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


# ─────────────────────────────────────────────────────────────
# Process cost — Orca runtime state, read-only
# ─────────────────────────────────────────────────────────────

class OrcaUnavailable(RuntimeError):
    pass


def yaml_value(dotted_path: str, config: Path = CONFIG) -> Any:
    """Read one scalar or inline-list value without PyYAML, via config_view."""
    lines = config.read_text(encoding="utf-8").splitlines()
    raw = extract(lines, dotted_path)[0].split(":", 1)[1].split("#", 1)[0].strip()
    if raw.startswith("["):
        return [item.strip() for item in raw.strip("[]").split(",") if item.strip()]
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return raw.strip("'\"")


def yaml_children(dotted_path: str, config: Path = CONFIG) -> dict[str, Any]:
    lines = config.read_text(encoding="utf-8").splitlines()
    block = extract(lines, dotted_path)
    indent = len(block[0]) - len(block[0].lstrip()) + 2
    keys = [
        line.strip().split(":", 1)[0]
        for line in block[1:]
        if line.strip() and not line.strip().startswith("#")
        and len(line) - len(line.lstrip()) == indent
    ]
    return {key: yaml_value(f"{dotted_path}.{key}", config) for key in keys}


def orca(*args: str) -> Any:
    exe = shutil.which("orca")
    if not exe:
        raise OrcaUnavailable("orca CLI not found on PATH")
    try:
        proc = subprocess.run(
            [exe, "orchestration", *args, "--json"],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise OrcaUnavailable(f"orca orchestration {args[0]}: {exc}") from exc
    if proc.returncode != 0:
        raise OrcaUnavailable(
            f"orca orchestration {args[0]} exited {proc.returncode}: {proc.stderr.strip()[:200]}"
        )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise OrcaUnavailable(f"orca orchestration {args[0]}: invalid JSON: {exc.msg}") from exc
    if isinstance(data, dict) and data.get("ok") is False:
        raise OrcaUnavailable(f"orca orchestration {args[0]}: {data.get('error')}")
    return data.get("result", data) if isinstance(data, dict) else data


def paged(command: str, key: str, *args: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cursor = None
    for _ in range(50):
        result = orca(command, *args, *(["--cursor", cursor] if cursor else []))
        items.extend(result.get(key) or [])
        cursor = result.get("nextCursor") or (result.get("page") or {}).get("nextCursor")
        if not cursor:
            break
    return items


def collect_orca(run_ids: list[str], limit: int) -> dict[str, Any]:
    if run_ids:
        known = {run["id"]: run for run in paged("run-list", "runs")}
        runs = [known.get(run_id, {"id": run_id}) for run_id in run_ids]
    else:
        runs = orca("run-list", "--limit", str(limit)).get("runs", [])[:limit]
    snapshot_runs = []
    for run in runs:
        tasks = orca("task-list", "--run", run["id"]).get("tasks", [])
        workers = paged("worker-list", "workers", "--run", run["id"])
        dispatches = [orca("worker-show", "--dispatch", worker["dispatchId"]) for worker in workers]
        snapshot_runs.append({"run": run, "tasks": tasks, "dispatches": dispatches})
    return {
        "source": "orca",
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runs": snapshot_runs,
    }


TAG = re.compile(r"orca-tag((?:\s+[a-z_]+=[A-Za-z0-9_.-]+)+)")
ROLE_IN_TEXT = re.compile(r"^\s*(BA|Dev|QC)\b|You are the (BA|Dev|QC)\b", re.IGNORECASE)
BAND_IN_TEXT = re.compile(r"\bband\b\W{0,5}(XS|XL|S|M|L)\b")
INFERRED_REASONS = (
    (re.compile(r"correction|resend", re.IGNORECASE), "report_correction"),
    (re.compile(r"re-?launch|restart", re.IGNORECASE), "relaunch"),
    (re.compile(r"escalat", re.IGNORECASE), "escalation"),
    (re.compile(r"rework|redo|re-?verif", re.IGNORECASE), "rework"),
)


def parse_tag(*texts: str) -> dict[str, str]:
    for text in texts:
        match = TAG.search(text)
        if match:
            return dict(pair.split("=", 1) for pair in match.group(1).split())
    return {}


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00").replace(" ", "T", 1))
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)


def minutes(start: datetime | None, end: datetime | None) -> float | None:
    return round((end - start).total_seconds() / 60, 2) if start and end else None


def infer_reason(title: str, retry_of: Any, seen_role_before: bool) -> str:
    for pattern, reason in INFERRED_REASONS:
        if pattern.search(title):
            return reason
    if retry_of or re.search(r"retry", title, re.IGNORECASE):
        return "retry_unclassified"
    return "repeat_unclassified" if seen_role_before else "initial"


def mode_pattern(mode_names: Iterable[str]) -> re.Pattern[str]:
    names = "|".join(sorted(map(re.escape, mode_names), key=len, reverse=True))
    return re.compile(rf"\b(?:workflow_)?mode\b[\"']?\s*[:= ]\s*[\"']?({names})\b")


def dispatch_row(show: dict[str, Any], tasks: dict[Any, dict[str, Any]]) -> dict[str, Any]:
    dispatch = show.get("dispatch") or {}
    worker = show.get("worker") or {}
    task_id = dispatch.get("taskId") or dispatch.get("task_id")
    task = tasks.get(task_id) or {}
    task_id = (
        task_id
        or task.get("id")
        or f"dispatch:{dispatch.get('id') or worker.get('dispatchId')}"
    )
    title = str(task.get("task_title") or task.get("display_name") or "")
    spec = str(task.get("spec") or "")
    result = str(task.get("result") or "")
    launch = ((worker.get("startOptions") or {}).get("launch") or {}).get("effective") or {}
    start = parse_ts(dispatch.get("dispatchedAt") or dispatch.get("createdAt") or task.get("created_at"))
    end = parse_ts(dispatch.get("completedAt") or task.get("completed_at"))
    return {
        "dispatch": dispatch.get("id") or worker.get("dispatchId"),
        "task_id": task_id,
        "tag": parse_tag(json.dumps(show), spec.split("\n", 1)[0], spec),
        "title": title,
        "text": f"{title}\n{spec}\n{result}",
        "result": result,
        "retry_of": dispatch.get("retryOfDispatchId"),
        "failures": int(dispatch.get("failureCount") or 0),
        "model": launch.get("model") or "unknown",
        "start": start,
        "end": end,
        "minutes": minutes(start, end),
    }


def first_group(match: re.Match[str] | None) -> str | None:
    return next((group for group in match.groups() if group), None) if match else None


def classify(
    row: dict[str, Any], mode_in_text: re.Pattern[str], seen_task_roles: set[tuple[str, str]]
) -> None:
    """Fill role/mode/band/reason from the tag, else infer them from the text."""
    tag, text = row["tag"], row["text"]
    role = first_group(ROLE_IN_TEXT.search(row["title"]) or ROLE_IN_TEXT.search(text))
    row["role"] = tag.get("role") or (role.lower() if role else "unknown")
    row["mode"] = tag.get("mode") or first_group(mode_in_text.search(text))
    row["band"] = tag.get("band") or first_group(BAND_IN_TEXT.search(text))
    task_role = (row["task_id"], row["role"])
    row["reason"] = tag.get("reason") or infer_reason(
        row["title"], row["retry_of"], task_role in seen_task_roles
    )
    row["inferred"] = not tag
    seen_task_roles.add(task_role)


def normalize_run(entry: dict[str, Any], mode_in_text: re.Pattern[str]) -> dict[str, Any]:
    run = entry.get("run") or {}
    tasks = {task.get("id"): task for task in entry.get("tasks") or []}
    rows = [dispatch_row(show, tasks) for show in entry.get("dispatches") or []]
    rows.sort(key=lambda row: row["start"] or datetime.max.replace(tzinfo=timezone.utc))
    seen_task_roles: set[tuple[str, str]] = set()
    for row in rows:
        classify(row, mode_in_text, seen_task_roles)

    modes = Counter(row["mode"] for row in rows if row["mode"])
    bands = Counter(row["band"] for row in rows if row["band"])
    ends = [row["end"] for row in rows if row["end"]]
    starts = [stamp for stamp in [parse_ts(run.get("created_at"))] + [row["start"] for row in rows] if stamp]
    return {
        "id": run.get("id"),
        "mode": modes.most_common(1)[0][0] if modes else "unknown",
        "band": bands.most_common(1)[0][0] if bands else None,
        "dispatches": rows,
        "wall_minutes": minutes(min(starts), max(ends)) if starts and ends else None,
    }


def process_cost(snapshot: dict[str, Any], config: Path = CONFIG) -> dict[str, Any]:
    ceremony_reasons = set(yaml_value("orchestration.dispatch_tag.ceremony_reasons", config))
    flag_when = yaml_children("retrospective.process_cost.flag_when", config)
    mode_in_text = mode_pattern(yaml_children("workflow_modes", config))
    runs = [normalize_run(entry, mode_in_text) for entry in snapshot.get("runs") or []]

    by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        by_mode[run["mode"]].append(run)

    def mean(values: list[float | None]) -> float | None:
        known = [value for value in values if value is not None]
        return round(sum(known) / len(known), 2) if known else None

    modes: dict[str, Any] = {}
    for mode, mode_runs in sorted(by_mode.items()):
        rows = [row for run in mode_runs for row in run["dispatches"]]
        ceremony = [row for row in rows if row["reason"] in ceremony_reasons]
        worker_minutes = sum(row["minutes"] or 0 for row in rows)
        repeats = sum(
            count - 1
            for run in mode_runs
            for count in Counter(
                (row["task_id"], row["role"]) for row in run["dispatches"]
            ).values()
            if count > 1
        )
        modes[mode] = {
            "runs": len(mode_runs),
            "dispatches": len(rows),
            "dispatches_per_run": round(len(rows) / len(mode_runs), 2),
            "worker_minutes_per_run": round(worker_minutes / len(mode_runs), 2),
            "wall_minutes_per_run": mean([run["wall_minutes"] for run in mode_runs]),
            "repeat_dispatches": repeats,
            "ceremony_dispatches": len(ceremony),
            "ceremony_dispatch_share": round(len(ceremony) / len(rows), 4) if rows else 0.0,
            "ceremony_minute_share": round(
                sum(row["minutes"] or 0 for row in ceremony) / worker_minutes, 4
            ) if worker_minutes else 0.0,
            "inferred_dispatches": sum(row["inferred"] for row in rows),
        }

    flags = []
    share_limit = flag_when.get("ceremony_dispatch_share_above")
    for mode, stats in modes.items():
        if share_limit is not None and stats["ceremony_dispatch_share"] > share_limit:
            flags.append(
                f"{mode}: ceremony share {stats['ceremony_dispatch_share']:.0%} > {share_limit:.0%}"
            )
    for key, limit in flag_when.items():
        if key.endswith("_dispatches_per_run_above"):
            mode = key[: -len("_dispatches_per_run_above")]
            stats = modes.get(mode)
            if stats and stats["dispatches_per_run"] > limit:
                flags.append(f"{mode}: {stats['dispatches_per_run']} dispatches/run > {limit}")

    all_rows = [row for run in runs for row in run["dispatches"]]
    return {
        "runs": len(runs),
        "dispatches": len(all_rows),
        "inferred_dispatches": sum(row["inferred"] for row in all_rows),
        "token_counts": "not exposed by Orca; dispatches, minutes and model tier are the proxies",
        "by_mode": modes,
        "reasons": dict(sorted(Counter(row["reason"] for row in all_rows).items())),
        "ceremony_by_reason": dict(sorted(
            Counter(row["reason"] for row in all_rows if row["reason"] in ceremony_reasons).items()
        )),
        "retries_with_retry_of": sum(bool(row["retry_of"]) for row in all_rows),
        "recorded_failures": sum(row["failures"] for row in all_rows),
        "models": dict(sorted(Counter(row["model"] for row in all_rows).items())),
        "flags": flags,
    }


def print_process_cost(cost: dict[str, Any]) -> None:
    print("Process cost (Orca runtime)")
    print(
        f"runs: {cost['runs']}  dispatches: {cost['dispatches']}  "
        f"untagged (inferred): {cost['inferred_dispatches']}"
    )
    print(f"tokens: {cost['token_counts']}")
    header = f"{'mode':<20}{'runs':>5}{'disp/run':>10}{'worker-min':>12}{'wall-min':>10}{'repeats':>9}{'ceremony':>14}"
    print(header)
    for mode, stats in cost["by_mode"].items():
        wall = "-" if stats["wall_minutes_per_run"] is None else f"{stats['wall_minutes_per_run']:.1f}"
        ceremony = f"{stats['ceremony_dispatches']} ({stats['ceremony_dispatch_share']:.0%})"
        print(
            f"{mode:<20}{stats['runs']:>5}{stats['dispatches_per_run']:>10.2f}"
            f"{stats['worker_minutes_per_run']:>12.1f}{wall:>10}{stats['repeat_dispatches']:>9}{ceremony:>14}"
        )
    print(f"dispatch reasons: {cost['reasons']}")
    print(f"ceremony by reason: {cost['ceremony_by_reason']}")
    print(f"retries with --retry-of: {cost['retries_with_retry_of']}  recorded failures: {cost['recorded_failures']}")
    print(f"models: {cost['models']}")
    for flag in cost["flags"]:
        print(f"! {flag}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="*", default=[".docs/features"])
    parser.add_argument(
        "--runtime-export",
        action="append",
        default=[],
        metavar="PATH",
        help="Orca JSONL export to include without copying it into project docs",
    )
    parser.add_argument(
        "--orca-runs",
        nargs="*",
        metavar="RUN_ID",
        help="read process cost from Orca (read-only); no IDs = latest batch",
    )
    parser.add_argument(
        "--orca-limit",
        type=int,
        help="runs to read when --orca-runs has no IDs (default: retrospective.batch.every_n_tasks)",
    )
    parser.add_argument("--orca-json", metavar="PATH", help="read a snapshot saved by --orca-save")
    parser.add_argument("--orca-save", metavar="PATH", help="save the Orca snapshot (keep it outside the project)")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    snapshot = None
    if args.orca_json:
        try:
            snapshot = json.loads(Path(args.orca_json).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"retro-report: {args.orca_json}: {exc}", file=sys.stderr)
            return 2
    elif args.orca_runs is not None:
        limit = args.orca_limit or int(yaml_value("retrospective.batch.every_n_tasks"))
        try:
            snapshot = collect_orca(args.orca_runs, limit)
        except OrcaUnavailable as exc:
            print(f"retro-report: {exc}", file=sys.stderr)
            return 2
        if args.orca_save:
            Path(args.orca_save).write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    files = decision_files([*args.inputs, *args.runtime_export])
    if not files and snapshot is None:
        print("retro-report: no runtime export or decisions.jsonl files found", file=sys.stderr)
        return 2
    records, errors = load_records(files)
    if args.strict and errors:
        for error in errors:
            print(f"retro-report: {error}", file=sys.stderr)
        return 1

    summary = summarize(records, files) if files else {}
    cost = process_cost(snapshot) if snapshot is not None else None
    if args.as_json:
        output = {**summary, "warnings": errors}
        if cost is not None:
            output["process_cost"] = cost
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        if files:
            print_human(summary, errors)
        if cost is not None:
            if files:
                print()
            print_process_cost(cost)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
