# Lead Task Decomposition

Decompose by ownership and verification boundary, not by arbitrary file count.

## Good decomposition
- BA: clarify behavior, acceptance criteria, dependencies, architecture questions.
- Dev: one coherent implementation slice with explicit expected outcome and owned files/areas.
- QC: independently verify the completed slice against approved requirements and risk areas.

Prefer one Dev task when changes are tightly coupled and must be reasoned about together. Split Dev tasks only when slices are independently testable, have clear ownership, and parallel work cannot create merge/conflict risk.

Every dispatch must include:
- objective;
- approved scope;
- explicit non-goals;
- required artifact(s);
- known constraints;
- completion evidence expected;
- escalation triggers.
