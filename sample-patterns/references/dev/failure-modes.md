# Failure-Mode Analysis

For each material behavior, consider only plausible failure modes:
- dependency timeout/unavailable/malformed response;
- duplicate request, retry, double-click, replay, idempotency;
- stale/missing cache or storage;
- partial state update;
- race/concurrency/order change;
- user/session/account switch;
- old/new client or server version coexistence;
- config missing/invalid;
- network reconnect/navigation/unmount;
- permission/auth expiration;
- rollback after partial rollout.

Do not manufacture exhaustive edge cases. Prioritize failure modes by likelihood x impact and cover high-impact cases for auth, payment, persistent state, cache, and distributed flows.
