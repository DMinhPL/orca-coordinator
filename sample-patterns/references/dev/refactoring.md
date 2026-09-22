# Developer Refactoring

Refactor only when required for the approved change or explicitly requested.

Preserve observable behavior unless behavior change is approved. Separate mechanical changes from semantic changes when practical. Keep public contracts stable, migrate call sites coherently, and use focused tests around the moved abstraction.

Stop if the refactor expands into architecture redesign not required by the task; report that opportunity separately.
