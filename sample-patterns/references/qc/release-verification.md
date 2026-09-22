# Release Verification

Map release checks to risk rather than running every suite.

For elevated release risk verify as applicable:
- compatibility with previous client/server/schema/config;
- migration/default behavior;
- feature-flag/kill-switch behavior;
- cache invalidation/stale behavior;
- readiness/health and traffic timing;
- rollback assumptions;
- old/new version coexistence;
- critical negative/error path;
- monitoring signal for rollout failure.

Return evidence and residual risk. Do not claim release safety for unverified high-impact assumptions.
