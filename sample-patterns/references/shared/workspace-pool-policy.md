# Workspace Pool Selection Policy

## Goal

Reuse a small, bounded pool of existing Orca/Git worktrees instead of creating a new worktree for every task. Prefer 2-3 reusable task workspaces per project unless the user explicitly requests more isolation.

Primary is never part of the reusable execution pool. Keep the Primary worktree on its coordinator branch.

## Mandatory preflight before worker-start

Before Lead creates or starts any BA, Dev, or QC worker for a task that requires repository access:

1. Inspect registered Git worktrees for the project. Prefer `git worktree list --porcelain` or equivalent read-only Git commands.
2. Identify the Primary worktree and exclude it from candidate execution workspaces unless the user explicitly overrides the Primary policy.
3. Identify reusable task workspaces/worktrees, including worktrees that still exist and are registered even if their old Orca chat/session is hidden or closed.
4. For every candidate workspace, inspect read-only Git state:
   - workspace/worktree name and absolute path;
   - current local branch;
   - upstream/tracking branch, or `none`;
   - current commit SHA (short SHA is sufficient);
   - staged changes;
   - unstaged changes;
   - untracked files.
5. Do not create a new workspace/worktree automatically while any reusable candidate exists.
6. If one or more reusable non-Primary workspaces exist, present the workspace inventory to the user and ask which workspace to use.
7. If ZERO reusable non-Primary workspaces/worktrees exist, explicitly tell the user that the reusable workspace pool is empty and a new workspace must be created. Ask the user to provide the new workspace name before creating anything.
8. If the requested task targets a branch different from the chosen/new workspace branch, ask how the user wants the workspace prepared before checkout.
9. Only after the user chooses an existing workspace or provides a new workspace name, and the checkout strategy is resolved, may Lead prepare that worktree and start a fresh supervised worker there.
## Orca setup path and physical location

Use Orca's configured setup path as the authoritative workspace pool root. A new task workspace should normally have this sibling layout:

```text
<orca-setup-path>/
├── <primary-repository>/       # Primary worktree
└── <task-workspace>/           # Supervised task worktree
```

The logical `child` relationship shown in Orca does not by itself prove filesystem nesting. Always verify the absolute filesystem path and Git worktree metadata.

Before creating or dispatching into a new workspace:

- resolve the configured Orca setup path and the Primary repository root;
- require the task workspace path to be different from and not a descendant of the Primary repository root;
- require the task workspace path to be under the approved Orca setup path or another explicitly approved external workspace pool;
- verify the result with the absolute path and `git worktree list --porcelain` or an equivalent read-only check.

Never create or use:

```text
<primary-repository>/<task-workspace>/
```

If Orca's configured setup path is the Primary repository root, or if Orca cannot expose and verify the destination path, stop before `worker-start` and report the setup/path blocker. Do not silently create a nested or unverified workspace.


## Required inventory format

Use a compact human-readable report similar to:

```text
workspace_1 hiện đang:
- Branch: release/feature-game-section-102924
- Tracking: origin/release/feature-game-section-102924
- Commit hiện tại: 09cc4d3e881
- Trạng thái: sạch, không có code chưa commit
  - Staged: không
  - Unstaged: không
  - Untracked: không

workspace_2 hiện đang:
- Branch: release/demo
- Tracking: origin/release/demo
- Commit hiện tại: a1b2c3d4e5f
- Trạng thái: có thay đổi chưa commit
  - Staged: có (2 files)
  - Unstaged: có (1 file)
  - Untracked: không
```

When useful, include absolute worktree path as a secondary line, but keep the first report concise.

## Empty workspace pool gate

Treat the reusable execution pool as empty when there are no safe, registered, non-Primary Git worktrees available for BA/Dev/QC execution. A hidden/closed Orca session does NOT make the pool empty if its Git worktree is still registered and reusable.

When the pool is empty:
- do not silently create a default `workspace_1` or derive a workspace name from the branch;
- report that no reusable task workspace/worktree exists;
- explain that a new workspace must be created before supervised execution can begin;
- ask the user for the workspace name;
- wait for the user's answer before creating the worktree;
- after receiving the name, validate that it is not already in use and is a safe filesystem/worktree name;
- then ask/confirm the branch preparation strategy when it is not already explicit.

Use a concise prompt like:

```text
Hiện tại không có workspace/worktree task nào có thể reuse (Primary không dùng để execute).
Cần tạo workspace mới trước khi chạy worker.

Bạn muốn đặt tên workspace mới là gì?
Ví dụ: workspace_1, workspace_2, feature-payment
```

After the user supplies a name, if the target branch is already known, continue with a checkout question such as:

```text
Workspace mới: workspace_2
Target branch: origin/release/feature-game-section-102924

Bạn muốn workspace_2:
1. Checkout/create local branch tracking target branch; hoặc
2. Khởi tạo workspace trước nhưng chưa checkout target branch?
```

Do not start BA/Dev/QC until the new workspace exists and its branch state is confirmed.

## Workspace choice gate

After reporting inventory, ask exactly one workspace-selection question when the user has not already named a workspace:

```text
Bạn muốn dùng workspace nào cho task này: workspace_1 hay workspace_2?
```

If the user already named a workspace, verify that workspace only plus any branch-conflict information required for safe checkout. Do not ask the user to choose again.

## Checkout strategy gate

If the selected workspace is clean and the requested branch differs from the current branch, report both branches and ask how to prepare it. Prefer a short choice:

```text
workspace_2 đang ở release/demo và sạch.
Task target: origin/release/feature-game-section-102924.

Bạn muốn:
1. Checkout/create local branch tracking branch target trong workspace_2; hoặc
2. Giữ branch hiện tại và chỉ review target bằng Git refs (read-only)?
```

For implementation/fix work, option 1 is normally required. For review-only work, option 2 may be valid when no working-tree execution is needed; if tests/builds must run against target code, use option 1.

## Dirty workspace safety

Never automatically checkout, reset, stash, clean, discard, or overwrite a workspace that has staged, unstaged, or untracked changes.

If a selected workspace is dirty:
- report the exact dirty categories and concise affected-file counts;
- ask the user to choose another clean workspace or explicitly decide what to do with the existing changes;
- never auto-stash or auto-reset unless the user explicitly asks for it.

## Branch occupancy safety

A local branch can normally be checked out by only one Git worktree at a time. Before checkout:
- detect whether the target local branch is already attached to another worktree;
- if it is, do not attempt duplicate checkout;
- tell the user which workspace owns the branch and offer to use that workspace instead, or ask for a different branch/workspace strategy.

## New workspace creation

Create a new Orca/Git worktree only when one of these is true:
- the reusable non-Primary workspace pool is empty and the user has supplied the new workspace name;
- the user explicitly asks for a new workspace/worktree;
- all reusable workspaces are dirty or otherwise unsafe and the user approves creation;
- the task requires isolation that cannot safely share the existing pool;
- branch occupancy/conflict makes all existing candidates unusable and the user approves creation.

Never invent the new workspace name. When creation is required, obtain the name from the user first.

Do not create a new workspace merely because the target branch is new. Prefer reusing a clean existing workspace and checking out/creating the target branch there after user approval.

## Worker launch after selection

Workspace reuse never means session reuse. After workspace selection/preparation:
- start a FRESH supervised worker with Orca `worker-start`;
- bind the worker to the selected existing worktree;
- preserve configured role provider/model/effort;
- never send the task into an old ordinary chat session merely because that workspace had one before.

## Single-worker launch invariant

For each workflow stage and Task, allow at most ONE active supervised worker for that role. Display naming is metadata on the first worker launch; it must never cause another worker to be created.

Before every `worker-start`:
- inspect the Task/Dispatch/worker state for the current stage;
- if an active worker already exists for the same Task + role/stage, do not call `worker-start` again; continue supervising that existing Dispatch;
- if a settled historical/retained terminal exists, do not count it as an active worker, but do not reuse it as the new worker;
- create a second worker only for an explicit new attempt after the previous attempt is settled (retry, rework, escalation, or user-approved parallel work).

When a display name such as `workspace_2 · QC` is desired, pass it on the FIRST supported worker launch operation. Never start a replacement worker merely to rename a default `worker-task_*` session or to repair a display-name mismatch. If the runtime cannot apply the desired display name, keep the existing worker and report the naming limitation.

After launch, record and verify the single authoritative Task ID, Dispatch ID, terminal handle, workspace, role, requested profile, effective profile, and display name. If two active Dispatches are detected for the same role/stage without an explicit retry/parallel approval, stop creating workers and report a duplicate-worker lifecycle anomaly to the user.

## Workspace identity and display-name policy

Treat the user-selected workspace/worktree name as the human-facing execution identity. Keep workspace identity separate from Git branch identity.

Example:

```text
Workspace: workspace_2
Branch: release/feature-game-section-102924
Tracking: origin/release/feature-game-section-102924
```

Do NOT silently replace `workspace_2` with the branch name in worker/session naming.

When starting a supervised worker in a selected workspace:
- preserve the exact user-selected workspace name;
- use that workspace name in the worker/session display name whenever Orca supports a display-name field;
- prefer the format `<workspace> · <ROLE>`, for example `workspace_2 · DEV`, `workspace_2 · QC`, or `workspace_2 · BA`;
- keep branch/tracking details as separate metadata/report lines, not as the primary display identity;
- do not derive the worker display name from the Git branch unless the user explicitly asks for branch-based naming;
- if the Orca version exposes a separate workspace/worktree display-name operation, set the visible workspace identity to the user-selected workspace name;
- if Orca does not expose a supported way to rename the top-level workspace node, do not invent unsupported commands or flags. Preserve the workspace name in worker display names and Lead reports, and state that the top-level UI label is runtime-controlled.

Before worker-start, Lead should report the final mapping concisely:

```text
Selected workspace: workspace_2
Branch: release/feature-game-section-102924
Tracking: origin/release/feature-game-section-102924
Worker: DEV
Display name: workspace_2 · DEV
```

The workspace name remains stable even when that workspace checks out a different branch later. Branch changes must not silently rename the logical workspace identity.
