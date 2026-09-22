# Escalation Policy

Escalate based on observed evidence, not task labels alone.

## Model/effort escalation
- Start with configured default.
- Raise effort/model only when the current role is blocked by demonstrated complexity, repeated failed reasoning, ambiguous architecture, or high-risk verification needs.
- Record the trigger and expected benefit.
- Do not escalate all roles together.

## Rework stop conditions
- A worker gets one substantive phase result per dispatch.
- If the same material defect/root-cause hypothesis fails twice, stop blind retry and escalate to Lead/User or a stronger model with explicit reason.
- Missing requirement/business decision is not solved by repeated Dev/QC retries.
- Do not use Sol/Opus merely because a task looks large; require an observed failure/complexity trigger.
