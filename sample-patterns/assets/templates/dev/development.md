# Development Notes — {Feature Name}

> Feature: {Feature Name} · Branch: {branch-name} · Date: {YYYY-MM-DD} · Status: Draft · Ticket: {ticket-or--}

See `ba/requirement.md` for the business rules.

## Business rule -> technical mapping
| Business rule | Technical decision |
|---|---|
| ... | ... |

## File(s) to change
- ...

## Current baseline
- ...

## Relevant models/APIs
- ...

## Assumptions & Risk Register (REQUIRED)
Every statement about external data (backend/DB/config/upstream) shape or value.
Unproven assumptions may NOT underpin any Pass.
| Assumption | Source of truth | Evidence tier (EXECUTED/STATIC/REASONED-ONLY/UNVERIFIED) | Risk if wrong |
|---|---|---|---|
| e.g. `balance.Balance` is a number, not string | captured API sample | ... | wrong falsy branch |

## Falsy Trace (REQUIRED if any truthy/falsy check on possibly-0/""/false/null)
Covers `if(x)`, `!x`, `x?a:b`, `Boolean(x)`, `x && ...`, `x || d`, `??`, loose `==`.
| Input value | Coerces to | Branch taken | Correct? |
|---|---|---|---|
| positive | true | ... | ... |
| `0` / `0.00` | false | ... | ... |
| `""` | false | ... | ... |
| `false` | false | ... | ... |
| `NaN` | false | ... | ... |
| `null` | false | ... | ... |
| `undefined` | false | ... | ... |

## Boundary matrix per touched variable (REQUIRED, no blank cells)
| Variable | positive | zero | negative | null | undefined | empty "" | NaN | error path |
|---|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Implementation plan
1. ...

## Test Cases
Result must reflect EXECUTED status; a P0/P1 case cannot be Pass without pasted run output.
| TC | Priority | Scenario | Expected | Evidence tier | Actual Result | Result |
|---|---|---|---|---|---|---|
| A-01 | P0 | Balance = 0 renders 0.00, not "no funds" | shows 0.00 | EXECUTED | ... | Blocked |

## Test Execution Summary
- Executed on: -
- Runner/command + pasted output: -
- P0 cases: 0/1 EXECUTED-pass
- Open failures / blocked / UNVERIFIED: A-01 Blocked - not executed yet

## Provider review recipe (self-review input, NOT sign-off)
Fill only if you ran the provider's built-in review before handoff
(Codex `/review`, Claude Code `/code-review`). It is a self-check to catch
obvious issues early; it does not replace QC and does not certify "tested".
- Recipe run: `/review` | `/code-review` | not run | UNAVAILABLE (headless) -> fell back to manual self-review
- Issues surfaced & fixed: <list, or "none">
- Issues surfaced & deferred (with reason): <list, or "none">
- Note: the recipe does not know the boundary/Falsy/evidence gates above; those still apply.

## Code Review
- Reviewed on: -
- Critical issues found: not reviewed yet
- Resolution: N/A

## Amendment Log
- None.
