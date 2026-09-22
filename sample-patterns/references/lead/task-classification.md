# Task Classification

Classify each incoming task before workflow selection. Use one primary type and optional secondary tags.

Primary types:
- `feature`
- `bug`
- `refactor`
- `performance`
- `security`
- `infra`
- `migration`
- `investigation`
- `review-only`
- `release-fix`

## Routing hints
- `feature`: BA when requirements/architecture are not already explicit; Dev implementation; QC by risk.
- `bug`: if root cause unknown, use Dev debugging playbook; BA only for unclear expected behavior.
- `refactor`: preserve behavior; emphasize compatibility/regression and minimal change surface.
- `performance`: load Dev + QC performance playbooks and require before/after evidence where measurable.
- `security`: high-risk routing; security playbooks; stronger QC and evidence requirements.
- `infra`: load distributed/release/observability playbooks; inspect rollout and multi-instance behavior.
- `migration`: require compatibility, ordering, rollback/data safety, and high-risk DoD as applicable.
- `investigation`: default to research/diagnosis; do not implement unless scope explicitly changes.
- `review-only`: QC owns review; do not spawn Dev unless the user asks for fixes.
- `release-fix`: optimize for minimal safe change, production evidence, rollback, and focused high-risk QC.

Classification informs workflow, model effort, BA depth, QC depth, and reference loading. It does not override explicit user instructions.
