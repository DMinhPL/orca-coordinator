# Developer Frontend Playbook

Load for browser, React, Next.js, SPA, UI, iframe, or WebView work.

Inspect relevant risks:
- server/client/rendering boundary and hydration;
- state ownership and stale state;
- effect cleanup, dependency stability, duplicate subscriptions, stale closures;
- loading/empty/error/disabled states;
- responsive layout, overflow, long content, keyboard/accessibility when UI-facing;
- browser storage identity/expiry and cross-tab behavior;
- network cancellation, race between requests, duplicate submits;
- bundle/lazy-load/image/animation cost for performance-sensitive screens;
- iframe/WebView origin, postMessage validation, navigation and close lifecycle;
- cache and asset versioning when deployed behind CDN/multiple pods.

Follow the project's framework conventions instead of introducing a new state/data-fetching pattern casually.
