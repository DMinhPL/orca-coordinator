# Context Budget Rules

Optimize context by relevance, not by skipping required evidence.

## Shared rules
- Read the smallest architecture slice required for the current decision.
- Prefer exact files/symbols/sections over repository-wide scans.
- Do not reread unchanged docs or successful logs unless a new question requires them.
- Summarize handoffs; do not forward full worker transcripts.
- Run focused tests first. Run broad/full suites only when risk, dependency surface, or repository policy requires them.
- Stop discovery when the next action is sufficiently supported by evidence.
- Record why broader inspection/testing was necessary when it materially increases cost.

## Role budgets
- Lead: consume specialist summaries + lifecycle state; avoid source-code deep dives unless needed to route a blocker.
- BA: inspect behavior/architecture surfaces needed for requirements; avoid implementation-level exhaustiveness.
- Dev: inspect direct dependencies and nearest analogous implementation; no full-repo comprehension goal.
- QC: delta-first; open extra files only to verify a concrete dependency, missing surface, or finding.
