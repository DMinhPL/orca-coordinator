# QC Edge Cases

Use only edge cases relevant to the changed boundary.

Common categories:
- null/undefined/empty/zero/max length;
- duplicate/out-of-order events;
- slow response/timeout/retry;
- refresh/reconnect/back-forward navigation;
- stale cache or old version coexistence;
- locale/timezone/date boundary;
- multiple tabs/users/instances;
- permission changes/session expiry;
- partial upstream data.

Avoid speculative combinatorial testing with no plausible failure mechanism.
