#!/usr/bin/env python3
"""
validate_worker_output.py — machine acceptance gate for engineering-manager.

Lints a Dev or QC artifact and exits non-zero if it violates the hard rules in
references/shared/role-contract.md. This is a LINTER that raises the floor; it
does not prove correctness and does not replace the QC gate. Lead runs it before
accepting a worker's worker_done.

Usage:
    python tools/validate_worker_output.py --role dev  path/to/development.md
    python tools/validate_worker_output.py --role qc   path/to/qc-report.md

Exit codes: 0 = valid (floor met), 1 = invalid (violations printed), 2 = usage error.
"""
import argparse
import re
import sys

# Signals that a truthy/falsy decision exists in the change/report.
FALSY_SIGNALS = [
    r"\bBoolean\s*\(", r"!\s*\w", r"\?\s*.+:\s*", r"&&", r"\|\|",
    r"\?\?", r"==\s*(null|undefined|0|''|\"\")", r"\bif\s*\(",
]
# Words that assert testing/verification.
TESTED_WORDS = re.compile(
    r"\b(tested|verified|passes|pass\b|works as expected|confirmed working|đã test|đã verify|chạy ok)\b",
    re.IGNORECASE,
)
EXEC_EVIDENCE = re.compile(
    r"(EXECUTED|```|\$ |PASSED|FAILED|assert|expect\(|HTTP/|status\s*200|pytest|npm test|vitest|jest)",
    re.IGNORECASE,
)
REQUIRED_BOUNDARY_CLASSES = ["zero", "null", "undefined", "empty", "nan", "negative"]
BLANK_CELL = re.compile(r"\|\s*(\.\.\.|-|)\s*(?=\|)")


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        print(f"[usage] cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)


def has_ack(text, role):
    return re.search(rf"ROLE CONTRACT ACK\s*[—-]\s*{role}", text, re.IGNORECASE) is not None


def mentions_falsy(text):
    return any(re.search(p, text) for p in FALSY_SIGNALS)


def has_falsy_trace(text):
    # A Falsy Trace table must enumerate 0 and at least one other falsy class.
    has_zero = re.search(r"\|\s*`?0", text) is not None
    header = re.search(r"Coerces to", text, re.IGNORECASE) is not None
    return header and has_zero


def boundary_section(text):
    m = re.search(r"[Bb]oundary (?:equivalence )?matrix", text)
    if not m:
        return None
    return text[m.start(): m.start() + 1500]


def find_blank_cells(section):
    """Return count of table rows containing an empty/placeholder data cell."""
    blanks = 0
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"\|[\s:|-]+\|?\s*$", line):  # separator row
            continue
        if re.search(r"variable|input value", line, re.IGNORECASE):  # header
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any(c in ("", "...", "-") for c in cells[1:]):
            blanks += 1
    return blanks


def check_tested_backed(text):
    """Every 'tested/verified/passes' claim needs execution evidence nearby."""
    problems = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if TESTED_WORDS.search(line):
            window = "\n".join(lines[max(0, i - 2): i + 3])
            if not EXEC_EVIDENCE.search(window):
                problems.append(f"  line {i+1}: '{line.strip()[:70]}' — asserts testing with no EXECUTED evidence nearby")
    return problems


def check_pass_backed(text):
    """A PASS verdict requires execution evidence somewhere in the report."""
    if re.search(r"Verdict[^\n]*\bPASS\b", text, re.IGNORECASE) or re.search(r"^\s*`?PASS`?\s*$", text, re.MULTILINE):
        if not EXEC_EVIDENCE.search(text):
            return ["  verdict is PASS but no EXECUTED evidence found in the artifact"]
        if re.search(r"\bUNVERIFIED\b", text) and re.search(r"P0|P1|money|balance|auth|state", text, re.IGNORECASE):
            return ["  verdict is PASS while a risk-bearing item is still UNVERIFIED"]
    return []


VAGUE_VERBS = re.compile(
    r"\b(should work|works? fine|handle(?:d|s)? properly|as expected|works? correctly|hoat dong dung|xu ly hop ly)\b",
    re.IGNORECASE,
)


def check_ba(text):
    """BA requirement-quality gates (not the Dev/QC evidence gates)."""
    problems = []
    if "Acceptance Criteria" not in text and "acceptance criteria" not in text.lower():
        problems.append("requirement has no Acceptance Criteria section")
    else:
        # Testable AC: expect given/when/then or an explicit pass/fail column.
        if not re.search(r"(given|when|then|pass/fail|pass\s*/\s*fail)", text, re.IGNORECASE):
            problems.append("acceptance criteria are not testable (no given/when/then or pass/fail check present)")
    if not re.search(r"edge case", text, re.IGNORECASE):
        problems.append("missing mandatory edge-case enumeration (zero/empty/null/error/boundary) — upstream feed for QC Phase A")
    if not re.search(r"assumption", text, re.IGNORECASE):
        problems.append("missing Assumptions register")
    for i, line in enumerate(text.splitlines()):
        if VAGUE_VERBS.search(line):
            problems.append(f"  line {i+1}: vague untestable wording '{line.strip()[:60]}' — make the pass/fail check concrete")
    return problems


def validate(path, role):
    text = load(path)
    role = role.lower()
    errors = []

    # ACK: required for every specialist worker.
    if not has_ack(text, role.upper()):
        errors.append(f"missing ROLE CONTRACT ACK — {role.upper()} block (skill not loaded/acknowledged)")

    if role in ("dev", "qc"):
        sec = boundary_section(text)
        if sec is None:
            errors.append("missing boundary matrix section")
        else:
            blanks = find_blank_cells(sec)
            if blanks:
                errors.append(f"boundary matrix has {blanks} row(s) with blank/placeholder cells (must be EXECUTED/STATIC/REASONED-ONLY/UNVERIFIED or justified N/A)")
        if mentions_falsy(text) and not has_falsy_trace(text):
            errors.append("change contains a truthy/falsy check but no Falsy Trace enumerating 0/''/false/null/undefined/NaN")
        errors += check_tested_backed(text)

    if role == "qc":
        errors += check_pass_backed(text)
        if "Phase A" not in text:
            errors.append("QC report missing Phase A (blind-derive) section — independence not demonstrated")

    if role == "ba":
        errors += check_ba(text)

    if errors:
        print(f"INVALID [{role}] {path}:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"VALID (floor met) [{role}] {path}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True, choices=["dev", "qc", "ba"])
    ap.add_argument("artifact")
    args = ap.parse_args()
    sys.exit(validate(args.artifact, args.role))


if __name__ == "__main__":
    main()
