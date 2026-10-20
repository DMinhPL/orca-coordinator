# Money conventions

Use this overlay only in repositories whose domain stores monetary values.

- Represent persisted amounts in integer minor units; do not introduce binary
  floating-point arithmetic for money.
- Reuse the repository's existing currency and rounding primitives.
- When an operation crosses currencies, require an explicit rate source and
  rounding rule in the acceptance criteria. If either is missing, raise the gap to
  Lead instead of inventing it.
- Add or tighten boundary checks for zero, negative values, maximum supported
  amounts, and rounding edges.

This overlay cannot widen the dispatch allowlist or modification tier.
