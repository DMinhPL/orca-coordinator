# Lead Rework Strategy

When QC returns FAIL/BLOCKED:
- classify the finding as implementation defect, requirement ambiguity, environment/tool blocker, or architecture conflict;
- send only the minimal finding/evidence to the appropriate owner;
- create a new Dev dispatch for code changes;
- after Dev `worker_done`, create a fresh QC dispatch;
- never keep one QC worker in an indefinite fix/retest loop.

Escalate to user when fixing requires changing approved behavior, accepting material risk, or choosing among product/architecture trade-offs.
