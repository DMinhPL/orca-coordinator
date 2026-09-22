# Developer API Playbook

Load when changing HTTP/RPC contracts or API consumers.

Verify:
- method semantics and status codes;
- request/response schema compatibility;
- optional vs required fields and defaults;
- null/empty/unknown values;
- pagination/filter/sort contracts;
- auth/authz and trust boundary;
- timeout/retry/idempotency behavior;
- versioning and old-client/new-server coexistence;
- error payload shape expected by consumers.

For consumer changes, handle malformed or partial upstream responses deliberately rather than assuming perfect data.
