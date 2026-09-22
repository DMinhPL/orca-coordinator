# Developer Database Playbook

Load when schema, query, persistence, or migration behavior changes.

Check:
- migration compatibility with existing data;
- forward/backward compatibility during rollout;
- indexes for new query paths;
- N+1 and unbounded scans;
- transaction/locking/deadlock implications;
- null/default semantics;
- uniqueness and race conditions;
- rollback/recovery implications.

Never assume an empty database or instantaneous migration in production-like systems.
