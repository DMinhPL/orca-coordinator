# QC Distributed-System Review

Load for multi-pod, cache, queue, async, sticky-session, or rolling-deployment changes.

Test/reason about:
- old and new versions coexisting;
- first request without affinity state;
- requests reaching different instances;
- shared vs local cache/state;
- duplicate/reordered/retried events;
- stale CDN/browser/server cache;
- readiness/drain timing;
- instance-specific evidence in logs.

A single-instance pass is insufficient evidence for a multi-instance correctness claim.
