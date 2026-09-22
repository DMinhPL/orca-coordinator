# Developer Performance Playbook

Load only when performance is a stated requirement or the change materially affects hot paths.

Measure or reason from a concrete bottleneck before optimizing.

Frontend: network waterfall, JS/CSS payload, render frequency, layout/paint cost, image/animation cost, cacheability, lazy loading.
Backend: query count/latency, serialization, external calls, contention, allocations only when material, cache hit/miss behavior.

Prefer removing repeated work over micro-optimization. Preserve correctness and cache invalidation semantics. Report expected impact and how it was validated.
