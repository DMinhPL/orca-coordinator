# QC Severity Model

Use one severity and one finding type.

## Severity
- P0 Critical: security compromise, data loss/corruption, money/privilege error, or system unavailable with no safe workaround.
- P1 High: core feature broken, major regression, or high-probability production failure.
- P2 Medium: incorrect behavior with limited scope or workable mitigation.
- P3 Low: minor correctness/robustness/maintainability issue with low operational impact.

## Finding type
- BLOCKER: cannot complete reliable verification.
- DEFECT: requirement or correctness failure proven by evidence.
- RISK: credible unverified failure mode needing decision/coverage.
- OBSERVATION: non-blocking note.

Do not inflate severity because a file is important; severity is based on impact and likelihood/preconditions.
