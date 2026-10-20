---
name: orca-closeout
description: >-
  Closing an Orca task, owned by Lead. Use this before reporting a final result to
  the user: it checks the result gate, validates runtime traceability,
  closes risks, writes the single outcome-first feature summary when applicable,
  and runs the per-task retrospective that calibrates the complexity
  rubric, and releases workers. Trigger it when a task is verified and about to be
  reported complete, and when a batch of tasks warrants reviewing whether the
  pod's sizing and escalation rates are healthy.
---

# Closeout

Owner: **Lead**. Load `python scripts/config_view.py --role closeout` for
`documentation`, `retrospective`, `cleanup_policy`, and dispatch lifecycle values.

Short phase, and the only mechanism the pod has for getting better rather than merely
faster.

## 1. Status gate

`documentation.status_gate` — all applicable checks must hold before status becomes
implemented:

- ☐ QC worker done, except in `xs_self_check`
- ☐ For `xs_self_check`: Dev worker done, machine-accepted self-revalidation passed,
  every criterion satisfied, and no unresolved band challenge
- ☐ No open critical review issues
- ☐ All P0 defects pass
- ☐ No allowlist violations
- ☐ Runtime traceability complete, from band M

Also `coordinator_continuity.no_final_while_required_dispatch_unsettled`: no final
report while any required dispatch is unsettled.

## 2. One durable feature outcome

- **XS:** do not create `.docs/features` or any durable task document. The accepted
  runtime payload is sufficient.
- **S/M/L/XL:** after the feature reaches an outcome, write exactly one `summary.md`
  with what changed, observable impact, verification, limitations, and risks.

Never create `dispatch.json`, worker-state files, or orchestration event logs inside
the project repository. Do not create separate BA, Dev, QC, decision, or traceability
files unless the user, project policy, or compliance requirements explicitly demand
them. The document is valuable only when it helps someone understand the delivered
feature; it is not proof that the process ran.

## 3. Traceability validation

From band M, walk the runtime traceability data against the two obligations:

- **Coverage** — every acceptance criterion has a test. A gap here is a P1.
- **Justification** — every changed file traces to a requirement. An unmatched file
  is scope creep that got through; record where it entered, because that tells you
  which control failed.

Any requirement not delivered becomes an explicit carry-forward task, not a footnote.

## 4. Risk closure

Each risk: `did_not_occur` · `occurred_response_worked` · `occurred_response_failed` ·
`carried_forward` · `superseded`.

The last three are the interesting ones. A response that failed is a lesson about the
response. A risk that materialised through a path nobody considered is a lesson about
the BA probe list, and it should end up *in* that list. A risk carried forward to
nobody is just closed with extra words — give it an owner outside the task.

## 5. Retrospective — the part that compounds

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

## 6. Worker cleanup

`cleanup_policy`. Release each worker after verified done, and record the outcome:
`RELEASED`, `RETAINED_USER_OWNED`, `RELEASE_NOT_VERIFIED`, `RELEASE_FAILED_ACTIVE`.
An accepted worker-done result is immutable during cleanup — cleanup never revises a
verified result. Report any unreleased terminal handle as a blocker.

## 7. Final report

One outcome-first report, from Lead only, **printed to the user**. XS keeps no durable
copy; every other band stores the same useful content in `summary.md`. Do not include
workflow, worker, dispatch, ACK, run, or task metadata unless it explains a blocker
the user must act on. Print rendered markdown in this shape:

````markdown
## <feature name> — <outcome>

<one sentence describing the observable result or the value delivered>

### What changed

| File | What changed | Scope |
|---|---|---|
| `<path>` | <short description of the meaningful change> | <user-facing / internal> |

### Verification

| Check | Result |
|---|---|
| <status_gate check or executed command, e.g. `tsc --noEmit`> | ✅ / ❌ / ⚠️ not run |

### Limitations and risks

- <only unresolved limitations, risks, or follow-up work>

**Rollback:** <include only when useful>

**Next action:** <include only when the user must decide or act>
````

Rules:

- Lead with the result and what the user or maintainer will notice.
- **What changed** lists only meaningful delivered changes. Omit the table for
  read-only work and report the useful finding instead.
- **Verification** includes anything that was *not* checked (e.g. "viewed in a
  running app — ⚠️ not run"), so a PASS never implies more than was done.
- **Limitations and risks** is omitted when nothing is carried forward and that is verified;
  do not print an empty section.
- Use verified facts from accepted return payloads. Do not expose the orchestration
  audit trail just because it exists.
- State git status only when uncommitted work, commit approval, or push approval
  changes what the user needs to do next.
- Omit **Next action** when the work is complete and the user has no decision to make.
- Keep the report short enough that the result is visible before any process detail.

## Batch retrospective

Every `retrospective.batch.every_n_tasks` (default 15), read the Orca runtime export
when available, then use final feature summaries only where they add outcome context.
Never create task documents solely to feed retrospective metrics.

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
- **What does the process itself cost?** Run
  `python scripts/retro_report.py --orca-runs` (read-only) and read
  `retrospective.process_cost` by mode: dispatches, worker minutes, repeats, and
  ceremony dispatches — the `report_correction` and `relaunch` retries that produced
  no new work. A flagged mode names a gate to simplify: report corrections point at
  the report contract or machine acceptance, relaunches at launch and bootstrap ACK.
  Cut ceremony, never a quality control: QC independence and the Dev dispatch are
  not on the table. Orca exposes no token counts, so these are proxies; a high
  share of untagged (inferred) dispatches means Lead is skipping
  `orchestration.dispatch_tag`, and the numbers deserve less trust.
