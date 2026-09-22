# QC Regression Testing

Focus regression on neighboring behavior that shares the changed boundary.

Examples:
- changed parser -> old valid payloads plus malformed/new payload;
- changed auth -> unauthenticated, authorized, unauthorized;
- changed cache -> hit, miss, invalidation, identity separation;
- changed state transition -> previous/next states and duplicate action;
- changed shared component -> highest-risk consumers, not every screen by default.

Do not run broad suites solely for ceremony when a focused suite provides stronger evidence.
