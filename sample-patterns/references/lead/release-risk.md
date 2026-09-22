# Release Risk Routing

Use the change-impact map and risk assessment to determine release depth.

Escalate release scrutiny when any of these apply:
- old/new versions may coexist;
- persistent data/schema changes;
- auth/payment/security path;
- cache/CDN/multi-pod consistency;
- runtime config or feature flags;
- irreversible external side effects;
- critical user flow or broad blast radius.

For elevated risk, require applicable checks from `references/shared/release-deployment-safety.md` and high-risk Definition of Done. Route missing product/business decisions to User instead of inventing them.
