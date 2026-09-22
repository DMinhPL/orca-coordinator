# Developer Debugging Playbook

Use evidence-driven debugging.

1. Reproduce or establish a trustworthy observable symptom.
2. Define expected vs actual behavior precisely.
3. Identify the earliest boundary where state/control diverges.
4. Form one or a small number of falsifiable hypotheses.
5. Collect targeted evidence: logs, state, request/response, timing, diff, stack trace.
6. Change one causal variable or implement the narrowest proven fix.
7. Re-run the failing scenario.
8. Run focused regression checks around the affected boundary.

Avoid shotgun edits, multiple speculative fixes at once, or treating a transient pass as proof. For intermittent/race/cache issues, preserve timing and instance identity evidence.
