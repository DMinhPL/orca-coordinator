# Lead Incident Debugging Coordination

For incidents or hard production-like failures:
1. Stabilize scope: what is broken, where, since when, and what changed.
2. Ask BA only when system-flow investigation or requirement ambiguity matters.
3. Give Dev evidence and reproduction details, not a proposed fix unless already proven.
4. Require Dev to isolate root cause before broad refactoring.
5. Require QC to verify both the fix and the failure mode that caused the incident.
6. Track deployment/cache/multi-instance effects separately from application logic.

Do not let multiple workers make independent speculative fixes to the same failure surface.
