---
name: sync-permissions
description: Sync allowed permissions from project .claude/settings.json files to user settings. Use when user wants to consolidate project-level permissions into their global ~/.claude/settings.json.
---

# Sync Claude Code Permissions

Discover permissions from all `.claude/settings*.json` files across projects and interactively add safe ones to `~/.claude/settings.json`.

## Scripts

This skill includes a Python script for discovering permissions:

- **[scripts/merge_claude_permissions.py](scripts/merge_claude_permissions.py)** - Scans directories for Claude settings files and extracts permissions

### Running the Script

```bash
# Full report with sources
python scripts/merge_claude_permissions.py

# JSON output only (for programmatic use)
python scripts/merge_claude_permissions.py --json-only

# Custom search directory
python scripts/merge_claude_permissions.py --search-dir ~/projects
```

## Workflow

### Step 1: Discover Permissions

Find and run the discovery script:

```bash
# Find the script (bundled with this plugin)
find ~/.claude/plugins/cache ~/projects -name "merge_claude_permissions.py" -path "*sync-permissions*" 2>/dev/null | head -1

# Run with search directory (use provided path or default to ~/projects)
python <script_path> --search-dir <directory> --json-only
```

The script:
- Searches for `.claude/settings*.json` files
- Extracts all `permissions.allow` entries
- Compares against current `~/.claude/settings.json`
- Returns only NEW permissions not already in user settings

### Step 2: Categorize Each Permission

**SAFE - Recommend adding globally:**

| Pattern | Why Safe |
|---------|----------|
| `Bash(*--version:*)` | Read-only version checks |
| `Bash(*--help:*)` | Read-only help output |
| `Bash(tree:*)` | Read-only directory visualization |
| `Bash(lsof:*)` | Read-only process inspection |
| `Bash(which:*)` | Read-only path lookup |
| `Bash(git branch:*)` | Read-only git operation |
| `Bash(git worktree:*)` | Git worktree management |
| `Bash(docker:*)` | Container management |
| `Bash(just:*)` | Task runner |
| `Bash(devcontainer:*)` | Dev container management |
| `Bash(npm install:*)` | Package installation |
| `Bash(uv *:*)` | Python package manager |
| `mcp__fetch__fetch` | URL fetching |
| `Skill(*)` | All skills are safe |

**OPTIONAL - User's choice:**

| Pattern | Notes |
|---------|-------|
| `Bash(supabase *:*)` | Supabase CLI - only if you use Supabase |
| `Bash(gcloud *:*)` | Google Cloud CLI - only if you use GCP |
| `Bash(aws *:*)` | AWS CLI - only if you use AWS |
| `WebSearch` | Web search access |

**SKIP - Keep project-specific:**

| Pattern | Why Skip |
|---------|----------|
| `Bash(./*:*)` | Project-specific scripts |
| `mcp__<project>__*` | Project-specific MCP tools |
| Redundant patterns | e.g., `Bash(just dc-up:*)` when `Bash(just:*)` exists |

### Step 3: Present Numbered Recommendations

Format your recommendations like this:

```
## Recommended (safe for all projects)

  [1] Bash(git --version:*)      Read-only version check
  [2] Bash(tree:*)               Directory visualization
  [3] Bash(docker:*)             Container management
  [4] mcp__fetch__fetch          URL fetching via MCP
  [5] Skill(pyright-strict-types) Python type checking

## Optional (useful but context-dependent)

  [6] Bash(supabase link:*)      Supabase CLI
  [7] WebSearch                  Web search access

## Skipped (project-specific)

  - Bash(./test-template.sh:*)   Project script
  - mcp__josh-mcp__create_item   Project MCP tool
```

### Step 4: Request Approval

Use AskUserQuestion with these options:

**Question:** "Which permissions should I add to ~/.claude/settings.json?"

**Options:**
1. `Add recommended [1-N]` - Add only the safe/recommended items
2. `Add all [1-M]` - Add recommended + optional
3. `Custom` - Let me specify which numbers to exclude
4. `Cancel` - Don't add anything

If user selects "Custom", ask: "Enter numbers to EXCLUDE (comma-separated), or press enter to add all:"

### Step 5: Apply Changes

For each approved permission:

1. Read `~/.claude/settings.json`
2. Parse the JSON
3. Add new items to `permissions.allow` array
4. Sort the array alphabetically
5. Write back using the Edit tool (preserve formatting)

### Step 6: Summary

Report what was done:

```
## Changes Applied

Added 5 permissions to ~/.claude/settings.json:

  + Bash(git --version:*)
  + Bash(tree:*)
  + Bash(docker:*)
  + mcp__fetch__fetch
  + Skill(pyright-strict-types)

Excluded by user:
  - Bash(supabase link:*)

Total permissions: 47 → 52
```

## Begin

Start by finding and running the discovery script to find all permissions across projects.
