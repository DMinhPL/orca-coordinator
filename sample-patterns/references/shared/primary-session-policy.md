# Primary Session Policy

## Core invariant

Primary coordinates. Workers execute.

Treat the Primary session as coordinator-only for all supervised engineering work. If an action changes code, performs specialist-level requirement analysis, reviews code as the authoritative reviewer, or validates implementation behavior, assign it to a fresh supervised BA/Dev/QC worker rather than executing it in Primary.

## Primary MAY

- Understand the user request only deeply enough to classify, route, and identify missing decisions.
- Inspect minimal orchestration state required to create, bind, recover, or resume a Run.
- Create Tasks/Dispatches and start, wait for, release, or recover workers.
- Answer worker questions and route all questions/blockers through Lead.
- Make Lead-level workflow, risk, model/effort, and escalation decisions.
- Inspect returned specialist evidence for completeness/consistency without repeating the specialist work.
- Report final results to the user.

## Primary MUST NOT

- Implement or modify production code.
- Review code as the final/authoritative reviewer.
- Run Dev validation as a substitute for Dev.
- Run QC verification, tests, lint, typecheck, browser/API checks, or diff review as a substitute for QC.
- Perform substantive BA analysis or invent requirements as a substitute for BA.
- Checkout another task branch inside the Primary worktree for implementation or review.
- Reuse itself as BA, Dev, or QC.
- Reuse an ordinary existing chat session as a supervised worker by default.
- Silently fall back to direct execution if Orca worker creation or orchestration fails.

## Fresh worker requirement

For every executable specialist phase:

1. Classify the task and select the smallest valid workflow.
2. Create or recover/bind the correct Orca Run.
3. Create a Task for the required role.
4. Start a FRESH supervised worker with the locally supported `orca orchestration worker-start` flow.
5. Run that worker in the appropriate worktree.
6. Wait for that exact Dispatch's `worker_done`, question, escalation, or terminal failure.
7. Process the accepted result and release the worker according to lifecycle policy.
8. Start the next required role as another fresh worker unless explicit same-terminal reuse is intentionally requested and compatible with model/effort requirements.
9. Finalize only when every required Dispatch is settled.

Apply this even when the task is trivial, the user says "check this" or "fix this quickly", only one role is required, Primary already understands the code, or an old worker/chat session already exists.

## Worktree and branch policy

Read and apply `references/shared/workspace-pool-policy.md` before allocating any repository-backed specialist worker. Worktree reuse and session reuse are separate decisions.

- Current-branch task: a fresh worker may use the current worktree when safe, but Primary itself must not execute specialist work.
- Continue existing task: reuse the existing task worktree when valid, but start a fresh supervised worker session.
- New task on another branch: keep Primary on its current branch; create or reuse a separate worktree for the target branch and start fresh workers there.
- Cross-branch review/test: keep Primary unchanged, create/reuse a separate worktree for the target branch, and start a fresh QC worker there. Start BA only if requirement/architecture clarification is materially needed; start Dev only if the user asks to fix findings.

## Worker identity is orchestration identity

Do not infer worker identity from a visible terminal, terminal title, process name, provider CLI, or terminal handle. `orca terminal create` creates a terminal resource only; it does not create a BA/Dev/QC orchestration worker.

A specialist worker is considered started only after:
- Task and Dispatch creation;
- successful `orca orchestration worker-start`; and
- inspection proves the terminal/process is bound to that exact Dispatch (use `exactWorker: true` when Orca exposes that field).

If this proof is missing, treat the specialist as NOT STARTED. Do not allow Primary to execute the requested specialist work and do not manufacture evidence by creating scratch scripts or generic worker-like terminals. Report the orchestration blocker instead.

## No-direct-fallback rule

If supervised worker creation fails, stop execution of that specialist phase. Diagnose/recover orchestration according to the recovery playbook or report the blocker. Never implement, review, test, or analyze directly in Primary as a fallback.

## Automatic continuation and finalization gate

Do not declare completion while any required Dispatch is ready, dispatched, running, waiting, or outcome-unknown, OR while the selected workflow still has a required downstream stage. `worker_done` ends one phase, not the coordinator workflow.

After accepted `worker_done`, Lead must immediately release/record cleanup, resolve the next required role, start its fresh supervised worker, and return to blocking wait. Do not end the turn with `QC is eligible to start`, `ready for QC`, `next step is Dev/QC`, or equivalent.

Only finalize when all required phases are terminal AND no required downstream stage remains.
