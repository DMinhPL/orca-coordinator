# QC Review Strategy

Verify risk, not just syntax.

1. Map approved acceptance criteria to observable implementation/test evidence.
2. Inspect the current diff and identify changed behavioral boundaries.
3. Ask what should have changed but did not.
4. Select focused checks based on risk categories.
5. Report PASS only when required behavior and material regression risks are covered.

Do not merely approve because code looks idiomatic. Do not broaden into an unrelated full-repository audit.
