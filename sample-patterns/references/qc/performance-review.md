# QC Performance Review

Load when performance is required or materially affected.

Verify the stated bottleneck and compare before/after when feasible. Check for new repeated requests, render loops, N+1 queries, unbounded processing, cache misses, large payloads, or animation/layout cost.

Do not fail a change for theoretical micro-performance concerns without material evidence or a clear hot-path risk.
