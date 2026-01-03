---
name: release-plugin
description: Release a plugin with version bump, commit, and git tag
arguments:
  - name: plugin
    description: Plugin name (e.g., browser-testing, python-dev)
    required: true
  - name: bump
    description: Version bump type (patch, minor, major)
    required: false
    default: patch
---

# Release Plugin Command

Automate plugin release workflow: stage plugin changes → version bump → commit → tag.

## Steps

1. **Check for plugin changes** in `plugins/$ARGUMENTS.plugin/` directory
   - Run `git status plugins/$ARGUMENTS.plugin/` to see staged/unstaged/untracked files
   - If no changes exist, warn the user and ask if they want to proceed with just a version bump
2. **Stage all plugin changes** with `git add plugins/$ARGUMENTS.plugin/`
3. **Read current marketplace.json** to get the current version for `$ARGUMENTS.plugin`
4. **Calculate new version** based on `$ARGUMENTS.bump` (default: patch)
   - patch: 1.2.3 → 1.2.4
   - minor: 1.2.3 → 1.3.0
   - major: 1.2.3 → 2.0.0
5. **Update marketplace.json** with the new version
6. **Stage marketplace.json** with `git add .claude-plugin/marketplace.json`
7. **Show staged changes** with `git diff --cached --stat` for user review
8. **Commit all changes** with message: `feat($ARGUMENTS.plugin): Release v{new_version}`
   - Include a brief summary of what changed in the commit body
9. **Create annotated git tag** `{plugin}-v{new_version}` with release notes
10. **Report** the new version and next steps

## Critical Rules

- **ALWAYS check `git status plugins/$ARGUMENTS.plugin/`** FIRST before doing anything else
- **ALWAYS stage plugin directory changes** before updating marketplace.json
- **NEVER commit just marketplace.json** if there are unstaged plugin changes
- Use `git add plugins/$ARGUMENTS.plugin/` to add all changes including untracked files

## Execution Order

```bash
# 1. FIRST: Check what changes exist in the plugin directory
git status plugins/{plugin}/

# 2. Stage ALL plugin changes (including untracked files)
git add plugins/{plugin}/

# 3. Read marketplace.json for current version
cat .claude-plugin/marketplace.json

# 4. Update marketplace.json with new version (use Edit tool)

# 5. Stage marketplace.json
git add .claude-plugin/marketplace.json

# 6. Show what will be committed
git diff --cached --stat

# 7. Commit everything together
git commit -m "feat({plugin}): Release v{new_version}

{brief summary of changes}"

# 8. Create tag
git tag -a {plugin}-v{new_version} -m "{plugin} v{new_version}: {summary}"
```

## Output

After successful release, display:
- Plugin: {plugin}
- Old version: {old_version}
- New version: {new_version}
- Files changed: {list from git diff --cached --stat}
- Tag created: {plugin}-v{new_version}
- Next steps: `git push && git push --tags`
