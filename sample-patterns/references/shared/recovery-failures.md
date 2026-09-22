# Recovery & Failure Playbook

Use for recreated Lead sessions, orphaned workers, missed deliveries, runtime startup issues, hook failures, or uncertain Dispatch outcomes.

## Coordinator recovery
1. Treat Orca orchestration state as source of truth.
2. Inspect existing Runs before creating a new one.
3. Bind/use the matching Run and inspect Tasks/Dispatches.
4. Reconcile expected workers with actual lifecycle state.
5. Resume blocking wait for active workers; do not redo completed work.

## Runtime readiness
A process existing is not enough. Require runtime `ready`, reachable, and a valid runtime identity before starting new orchestration work. If runtime remains `starting`/unreachable, stop orchestration startup and report the runtime blocker. Do not fall back to ordinary chat handoff.

## Uncertain worker outcome
For `outcome_unknown`, missed `worker_done`, or interrupted coordinator:
- inspect Task/Dispatch/worker state;
- recover/ack pending deliveries when supported;
- never infer PASS/completion from transcript text alone;
- re-dispatch only when lifecycle evidence shows the previous attempt cannot continue.

Hook warnings are evidence, not automatically root cause. Separate hook failure from runtime/worker lifecycle evidence.

## Worker start failure: `agent_prompt_stalled`
Treat `agent_prompt_stalled` during `dispatch_input` as a worker-start failure, not as specialist execution and not as a missing `worker_done` from a valid worker.

1. Inspect the exact Dispatch with the locally supported worker-show/status flow.
2. If the Dispatch is `failed` and `capability_revoked_at` is set, the worker no longer has orchestration authority.
3. Do not wait for `worker_done` from that attempt and do not accept later terminal output as the BA/Dev/QC result.
4. Attempt release/cleanup once using the exact Dispatch identity.
5. If retry is appropriate, create a fresh worker attempt for the same role only after the previous Dispatch is lifecycle-terminal. Never reuse the failed terminal.
6. Keep provider/model/effort unchanged unless the user explicitly approves a fallback or the configured escalation policy applies for a reasoning failure. Infrastructure/injection failure alone is not model escalation.

When the same provider repeatedly fails at `dispatch_input` while another provider starts normally in the same workspace, classify the evidence as provider-integration/runtime-specific until stronger evidence exists. Do not blame the repository, role logic, or workspace without supporting evidence.

## Cleanup anomaly: `identity_unproven`
If worker release returns `state: retained`, `reason: identity_unproven`, and `processAction: none`:

- treat the specialist/task outcome and cleanup outcome separately;
- inspect worker/terminal observation once;
- if the exact worker is already observed `exited`, classify cleanup as `RETAINED_IDENTITY_UNPROVEN` rather than active execution;
- do not repeatedly call release for the same retained identity;
- do not reuse that terminal for future work;
- use a fresh worker for any retry/rework;
- if a residual UI tab remains, report it as residual UI/lifecycle state rather than proof that the worker is still running.

`identity_unproven` is not the same as `user_takeover`: the former means Orca cannot prove the current terminal/process identity well enough to act safely; the latter means Orca considers the terminal user-owned.

