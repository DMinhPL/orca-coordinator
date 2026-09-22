# Observability & Production Debugging

Use when behavior differs in SAT/UAT/Live, across pods, or cannot be reproduced locally.

## Evidence-first flow
1. State expected vs actual behavior and environment.
2. Capture request identity/time window and, when available, correlation/request/trace ID.
3. Inspect targeted evidence: browser Network, request/response headers, status/body, application logs, proxy/CDN headers, pod/container logs, cache state, deployment version, timing.
4. Correlate evidence across boundaries before proposing a fix.
5. Form one hypothesis at a time and identify what evidence would confirm/refute it.
6. Prefer targeted reproduction or instrumentation over speculative code edits.

## Guardrails
- Never infer a pod, cache layer, CDN decision, or backend path from symptoms alone when headers/logs can verify it.
- Do not dump broad production logs into context. Use the narrowest time range and identifiers available.
- Redact secrets/tokens/PII from reports.
