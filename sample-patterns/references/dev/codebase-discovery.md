# Developer Codebase Discovery

Understand the smallest architecture slice necessary to implement safely.

## Discovery algorithm
1. Find the user-facing or runtime entry point for the requested behavior.
2. Trace direct callers/imports/dependencies only as needed.
3. Find the nearest analogous implementation and follow its conventions.
4. Locate tests, schemas/types, configuration, and persistence touched by the path.
5. Identify external boundaries: API, DB, cache, queue, iframe/WebView, CDN, filesystem, provider SDK.
6. Stop discovery when the implementation surface and validation path are clear.

## Avoid
- repository-wide scans by default;
- reading unrelated modules for general understanding;
- redoing BA architecture research;
- loading large generated/vendor files unless directly relevant.
