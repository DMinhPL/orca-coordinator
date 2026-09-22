# Risk-Based Definition of Done

Completion depth must match change risk.

## Low risk
Localized/reversible change with no persistent state, security, distributed, or contract impact:
- requested behavior implemented;
- focused tests/checks pass;
- changed surfaces reviewed;
- docs updated when required.

## Medium risk
Cross-module, API/contract, cache, config, or meaningful regression surface:
- low-risk criteria;
- impacted contracts/dependencies verified;
- negative/error path checked;
- relevant regression coverage;
- compatibility/release considerations recorded.

## High risk
Auth, payment, persistent migration, security boundary, concurrency, distributed state, critical cache, production incident, or high-blast-radius rollout:
- medium-risk criteria;
- explicit failure-mode review;
- rollback/feature-flag/readiness considerations as applicable;
- old/new version or state coexistence checked;
- targeted security/data-integrity checks;
- QC evidence sufficient for release decision.

Lead selects DoD depth from risk. Dev must not broaden checks without reason; QC must not reduce required high-risk coverage for token savings.
