# Lead Risk Assessment

Score internally; do not expose the numeric score unless useful.

## Dimensions
### Change surface
- 0: localized
- 1: one module
- 2: cross-module
- 3: cross-system

### Data impact
- 0: no persisted data
- 1: reversible/transient state
- 2: persisted compatible change
- 3: migration, destructive, or hard-to-recover change

### Security/business criticality
- 0: none
- 1: ordinary feature
- 2: authentication/authorization/payment/business-critical path
- 3: privilege, secrets, money movement, or externally exposed trust boundary

### Runtime/distribution
- 0: local synchronous logic
- 1: request lifecycle/client state
- 2: cache/async/background/multi-instance
- 3: concurrency, race, distributed consistency, deployment overlap

## Routing guidance
- Low: Simple/Review-fix; default Dev/QC.
- Medium: Standard when requirements are not already explicit; focused BA; default Dev; QC medium.
- High: Standard; deeper BA; Dev high or hard profile when conditions match; QC high for relevant risks.

A single critical dimension can justify escalation even when the total is otherwise low.
