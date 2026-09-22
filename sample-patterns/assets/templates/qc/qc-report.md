# QC Report — {Feature Name}

> Feature: {Feature Name} · Branch: {branch-name} · Date: {YYYY-MM-DD} · Reviewer: QC worker · Dispatch: {dispatch-id}

## ROLE CONTRACT ACK — QC
<paste the ACK block emitted at bootstrap>

## Verdict
`PASS` | `CONDITIONAL` | `FAIL` | `BLOCKED`
PASS is allowed only if every rule in role-contract.md §6 is met.

## Phase A — cases derived from acceptance criteria (BEFORE reading development.md)
- AC-1 -> ...
- AC-2 -> ...
(List frozen before Phase B. Dev notes may only ADD, never remove/weaken.)

## Phase B — additions/context from Dev notes
- Dev claim: "..." -> treated as hypothesis, verified independently: <result>

## Provider review recipe (input, NOT verdict)
Fill only if the dispatch asked you to run the provider's built-in review
(Codex `/review`, Claude Code `/code-review`). Its output is raw input: every
issue it raises must still be routed through the boundary matrix / Falsy Trace /
evidence tiers below, and it never sets the verdict on its own.
- Recipe run: `/review` | `/code-review` | not requested | UNAVAILABLE (headless) -> fell back to manual review
- Issues surfaced by recipe: <list, or "none">
- How each maps into this report: <issue -> AC/boundary cell/finding, with evidence tier>
- Recipe blind spots covered by the skill gates: <e.g. Balance=0 falsy trap, which the generic recipe does not check>

## Boundary matrix (no blank cells)
| Variable | positive | zero | negative | null | undefined | empty "" | NaN | error path |
|---|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Falsy Trace (if any truthy/falsy check on possibly-0/""/false/null)
| Input value | Coerces to | Branch taken | Correct? |
|---|---|---|---|
| `0` | false | ... | ... |
| ... | ... | ... | ... |

## Acceptance-criteria coverage
| AC | Covered by | Evidence tier | Result |
|---|---|---|---|
| ... | ... | EXECUTED/STATIC/REASONED-ONLY/UNVERIFIED | ... |

## Findings
| ID | Type (BLOCKER/DEFECT/RISK/OBSERVATION) | Severity (P0-P3) | File:line | Evidence tier | Evidence (pasted) |
|---|---|---|---|---|---|
| F-01 | ... | ... | ... | ... | ... |

## Dynamic verification (pasted run output)
- Command / payload used (real captured sample): ...
- Output: ...

## Unverified assumptions -> RISK
- ...

## Regression risk & recommended next action
- ...
