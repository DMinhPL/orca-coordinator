# Changelog — `references/agents-models.yaml`

Version history for the config. Newest first.

`schema_version` changes when the structure changes in a way a consumer must handle.
`config_version` changes on any edit, structural or not. They were a single `version`
integer until v13, which is why a consumer could not tell a model-default tweak from a
new policy block.

Rationale for the v13 additions is in [`REVIEW.md`](REVIEW.md); for the v14 workflow
changes, [`REVIEW-workflows.md`](REVIEW-workflows.md).

Legend: `+` added · `~` changed · `-` removed

---

## v30 — one outcome-first feature document

`schema_version: 8`

- `~ documentation.files_by_band` — XS still creates no document; every other band
  creates only `summary.md` after the feature reaches an outcome.
- `-` automatic BA, Dev, QC, decision-log, and traceability files. Their structured
  evidence remains in Orca runtime and is exported only when explicitly requested or
  required by project/compliance policy.
- `~ documentation.summary` — focuses on what changed, observable impact,
  verification, limitations, and risks; process narrative and worker metadata are
  excluded.
- `~ schema_version` `7` -> `8` and `~ config_version` `29` -> `30` because durable
  artifact consumers must now expect one final summary instead of role documents.

---

## v29 — band-scaled durable documentation

`schema_version: 7`

- `+ orchestration.runtime_artifacts` — Orca remains the source of truth for dispatch
  envelopes, worker identity, ACKs, lifecycle state, and `worker_done`; repository
  copies such as `dispatch.json` and orchestration event logs are forbidden.
- `~ orchestration.machine_acceptance.input` — validates the `worker_done` payload or
  an Orca-managed runtime copy instead of requiring a persisted role file.
- `~ documentation.files_by_band` — XS creates no feature folder or durable task
  document; S creates one maintenance-oriented `summary.md`; M/L/XL retain the full
  requirement, development, verification, traceability, and decision package.
- `~ documentation.decision_log` — becomes exception-only from band M. Routine
  classification, default routing/tier selection, source detection, dispatch, ACK,
  and completion remain runtime events rather than project documents.
- `~ scripts/retro_report.py` — accepts explicit Orca runtime JSONL exports, so
  retrospective metrics no longer force documents to be created for XS/S work.
- `~ schema_version` `6` -> `7` and `~ config_version` `28` -> `29` because artifact
  persistence and machine-acceptance inputs changed for consumers.

---

## v28 — XS self-revalidation and progressive config loading

`schema_version: 6`

- `+ workflow_modes.xs_self_check` and `+ complexity_profiles.xs` — clean fast-path
  XS work dispatches Dev only. Dev must return structured, machine-accepted
  self-revalidation; any uncertainty, failed check, or material band challenge causes
  a rescore and restores independent QC through the resulting mode.
- `~ simple` — now applies to band S and retains Dev plus independent QC.
- `~ orchestration.return_envelope` — adds `workflow_mode` and conditionally requires
  `self_revalidation` for XS Dev reports. The validator checks executed commands,
  exit codes, checks, result, and evidence.
- `+ scripts/config_view.py` — extracts role-specific or dotted-path views from the
  authoritative YAML so workers no longer load the full 70 KB config by default.
- `+ scripts/retro_report.py` — aggregates decision logs into escalation rate,
  allowlist amendments, requirement-gap change requests, upward rescores, band
  distribution, change-request origin, and QC-independence signals.
- `+ examples/extra-skills/dev/` — shipped project-overlay examples for money and
  ledger constraints, replacing the previously dangling README reference.
- `~ schema_version` `5` -> `6` and `~ config_version` `27` -> `28` because report
  consumers must handle `workflow_mode` and conditional XS self-revalidation.

---

## v27 — machine acceptance for Dev/QC reports

`schema_version: 5`

- `+ orchestration.machine_acceptance` — Lead validates Dev and QC role artifacts
  after `worker_done` and before accepting the phase. Invalid reports are rejected
  and re-dispatched to the same role; read/parse failures are coordinator blockers.
- `+ orchestration.return_envelope.artifact_embedding` and
  `role_required_fields.qc` — Dev/QC artifacts carry exactly one structured JSON
  return envelope, and QC includes its verdict.
- `+ scripts/validate_worker_output.py` — validates required fields and types,
  role/status vocabulary, criterion evidence, complete-status consistency,
  allowlist compliance, evidence-backed testing claims, QC approval preconditions,
  and boundary-matrix completeness when a matrix is present.
- `~ schema_version` `4` -> `5` and `~ config_version` `26` -> `27` because
  report consumers must handle the new embedded envelope and machine-acceptance
  block.

---

## v26 — high effort is the final escalation step

`schema_version: 4`

- `~ agents.{lead,ba,qc}.escalation` — replace the direct `medium` → `high`
  jump with an explicit model-first sequence. The role first moves to a stronger
  model at `medium`; `final_effort_escalation` may use `high` only after that model
  escalation is insufficient.
- `~ agents.dev.escalation_chain` — use `terra @ medium`, then `sol @ medium`, then
  `sol @ high`. The intermediate `high` rungs and the final `xhigh` rung are removed,
  so Dev has exactly one high-effort step and it is last.
- `~ optimization.rules` — codify the quota-first invariant: increase model
  capability at `medium` before increasing effort, reserve `high` for the final
  escalation step, and require concrete evidence that the preceding rung was
  insufficient. `high` remains an explicitly valued capability for work that
  genuinely needs deeper reasoning; it is not a default, a preemptive choice, or
  a shortcut based only on the task's complexity label.
- `~ references/agents-models.yaml` comments — remove inline `# vNN` annotations
  and historical migration prose. Operational rationale remains beside the policy;
  version history belongs in this changelog.
- `~ schema_version` `3` → `4` and `~ config_version` `25` → `26` because the
  escalation shape changed for config consumers.

This release also includes the coordinator observability and authorization
clarifications accumulated since v25:

- `+ modification_policy.commit_and_push_authorization` and
  `+ human_gates.G7_commit_push_approval` — require explicit user acceptance for
  every commit or push, including on a task work branch; Dev performs the accepted
  git operation, while rejected changes remain uncommitted and local.
- `~ modification_policy.branch_naming` — Lead names an M2+ work branch and Dev
  creates it at dispatch start.
- `+ workflows.md` verified launch receipt — retain complete launch metadata
  internally while printing only a short role/worker/workspace/scope/dispatch
  summary after verification.
- `+ worktree_selection_policy` safeguards — distinguish Lead-created worktrees
  from Orca-managed provisioning, enforce one active worker per task role/stage,
  and keep workspace display identity separate from branch identity.
- `+ worktree_selection_policy.new_worktree_bootstrap` — after creating a worktree,
  copy Primary's repository-local GitNexus and Knowns artifacts as independent
  snapshots, refresh and register GitNexus from the destination root, verify copied
  state, and stop before worker launch on copy or refresh failure.
- `~ README.md` and project-overlay guidance — document independent
  `extra-skills/{role}/*.md` overlays and add a worked-example reference.
- `~ orca-closeout/SKILL.md` § 6 — the final report is printed as rendered
  markdown, mandatory in every mode and band: an outcome headline with icon, a
  summary table, one Dispatches row per dispatch including retries, Changes,
  Verification (including what was not run), Notes & risks, and a closing
  `⏸ Your call` block of numbered decisions. Short cells, a fixed icon set.
  Launch and Bootstrap ACK receipts are unchanged.
- `~ orca-lead/SKILL.md` step 9 — Lead must read closeout § 6 and use its table
  format before writing the final report; a prose final report is a format defect.
- `+ SKILL.md` "A team, not a pool of workers" and `+` a "Who you are on this team"
  section opening each role skill — Lead as engineering manager, BA as business
  analyst, Dev as software engineer, QC as quality engineer, each with concrete
  behaviors for that job. The mindset shapes how a role works, never what it may do;
  authority still comes only from the YAML and the dispatch envelope.
- `~ handoff-protocol.md` Role Bootstrap ACK — adds an `Acting as` line in which the
  worker names its team role and what it owns; a generic or cross-role line is an
  inconsistent ACK.
- `+ handoff-protocol.md` § Sending `worker_done` and rule 7 — workers copy the
  `worker_done` command and its Task/Dispatch IDs verbatim from the injected Orca
  preamble, never retyping them; an ID-mismatch rejection is resent exactly once,
  `consumer_fenced` stops without retry, and an unclear outcome goes to Lead
  instead of a new report.
- `~ orca-lead/SKILL.md` § 6b — Lead treats an ID-mismatch rejection as a
  bookkeeping error: ask the worker to resend from its preamble, take any IDs from
  orchestration state rather than memory, and re-dispatch only if the resend fails.
- `~ SKILL.md` — rename the package skill to `orca-coordinator` and align its
  formatting with the current documentation style.
- `+ workflows.md` § 1.3b and `+ handoff-protocol.md` Role Bootstrap ACK — every
  BA/Dev/QC worker's first returned output must now be a `ROLE BOOTSTRAP ACK`
  block naming the role files it actually read and restating its mission; Lead
  prints a short ready receipt and does not release the worker into task work until
  the block is present and its declared file list matches the internal delivery
  manifest. A
  verified identity (`exactWorker: true`) no longer by itself means the worker
  loaded its role skill.
- `~ orca-closeout/SKILL.md` § 6 — the final report now has a concrete printed
  template (workflow/run/workspace header, one section per role actually
  dispatched with its dispatch id and verdict, status gate, risks, rollback, and
  a mandatory "Next step for you") instead of a bare list of topics to cover.
- `+ orchestration.forbidden_fallbacks: primary_direct_implementation` and
  `+ verification: verify_orchestration_runtime_reachable_before_classification` —
  closes an observed gap where Lead offered the user a "direct implementation"
  shortcut (not a documented mode) on an XS task and then wrote the code itself
  in Primary. No band skips dispatch; the fast path only collapses scoring/mode
  ceremony. Lead now verifies the orchestration runtime at step 0, before
  classification, and treats an unreachable runtime as a blocker to report, never
  a reason to implement directly. See `orca-lead/SKILL.md` step 0 and `~ do not`
  list, and `workflows.md` § 1.1.

## v25 — project overlay is a directory of files, not one file

v24 shipped as a single `.orca/{role}.md` file. In practice a project has several
unrelated things to add to a role — one domain convention, one guardrail, one
style note — and forcing them into one file means every unrelated addition or
removal touches the same file, which is the merge-conflict and review-noise
problem the overlay was supposed to avoid.

- `~ project_overlay.directory_pattern` — `{project_root}/.orca/{role}.md` (a
  file) → `{project_root}/extra-skills/{role}/*.md` (a directory). Any number of
  markdown files, each independent, each an additional skill on its own topic.
  An empty or absent directory is still silently ignored — the common case is
  unchanged, only the shape of the uncommon case is.
- `+ project_overlay.precedence.on_conflict_between_overlay_files` — two overlay
  files disagreeing is now a real possibility once there can be more than one;
  it is reported to Lead to arbitrate, never resolved by filename order.
- `~ references/handoff-protocol.md`, `~ skills/orca-{lead,ba,dev,qc}/SKILL.md`,
  `~ SKILL.md` — updated for the directory/file-list shape.
- `~ examples/project-overlay/` — the single-file example split into
  `examples/extra-skills/dev/` with two files, demonstrating the intended use:
  one file per concern.

**Considered and rejected:** keeping the single file and telling projects to use
headings for separate concerns — that still forces one shared file for
unrelated additions, which is exactly what a directory of independent files
avoids at no extra cost.

---

## v24 — optional per-project overlay for each role

Every role's defaults live in this shared package, used across projects. There was
no way for one project to tailor a role — house conventions, an extra guardrail,
which engineering principle it cares about most — without editing the package
itself, which would leak into every other project using it.

- `+ project_overlay` — an optional, per-project markdown file at
  `{project_root}/.orca/{role}.md` for `lead`, `ba`, `dev`, `qc`. Lead detects
  presence once per task at classification (same rhythm as `knowledge_sources`)
  and states it in the dispatch envelope; a missing file is the expected default
  state, not a fallback worth logging. Additive/tightening only — it can name
  conventions, add checks, narrow an allowlist further, or point at project
  references, but it cannot loosen a prohibition, change a tier or gate, widen an
  allowlist, or override any other value in this file. On conflict with the
  default skill or this file, the default wins and the overlay is the bug — the
  same shape as the existing YAML-wins rule.
- `~ references/handoff-protocol.md` — dispatch envelope example gets an optional
  `project_overlay` field alongside `knowledge_sources`.
- `~ skills/orca-{lead,ba,dev,qc}/SKILL.md` — each gets a short "Project overlay"
  note: check for the file, read it after the default skill, apply it as an
  additional layer, never a substitute.

**Considered and rejected:** storing the overlay inside this package (e.g. a
`projects/{name}/` subtree) — that would require editing the shared package per
project and defeats the purpose; the whole point is that it lives with the
project it tailors and this package never needs to change for it to exist.

---

## v23 — engineering design principles for Dev

`execution_policy` said *how much* to build (scope-bounded, no broad scan) but never
said anything about the *shape* of the code once written — that was left implicit,
so it varied by whichever model happened to be dispatched.

- `+ agents.dev.engineering_principles` — DRY, KISS, YAGNI, Law of Demeter, Defensive
  Programming, Principle of Least Surprise, Separation of Concerns, Composition over
  Inheritance, Fail Fast. Heuristics, not gates: applied with judgment, deferring to
  the codebase's existing idiom, and never license to widen the allowlist or
  `scope_bounded`.
- `~ skills/orca-dev/SKILL.md` — new "Engineering principles" section under
  Execution policy.

**Considered and rejected:** a separate scored checklist (like `d1`–`d6` complexity
dimensions) for principle adherence, and a new QC checklist item for it — these are
Dev's own design judgment while writing, not measurable signals Lead can gate on or
QC can verify against.

---

## v22 — worktree pool reuse is mandatory, not just permitted

`primary_session_policy.worktree_reuse_allowed` already existed, but nothing forced
Lead to inventory the pool first — reuse was optional, so a fresh worktree got
created by default on most M2+ tasks even when a clean one already existed, and only
`cross_branch_review` had an explicit reuse-first procedure.

- `+ worktree_selection_policy` — mandatory pre-dispatch inventory (name, path,
  branch, tracking, commit, staged/unstaged/untracked) for every repo-backed BA/Dev/QC
  dispatch, not only `cross_branch_review`. Reuse-first by default
  (`create_new_worktree_while_reusable_candidate_exists: forbidden`), an explicit
  pool-empty procedure that asks the user for a name rather than inventing one, dirty-
  worktree and branch-occupancy safety rules, and confirmation that worktree reuse is
  never session reuse.
- `+ worktree_selection_policy.new_worktree_path_policy` — new worktrees are created
  as a sibling of the project root, never nested inside it (project at
  `/c/DM/Mine/Sources/second-thoughts` → new worktree at
  `/c/DM/Mine/Sources/{worktree_name}`).
- `+ workflows.md` §1.9 Worktree pool gate — the procedure; `cross_branch_review`
  updated to note it is the branch-B-specific case of this general gate rather than a
  separate mechanism.
- `+ glossary.md` — **Worktree** was used throughout the config but never defined.

**Considered and rejected:** a separate "workspace" vocabulary distinct from
"worktree," and a standalone `references/shared/` policy file outside the existing
flat `references/` layout. Both were proposed externally; both would have created a
second name and a second source of truth for something `primary_session_policy` and
`cross_branch_review` already governed. Extending the existing block keeps
`worktree` as the one term and the YAML as the one place its values live.

## v21 — specialists can challenge the band

Lead still owns CAS. What changes is that the pod no longer has to wait for a
mis-scoring to cause damage before hearing about it.

- `+ complexity_assessment.rescore_triggers.specialist_reports_band_materially_wrong_on_first_read`
  — the other four triggers all require the error to have already cost something: an
  allowlist overrun, a repeated failure, a blocked question. Lead scores from the
  request text before anyone has read the code; the specialist is the first to read it.
- `+ complexity_assessment.band_challenge` — how it is raised. Deliberately **evidence,
  not a vote**: the specialist whose tier, effort and gates the band determines does not
  get to set it. Raisable by BA, Dev and QC on first read, with observed band,
  dimensions moved, evidence and evidence level. Lead must re-score or record why not.
  A challenge reaching L/XL or matching a hard override implies G1 should have fired
  before that phase, so the worker stops rather than writing past an ungated gate;
  every other case continues under the granted tier, which is the conservative
  direction.
- `+ orchestration.return_envelope.optional_fields` — `band_challenge` is optional, not
  required. A field every worker must fill even when empty becomes noise, and noise is
  how a real challenge gets skimmed past.

**Considered and rejected:** having Dev participate in the initial CAS scoring. It is
circular — the band sets Dev's own model, effort and tier, so Dev would be dispatched
to decide how Dev should be dispatched — and `G1_scope_approval` fires `before_phase:
dev` precisely to put a human between scoping and Dev starting. An M0 scoping dispatch
would also add a cold-boot worker to every task including XS fast-path ones.

## v20 — provider rebalance

`schema_version: 3`

- `~ agents.ba` — `codex/gpt-5.5` → `claude/claude-sonnet-5`. The pod was 3:1 on codex
  (lead, ba, dev) against claude (qc alone), and qc is the role deliberately kept
  lightest by `context_mode: delta_only`. BA is the second-heaviest consumer and the
  only heavy role with no independence constraint. Now 2:2 by role.
  **This is a partial rebalance, not a fix** — Dev remains the dominant codex consumer
  by token weight. If codex is still the binding constraint, the next lever is reducing
  Dev's consumption, not moving Dev.
- `~ agents.ba.escalation.model_escalation` — preferred is now cross-family
  (`codex/gpt-5.6-terra`); the old alternative had become the default. Alternative is
  `claude-opus-5`. Cross-family escalation suits a hard architecture question and keeps
  BA working when one provider is down.
- `+ qc_policy.independence` — BA and QC now share a provider and model. Recorded as
  deliberate, with the reasoning and a `revisit_if` condition.

## v19 — dev routing, quota-first and evidence-based

- `~ agents.dev.escalation_chain` — 3 rungs → 5, and Codex-only.
  - `+ broader_capability` (terra @ medium) buys capability without also buying effort.
    Sibling of `scoped_deeper_reasoning` (luna @ high), not sequential — Lead picks by
    which deficit was observed.
  - `~ very_hard` is now sol @ xhigh; the chain previously plateaued at high.
  - `-` **Removed the `claude-sonnet-5` / `claude-opus-5` alternatives.** QC is always
    claude, so both collided with `qc_provider_must_differ_from_dev_provider` and
    tripped `on_independence_unavailable` → Dev capped at M1 (propose-only) at the
    hardest moment. They were dead options, not fallbacks.
- `+ agents.dev.escalation_policy` — carry findings across escalation. Dev→Dev only;
  never into a QC dispatch, which stays `delta_only`.
- `~ optimization.rules` — `escalate_effort_before_escalating_model` was unconditional.
  Now: diagnose the deficit first — effort for reasoning on a known scope, model for
  missing context or capability.
- `+ retrospective.batch.dev_model_distribution_target` — a measurable target.

**Not adopted** from the routing proposal: a separate `blast_radius` scale (duplicates
CAS d3 + `hard_overrides`; mapped instead via `escalation_chain.hard.minimum_rung_when`),
a `context_policy` block (already covered by `execution_policy` + `knowledge_sources`),
and the Fable/Claude tier mapping (collides with the QC provider split).

## v18 — BA escalation ladder

Followed from lowering `agents.ba.effort` high → medium.

- `~ agents.ba.escalation.effort` — xhigh → high. medium → xhigh skipped a rung and
  breached `one_escalation_level_per_trigger`. The ladder is now
  medium → high → model_escalation, which is also monotonic; the old path dropped
  effort from xhigh back to high at the model step. Note xhigh is no longer reachable
  for BA — model escalation covers that ceiling.
- `~ agents.ba.escalation.when` — `+ complexity_band_is_L_or_XL`. BA's other conditions
  all require a judgement call. This one is mechanical, mirroring `lead.escalation`, so
  band L/XL cannot silently run at medium.

## v17 — knowledge sources

- `+ knowledge_sources` — GitNexus (code graph) and Knowns (project memory) as
  availability-gated context providers, with per-role access, a precedence order, and a
  freshness rule that stops a stale index from being cited as confirmed evidence.
- `~ qc_policy.allowed_context` — targeted queries admitted. A graph query is not a
  `full_repository_scan`, but Knowns is restricted for QC because it can carry Dev's
  reasoning.
- `~ optimization.rules` — prefer a targeted query over a broad scan.

## v16 — branch naming

- `~ modification_policy.branch_pattern` → `modification_policy.branch_naming` —
  `{category}/{slug}[-{ticket}]`, with the category derived from the task type rather
  than chosen freely.
  **Breaking** for anyone parsing `branch_pattern`: the branch no longer carries
  `{task_id}`; commit messages still do, via `[TASK-####]`.

## v15 — progressive complexity scoring

- `+ complexity_assessment.triage` — d2/d3/d7 first, full seven only when the triple is
  non-zero. Additive and backward compatible: set `enabled: false` to restore
  unconditional seven-dimension scoring.

## v14 — workflow modes, lifecycle, and authority

Reconstructed from inline `# v14` markers; this version was never recorded in the
config header. See [`REVIEW-workflows.md`](REVIEW-workflows.md) for the findings behind
it.

- `~ workflow_modes.review_fix` — flow reverted to Dev-first. v13 had changed it to
  QC-first, misreading the intent: `review_fix` is for defects whose expected behavior
  is *already* clear.
- `+ workflow_modes.defect_triage` — new. Previously an uncharacterized defect had to
  run `standard`, which puts BA on work QC owns.
- `+ workflow_modes.cross_branch_review` — new. `primary_session_policy` already
  required a separate worktree, but no mode named the flow.
- `+ workflow_modes.simple.ba_substitution` — the escape valve that stops Lead becoming
  a shadow BA.
- `+ engineering_policy.task_classification.mode_selection_within_type` — `review_fix`
  and `defect_triage` share the `bug` type; the entry condition decides.
- `+ document_status` — `documentation.status_gate` referenced "implemented" with no
  enumeration, the same defect class as the v13 `p0` reference.
- `+ dispatch_lifecycle` — distinct from the report status in `return_envelope`. A
  worker's report says whether the *work* is done; the dispatch state says whether the
  *exchange* is settled. Conflating them is how a timeout becomes a success.
- `+ lead_authority_boundary` — the strongest control in the pod, and the one most
  likely to erode, because doing it yourself is faster.
- `+ coordinator_resume` — `coordinator_continuity` stated properties; this states the
  order. A reopened Lead session that skips step 2 duplicates a live Run.
- `+ rework_loop` — the QC-fail cycle, named and budgeted.
- `+ cleanup_policy.future_work_after_non_released_outcome_requires_fresh_worker`

## v13 — governance layer

`schema_version: 2` — split from the single `version` integer, so a compatible edit is
distinguishable from a structural one. Full rationale in [`REVIEW.md`](REVIEW.md).

- `+ complexity_assessment` — sizing rubric driving profile and mode selection
- `+ modification_policy` — write-permission tiers, allowlist, protected paths
- `+ human_gates` — enumerated user-approval points
- `+ change_control` — classes, authority, propagation
- `+ traceability` — ID scheme and RTM obligation
- `+ defect_severity` — resolves the dangling `p0` reference in
  `documentation.status_gate`
- `+ evidence_policy` — binds `engineering_policy.evidence_levels` to where they apply
- `+ budgets` — measurable ceilings behind `optimization.objective`
- `~ workflow_modes` — `review_fix` differentiated from `simple`; type→mode defaults
- `~ agents.ba.escalation` — model escalation added alongside effort
- `~ documentation.files` — QC report, decision log, risk section

## v12 and earlier

Not recorded. v12 is the baseline reviewed in [`REVIEW.md`](REVIEW.md), which enumerates
its gaps as findings F-01 through F-15.
