---
description: Sync project permissions to user settings
allowed-tools: Bash, Read, Edit, AskUserQuestion
arguments:
  - name: search_dir
    description: Directory to search for .claude settings files (defaults to ~/projects)
    required: false
---

Load and execute the `sync-permissions` skill.

**Search directory:** `$ARGUMENTS` (default: ~/projects)

Read the skill file at `.claude/skills/sync-permissions/SKILL.md` and follow its workflow.
