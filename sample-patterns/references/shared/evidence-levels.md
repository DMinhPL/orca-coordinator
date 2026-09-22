# Evidence-Based Decisions

Label material technical claims internally and in reports when ambiguity matters:

- `confirmed`: directly supported by requirement, code, test, runtime state, logs, or authoritative configuration.
- `likely`: best-supported explanation with meaningful evidence, but not proven.
- `hypothesis`: plausible explanation awaiting targeted verification.
- `unknown`: insufficient evidence to choose safely.

## Execution-grade evidence (for "tested"/"verified" claims)
`confirmed` for *runtime behavior* requires EXECUTION, not reasoning. See
`references/shared/role-contract.md` §1–2. Operationally:

- **EXECUTED** — the check was actually run and its raw output is pasted in the artifact. Only this justifies "tested"/"verified"/"passes".
- **STATIC** — proven by reading code/spec/type only. Valid for structural facts; NOT valid for money/auth/state/type-coercion runtime behavior.
- **REASONED-ONLY** — traced in the head, not run. Never justifies a PASS on a risk-bearing case.
- **UNVERIFIED** — no basis; must surface as RISK.

A claim about the shape/value of external data (backend, DB, config, upstream) is a `hypothesis` until a real captured sample makes it `confirmed`. Guessing the type (`'0'` vs `0`) is not evidence.

## Rules
- Never present `likely`, `hypothesis`, or `REASONED-ONLY` as confirmed/tested.
- Never convert `unknown`/`UNVERIFIED` into a silent implementation decision when it can affect behavior, data, security, payment, compatibility, or rollout.
- State the minimal evidence needed to promote a hypothesis to confirmed.
- Prefer one discriminating check over many speculative checks.
- Another worker's document is context, not execution evidence.
- Lead routes unresolved material uncertainty to the appropriate specialist or User.
