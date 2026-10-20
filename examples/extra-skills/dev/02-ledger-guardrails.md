# Ledger guardrails

Apply these constraints when the task touches ledger entries or balances.

- Prefer append-only corrections over mutating historical entries.
- Preserve idempotency keys across retries and test the duplicate-delivery path.
- Treat an unbalanced debit/credit pair, a destructive migration, or an unclear
  reconciliation rule as a blocker requiring Lead review.
- Include a rollback note that explains how partially written entries are detected
  and reconciled; "revert the code" alone is insufficient for persisted ledger data.

These rules only tighten the base Dev skill. They do not authorize new files,
schema changes, or production writes.
