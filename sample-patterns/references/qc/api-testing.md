# QC API Testing

Load for API/server contract changes.

Verify relevant combinations of:
- valid request;
- malformed/missing field;
- auth/authz failure;
- not found/conflict/rate limit when applicable;
- timeout/upstream failure;
- response schema and status semantics;
- backward compatibility with existing consumer expectations;
- retry/idempotency for writes.
