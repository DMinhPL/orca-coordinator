# Developer Caching

Load for browser/CDN/server/Redis/application cache changes.

For every cache, identify:
- key and identity dimensions;
- value/source of truth;
- TTL/expiry;
- invalidation trigger;
- stale-data tolerance;
- multi-instance ownership;
- version/deploy interaction.

Avoid cache keys that omit user/session/locale/version dimensions required for correctness. Distinguish browser, CDN, reverse-proxy, framework, object, query, and Redis caching rather than treating 'cache' as one layer.
