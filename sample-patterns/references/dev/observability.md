# Dev Observability

When implementation or debugging crosses runtime boundaries, preserve enough observability to verify behavior.

Prefer existing logging/metrics/tracing conventions. Add targeted instrumentation only when needed and approved by repository conventions.

Useful evidence includes correlation/request IDs, operation/result, dependency latency, retry count, cache hit/miss, selected version/config, and relevant state transition. Never log secrets, credentials, raw tokens, or unnecessary PII.

For SAT/UAT/Live-only bugs, follow `references/shared/observability-production-debugging.md` before speculative edits.
