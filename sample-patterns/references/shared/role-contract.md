# Role Contract — Mandatory Enforcement Spine

This file is the single source of truth for how BA/Dev/QC workers must load
their role, state claims, and gate their own verdicts. Every specialist worker
MUST read this file as part of its Role Bootstrap. Lead MUST NOT accept a
worker's `worker_done` unless the worker's output satisfies the rules here.

These rules exist because a role reference is a *document*, not a hard control.
A worker can read "verify independently" and still rationalize a shortcut. The
gates below convert soft guidance into checkable structure: no valid artifact,
no accepted `worker_done`.

---

## 1. Operational definitions (no soft synonyms)

A worker MUST use these words with exactly these meanings. Any other usage is a
contract violation.

- **EXECUTED** — the check was actually run and its raw output is pasted into
  the artifact (test runner output, dry-run/REPL transcript, HTTP response,
  build/log line). A described-but-not-shown run does NOT count.
- **REASONED-ONLY** — the worker mentally traced the behavior but did not run
  it. This is NOT "tested" and can never justify PASS on a risk-bearing case.
- **UNVERIFIED** — the worker could not obtain evidence. Must be surfaced as a
  RISK, never silently dropped, never marked PASS.

Banned unless backed by EXECUTED evidence in the same artifact:
`tested`, `verified`, `confirmed working`, `passes`, `works as expected`,
`đã test`, `đã verify`, `chạy ok`. If there is no pasted run output next to the
claim, the claim is REASONED-ONLY by definition and must be labeled so.

A worker may NOT cite another worker's document as evidence of execution.
"Dev says it was tested" / "theo development.md" is context, not evidence.

## 2. Evidence tiers per claim

Every material behavioral claim carries one tier (see also
`references/shared/evidence-levels.md`):

- `EXECUTED` — run output present.
- `STATIC` — proven by reading code/spec/type only (acceptable for pure
  structural facts, never for runtime behavior of money/auth/state/coercion).
- `REASONED-ONLY` — traced, not run.
- `UNVERIFIED` — no basis.

Rule: for any surface touching money, balance, auth, permissions, persistent
state, data integrity, type coercion, or release rollout, a PASS requires
`EXECUTED`. `STATIC` or `REASONED-ONLY` on those surfaces caps the verdict at
`CONDITIONAL` and forces a RISK entry.

## 3. External-data assumption rule

Any statement about the *shape or value of data coming from outside the changed
code* (backend response, DB row, config, upstream API, user input) is an
ASSUMPTION until proven with a real captured sample.

- You may not test against an imagined payload. `Boolean('0')` vs `Boolean(0)`
  is decided by the real payload, not by what the worker guessed the type is.
- Every such assumption goes in the Assumptions & Risk Register with its
  evidence tier. An unproven assumption can never underpin a PASS or a "tested"
  claim.

## 4. Truthy/falsy & boundary standard (the "Balance = 0" rule)

Whenever the change contains ANY truthy/falsy decision on a value that could be
`0`, `""`, `false`, `NaN`, `null`, or `undefined` — this includes `if (x)`,
`!x`, `x ? a : b`, `Boolean(x)`, `x && ...`, `x || default`, `??`, loose `==` —
the worker MUST emit a Falsy Trace table enumerating each value and the branch
it takes:

| Input value | Coerces to | Branch taken | Correct? |
|---|---|---|---|
| positive | true | ... | ... |
| `0` | false | ... | ... |
| `""` | false | ... | ... |
| `false` | false | ... | ... |
| `NaN` | false | ... | ... |
| `null` | false | ... | ... |
| `undefined` | false | ... | ... |

For the known incident (`Boolean(balance?.Balance)` with `Balance = 0`) this
table forces the worker to write `0 -> false -> hasBalance=false -> wrong`.
It cannot be skimmed past.

## 5. Boundary equivalence matrix (mandatory for every touched variable)

For each variable/field the change reads or decides on, fill every class. Empty
cells are not allowed — use `EXECUTED`, `REASONED-ONLY`, or `UNVERIFIED`, plus a
Result. A matrix with any blank cell is an INVALID artifact.

| Variable | positive | zero (0/0.00) | negative | null | undefined | empty "" | NaN | error path |
|---|---|---|---|---|---|---|---|---|
| Balance | ... | ... | ... | ... | ... | ... | ... | ... |

A cell may be marked `N/A` only with a one-line reason why the class is
impossible for that variable (e.g. "field is unsigned enum, negative unreachable
by schema" + tier `STATIC`).

## 6. Verdict / status gate

- `PASS` is allowed ONLY when: every required boundary cell is `EXECUTED` or a
  justified `N/A`; the Falsy Trace (if applicable) is present and all branches
  correct; no `UNVERIFIED` risk-bearing item remains; no unproven external-data
  assumption underpins the result.
- If any risk-bearing cell is `REASONED-ONLY`/`STATIC`/`UNVERIFIED` -> verdict is
  at most `CONDITIONAL`, with the gaps listed.
- Any proven defect, or any BLOCKER preventing verification -> `FAIL` / `BLOCKED`.
- The phrase "looks fine" / "có vẻ ổn" is banned as a basis for any verdict.

## 7. Role Contract Acknowledgment (Bootstrap output — required BEFORE work)

Before doing ANY task work, a specialist worker MUST emit this block as its
first output. Lead does not release the worker into task execution until this
block is present and consistent with the worker's role file. This proves the
role + rules actually entered the worker's context rather than sitting unread.

```text
ROLE CONTRACT ACK — <BA|Dev|QC>
- Role files loaded: <list exact paths actually read, incl. references/shared/role-contract.md>
- I will label every behavioral claim EXECUTED / STATIC / REASONED-ONLY / UNVERIFIED.
- I will not call anything "tested/verified" without pasted run output.
- I will treat all external-data shapes as assumptions until proven with a real sample.
- <QC only> I will derive test cases from acceptance criteria BEFORE reading development.md, and Dev notes may only ADD cases, never remove or weaken a derived case.
- <BA only> Every acceptance criterion I write will be testable with an explicit pass/fail check, and I will enumerate the mandatory edge cases (zero/empty/null/error/boundary) for each rule that has them.
- I will emit the Falsy Trace for any truthy/falsy check on possibly-0/""/false/null values.
- I will fill every boundary matrix cell; blanks = invalid artifact.
- I will cap the verdict at CONDITIONAL if any risk-bearing cell lacks EXECUTED evidence.
- Task understood in one sentence: <restate the objective>
```

If a worker starts producing findings/implementation without this ACK, Lead
treats the output as INVALID and re-dispatches. Missing ACK = unloaded skill.

The `Role files loaded` list in this ACK is what Lead renders on the **Contract
ACK receipt** (see `SKILL.md` → "Mandatory Contract ACK receipt"). This is the
only checkpoint that answers "did the worker load its role skill?" — the launch
receipt's `exactWorker`/`Injected` fields do not, because at launch the worker
has read nothing yet. The list a worker declares here must match the files Lead
injected in the dispatch; a mismatch is an INCONSISTENT ACK and blocks work.
The ACK is a self-report plus a structural form check — it proves delivery and
acknowledgment, never final compliance. Compliance is proven only by
`tools/validate_worker_output.py` on the artifact at `worker_done`.
