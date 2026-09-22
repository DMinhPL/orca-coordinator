# Change Impact Analysis

Use before implementation and again before QC completion.

## Impact map
Classify only relevant surfaces:
- code: entry points, callers, shared utilities, generated output;
- contracts: API, schema, events, postMessage, storage keys, URLs, headers;
- state: DB, Redis, browser storage, framework cache, CDN cache;
- runtime: process, pod, worker, queue, scheduled job;
- config: env vars, feature flags, secrets, build/runtime config;
- deployment: old/new version coexistence, readiness, rollback, asset compatibility;
- clients: browser, mobile WebView, iframe host, external consumers;
- security/payment: authn/authz, trust boundaries, transaction/idempotency paths.

## Rules
1. Start from the requested behavior and trace only direct/credible dependency edges.
2. Mark each surface as `changed`, `must-verify`, `not-affected`, or `unknown`.
3. Do not scan the whole repository to prove a negative. Stop when all credible surfaces are accounted for.
4. Escalate any `unknown` that can change user-visible behavior, data, security, payment, or deployment safety.
5. Lead uses the map for routing; Dev uses it to bound implementation; QC uses it to detect missing change surfaces.
