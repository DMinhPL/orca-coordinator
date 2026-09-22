# Lead Task Triage

Use this before choosing workflow, models, or workers.

## Triage questions
1. Is the requested outcome explicit enough to implement without inventing business behavior?
2. Is this analysis-only, review-only, implementation, review+fix, or a full feature?
3. What is the smallest change surface: single file, module, cross-module, cross-system?
4. Does the task touch auth, payments, persistent data, caching, concurrency, distributed state, migration, deployment, or security boundaries?
5. Is there an existing worktree/Run that must be resumed rather than recreated?

## Workflow routing
- `research_only`: no implementation requested; BA investigates and reports.
- `qc_only`: implementation already exists and user asks only for review/verification.
- `simple`: requirement is explicit; localized low-risk implementation; BA may be skipped.
- `review_fix`: defect/expected behavior is clear; Dev fixes, then independent QC.
- `standard`: default for ambiguous, multi-module, architecture-sensitive, or feature work.

## Do not over-orchestrate
Do not spawn BA merely to restate a precise user request. Do not spawn Dev for review-only work. Do not spawn QC for research-only work.
