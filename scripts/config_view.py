#!/usr/bin/env python3
"""Print a small, role-specific view of agents-models.yaml.

The source YAML remains authoritative. This helper performs text-level extraction so
workers do not need PyYAML and do not have to load the full policy file into context.
The output is a context view, not a standalone YAML document.

Usage:
    python scripts/config_view.py --role dev
    python scripts/config_view.py --role lead --path retrospective
    python scripts/config_view.py --list
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CONFIG = Path(__file__).resolve().parents[1] / "references" / "agents-models.yaml"
KEY = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z_][A-Za-z0-9_-]*):")

# These are routing lists, not copied policy values. Add --path for a conditional
# section rather than widening every worker's default view.
ROLE_PATHS = {
    "lead": [
        "agents.lead",
        "complexity_assessment",
        "modification_policy",
        "human_gates",
        "engineering_policy.task_classification",
        "budgets",
        "communication",
        "workflow_modes",
        "optimization",
        "resolution",
        "orchestration",
        "documentation.status_gate",
        "primary_session_policy",
        "dispatch_lifecycle",
        "lead_authority_boundary",
    ],
    "ba": [
        "agents.ba",
        "complexity_assessment.band_challenge",
        "modification_policy.file_allowlist",
        "engineering_policy.evidence_levels",
        "engineering_policy.evidence_policy",
        "engineering_policy.traceability",
        "budgets",
        "communication",
        "change_control",
        "knowledge_sources.by_role.ba",
        "project_overlay",
        "optimization",
        "resolution",
        "orchestration.dispatch_envelope",
        "orchestration.return_envelope",
        "documentation.files_by_band",
    ],
    "dev": [
        "agents.dev",
        "complexity_assessment.band_challenge",
        "modification_policy",
        "engineering_policy.evidence_levels",
        "engineering_policy.evidence_policy",
        "engineering_policy.traceability",
        "engineering_policy.rework_stop_conditions",
        "budgets",
        "communication",
        "change_control",
        "workflow_modes.xs_self_check",
        "knowledge_sources.by_role.dev",
        "project_overlay",
        "optimization",
        "resolution",
        "orchestration.dispatch_envelope",
        "orchestration.return_envelope",
        "orchestration.machine_acceptance",
        "documentation.files_by_band",
    ],
    "qc": [
        "agents.qc",
        "complexity_assessment.band_challenge",
        "engineering_policy.evidence_levels",
        "engineering_policy.evidence_policy",
        "engineering_policy.defect_severity",
        "engineering_policy.traceability",
        "budgets",
        "qc_policy",
        "communication",
        "change_control",
        "knowledge_sources.by_role.qc",
        "project_overlay",
        "optimization",
        "resolution",
        "orchestration.dispatch_envelope",
        "orchestration.return_envelope",
        "orchestration.machine_acceptance",
        "documentation.status_gate",
        "rework_loop",
    ],
    "closeout": [
        "documentation",
        "cleanup_policy",
        "retrospective",
        "dispatch_lifecycle",
    ],
}


def block_end(lines: list[str], start: int, indent: int) -> int:
    for index in range(start + 1, len(lines)):
        match = KEY.match(lines[index])
        if match and len(match.group("indent")) <= indent:
            return index
    return len(lines)


def extract(lines: list[str], dotted_path: str) -> list[str]:
    start, end, parent_indent = 0, len(lines), -2
    for segment in dotted_path.split("."):
        found = None
        for index in range(start, end):
            match = KEY.match(lines[index])
            if not match:
                continue
            indent = len(match.group("indent"))
            if indent == parent_indent + 2 and match.group("key") == segment:
                found = (index, indent)
                break
        if found is None:
            raise KeyError(dotted_path)
        start, parent_indent = found
        end = block_end(lines, start, parent_indent)
        start += 1
    return lines[start - 1 : end]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=sorted(ROLE_PATHS))
    parser.add_argument("--path", action="append", default=[], help="extra dotted YAML path")
    parser.add_argument("--list", action="store_true", help="list built-in role views")
    parser.add_argument("--config", type=Path, default=CONFIG)
    args = parser.parse_args()

    if args.list:
        for role, paths in ROLE_PATHS.items():
            print(f"{role}: {', '.join(paths)}")
        return 0
    if not args.role and not args.path:
        parser.error("provide --role, --path, or --list")

    try:
        lines = args.config.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError as exc:
        print(f"config-view: cannot read {args.config}: {exc}", file=sys.stderr)
        return 2

    paths = ["schema_version", "config_version"]
    if args.role:
        paths.extend(ROLE_PATHS[args.role])
    paths.extend(args.path)
    paths = list(dict.fromkeys(paths))

    print(f"# Context view from {args.config}")
    print("# The source file is authoritative; this combined output is not standalone YAML.")
    for path in paths:
        try:
            snippet = extract(lines, path)
        except KeyError:
            print(f"config-view: path not found: {path}", file=sys.stderr)
            return 1
        print(f"\n# --- {path} ---")
        sys.stdout.writelines(snippet)
        if snippet and not snippet[-1].endswith("\n"):
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
