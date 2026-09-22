# QC Code Review

Inspect changed code for:
- requirement mismatch or missing implementation surface;
- incorrect assumptions and silent fallback behavior;
- state/lifecycle/resource leaks;
- boundary validation and error handling;
- backward compatibility;
- duplicated or unreachable logic introduced by the change;
- tests that assert implementation details but miss behavior.

Prefer concrete defects with evidence over style preferences. Mention maintainability only when it creates credible future correctness/risk problems.
