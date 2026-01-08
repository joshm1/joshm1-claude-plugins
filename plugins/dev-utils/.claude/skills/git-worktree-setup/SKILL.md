---
name: git-worktree-setup
description: Set up Git worktrees with environment isolation. Use when creating worktrees, managing port conflicts between worktrees, copying .env files to worktrees, or isolating Claude settings per worktree. Handles PORT_OFFSET calculation, file copying, database isolation, and IDE configs.
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# Git Worktree Setup Skill

Set up and configure Git worktrees with proper environment isolation to avoid port conflicts and ensure correct file copying.

## When to Use This Skill

- Creating a new worktree for parallel development
- Setting up worktree environments with port isolation
- Copying non-git-controlled files (.env, .claude/settings.local.json)
- Troubleshooting port conflicts between worktrees
- Managing Claude Code settings across worktrees
- Understanding worktree isolation strategies

## Quick Start

### Using the Setup Script

```bash
# Navigate to your worktree and run:
uv run /path/to/setup_worktree.py

# Or specify paths explicitly:
uv run setup_worktree.py --worktree ../project-feature --source .

# Preview changes without applying:
uv run setup_worktree.py --dry-run
```

### Manual Workflow

1. Create the worktree: `git worktree add ../project-feature feature-branch`
2. Copy environment files with port adjustments
3. Copy Claude settings with path transformation
4. Verify setup

## Workflow

### Step 1: Create the Worktree

```bash
# From existing branch
git worktree add ../project-feature feature-branch

# Create new branch from current HEAD
git worktree add -b feature-branch ../project-feature HEAD
```

**Naming convention:** `<project>-<branch-or-purpose>`
**Location convention:** Sibling directory to main repo

### Step 2: Calculate Port Offset

Each worktree gets a unique port offset (100-999) based on its name:

```python
# Formula used by the script
offset = 100 + (hash(worktree_name) % 900)
```

**Example port mapping with offset 347:**

| Service | Base Port | With Offset |
|---------|-----------|-------------|
| Vite/Dev Server | 3000 | 3347 |
| API Server | 8000 | 8347 |
| PostgreSQL | 5432 | 5779 |
| Redis | 6379 | 6726 |

### Step 3: Copy and Transform Files

**Files to copy:**

| File | Transformation |
|------|----------------|
| `.env` | Adjust port values |
| `.env.local` | Adjust ports, add WORKTREE_* vars |
| `.env.*.local` | Adjust port values |
| `.claude/settings.local.json` | Transform path-based permissions |
| `.vscode/` | Copy as-is |
| `.idea/` | Copy as-is |
| `.mcp.json` | Transform paths |

**Files NOT to copy:**

| File | Reason |
|------|--------|
| `.claude/*.local.md` | Plugin session state - start fresh |
| `node_modules/` | Regenerate via npm install |
| `.venv/` | Regenerate via uv sync |

### Step 4: Verify Setup

```bash
# Check worktree is registered
git worktree list

# Verify files exist
ls -la .env* .claude/settings.local.json

# Test port availability
lsof -i :3347  # Should be empty

# Start your dev server
npm run dev
```

## Port Isolation Strategy

The skill uses `PORT_OFFSET` environment variables to avoid conflicts:

### How It Works

1. **Auto-detection** - Finds ANY variable containing `PORT` or `port` (e.g., `VITE_PORT`, `CUSTOM_SERVICE_PORT`)
2. **Deterministic offset** - Same worktree name always gets same offset
3. **Wide range** - Offsets 100-999 provide good distribution
4. **Nice labels** - Known services get readable labels, others are derived from variable names

### Generated `.env.local` Additions

```bash
# Worktree configuration (auto-generated)
WORKTREE_NAME=feature-auth
WORKTREE_OFFSET=347

# Ports with offset applied
VITE_PORT=3347
API_PORT=8347
DB_PORT=5779
```

### Framework Integration

**Vite:**
```javascript
// vite.config.js
export default {
  server: {
    port: parseInt(process.env.VITE_PORT || '3000')
  }
}
```

**Next.js:**
```bash
PORT=3347 next dev
```

**Express:**
```javascript
const PORT = parseInt(process.env.PORT || '3000');
```

**Docker Compose:**
```yaml
ports:
  - "${DB_PORT:-5432}:5432"
```

## Database Isolation

For projects with databases, the script generates worktree-specific database names:

### Strategy: Database Name Suffix

```
Base:      postgres://user:pass@localhost:5432/myapp
Worktree:  postgres://user:pass@localhost:5779/myapp_feature_auth
```

### Creating the Database

The script does NOT create databases automatically. Create manually:

```bash
# PostgreSQL
createdb myapp_feature_auth

# Or via psql
psql -c "CREATE DATABASE myapp_feature_auth;"
```

## Claude Settings Isolation

### What's Shared (via Git)

- `.claude/settings.json` - hooks, plugins
- `.claude/agents/`, `commands/`, `skills/`
- `.claude/scripts/`

### What Needs Copying

- `.claude/settings.local.json` - with path transformation

### Path Transformation

The script transforms absolute paths in permissions:

```
Before: Bash(git -C /Users/josh/projects/repo status)
After:  Bash(git -C /Users/josh/projects/repo-feature status)
```

## Automation Script

### Location

```
plugins/dev-utils/.claude/skills/git-worktree-setup/scripts/setup_worktree.py
```

### Usage

```bash
# Basic usage (auto-detect source repo)
uv run setup_worktree.py

# Specify worktree and source
uv run setup_worktree.py --worktree ../project-feature --source .

# Custom port offset
uv run setup_worktree.py --offset 200

# Preview without changes
uv run setup_worktree.py --dry-run

# Force overwrite existing files
uv run setup_worktree.py --force
```

### Options

| Option | Description |
|--------|-------------|
| `--worktree, -w` | Path to worktree (default: current directory) |
| `--source, -s` | Path to source repo (auto-detected) |
| `--offset, -o` | Manual port offset (auto-calculated) |
| `--dry-run` | Preview without making changes |
| `--force, -f` | Overwrite existing files |

## Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :3347

# Kill process if needed
kill -9 <PID>

# Or use different offset
uv run setup_worktree.py --offset 500
```

### Source Repo Not Detected

The script auto-detects the source repo from Git's `.git` file in the worktree. If this fails:

```bash
# Specify source manually
uv run setup_worktree.py --source /path/to/main/repo
```

### Files Not Copied

Check if files exist in source:

```bash
ls -la /path/to/main/repo/.env*
ls -la /path/to/main/repo/.claude/
```

### Claude Permissions Not Working

Verify `.claude/settings.local.json` was copied and paths transformed:

```bash
cat .claude/settings.local.json | grep -i "worktree"
```

### Database Connection Failed

1. Verify database exists: `psql -l | grep myapp_feature`
2. Check port in `.env.local`: `grep DB_PORT .env.local`
3. Create if missing: `createdb myapp_feature_auth`

## Best Practices

1. **Consistent naming** - Use `<project>-<branch>` for worktree directories
2. **Sibling directories** - Keep worktrees as siblings to main repo
3. **Port spacing** - Default offset range (100-999) handles most cases
4. **Always verify ports** - Run `lsof -i :<port>` before starting servers
5. **Document offsets** - The script adds comments to `.env.local`
6. **Clean up** - Remove worktrees when done: `git worktree remove <path>`

## Integration with Other Skills

- **parallel-implement** - Worktrees enable true parallel development across branches
- **sync-permissions** - Permission patterns apply across worktrees
- **commit** - Each worktree commits independently

## References

- [Port Isolation Deep Dive](references/port-isolation.md)

## Changelog

### v1.0.0 (2025-01-07)
- Initial release
- Port offset calculation (hash-based, 100-999 range)
- Environment file copying with port transformation
- Claude settings path transformation
- IDE config copying (.vscode, .idea)
- Database URL transformation
- Dry-run mode
