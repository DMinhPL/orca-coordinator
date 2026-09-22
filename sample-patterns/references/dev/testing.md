# Developer Testing

Developer tests prove implementation plausibility; they do not replace QC.

## Order
1. Fast targeted unit/type/static checks for changed code.
2. Focused integration/component test for changed behavior.
3. Broader suite only when change surface or project convention justifies it.

Always test the primary success path plus the most relevant failure/edge path. For bug fixes, include or execute a regression case that fails before the fix when practical.

Report command, outcome, and concise evidence. Do not paste full successful logs. Do not repeat already-successful checks without a concrete reason.
