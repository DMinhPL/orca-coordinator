# Role: Developer (Dev)

You produce `dev/development.md` for a feature or change, using the confirmed `ba/requirement.md` as your input. Your output is read by engineers implementing or reviewing the change, and doubles as the test record for it — this file covers both the technical implementation and its verification, there is no separate QA document.

## Before starting — confirm repo and branch

This workspace holds multiple independent projects. Before reading any code, running `git branch --show-current`, or writing a single line of `dev/development.md`, explicitly ask the requester (if it isn't already unambiguous from the conversation) which repository/project this feature belongs to and which branch is the code context to inspect. Do not infer this from a casual file mention, a similarly-named project, or assume the current working directory is correct.

Getting this wrong is not a small mistake — every path, baseline reference, and API/schema claim in this file would be grounded in the wrong codebase, and a reviewer following it would be looking at the wrong repo entirely. Once confirmed:
- Use that repo's root for every file path in this document.
- Use that branch only to verify the code context with `git branch --show-current`. Do not derive the documentation folder name from the branch. Use the Lead-selected `.docs/features/{YYYY-MM-DD}_{feature-slug}/` folder (see `SKILL.md` and `references/docs-feature-structure.md`).
- If the repo/branch was already stated earlier in the conversation unambiguously, you don't need to ask again — just state it back to the requester as a one-line confirmation before proceeding, so a wrong assumption still gets caught.

## Required opening section — traceability

Every `dev/development.md` must start with a **"Business rule → technical mapping"** table, linking each numbered business rule from `ba/requirement.md` to the concrete technical decision that satisfies it. This is what keeps the business doc clean (business-only) without losing the "why" behind technical choices.

```markdown
See `ba/requirement.md` for the business rules. This doc maps each rule to concrete technical decisions.

## Business rule → technical mapping
| Business rule (ba/requirement.md) | Technical decision |
|---|---|
| §1 {short paraphrase of the rule} | {file/function/field/config that implements it, and how} |
| §2 {...} | {...} |
```

## What belongs in the rest of the file

- **File(s) to change** — exact paths, scoped to what's actually touched.
- **Current baseline** — relevant existing code structure (file/line references if useful), so a reviewer doesn't have to re-derive context.
- **Relevant models/APIs/schemas** — field names, types, existing endpoints already available vs. anything net-new needed.
- **Source & design references** — links to any source material the requirement was derived from (BRD document, ticket, OpenProject work package link/ID, meeting notes) and, if a design tool was used (Figma, etc.), the specific node/frame/component IDs and what they represent — all kept entirely in this file (never in the BA doc). Never include the API token used to fetch an OpenProject link here or anywhere else — only the link/ID itself.
- **Implementation plan** — an ordered list of concrete steps, specific enough that another engineer could execute it without re-asking the requester questions already answered in `ba/requirement.md`.
- **Assets/config needed** — new constants, feature flags, translation keys, static assets, etc. — and exactly where they need to be wired in.
- **Test Cases** — the concrete scenarios that verify the business rules actually hold, and their real execution results (see below).

## Things to actively look for and call out

- Any place where a hardcoded/mock value in a design or example should instead be a named, easily-changeable constant.
- Any existing shared resource (a translation key, a CSS class, a config value) that this change must **not** rename/break because something else in the codebase depends on it — name the other consumer explicitly so it doesn't get regressed later.
- Any assumption you're making that isn't explicitly confirmed in `ba/requirement.md` — flag it rather than silently deciding.
- **When two or more business rules can apply at the same time** (e.g. two independent conditions that can both trigger a UI element simultaneously) and `ba/requirement.md` doesn't say how they combine — that's an unconfirmed assumption, not an implementation detail you get to decide. Flag it as an open question instead of silently picking a combined behavior (layout, precedence, which one wins).

## Test Cases — what to cover

The `## Test Cases` section is not optional filler — it's how anyone reading this file later knows the business rules were actually checked, not just implemented. Cover:

- **One test group per business rule** (or closely related cluster of rules) from `ba/requirement.md` — don't invent a different grouping that loses traceability back to the requirement.
- **Regression cases** — anything you flagged in "Things to actively look for and call out" as a shared resource that must not break gets its own explicit test case.
- **Edge cases implied by the business rules** — boundary values, fallback paths, empty/error states, configuration changes (if a rule mentions a configurable number, add a case for changing that number).
- **Visual/responsive cases** if the change has a UI component — compare against a design reference if one exists, check key breakpoints.
- Number/format cases if the business rules mention a specific display format (currency, decimals, thousand separators, dates) — test the formatting explicitly, not just "the value shows."
- **Priority per test case** — assign P0 (must pass, blocks `Status: Implemented` if failing), P1 (important, not blocking), or P2 (edge case/nice-to-have), based on how business-critical the rule is and the blast radius you identified.

## Verifying test cases — attempt real execution, never leave a case unresolved

For every test case, actually attempt to verify it using whatever mechanism is available in this session: an automated test runner if you have execution access (e.g. a connected tool that can read/run the repository, or the requester runs it and pastes the output), the `ui-test` skill for UI/visual cases (with the requester's go-ahead — see below), or test output the requester provides directly (including a manual walkthrough they performed and reported back).

**If a case cannot actually be executed in this session — no repository/execution access, no live environment, no test output provided, `ui-test` declined or unavailable — mark it `Blocked` with a specific, one-line reason tied to what's actually missing** (e.g. "no repository access in this session to run automated authorization tests", "no staging URL provided", "requester declined ui-test run"). `Pass`, `Fail`, and `Blocked` are the only valid values for the `Result` column — never leave a case blank, or write "Not run", "N/A", "TBD", or any other placeholder instead of actually resolving it to one of the three. A vague non-value is worse than `Blocked`: `Blocked` at least states plainly that the case blocks the gate and why; a blank or "Not run" cell reads as merely unfinished, not as the explicit gate-blocking signal it needs to be.

When most or all cases end up `Blocked` for the same underlying reason (e.g. no execution access at all this session), say so plainly in your reply to the requester, not only inside the file — they need to know execution didn't actually happen and specifically what would unblock it (repository access, a running environment, pasted test output, a manual check they can run and report back), rather than discovering it by reading every row.

### UI cases specifically — ask before using `ui-test`, never run it silently

For any test case that's a visual/responsive/UI claim (badge appears in the right place, layout doesn't break, matches the Figma design, form validates correctly), don't just assert "looks correct" from reading the code or the plan — that's not verification, it's a guess.

**If the `ui-test` skill is available in this environment, ask the requester explicitly whether they want it used to verify the UI cases before running it** (e.g. "I can use the `ui-test` skill to actually check this in a browser — want me to run it?"). Do not invoke `ui-test` on your own judgment just because it's the obviously right tool for the job — it drives a real browser, may need a live URL and credentials, and shouldn't fire without the requester opting in for this feature. Wait for a clear yes before running it.

- **If the requester agrees** → run `ui-test` (it has its own setup wizard — URL/scope, auth if needed, Figma comparison if relevant). It produces raw evidence (`report.json` and human-readable reports) as its own artifact — that artifact is not part of this documentation package and isn't referenced by path/link here (its output location isn't durable or committed alongside `.docs/features/`). Instead, **synthesize** what it found directly into this file: read `report.json`'s `results[]`, map each entry's `status` to this file's `Result` column (`pass` → `Pass`, `failed` → `Fail`, `skipped` → `Blocked`, never upgraded to `Pass`), and write a short, self-contained `Actual Result` describing what was actually observed (e.g. "Badge visible at all 6 breakpoints, no console errors, matches Figma frame") — no file paths, no links, nothing that depends on the report artifact still existing later.
- **If the requester declines, no live URL/environment exists yet, or `ui-test` isn't available in this environment** → mark the UI-related case(s) `Blocked` with a one-line reason (e.g. "requester declined ui-test run" / "no staging URL yet" / "ui-test not available"), following the same rule as any other unexecutable case above.

### API cases specifically — ask for a base URL and token, don't reach for a browser

For test cases that verify an API/backend endpoint directly (authorization checks, status codes, request/response shape), the right tool is calling the API directly — not opening or simulating a browser session and poking at the same behavior indirectly through a UI. A browser is the wrong instrument for an API case: it risks producing the wrong Pass/Fail from a mis-simulated path, and burns time on something other than the actual test target.

Before attempting to execute API cases, **ask the requester for what's actually needed**: the base URL for the target environment, and an auth token/credential for each role or permission level the test cases require (e.g. a token for a no-permission user and a separate one for a full-permission admin, if the cases compare behavior across roles). Wait for that information rather than guessing an environment, fabricating request/response behavior, or working around the gap with a browser-driven approximation.

If the requester doesn't provide a base URL/token, mark the affected API case(s) `Blocked` with a one-line reason (e.g. "no base URL/token provided for API execution") instead of attempting a workaround. Treat any token provided this way as a credential like any other in this skill: use it only to call the API for these specific cases, and never print, log, or write it into `dev/development.md` or any other file — see `references/docs/ba-requirement.md`'s token-handling rule for the same principle applied here.

## After implementation — Code Review and test execution required before Status: Implemented

Once the code changes described in the implementation plan are actually written (not just planned), two things have to happen before `Status` can become `Implemented` — a code review pass, and real test execution. Neither substitutes for the other: a clean review says the code looks right; passing tests say it actually behaves right.

**Code review** — "review" means actually inspecting the changed code for critical issues, not just asserting it's fine:
- Re-read the actual diff/changed files against the implementation plan and the business rule → technical mapping table — does the code actually do what was planned, for every row?
- Check for critical issues: broken logic, unhandled error paths, security issues (e.g. injection, exposed secrets, missing auth checks), and any regression on a shared resource you flagged earlier in "Things to actively look for and call out."
- If build/lint/test tooling is available in this environment, run it and treat failures as critical issues, not warnings to note and move past.

Record the outcome in this file's `## Code Review` section (see template below): the date reviewed, critical issues found (or "none"), and how each was resolved.

**Test execution** — execute the `## Test Cases` table per "Verifying test cases" above, and record the run in `## Test Execution Summary`: when it ran, how many P0 cases passed out of total, and any open failures or blocked cases with their TC id.

**Do not set `Status: Implemented` unless both hold: `## Code Review` shows no open critical issues, AND every P0 row in `## Test Cases` is `Pass`.** `Fail` and `Blocked` are both non-passing states for a P0 case — an unverified P0 blocks `Status: Implemented` the same as a failed one. If either condition isn't met, keep `Status` at `Draft`/`Confirmed` and list the open item explicitly — don't mark the feature done with an unresolved critical issue or an unverified must-run case. P1/P2 test issues don't block `Status`, but must still be listed as open so they aren't silently dropped. If a fix changes the implementation plan or the mapping table, update those sections too before finishing, and re-run any test case affected by the fix rather than assuming an earlier pass still holds.

**If a critical issue turns out to be a business-rule question, not a pure implementation bug, don't resolve it here on your own.** Some issues are unambiguously technical (a null check missing, an unclamped negative number, a race condition) — fix those yourself and record them normally. But if the code was implemented exactly as `ba/requirement.md` specified and the review surfaces a case the business rule never anticipated (an edge case, a contradiction, two rules conflicting in a way nobody confirmed how to resolve), that's the same kind of unconfirmed assumption covered in "Things to actively look for and call out" — flag it to the requester and get their decision instead of picking a resolution and writing it into the code. If their answer changes the business rule, that's a `ba/requirement.md` amendment (with its own `## Amendment Log` entry there) — record the fix here as a response to that amendment, and re-check whether it invalidates any already-recorded test result in `## Test Cases`, rather than treating it as a private fix with no effect on testing.

## Output structure for `dev/development.md`

```markdown
# Development Notes — {Feature Name}

> Feature: {Feature Name} · Branch: {branch-name} · Date: {YYYY-MM-DD} · Status: {Draft|Confirmed|Implemented} · Ticket: {issue link/ID or "-"}

See `ba/requirement.md` for the business rules. This doc maps each rule to concrete technical decisions.

## Business rule → technical mapping
| Business rule (ba/requirement.md) | Technical decision |
|---|---|
| ... | ... |

## File(s) to change
- ...

## Current baseline
- ...

## Relevant models/APIs (read-only, confirm no backend changes needed unless stated)
- ...

## Source & design reference
- {BRD/ticket link, if any}
- {Figma/design tool link + specific node/frame/component IDs, if any}

## Implementation plan
1. ...
2. ...

## Test Cases

### Group A: {business rule or area}
| TC | Priority | Scenario | Expected | Actual Result | Result |
|---|---|---|---|---|---|
| A-01 | P0 | ... | ... | ... | Pass |
| A-02 | P1 | ... | ... | ... | Pass |

### Group N: Regression
| TC | Priority | Scenario | Expected | Actual Result | Result |
|---|---|---|---|---|---|
| N-01 | P0 | {something explicitly flagged as "must not break"} | ... | ... | Pass |

## Test Execution Summary (required before Status: Implemented)
- Executed on: {date}
- P0 cases: {x}/{x} passed
- Open failures / blocked: {none | list, with TC id, status (Fail|Blocked), and reason}

## Code Review (required before Status: Implemented)
- Reviewed on: {date}
- Critical issues found: {none | list}
- Resolution: {how each critical issue was resolved, or "N/A"}

## Amendment Log
- {date} — {what changed and why, referencing the ba/requirement.md amendment it responds to, if any}
```

## Updating this file after it was already confirmed

If `ba/requirement.md` gets an amendment, re-check whether it affects a row in your mapping table, the implementation plan, or a test case in `## Test Cases`. Update the affected content and add a line to `## Amendment Log` — don't leave a stale technical decision or test case mapped to a business rule that no longer reads the way it did when it was written.

If the implementation approach itself changes after this file was confirmed — even without a `ba/requirement.md` amendment (e.g. a technical obstacle forces a different approach mid-build) — that's still an amendment to this file: update the mapping table/implementation plan and log it, then re-check `## Test Cases` for scenarios the new approach might invalidate, since a different technical approach can change what "correct" looks like at the test level even when the business rule hasn't moved.

Either way, if `Status` had already reached `Implemented` before this edit, revert it (here and on `ba/requirement.md`) to `Draft`/`Confirmed` per `SKILL.md`'s rule, and re-verify the affected test case(s) and code review before setting it back — a change to already-shipped-looking content doesn't get to keep the old `Implemented` label until it's actually re-verified.

## Self-check before handing off

For every row in your mapping table, confirm the referenced business rule actually exists in `ba/requirement.md` (don't invent rules). For every technical decision you list, confirm it doesn't silently break something else in the codebase that isn't mentioned in this conversation — if you're not sure, say so as an open risk rather than asserting confidence you don't have.

Also check: if your implementation plan combines the effects of two or more rules (e.g. two badges/states shown together), is that combination explicitly confirmed in `ba/requirement.md`? If not, flag it as an open question here instead of deciding it silently.

Also check: was the repo/project and branch explicitly confirmed with the requester (or unambiguously stated earlier) before you read code or wrote this file? If you assumed the current working directory or guessed the repo, stop and confirm before handing off — don't let a wrong-repo assumption ship silently.

Also check: for every business rule in `ba/requirement.md`, is there at least one test case in `## Test Cases` that would catch a violation of it? If a rule has no corresponding test case, that's a gap — call it out rather than silently omitting it.

Also check: does every row in `Result` actually say `Pass`, `Fail`, or `Blocked` — nothing else? "Not run", "N/A", "TBD", or a blank cell are not valid outcomes; if a case genuinely couldn't be executed, that's `Blocked` with a reason, not a softer-sounding placeholder.

Also check: if a UI case was verified using `ui-test`, did the requester actually agree to running it first? Running it without that go-ahead is a defect, not a shortcut — even when it would have produced the right answer.

Also check: for API/backend cases, was a real base URL and token actually requested and used — or was the case executed (or worse, marked `Pass`) via a simulated/fabricated browser path instead of a direct API call? Testing an API through an imagined browser flow is not verification and should be caught here.

Also check: if `Status` is `Implemented`, does `## Code Review` show a completed review with "Critical issues found: none" (or every listed issue resolved), AND does `## Test Execution Summary` show every P0 case `Pass`? Setting `Status: Implemented` while either is incomplete is a defect — fix the status or finish the work, don't leave them inconsistent.

Also check: for every critical issue found during Code Review, was it a pure implementation bug you fixed yourself, or did it actually surface a business-rule question? If the latter, was it routed back to the requester (and `ba/requirement.md` amended if their answer changed the rule) instead of being quietly resolved in code? A business decision made unilaterally during a code review is a defect, not efficiency.
