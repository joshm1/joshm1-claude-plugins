---
allowed-tools: Bash(git worktree:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(ls:*), Bash(mkdir:*), Bash(uv run:*), Bash(python:*), Read, Write, AskUserQuestion
argument-hint: <branch> [--path <dir>] [--offset <n>] [-b] [--dry-run]
description: Create a Git worktree with proper environment isolation
---

# Create Git Worktree

Create a new Git worktree with automatic environment isolation including port configuration, file copying, and Claude settings.

## Current Context

**Repository:** !`basename $(git rev-parse --show-toplevel 2>/dev/null || pwd)`

**Current branch:** !`git branch --show-current 2>/dev/null || echo "N/A"`

**Existing worktrees:**
!`git worktree list 2>/dev/null || echo "Not a git repository"`

## Arguments

$ARGUMENTS

Parse these arguments:
- `branch` (required) - Branch name to create worktree for
- `--path <dir>` - Worktree directory (default: `../<project>-<branch>`)
- `--offset <n>` - Manual port offset (default: auto-calculated 100-999)
- `-b` - Create new branch from current HEAD
- `--dry-run` - Preview without making changes

---

## Workflow

### Step 1: Validate Arguments

1. Extract branch name from arguments (required)
2. Determine worktree path (use `--path` or default to sibling directory)
3. Check for `-b` flag (create new branch)
4. Check for `--dry-run` flag

### Step 2: Validate Branch

**If `-b` flag NOT provided:**
```bash
git rev-parse --verify <branch> 2>/dev/null
```
- If branch doesn't exist, inform user and suggest using `-b` flag

**If `-b` flag provided:**
- Branch will be created from current HEAD

### Step 3: Validate Worktree Path

```bash
# Check path doesn't exist
! test -d <path>
```
- If path exists, ask user whether to proceed or choose different path

### Step 4: Create Worktree

**For existing branch:**
```bash
git worktree add <path> <branch>
```

**For new branch:**
```bash
git worktree add -b <branch> <path> HEAD
```

### Step 5: Run Setup Script

Locate and run the environment setup script:

```bash
# Find the setup script
find ~/.claude/plugins -name "setup_worktree.py" -path "*git-worktree-setup*" 2>/dev/null | head -1
```

Run with appropriate options:
```bash
uv run <script_path> --worktree <path> --source . [--offset <n>] [--dry-run]
```

If script not found, perform manual setup:
1. Copy `.env*` files
2. Copy `.claude/settings.local.json`
3. Copy `.vscode/` or `.idea/` if present

### Step 6: Present Summary

Display results in a formatted table:

```
## Worktree Created Successfully

| Property | Value |
|----------|-------|
| Branch | <branch> |
| Path | <path> |
| Port Offset | <offset> |

### Files Copied
- .env
- .env.local
- .claude/settings.local.json
- .vscode/

### Port Assignments
| Service | Port |
|---------|------|
| Dev Server | 3XXX |
| API | 8XXX |
| Database | 5XXX |

### Next Steps
1. `cd <path>`
2. `npm install` (if needed)
3. `npm run dev`
```

### Step 7: Offer Follow-up Actions

Ask user:
- "Would you like to open VS Code in the new worktree?" → `code <path>`
- "Would you like to run npm install?" → `cd <path> && npm install`
- "Would you like me to switch to the new worktree directory?"

---

## Examples

**Basic usage:**
```
/create-worktree feature-auth
```
Creates worktree at `../project-feature-auth` for existing `feature-auth` branch.

**Create new branch:**
```
/create-worktree feature-new-login -b
```
Creates new branch `feature-new-login` from HEAD and worktree.

**Custom path:**
```
/create-worktree main --path ~/worktrees/project-main
```
Creates worktree at specified path.

**Custom port offset:**
```
/create-worktree feature-api --offset 200
```
Uses port offset 200 instead of auto-calculated.

**Preview mode:**
```
/create-worktree feature-test --dry-run
```
Shows what would be done without making changes.

---

## Related

- **Skill:** `git-worktree-setup` - Detailed guidance on worktree isolation
- **Command:** `/clean-worktree` - Remove worktrees properly
