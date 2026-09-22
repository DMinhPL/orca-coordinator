# Production Risk Review

Use for environment-only, distributed, cache, auth/payment, migration, or critical-release changes.

Verify plausible production dimensions:
- environment/config differences;
- multi-pod/version coexistence;
- CDN/proxy/cache state;
- retry/idempotency/race behavior;
- data/session/account transitions;
- degraded dependency behavior;
- observability needed to diagnose failure;
- blast radius and rollback feasibility.

Use runtime evidence when available. Do not infer production behavior solely from local code structure.
