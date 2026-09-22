# Contract-First Engineering

Before changing a boundary, identify the contract and its consumers.

Contracts include:
- HTTP/RPC request/response shape and status semantics;
- events/messages/postMessage payloads and origin rules;
- DB/schema fields and migrations;
- local/session storage keys and serialized values;
- URL/query/path conventions;
- config/env values and defaults;
- cache keys/invalidation behavior;
- public component/module interfaces.

Preserve backward compatibility unless the approved requirement explicitly changes it. Update producers and consumers together when required. Do not silently rename/remove contract fields.
