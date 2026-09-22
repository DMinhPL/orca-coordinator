# Developer Implementation Strategy

Before editing, state internally:
- intended behavior change;
- affected surface;
- invariants to preserve;
- validation plan.

Then:
1. Implement the minimal coherent change.
2. Update types/contracts/config together when they form one compatibility boundary.
3. Reuse existing abstractions unless they force unsafe duplication or incorrect semantics.
4. Keep feature flags/defaults backward compatible when rollout may overlap old/new versions.
5. Run focused validation first.
6. Inspect final diff for accidental scope expansion.

If implementation requires changing approved behavior, stop and ask Lead rather than silently adapting the requirement.
