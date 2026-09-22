# Lead Review Gates

Gates run in order. A failed gate means re-dispatch or block — never Lead doing
the specialist work itself, and never accepting output "close enough".

## Gate 0 — Role load & contract gate (NEW, runs on every worker)
Before treating any worker output as real work, verify:
- The worker emitted a `ROLE CONTRACT ACK — <ROLE>` block as its first output.
- The ACK lists `references/shared/role-contract.md` and the correct role file among files actually read.
- The ACK's one-sentence objective matches the dispatched task.

If the ACK is missing or inconsistent, the worker did not load its skill.
Result = INVALID; re-dispatch with the Role Bootstrap block. Do not proceed.
This gate is separate from worker *identity* verification (`worker-show
--exactWorker`): identity proves the right model ran; this gate proves the right
role + rules entered its context. Both must be green.

## BA gate
Before Dev starts, verify BA output has: the ACK, objective, scope/non-goals, testable acceptance criteria (given/when/then with explicit pass/fail), the mandatory edge-case list per value-bearing rule, dependencies, the Assumptions register, risks, and open questions. Reject vague untestable criteria ("should work", "handle properly") and any value-bearing rule with no edge-case enumeration — that gap is what lets the Balance=0 class of bug through at the source. Run `tools/validate_worker_output.py --role ba <artifact>`. Block Dev if unresolved questions materially affect implementation.

## Dev gate
Before QC starts, verify Dev reports: the ACK, changed files, implementation summary, EXECUTED validation evidence, the boundary matrix + Falsy Trace when the change has any truthy/falsy check on possibly-`0`/`""`/`false`/`null` values, the Assumptions & Risk Register, deviations, and unresolved risks. Reject any "tested/passed" claim with no pasted run output — that is REASONED-ONLY, not done. Do not redo the checks in Lead; re-dispatch Dev.

## QC gate
Before final success, require QC `worker_done` and a clear PASS/CONDITIONAL/FAIL/BLOCKED result. A PASS is only acceptable if the QC report satisfies `references/shared/role-contract.md` §6: full boundary matrix (no blank cells), correct Falsy Trace where applicable, EXECUTED evidence on money/state/coercion cells, no risk-bearing UNVERIFIED left as passing, and no Dev-document-as-evidence. A PASS that fails any of these is INVALID; re-dispatch QC. Lead must not run an independent review to "confirm" a weak QC PASS.

## Machine acceptance gate (NEW)
Every Dev and QC artifact must pass `tools/validate_worker_output.py --role <role> <artifact>`
before its `worker_done` is accepted. A non-zero exit = INVALID artifact =
re-dispatch. The validator is a linter (raises the floor), not a proof of
correctness; it does not replace the QC gate above.

## Documentation gate
Do not mark `Status: Implemented` until latest required QC is complete, no critical review issue remains, required P0 checks are EXECUTED and pass, and both artifacts pass the validator.
