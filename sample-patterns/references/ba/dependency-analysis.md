# BA Dependency Analysis

Identify dependencies that can change scope or acceptance criteria:
- upstream/downstream APIs;
- persisted data/schema;
- cache/session/shared state;
- deployment/config/environment;
- external provider/browser/WebView constraints;
- other features consuming the same contract.

Classify each as required, optional, unknown, or out of scope. Raise unknowns to Lead when they can alter implementation behavior.
