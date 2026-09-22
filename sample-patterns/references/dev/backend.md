# Developer Backend Playbook

Load for server/service/API-processing work.

Check:
- request validation and normalization at the boundary;
- authentication vs authorization responsibilities;
- service/domain separation already used by the codebase;
- idempotency for retryable writes;
- timeout, cancellation, retry, and partial-failure behavior;
- transaction boundaries and side effects;
- structured error mapping without leaking sensitive internals;
- logs/metrics around materially important failures;
- backward compatibility during rolling deployments.

Do not add retries around non-idempotent operations without an explicit safety mechanism.
