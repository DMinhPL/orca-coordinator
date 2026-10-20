# orca-coordinator

A Claude Code skill that runs a risk-scaled engineering pod with four available
roles — **Lead, BA, Dev, QC** — in hub-and-spoke coordination. Every task enters
through Lead; specialists never talk to each other. XS tasks use Dev
self-revalidation; S and above retain independent QC.

The skill installs as **`orca-coordinator`** (the `name` in [`SKILL.md`](SKILL.md)
and the folder name under `~/.claude/skills/`); _orca-coordinator_ is the project name.

```
        user ⇄ LEAD ⇄ BA
                 ⇄ DEV
                 ⇄ QC
```

## New here? Start with this

| If you want to…                        | Read                                                                                                               |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Understand what Orca is and why        | [Why](#why) and [How it works](#how-it-works) below                                                                |
| Check that your checkout works         | [Verify your setup](#verify-your-setup)                                                                            |
| Decode an acronym (CAS, M0–M4, G1–G6…) | [`references/glossary.md`](references/glossary.md)                                                                 |
| See how a task gets sized and routed   | [Complexity bands → workflow modes](#complexity-bands--workflow-modes)                                             |
| Follow the gates a task passes through | [`workflows.md`](workflows.md) Part 1                                                                              |
| Change a model, threshold, or policy   | [`references/agents-models.yaml`](references/agents-models.yaml), then [Changing the config](#changing-the-config) |
| Tailor a role for one project          | [Project overlay](#project-overlay-optional)                                                                       |

Suggested reading order for a first pass: this README → [`SKILL.md`](SKILL.md) →
[`skills/orca-lead/SKILL.md`](skills/orca-lead/SKILL.md) →
[`workflows.md`](workflows.md) → [`references/glossary.md`](references/glossary.md)
as needed. Read the BA/Dev/QC role skills only when you need that role's detail.

## Why

Letting one agent analyse, implement, and verify its own change collapses the one
control that catches its own mistakes: independent review. Orca enforces four
non-negotiable commitments instead:

1. **Cheap first, expensive on evidence.** Default model/effort until a defined
   condition is observed; one escalation step per trigger; de-escalate after a clean
   phase.
2. **Verification matches risk.** S and above use independent QC on a different
   provider with delta-only context. XS uses structured, machine-accepted Dev
   self-revalidation and is labeled accordingly.
3. **Writing is a granted permission.** Modification tier and file allowlist are set
   in the dispatch envelope, not assumed by the worker. Default is M1 — propose, do
   not apply.
4. **Everything routes through Lead.** One reporter to the user and one arbiter of
   conflicts. Runtime events stay in Orca; only material exceptions become durable
   decisions.

No band is small enough to relax commitment 4: Lead never implements a task itself,
and an unreachable Orca runtime is a blocker to report, not a reason to skip the
Dev dispatch.

The workflow is a deliberate tailoring of PMBOK 8th/7th, the Agile Practice Guide,
and PMI's AI standard to small, high-frequency software tasks — see
[`references/pmbok-mapping.md`](references/pmbok-mapping.md) for the traceability.

## How it works

1. **Every task enters through [`SKILL.md`](SKILL.md)**, which routes by role to the
   matching skill file. [`references/agents-models.yaml`](references/agents-models.yaml)
   remains authoritative, while `scripts/config_view.py` extracts only the paths a
   role needs.
2. **Lead** scores task complexity into a band (XS–XL) using a progressive rubric —
   hard overrides first, then three safety dimensions, then the remaining four only
   if needed (see [`references/complexity-model.md`](references/complexity-model.md))
   — picks a workflow mode, and dispatches specialists as fresh, cold-boot supervised
   Orca workers.
3. **BA, Dev, QC** each read only their own role skill plus a generated role config
   view — never the whole lifecycle or the full YAML — and do their phase. Dev/QC
   preflight their report from an OS-temporary path before returning it to Lead.
4. **Lead** waits for each dispatch to reach a terminal state, runs the machine
   acceptance gate on Dev/QC reports (`scripts/validate_worker_output.py`), checks
   them for internal consistency (never redoing the specialist's work), and advances
   or loops back per [`workflows.md`](workflows.md).

```
skills/
├── orca-lead/               dispatch procedure, arbitration, gates, escalation
├── orca-ba/                 requirements, acceptance criteria, risk, blast radius
├── orca-dev/                implementation bounded by modification tier, allowlist, and design heuristics (DRY, KISS, YAGNI, ...)
├── orca-qc/                 delta-only independent verification and review
├── orca-change-control/     Lead-owned — mid-flight scope changes
└── orca-closeout/           Lead-owned — status gate and retrospective
```

When `knowledge_sources` declares them available, **GitNexus** (code graph) and
**Knowns** (project memory) are queried before broad repository scanning. Lead
detects availability once per task; a missing source is never a blocker.

## Complexity bands → workflow modes

Lead scores seven dimensions (0–3 each, total 0–21). Any hard override (security
boundary, production schema, public API, secrets, PII, infra, …) forces band ≥ L and
human gate G1.

| Band | Score | Default mode    | Max modification tier | Notes                               |
| ---- | ----- | --------------- | --------------------- | ----------------------------------- |
| XS   | 0–3   | `xs_self_check` | M2                    | Dev self-revalidation, no BA/QC     |
| S    | 4–7   | `simple`        | M2                    | Dev then independent QC             |
| M    | 8–12  | `standard`      | M3                    |                                     |
| L    | 13–16 | `standard`      | M3                    |                                     |
| XL   | 17–21 | `standard`      | M4                    | Decompose into child tasks, rescore |

These values live in `complexity_assessment.bands` in the YAML; if this table and the
YAML ever disagree, the YAML is right.

### Workflow modes

Eight modes cover the shape of the work — see [`workflows.md`](workflows.md) Part 2
for when each applies and which gates it emphasises:

- **standard** — the default: analysis, build, verify
- **xs_self_check** — explicit, confirmed XS work; one Dev dispatch with machine-accepted self-revalidation, no BA/QC dispatch
- **simple** — explicit, confirmed S work with Dev then independent QC
- **review_fix** — defect and expected behavior already clear; QC leads, then Dev fixes, then QC re-verifies
- **defect_triage** — root cause not yet established; QC characterizes first
- **research_only** — analysis or documentation, no code changes (tier M0)
- **qc_only** — verification of existing changes, no new implementation (tier M0)
- **cross_branch_review** — reviewing another branch while Primary stays on its own

## Single source of truth

[`references/agents-models.yaml`](references/agents-models.yaml) carries every
provider, model, effort, threshold, path, condition list, and policy value. Skill
files are the _procedure_; the YAML is the _parameter table_. Where they disagree,
the YAML wins and the skill file is the bug —
[`scripts/lint_config.py`](scripts/lint_config.py) enforces this mechanically.

Resolution precedence: `task_override` → `conditional_escalation` → YAML default →
provider default. On any unavailable provider/model/effort, Orca stops and reports;
it never substitutes silently.

After each verified worker launch, Lead retains the complete orchestration metadata
internally but prints only a short role, worker, workspace, scope, and Dispatch
summary. This keeps status visible without exposing the full worker envelope.

## Prerequisites

- **Claude Code** with this folder installed as a skill
  (`~/.claude/skills/orca-coordinator/`).
- **Orca** with its orchestration CLI available — specialists are real Orca workers
  started by Lead, not simulated personas. Without a reachable Orca runtime, Lead
  stops and reports.
- **Python 3** for the helper scripts. They use only the standard library (no PyYAML,
  no pytest).
- The providers/models named in `agents-models.yaml` must exist in your local
  Claude/Codex CLIs.

## Verify your setup

Run from the repository root. All four should succeed on a clean checkout.

```sh
python scripts/lint_config.py                 # expect: 0 error(s), 0 warning(s) / config is single-sourced
python -m unittest discover -s tests          # expect: OK (11 tests at the time of writing)
python scripts/config_view.py --list          # lists the built-in role views
python -X utf8 scripts/complexity_score.py --triage --d2 0 --d3 0 --d7 0   # expect: FAST PATH yes, SIZE XS
```

> **Windows note:** `complexity_score.py` draws its report with box-drawing
> characters and crashes with `UnicodeEncodeError` on a default `cp1252` console. Use
> `python -X utf8 …` (as above), set `PYTHONIOENCODING=utf-8`, or pass `--json`.

## Scripts

| Script                              | What it does                                                                             | Typical use                                                                                                                             |
| ----------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/complexity_score.py`       | Deterministic CAS scorer                                                                 | `--triage --d2 N --d3 N --d7 N` for the fast-path check; all `--d1`…`--d7` for a full score; `--override <flag>` (repeatable); `--json` |
| `scripts/config_view.py`            | Role/path-specific view of the YAML, without copying policy                              | `--role <lead\|ba\|dev\|qc\|closeout>`; add `--path dotted.path` for conditional policy                                                 |
| `scripts/validate_worker_output.py` | Machine acceptance gate for Dev/QC `worker_done` payloads                                | `--role dev report.json` or pipe via `-`; exit 0 valid, 1 invalid, 2 usage error                                                        |
| `scripts/lint_config.py`            | Fails when a value is restated outside the YAML, or the changelog drifts from the config | Run on every YAML change; `--strict` treats warnings as failures                                                                        |
| `scripts/retro_report.py`           | Batch metrics from Orca runtime exports and legacy `decisions.jsonl`; process cost per workflow mode (dispatches, minutes, repeats, ceremony) read from Orca | `--orca-runs [RUN_ID ...]` (read-only, default latest batch); `--orca-save`/`--orca-json` for snapshots; `--runtime-export <export.jsonl>`; `--json`, `--strict` |

## Repository layout

| Path                                | Purpose                                                                                                                                           |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SKILL.md`                          | Entry point and role router                                                                                                                       |
| `workflows.md`                      | The gate set, workflow-mode catalogue, and cross-cutting operations                                                                               |
| `skills/orca-*/SKILL.md`            | Role-scoped procedures (Lead, BA, Dev, QC, change control, closeout)                                                                              |
| `references/agents-models.yaml`     | All providers, models, efforts, thresholds, and policy                                                                                            |
| `references/glossary.md`            | Definitions for the acronyms and abbreviations used throughout (CAS, M0–M4, G1–G6, PMBOK, etc.)                                                   |
| `references/complexity-model.md`    | The seven-dimension sizing rubric                                                                                                                 |
| `references/modification-policy.md` | How write tiers M0–M4, allowlists, and protected paths work                                                                                       |
| `references/handoff-protocol.md`    | Dispatch/return envelopes and delta-only context                                                                                                  |
| `references/pmbok-mapping.md`       | Traceability to PMBOK 8th, the Agile Practice Guide, and PMI's AI standard                                                                        |
| `scripts/`                          | Helper scripts — see [Scripts](#scripts)                                                                                                          |
| `tests/`                            | `unittest` suites for `config_view`, `retro_report`, and `validate_worker_output`                                                                 |
| `CHANGELOG.md`                      | Version history for `agents-models.yaml`                                                                                                          |
| `REVIEW.md` / `REVIEW-workflows.md` | Design review findings behind the v13 and v14 changes                                                                                             |
| `examples/extra-skills/`            | Worked example of a project overlay (see below)                                                                                                   |
| `sample-patterns/`                  | A separate, standalone reference package with its own `SKILL.md` and config. It is not loaded by this skill and is excluded from `lint_config.py` |

## Getting started on a real project

1. Read [`SKILL.md`](SKILL.md) to understand the router and the four commitments.
2. Set `protected_paths` in `references/agents-models.yaml` for your own repository —
   the shipped defaults are generic placeholders.
3. Use `python scripts/config_view.py --role <role>` when loading role parameters;
   add `--path dotted.path` only for conditional policy.
4. Run a handful of tasks with Lead scoring complexity in shadow mode before letting
   the score drive `workflow_mode` selection automatically (see
   [`references/complexity-model.md`](references/complexity-model.md)).
5. Run `python scripts/retro_report.py --orca-runs` at the configured batch interval
   to review whether routing, escalation, and each gate are paying for themselves.
   It reports dispatches, worker minutes, and ceremony retries per workflow mode, and
   flags modes over the thresholds in `retrospective.process_cost`. Orca exposes no
   token counts, so these are proxies. `--runtime-export` and positional
   `decisions.jsonl` inputs remain supported for old runs.

## Changing the config

1. Edit [`references/agents-models.yaml`](references/agents-models.yaml) — never
   restate a value in a skill file; reference the YAML path instead.
2. Bump `config_version` on every edit, and `schema_version` when the structure
   changes in a way a consumer must handle.
3. Add a matching entry at the top of [`CHANGELOG.md`](CHANGELOG.md).
4. Run `python scripts/lint_config.py` and `python -m unittest discover -s tests`
   before committing.

## Project overlay (optional)

This package is shared across projects, so its defaults are generic. A single
project can tailor a role — a domain convention, an extra guardrail, which
engineering principle to weigh heaviest — without editing the package itself, by
dropping markdown files into its own repository:

```
your-project/
  extra-skills/
    lead/
    ba/
    dev/
      01-money-conventions.md
      02-ledger-guardrails.md
    qc/
```

Each file under `extra-skills/{role}/` is an independent additional skill for
that role, read after the role's default `SKILL.md`, in filename order. An empty
or absent folder for a role is the common case and is silently ignored — nothing
to set up if you don't need it. Lead detects what exists once per task and hands
the file list to the dispatched worker, the same way it hands over
`knowledge_sources`.

An overlay file may only add or tighten — name conventions, add checks, narrow an
already-granted allowlist, point at project docs. It may never loosen a
prohibition, change a modification tier or gate, or widen an allowlist: where an
overlay disagrees with the role's default skill or `agents-models.yaml`, the
default wins and the overlay is the bug. Two overlay files disagreeing with each
other is reported to Lead, never resolved by file order.

See [`references/agents-models.yaml`](references/agents-models.yaml) →
`project_overlay` for the full contract, and
[`examples/extra-skills/dev/`](examples/extra-skills/dev/) for a worked example.

## Documentation economy

Operational state belongs to Orca, not the project repository. Never create
`dispatch.json`, worker-state files, bootstrap receipts, or orchestration event logs
under `.docs/features`.

- **XS:** no durable document and no feature folder; validation stays in the accepted
  `worker_done` payload.
- **S/M/L/XL:** one concise `summary.md`, written after the feature reaches an
  outcome, covering what changed, verification, and remaining limitations or risks.

Role reports, traceability, decisions, dispatch, ACK, and worker completion remain
runtime state. Export a separate artifact only when the user, project policy, or a
compliance requirement explicitly needs it. The repository document exists to explain
the feature result, not to archive the process.

## Troubleshooting

| Symptom                                                           | Cause / fix                                                                                                        |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `UnicodeEncodeError: 'charmap' codec…` from `complexity_score.py` | Windows console encoding — run with `python -X utf8` or `--json`                                                   |
| `No module named pytest`                                          | Not needed — the tests use `unittest`: `python -m unittest discover -s tests`                                      |
| `lint_config.py` reports a restated value                         | A skill/reference file hard-codes something that belongs in the YAML; replace it with a reference to the YAML path |
| Lead refuses to "just do it"                                      | By design (commitment 4) — every code change goes through a Dev dispatch                                           |
| Lead stops on an unavailable model/provider                       | By design — fix the model in your local CLI or set a `task_override`; Orca never substitutes silently              |

## Status

Config `schema_version: 10`, `config_version: 32` — see [`CHANGELOG.md`](CHANGELOG.md)
for the version history, and [`REVIEW.md`](REVIEW.md) /
[`REVIEW-workflows.md`](REVIEW-workflows.md) for the design review findings behind it.
Last revalidated 2026-10-20: lint clean, 13/13 tests passing.
