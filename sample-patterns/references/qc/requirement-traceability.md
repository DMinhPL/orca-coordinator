# Requirement Traceability

Derive verification from approved requirement/acceptance criteria, not from Dev's implementation explanation.

For each acceptance criterion classify:
- `covered-pass`
- `covered-fail`
- `not-testable` with reason
- `missing-implementation-surface`
- `ambiguous` requiring Lead decision

Inspect both changed code and credible required surfaces that did not change. A clean diff is not sufficient if an acceptance criterion has no implementation/evidence path.
