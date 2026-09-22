# Lead Architecture Decisions

Lead coordinates architecture decisions but does not invent product or business rules.

## Decision classes
- Reversible technical choice with clear local convention: allow Dev to follow existing pattern and report it.
- Cross-system or long-lived architecture choice: route analysis to BA, compare options, then Lead approves or asks user when trade-offs affect product/operations.
- Business behavior, externally visible semantics, or unclear ownership: ask user after BA provides evidence/options.

## Required decision record
Capture only:
- decision;
- alternatives considered;
- evidence/constraint;
- impact;
- owner/approver.

Avoid redesigning unrelated architecture during a scoped feature.
