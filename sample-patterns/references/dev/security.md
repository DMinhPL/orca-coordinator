# Developer Security Playbook

Load for auth, externally supplied input, privileged actions, secrets, uploads, redirects, or security-sensitive boundaries.

Inspect:
- authentication and authorization separately;
- input validation and canonicalization;
- injection risks appropriate to the stack;
- XSS/HTML/URL handling in browser-facing output;
- CSRF for cookie-authenticated state changes;
- SSRF/open redirect/path traversal for URL/path inputs;
- secret/token exposure in logs, client bundles, errors, or URLs;
- origin/source validation for postMessage/webhooks;
- privilege escalation and object-level authorization.

Do not invent custom crypto or security protocols when established platform mechanisms exist.
