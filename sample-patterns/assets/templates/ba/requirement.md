# Requirement — {Feature Name}

> Feature: {Feature Name} · Branch: {branch-name} · Date: {YYYY-MM-DD} · Status: Draft · Ticket: {ticket-or--}

## ROLE CONTRACT ACK — BA
<paste the ACK block emitted at bootstrap>

## Background
- ...

## Current behavior
- Statement [fact/inference/assumption] — source if fact: ...

## Required behavior
- ...

## Business Rules
1. Rule: ... — Applies to value(s): ...

## Acceptance Criteria (must be testable — given/when/then, explicit pass/fail)
| AC | Given (input/state) | When (action) | Then (observable result) | Pass/Fail check |
|---|---|---|---|---|
| AC-1 | Balance = 0 | screen loads | shows "0.00" | renders "0.00", NOT "no funds" |
| AC-2 | ... | ... | ... | ... |

## Mandatory edge cases per value-bearing rule (upstream feed for QC Phase A)
| Rule / field | zero | empty | null/missing | negative | boundary | error | Expected handling |
|---|---|---|---|---|---|---|---|
| Balance | 0 -> "0.00" | ... | ... | ... | ... | ... | ... |

## Assumptions register
| Assumption | About (rule/data/behavior) | Impact if wrong |
|---|---|---|
| e.g. Balance is a number, not string | external data shape | wrong falsy handling downstream |

## Dependencies
- ...

## Out of Scope
- ...

## Risks
- ...

## Open Questions
- None.

## Amendment Log
- None.
