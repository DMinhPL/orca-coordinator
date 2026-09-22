# Feature Documentation Structure

This documentation package is part of the Engineering Manager workflow. Do not invoke a separate `docs-feature-structure` skill; the rules are integrated here.

## Completion requirement

Before an engineering task is reported as successfully complete, ensure the target repository contains:

```text
.docs/features/{YYYY-MM-DD}_{feature-slug}/
  ba/
    requirement.md
  dev/
    development.md
```

All Markdown content must be in English.

## Folder naming

Create the folder inside the target repository root, not a multi-repo workspace root.

Use this format:

```text
YYYY-MM-DD_<feature-slug>
```

Where:
- `YYYY-MM-DD` = current local date.
- `<feature-slug>` = a short human-readable description of the actual feature/task meaning.
- Derive the slug from confirmed requirements, task intent, and feature semantics.
- Do **not** copy the Git branch name as the default slug. The branch is context only.
- Prefer 2-4 meaningful words.
- Use lowercase kebab-case.
- Keep the slug at or below 32 characters when practical.
- Name **what the feature is**, not the environment, workflow, ticket, implementation technique, or branch history.
- Remove noise such as `sat`, `uat`, `prod`, `release`, `feature`, `fix`, `refactor`, ticket numbers, and suffixes such as `v2`/`v3` unless they are genuinely part of the user-facing feature name.
- Keep meaningful digits that are part of the feature identity, for example `win2dao`.

### Suggest before creation

Lead owns folder-name selection. Before creating a new feature documentation folder:

1. Read the confirmed task/requirement context.
2. Generate one concise recommended feature slug.
3. Announce the proposed folder name to the user/Lead context before creating it.
4. If the feature meaning is clear, proceed with that name without requiring confirmation.
5. If the feature meaning is ambiguous, propose at most two concise alternatives and ask the user to choose before creating the folder.
6. Once the folder is created for the task, keep that folder name stable for later BA/Dev/QC updates. Do not rename it because the branch name or implementation details change.

Examples:

```text
Branch: sat/feature-sections-config-v2
Task: configure dynamic feature sections
Folder: 2026-08-25_feature-sections
```

```text
Branch: fix/portal-wallet-auto-connect-sign-v3
Task: fix automatic wallet signing flow
Folder: 2026-08-25_wallet-auto-sign
```

```text
Branch: refactor/win2dao-update-locale-101488
Task: update WIN2DAO locale handling
Folder: 2026-08-25_win2dao-locale
```

If task semantics are unavailable or too vague to produce a trustworthy feature slug, do not silently fall back to the branch name. Ask the user for the feature name or present two short candidate names derived from the available context.

## Ownership

### `ba/requirement.md`
Business-only. BA owns it when BA participates. Read `references/docs/ba-requirement.md` before creating/updating it.

It must describe what should happen, business rules, acceptance criteria, confirmed decisions, out-of-scope items, and amendments. It must not contain code/file/API/DB/config/design-node implementation details.

### `dev/development.md`
Technical and implementation record. Dev owns it when Dev participates. Read `references/docs/dev-development.md` before creating/updating it.

It must include technical mapping, files/baseline, implementation plan, test cases, test execution summary, code review, and amendments as applicable.

## Lifecycle

- Standard: BA updates `ba/requirement.md` after requirement confirmation; Dev updates `dev/development.md`; QC evidence is incorporated into the development document only after QC reports `worker_done`.
- Simple: if BA is skipped, Lead may create a minimal `ba/requirement.md` only from an already-explicit, already-confirmed user requirement. Lead must not invent new business rules.
- Research-only: BA creates/updates `ba/requirement.md`; create/update `dev/development.md` as a non-implementation planning record and keep status Draft/Confirmed.
- QC-only: update existing docs when available; if absent, create the two-file package with minimal traceability and mark unknown items explicitly instead of guessing.

## Status gate

Never set `Status: Implemented` unless all of these are true:
1. The latest Dev phase returned `worker_done` for implementation work when implementation was required.
2. The latest QC phase returned `worker_done`.
3. `## Code Review` has no open critical issues.
4. Every P0 test case is Pass.

If QC did not return `worker_done`, status cannot be Implemented.

## Amendments

If a confirmed requirement or implementation changes, update the affected section in place and append an `## Amendment Log` entry. Re-open status from Implemented to Draft/Confirmed until affected review/tests are re-verified.
