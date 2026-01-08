---
allowed-tools: Bash(git worktree:*), Bash(git branch:*), Bash(git status:*), Bash(rm:*), Bash(dropdb:*), Bash(psql:*), AskUserQuestion
argument-hint: [<path-or-name>] [--force] [--drop-db]
description: Remove a Git worktree with proper cleanup
---

# Clean Git Worktree

Safely remove a Git worktree with proper cleanup, including optional database removal.

## Current Context

**Existing worktrees:**
!`git worktree list 2>/dev/null || echo "Not a git repository"`

## Arguments

$ARGUMENTS

Parse these arguments:
- `path-or-name` (optional) - Worktree path or branch name to remove
- `--force` - Force removal even with uncommitted changes
- `--drop-db` - Also drop associated database (prompts for confirmation)

---

## Workflow

### Step 1: List Worktrees

If no worktree specified, list all worktrees and ask user to select:

```bash
git worktree list
```

Display in a numbered list:
```
Available worktrees:
1. /path/to/main (main) [bare]
2. /path/to/feature-auth (feature-auth)
3. /path/to/feature-api (feature-api)

Which worktree would you like to remove? (Enter number or path)
```

### Step 2: Validate Selection

1. Verify the selected worktree exists
2. **CRITICAL**: Never allow removal of the main worktree (marked `[bare]` or the primary repo)
3. Confirm the worktree path

### Step 3: Check for Uncommitted Changes

```bash
git -C <worktree-path> status --porcelain
```

If changes exist:
- **Without `--force`:** Warn user and ask to confirm
- **With `--force`:** Proceed but log warning

**Warning message:**
```
WARNING: Worktree has uncommitted changes:
  M  src/file.ts
  ?? new-file.js

These changes will be LOST. Continue? (y/n)
```

### Step 4: Check for Unpushed Commits

```bash
git -C <worktree-path> log @{u}..HEAD --oneline 2>/dev/null
```

If unpushed commits exist, warn user:
```
WARNING: Worktree has X unpushed commits:
  abc1234 feat: add new feature
  def5678 fix: resolve bug

These commits will be LOST if the branch is deleted. Continue? (y/n)
```

### Step 5: Optional Database Cleanup

If `--drop-db` flag provided or if `.env.local` contains `DATABASE_URL`:

1. Extract database name from `.env.local`:
   ```bash
   grep DATABASE_URL <worktree-path>/.env.local
   ```

2. Parse worktree-specific database name (e.g., `myapp_feature_auth`)

3. **Ask for confirmation:**
   ```
   Drop database 'myapp_feature_auth'? This cannot be undone. (y/n)
   ```

4. If confirmed:
   ```bash
   dropdb myapp_feature_auth
   ```

### Step 6: Remove Worktree

```bash
# Standard removal
git worktree remove <path>

# Force removal (if uncommitted changes and --force)
git worktree remove --force <path>
```

### Step 7: Clean Up Stale Entries

```bash
git worktree prune
```

### Step 8: Present Summary

```
## Worktree Removed Successfully

| Property | Status |
|----------|--------|
| Path | /path/to/worktree (removed) |
| Branch | feature-auth (retained) |
| Database | myapp_feature_auth (dropped) |
| Stale entries | Pruned |

### Next Steps
- Branch 'feature-auth' still exists. Delete with: `git branch -d feature-auth`
- Or keep the branch for future work
```

---

## Safety Rules

1. **Never remove the main worktree** - Protect the primary repository
2. **Warn about uncommitted changes** - Data loss is irreversible
3. **Warn about unpushed commits** - Commits may be lost
4. **Require confirmation for database drop** - Database deletion is permanent
5. **Always run `git worktree prune`** - Clean up stale metadata

---

## Examples

**Interactive selection:**
```
/clean-worktree
```
Lists worktrees and prompts for selection.

**Specific worktree:**
```
/clean-worktree ../project-feature-auth
```
Removes the specified worktree.

**Force removal:**
```
/clean-worktree ../project-feature-auth --force
```
Removes even with uncommitted changes (still warns).

**With database cleanup:**
```
/clean-worktree ../project-feature-auth --drop-db
```
Also drops associated database after confirmation.

---

## Related

- **Skill:** `git-worktree-setup` - Detailed guidance on worktree management
- **Command:** `/create-worktree` - Create new worktrees
