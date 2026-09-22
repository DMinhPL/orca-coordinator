# Developer Compatibility

Load when old/new clients, schemas, pods, cached assets, or staged rollout can coexist.

Check compatibility across:
- API request/response versions;
- persisted data and migrations;
- feature flags/config defaults;
- server-rendered HTML vs static assets;
- cache keys/ETags/version hashes;
- events/messages consumed by old and new code.

Prefer additive transitions before removal. Define when old behavior/data can be safely retired.
