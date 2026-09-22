# Coordinator Continuity and Run Recovery

Use this reference whenever Lead starts supervised work, a Primary session is reopened/recreated, or the user asks to continue prior orchestration.

## Mental model

- Primary/Lead session: coordinator surface the user talks to.
- Run: durable coordinator namespace/inbox for one supervised workflow.
- Task: one work item (BA, Dev, QC, or another bounded unit).
- Dispatch: one supervised attempt of one Task assigned to one worker.
- Worker terminal/session: execution surface owned by an active Dispatch.

A new chat session is not automatically the owner of an old Run.

## New supervised workflow

1. Resolve the installed Orca CLI. On packaged Windows, prefer `orca`.
2. Confirm runtime readiness with `orca status --json`.
3. Create one Run for the workflow.
4. Create Tasks.
5. Start supervised workers with the exact configured provider/model/effort.
6. Wait for lifecycle messages until all expected Dispatches settle.

## Resume after Lead was closed or recreated

1. Do NOT create a new Run immediately.
2. Inspect existing Runs.
3. Match the intended workflow using objective plus task/worktree context.
4. Inspect the candidate Run's Tasks and Dispatches.
5. Bind/use the matching Run with the locally installed/version-matched Orca guidance.
6. Resume waiting for active Dispatches.
7. If no matching active/recoverable Run exists, then create a new Run.

Use takeover/recovery options only when the installed Orca guide says the specific Run requires them. Do not guess recovery flags.

## Source of truth

Use Orca orchestration state as lifecycle truth. Conversation history may explain intent but must not be used to claim that a worker is completed, failed, released, or still owned.

## Existing worktree versus existing chat

Reuse the existing worktree when the task must continue on that checkout. By default, do not reuse an existing ordinary chat/agent session as the worker. Start a fresh supervised worker in that existing worktree so Orca can enforce:

- Task/Dispatch provenance;
- `worker_done` authority;
- configured provider/model/effort;
- worker lifecycle cleanup.

Reuse an existing terminal only when the user explicitly asks for it or the workflow has a concrete reason and the installed Orca guide confirms the limitations.

## Wait discipline

After each supervised dispatch, Lead must remain in the coordinator loop until a lifecycle outcome arrives. Use the locally supported blocking `check --wait` flow for active supervision. Timeout/empty wait windows are checkpoints, not completion. If the worker is alive, wait again. Never replace a slow specialist with Lead's own work.

After an accepted `worker_done`, do not end the Lead turn merely because the current worker settled. Resolve the active workflow's next required stage immediately. If another stage remains, release/record cleanup for the completed worker, start the next fresh worker, and re-enter `check --wait` without requiring another user message. A diagnostic `--peek`/one-shot check must never be the final lifecycle action while required work remains.

## Failure behavior

If Run binding, Dispatch authority, or worker ownership cannot be proven:

- stop lifecycle mutation for that branch;
- report the Run/Task/Dispatch identifiers that are known;
- explain what ownership/binding is missing;
- do not silently create a duplicate Run;
- do not self-complete the specialist role.
