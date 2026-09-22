# Workflow Modes and Gates

## Primary coordinator-only gate

Apply `references/shared/primary-session-policy.md` to every workflow. Primary coordinates only. Every BA/Dev/QC phase must be a fresh supervised worker started through Orca. Reusing a worktree does not authorize reusing Primary or an ordinary chat session as the worker. If worker creation fails, stop/recover/report; never fall back to direct specialist execution in Primary.

For new work or review on another branch, Primary stays on its branch and the target branch runs in a separate worktree. Before selecting/creating that worktree, apply `references/shared/workspace-pool-policy.md`: inventory existing worktrees, show reusable workspace Git state, ask the user to choose a workspace when none was specified, and ask how to prepare/checkout it before changing branches. Prefer reuse over creating a new worktree.

## Workspace pool allocation gate

Before the first repository-backed specialist dispatch for a new task:

1. List registered project worktrees.
2. Exclude Primary from the reusable execution pool.
3. Inspect each reusable workspace for branch, upstream/tracking, current commit, staged, unstaged, and untracked state.
4. Show the compact workspace inventory to the user.
5. If the user did not name a workspace, ask which existing workspace to use.
6. If the selected workspace must move to another branch, ask for checkout strategy before changing it.
7. Never auto-stash/reset/clean a dirty workspace.
8. Detect when the target branch is already attached to another worktree.
9. Create a new workspace only with explicit user approval or when no existing workspace can be used safely.
10. Once selected/prepared, start a fresh supervised worker in that worktree; never reuse an old chat session as the worker.

A hidden/closed Orca session does not make a registered worktree unusable. If the worktree still exists and Git registers it, it remains eligible after Git-state verification.

## Coordinator resume/recovery gate

When the current Lead/Primary session is new, reopened, or replacing a closed coordinator and the user asks to continue previous work:

1. Confirm Orca runtime readiness. On packaged Windows, prefer the `orca` executable that `Get-Command orca` resolves.
2. Inspect existing orchestration Runs before creating anything new.
3. Identify the Run that matches the current objective/worktree/task context.
4. Bind/use that Run with the locally supported `run-use` command. Use takeover/recovery flags only when the installed Orca guide explicitly says they apply to that Run type.
5. Inspect Tasks and active Dispatches.
6. Resume the coordinator wait loop for unsettled Dispatches.
7. Create a new Run only if no matching active or recoverable Run exists.

Never use conversation history alone to resume lifecycle ownership. Never duplicate an active workflow just because the previous Lead session was closed.

### Mandatory coordinator wait loop

After dispatching any supervised worker, Lead must keep the workflow open until every expected Dispatch reaches a terminal lifecycle outcome.

- Use the locally supported blocking `check --wait` flow for `worker_done`, `question`, and `escalation`.
- Process the whole returned Delivery and acknowledge it only after required actions are handled.
- A timeout or empty checkpoint is NOT completion. Inspect worker/task state; if the worker is still alive, enter another blocking wait.
- Do not rapidly poll, restart, or self-complete the specialist role.
- Do not issue a final success report while any required Dispatch is still `ready`, `dispatched`, running, or otherwise unsettled.
- After accepted `worker_done`, either reuse that exact terminal for an immediate next Dispatch or release it before continuing/finalizing.

## Global phase gate

Every specialist phase is asynchronous and authoritative for its own role.

1. Lead dispatches the specialist through Orca orchestration.
2. Lead waits for that specialist's `worker_done` event.
3. Lead reads the specialist report/evidence.
4. Lead may check completeness/consistency of the report, but MUST NOT redo the specialist's work as a substitute.
5. Only then may Lead advance to the next phase.

If a worker crashes, times out, or never returns `worker_done`, Lead must retry/re-dispatch that same role when reasonable, or report the blocker to the user. Lead must not replace the missing specialist by doing that specialist's work itself.

## Mandatory automatic stage continuation

Treat each workflow as an executable state machine, not a sequence of suggestions. Keep `current_stage` and `remaining_stages` conceptually explicit.

After an accepted `worker_done`:
1. Mark only that phase settled.
2. Resolve the next required stage immediately.
3. Release/record cleanup for the completed worker.
4. If `remaining_stages` is non-empty, create the next Task and start the next fresh worker immediately.
5. Enter the blocking `check --wait` loop immediately after the new dispatch.
6. Do not require a user nudge to continue an already-approved workflow.

Forbidden terminal patterns:
- `BA completed; Dev can now start.` -> dispatch Dev now.
- `Dev completed; QC is now eligible/ready to start.` -> dispatch QC now.
- `Dev rework completed; next step is QC.` -> dispatch a fresh QC verification now.
- `check --peek` -> report -> end turn while a Dispatch or downstream stage remains.

Finalization requires BOTH:
- `remaining_stages` is empty; and
- no required Dispatch is `ready`, `dispatched`, `running`, `waiting`, `outcome_unknown`, or otherwise unsettled.

`--peek`/one-shot checks are diagnostics only. They may inspect state, but they never replace the blocking coordinator wait loop. A timeout/empty wait is a checkpoint; if the worker remains active, wait again.

## QC delta-only and retry gate

For every QC phase, Lead sends only:
- the current `git diff`;
- relevant sections of `ba/requirement.md`;
- relevant sections of `dev/development.md`;
- concise test/check results needed for the changed behavior.

QC must not rescan the full repository by default and must not ingest full worker transcripts or large successful test logs.

A single QC dispatch performs one substantive verification attempt. On FAIL/BLOCKED/ambiguity, QC gathers minimal evidence, reports to Lead, and stops. QC does not fix code and does not retry until success. If Lead sends Dev back for a fix, any re-verification is a NEW QC dispatch.

## Standard (default)

User -> Lead -> BA -> Lead -> Dev -> Lead -> QC -> Lead -> User

Use for feature work, non-trivial bugs, refactoring, architecture changes, or tasks requiring analysis before coding.

Mandatory gates:
- BA `worker_done` before Dev starts.
- Dev `worker_done` before QC starts.
- QC `worker_done` before Lead reports validation/final success.
- Required documentation exists and is current before final success.

## Simple

User -> Lead -> Dev -> Lead -> QC -> Lead -> User

Use only when the user's requirement is already explicit and confirmed and no separate BA investigation is needed.

Mandatory gates:
- Dev `worker_done` before QC starts.
- QC `worker_done` before Lead reports validation/final success.
- Lead may persist the user's already-confirmed requirement into `ba/requirement.md`, but must not invent or derive new business rules in place of BA.


## Review-fix

User -> Lead -> Dev -> Lead -> QC -> Lead -> User

Use for code-review/fix-bug work when the defect and expected behavior are already clear enough that separate BA analysis would duplicate context.

Mandatory gates:
- Dev `worker_done` before QC starts.
- QC receives delta-only context.
- QC performs one substantive verification attempt per dispatch.
- On QC FAIL/BLOCKED, QC reports to Lead and stops.
- Lead decides whether to ask the user, re-dispatch Dev, or stop.
- After any Dev fix, Lead starts a fresh QC dispatch for re-verification.
- No QC `worker_done` means no final validated-success claim.

## Research-only

User -> Lead -> BA -> Lead -> User

Use for analysis, investigation, requirement clarification, architecture review, or development documentation without code changes.

Mandatory gate:
- BA `worker_done` before Lead reports the research result.
- Documentation completion still applies. `dev/development.md` must clearly state that implementation was not performed and remain Draft/Confirmed, never Implemented.

## Cross-branch review/test

Use when Primary is on branch A and the user asks to review or test branch B.

User -> Lead (Primary on A) -> fresh QC worker (separate worktree on B) -> Lead -> User

Rules:
- Primary MUST remain on branch A.
- Create or reuse a separate worktree for branch B.
- Start QC as a fresh supervised worker in branch B's worktree.
- Start BA only if requirement/architecture clarification is materially required.
- Do not start Dev unless the user asks to fix findings.
- Never checkout branch B inside Primary to perform review/testing.
- QC `worker_done` is mandatory before Lead reports Pass/Fail/Blocked.

## QC-only

User -> Lead -> QC -> Lead -> User

Use for review or verification of existing changes without new implementation.

Mandatory gate:
- QC `worker_done` before Lead reports Pass/Fail/Blocked.
- If feature documentation already exists, update it with the QC evidence. If it does not exist, create the required two-file package with minimal traceability and mark unknown/unconfirmed items explicitly.

## QC authority boundary

Once QC is dispatched, QC owns quality validation for that phase.

Lead MUST NOT run tests, lint, typecheck, diff validation, code review, browser checks, API checks, or any other QC validation as a substitute for QC.

Lead may inspect QC's returned evidence after `worker_done` to verify the report is internally consistent. That inspection is not a second QC pass and must not produce an independent Pass/Fail conclusion.

No QC `worker_done` => no QC conclusion => no final validated-success claim.

## Rework loop

QC -> Lead -> Dev -> Lead -> QC -> Lead

If QC finds defects:
1. QC reports defects only to Lead and returns `worker_done` with Fail/Blocked as appropriate.
2. Lead decides whether the issue is a technical fix or a user decision.
3. Technical fix: Lead dispatches Dev with the QC findings.
4. User/business decision: Lead escalates to the user before Dev changes behavior.
5. After Dev returns `worker_done`, Lead dispatches QC again.
6. Final success requires the latest QC run to return `worker_done` with acceptable evidence.

## Worker cleanup

After Lead consumes and verifies a worker's `worker_done` report, call the locally supported Orca worker-release flow. Track task outcome and cleanup outcome separately.

- `RELEASED`: release confirmed.
- `RETAINED_USER_OWNED`: `user_takeover`/`user_owned`; task result remains settled, do not retry endlessly, and do not reuse that terminal.
- `RELEASE_NOT_VERIFIED`: `release_unknown`/`tab_not_found`; inspect worker/process state once and report the anomaly without converting an accepted `worker_done` into task failure.
- `RELEASE_FAILED_ACTIVE`: worker/process still appears active after failed cleanup; report the lifecycle blocker.

Future work after any non-released outcome must use a fresh worker session.

## Token-optimized execution profile

Use the configured default model/effort first. Do not escalate a role simply because the overall task is large.

- Lead default: Codex `gpt-5.6-luna` / `medium`.
- BA default: Codex `gpt-5.5` / `high`; escalate BA only to `xhigh` when its configured escalation condition is observed.
- Dev default: Codex `gpt-5.6-luna` / `medium`. Escalate in stages only when needed: Luna `high` for complex coding; Terra `high` (preferred) or Sonnet `high` for hard debugging/architecture-heavy work; Sol `high` (preferred) or Opus `high` only for very hard or repeatedly failed work. Read the exact selection rules from `agents-models.yaml`.
- QC default: Claude `claude-sonnet-5` / `medium`; escalate QC only to `high` when its configured escalation condition is observed.

Prefer `simple` mode for small explicit changes so BA is not started unnecessarily. Keep all mandatory worker_done, QC authority, documentation, and cleanup gates unchanged.

Avoid duplicate context consumption. Lead should provide each worker with the approved requirement, the immediately relevant prior-phase summary, required file paths/evidence, and open questions. Do not forward full prior transcripts unless the worker needs them.
