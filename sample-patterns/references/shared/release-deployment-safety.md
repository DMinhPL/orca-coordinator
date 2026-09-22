# Release & Deployment Safety

Apply when a change affects runtime configuration, persistent data, cache, assets, APIs, distributed systems, or rollout behavior.

Check as applicable:
- backward compatibility with existing clients/data;
- old/new application versions coexisting during rolling deployment;
- schema/config migration ordering and defaults;
- cache invalidation and stale-key behavior;
- static asset/hash compatibility across pods/CDN;
- feature-flag default, rollout, and kill-switch behavior;
- readiness/health behavior before traffic is accepted;
- graceful shutdown/in-flight request handling;
- rollback feasibility and rollback data compatibility;
- external dependency/version compatibility;
- observability needed to detect rollout failure.

Do not require every item for every task. Increase depth for auth, payment, cache, migration, distributed state, or critical release paths.
