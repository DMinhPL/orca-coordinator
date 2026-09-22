# Developer Engineering Principles

Implement the smallest safe change that satisfies the approved requirement.

## Principles
- Preserve established local architecture and naming unless the requirement justifies change.
- Prefer causal fixes over symptom masking.
- Avoid unrelated cleanup in feature/bug work.
- Maintain backward compatibility unless a breaking change is explicitly approved.
- Treat existing tests, types, schemas, API contracts, and config as constraints until proven otherwise.
- Make failure behavior explicit: invalid input, missing data, timeout, partial failure, cancellation, and retry.
- Keep observability proportional to runtime risk; do not hide failures behind silent catch/fallback behavior.
- Report any assumption that materially affects behavior.
