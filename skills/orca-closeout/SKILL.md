---
name: orca-closeout
description: >-
  Closing an Orca task, owned by Lead. Use this before reporting a final result to
  the user: it checks the documentation status gate, validates traceability,
  closes risks, runs the per-task retrospective that calibrates the complexity
  rubric, and releases workers. Trigger it when a task is verified and about to be
  reported complete, and when a batch of tasks warrants reviewing whether the
  pod's sizing and escalation rates are healthy.
---

# Closeout

Owner: **Lead**. Parameters: `documentation.status_gate`, `retrospective`,
`cleanup_policy` in `references/agents-models.yaml`.

Short phase, and the only mechanism the pod has for getting better rather than merely
faster.

## 1. Status gate

`documentation.status_gate` — all must hold before status becomes implemented:

- ☐ QC worker done (verified, not timed out — a timeout is a checkpoint)
- ☐ No open critical review issues
- ☐ All P0 defects pass
- ☐ No allowlist violations
- ☐ Traceability complete, from band M

Also `coordinator_continuity.no_final_while_required_dispatch_unsettled`: no final
report while any required dispatch is unsettled.

## 2. Traceability validation

Walk `traceability.csv` against the two obligations:

- **Coverage** — every acceptance criterion has a test. A gap here is a P1.
- **Justification** — every changed file traces to a requirement. An unmatched file
  is scope creep that got through; record where it entered, because that tells you
  which control failed.

Any requirement not delivered becomes an explicit carry-forward task, not a footnote.

## 3. Risk closure

Each risk: `did_not_occur` · `occurred_response_worked` · `occurred_response_failed` ·
`carried_forward` · `superseded`.

The last three are the interesting ones. A response that failed is a lesson about the
response. A risk that materialised through a path nobody considered is a lesson about
the BA probe list, and it should end up *in* that list. A risk carried forward to
nobody is just closed with extra words — give it an owner outside the task.

## 4. Retrospective — the part that compounds

`retrospective.per_task`, required from band M:

```
band_at_intake        L (14)
band_final            L (15)
escalations_used      1 of 2      dispatches: ba 1, dev 3, qc 2
change_requests       2  (1 allowlist amendment, 1 scope addition from QC)
mis_scored_dimensions d5 — scored 2, actually 3

generalizable_probe   "How many ways can the entity under change come into
                       existence?"  BA looked at the auth module but never at
                       account creation paths. This generalises well beyond auth.
```

The `generalizable_probe` is the deliverable. A note about this particular auth bug
helps nobody; a question that catches the same *class* of miss on an unrelated task
is worth the five minutes.

If a lesson should change a skill file or a YAML condition list, **change it**. A
lesson recorded and never applied is the commonest form of organisational amnesia.

## 5. Worker cleanup

`cleanup_policy`. Release each worker after verified done, and record the outcome:
`RELEASED`, `RETAINED_USER_OWNED`, `RELEASE_NOT_VERIFIED`, `RELEASE_FAILED_ACTIVE`.
An accepted worker-done result is immutable during cleanup — cleanup never revises a
verified result. Report any unreleased terminal handle as a blocker.

## 6. Final report

One report, from Lead only, **printed to the user** — this is a spoken summary, not a
substitute for the persisted files under `.docs/features/...` or `decisions.jsonl`,
which remain the durable audit trail. **This format is mandatory in every mode and
band** — `simple`, XS and one-file fixes included. Never replace it with prose
paragraphs. Print it as rendered markdown (not inside a code fence), in this shape:

````markdown
## <outcome icon> <feature slug> — <outcome in ≤8 words, e.g. "fixed, QC-verified, not committed">

<one plain sentence: what the user will notice, e.g. "The All statuses and All types
dropdowns now show the same chevron as All priorities.">

| | |
|---|---|
| 🧭 Workflow | <mode> · band <band> · <Lead → Dev → QC → Lead, roles actually dispatched> |
| ⏭️ Skipped | <why a stage was skipped, e.g. "no BA — requirement was explicit"> |
| 🆔 Run / Task | `<run_id>` / `<task_id>` |
| 🌿 Branch | `<branch>` off `<base>` · <workspace> |
| 💾 Git | <uncommitted / committed `<sha>` / pushed> |

### 🤖 Dispatches

| # | Role | Dispatch | Worker | Checks | Result | Criteria |
|---|---|---|---|---|---|---|
| 1 | 🛠️ Dev | `<dispatch_id>` | <model>/<effort> | exact ✅ · ACK ✅ | ✅ accepted | 4/4 |
| 2 | 🔍 QC | `<dispatch_id>` | <model>/<effort> | exact ✅ · ACK ✅ | ❌ FAIL | 3/4 |
| 3 | 🔍 QC #2 | `<dispatch_id>` | <model>/<effort> | exact ✅ · ACK ✅ | ✅ PASS | 4/4 |

<one short line per non-green row, keyed by #, e.g. "#2 — AC-03: Lead gave the wrong
diff baseline; re-dispatched as #3.">

### 📝 Changes

| File | What changed | Scope |
|---|---|---|
| `<path>` | <≤10 words, e.g. "chevron icon on status/type triggers"> | ✅ in allowlist |

### 🛡️ Verification

| Check | Result |
|---|---|
| <status_gate check or executed command, e.g. `tsc --noEmit`> | ✅ / ❌ / ⚠️ not run |

### ⚠️ Notes & risks

- ⚠️ <leftover difference, risk or process note — one line each, owner if any>

↩️ **Rollback:** <the recorded rollback mechanism>

> ### ⏸ Your call
> 1. **<decision>** — <options, e.g. "commit as `fix(tickets): …` and push? yes / no">
> 2. **<decision>** — <options>
````

Rules:

- **Outcome icon** in the heading: ✅ done and verified · ⚠️ done with conditions or
  unverified parts · ❌ failed or blocked. The outcome text must state the git
  state when anything is uncommitted.
- One **Dispatches** row per dispatch **actually made**, in dispatch order. Retries
  and escalations get their own row (`QC #2`), never overwrite the earlier one. A
  skipped role (BA in `simple` mode, QC in `research_only`) gets no row — its absence
  is the `Skipped` line, not repeated in the table. Role icons: 📋 BA · 🛠️ Dev ·
  🔍 QC.
- Column values come from the return envelope and receipts: `Worker` is
  `<model>/<effort>` (add the provider only when two dispatches differ by provider);
  `Checks` is exactWorker and Bootstrap ACK (`MISSING` / `INCONSISTENT` / ⚠️ printed
  in place of ✅); `Result` is QC's verdict (`PASS` / `CONDITIONAL` / `FAIL`) or, for
  BA/Dev, the `worker_done` outcome; `Criteria` is satisfied / total.
- Keep every cell short — ids, verdicts, counts, file paths, ≤10-word phrases.
  Anything that needs a sentence goes in a note under the table or in **Notes &
  risks**. Terminal tables wrap badly, so never put a paragraph in a cell.
- Icons: use the section and role icons shown above plus the status set ✅ ❌ ⚠️ ⏸.
  Do not add others.
- **Changes** lists Dev's `files_changed`; an allowlist violation shows ❌ with the
  violated rule. Omit the table for read-only runs (`research_only`, review-only).
- **Verification** includes anything that was *not* checked (e.g. "viewed in a
  running app — ⚠️ not run"), so a PASS never implies more than was done.
- **Notes & risks** is omitted when nothing is carried forward and that is verified;
  do not print an empty section.
- Pull every field from the return envelope and the receipts already printed during
  the run (`workflows.md` § 1.3a/1.3b) — never restate from memory or re-derive.
  A field with no verified value (no `band_challenge` was raised, no risk was
  carried) is omitted, not invented as `none` unless that is itself verified.
- **Your call** is mandatory, always last, and holds one to three numbered concrete
  decisions with their options — never a closing pleasantry. G7's commit/push
  approval belongs here when the task reached a work branch and nothing has been
  committed yet. When there is truly nothing to decide, it states the one next action.
- Keep it to what changed and what is decided — this is the report, not a second
  retrospective; the `generalizable_probe` and batch-level analysis stay in § 4.

## Batch retrospective

Every `retrospective.batch.every_n_tasks` (default 15), read across tasks:

- **Which dimension is systematically mis-scored?** Adjust the rubric, not individual
  estimates. It is usually d5, verification difficulty.
- **Escalation rate** — target band 0.15–0.35. Near zero means the defaults are too
  generous and you are over-spending by default. Near one means they are too thin and
  every task pays a re-dispatch tax.
- **Where do change requests originate?** Mostly from QC means BA analysis is running
  thin. Mostly from Dev means blast-radius work is weak.
- **Did QC independence hold?** Check the provider split and the delta-only context
  actually applied. Under time pressure this is the first control to erode and the
  one most worth defending.
- **Cost share by band.** If XS and S tasks consume a disproportionate share, the mode
  downgrade rule or the defaults are wrong.
