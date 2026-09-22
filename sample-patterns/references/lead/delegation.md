# Delegation Skill

Use when assigning work to ba, dev, or qc.

A specialist worker starts with an EMPTY context. It does not inherit Lead's
skill, files, or memory. It only knows what the dispatch injects. Therefore the
dispatch MUST hand the worker its role and force it to load and acknowledge the
contract before doing work. A task description alone is not enough — that is how
workers "bypass" rules they were never actually given.

## Delegation format
Every dispatch to BA/Dev/QC MUST contain, in this order:

1. **Role Bootstrap (mandatory first block)**
   - `You are the <ROLE> worker.`
   - `Absolute paths to read FIRST:` list `references/shared/role-contract.md`,
     the role file (`references/<role>.md`), and the role's mandatory core
     playbooks. Use paths resolved in the target workspace, not relative guesses.
   - `Before any task work, emit the ROLE CONTRACT ACK block from role-contract.md §7.`
   - `Do not read/edit/produce anything else until the ACK is emitted.`
2. **Context** — approved requirement sections, prior-stage outputs, workspace path, branch.
3. **Objective** — one clear task.
4. **Constraints** — scope/non-goals, evidence rules that apply, risk level (DoD depth).
5. **Expected output** — the exact structures required (boundary matrix, Falsy Trace when applicable, evidence tiers, verdict).
6. **Definition of done** — from `references/shared/definition-of-done.md` at the selected risk depth, plus "artifact passes `tools/validate_worker_output.py`".

## Agent mapping
- ba: requirements, business rules, acceptance criteria.
- dev: code, architecture, technical solution, implementation.
- qc: test strategy, test cases, regression, quality risks.

## Rules
- Give one clear task at a time.
- Pass relevant context from previous agents.
- Ask for concise, decision-ready output.
- Never dispatch a specialist without the Role Bootstrap block.
- The first thing Lead checks on any worker output is the presence and
  consistency of the ROLE CONTRACT ACK. Missing/inconsistent ACK = INVALID =
  re-dispatch, not "close enough".

## Copy-paste dispatch skeleton
```text
You are the <ROLE> worker in an Orca engineering workflow. Lead coordinates; you report only to Lead.

ROLE BOOTSTRAP (do this before anything else):
- Read now, in full: <abs>/references/shared/role-contract.md, <abs>/references/<role>.md, and that role's mandatory core playbooks.
- Then emit the "ROLE CONTRACT ACK — <ROLE>" block exactly as defined in role-contract.md §7.
- Do not read source, edit files, or produce findings before the ACK.

CONTEXT:
<approved requirement + prior outputs + workspace path + branch>

OBJECTIVE:
<one task>

CONSTRAINTS:
- Risk level: <low|medium|high> (apply matching Definition of Done depth).
- Evidence rules: label every behavioral claim EXECUTED/STATIC/REASONED-ONLY/UNVERIFIED. No "tested" without pasted run output. External data shapes are assumptions until proven with a real sample.
- <QC only> Phase A derive from acceptance criteria BEFORE reading development.md.

EXPECTED OUTPUT:
<verdict/report or changed-files/development.md> including the boundary matrix, the Falsy Trace if any truthy/falsy check on possibly-0/""/false/null exists, and evidence tiers per claim.

DEFINITION OF DONE:
- Meets the risk-matched DoD.
- Artifact passes tools/validate_worker_output.py --role <role>.
- Ends with exactly one Orca worker_done.
```
