# QC Security Review

Use for security-sensitive changes and raise QC effort when configured conditions match.

Look for evidence of:
- authorization bypass/object access mismatch;
- unsafe trust of client/upstream data;
- injection/XSS/CSRF/SSRF/open redirect/path issues where relevant;
- secret/token/PII exposure;
- insecure postMessage/webhook origin validation;
- privilege changes without explicit checks.

Report security findings with concrete attack/precondition and affected boundary; avoid unsupported vulnerability claims.
