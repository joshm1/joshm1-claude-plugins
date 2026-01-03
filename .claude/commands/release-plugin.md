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

Automate plugin release workflow: version bump → commit → tag.

## Steps

1. **Read current marketplace.json** to get the current version for `$ARGUMENTS.plugin`
2. **Calculate new version** based on `$ARGUMENTS.bump` (default: patch)
   - patch: 1.2.3 → 1.2.4
   - minor: 1.2.3 → 1.3.0
   - major: 1.2.3 → 2.0.0
3. **Update marketplace.json** with the new version
4. **Git add and commit** with message: `chore(marketplace): Bump {plugin} to v{new_version}`
5. **Create annotated git tag** v{new_version} with release notes
6. **Report** the new version and next steps (e.g., `git push && git push --tags`)

## Execution

```bash
# Read marketplace.json
cat .claude-plugin/marketplace.json

# After determining new version, update and commit:
# 1. Edit marketplace.json
# 2. git add .claude-plugin/marketplace.json
# 3. git commit -m "chore(marketplace): Bump {plugin} to v{new_version}"
# 4. git tag -a v{new_version} -m "{plugin} v{new_version}: {summary}"
```

## Output

After successful release, display:
- Plugin: {plugin}
- Old version: {old_version}
- New version: {new_version}
- Tag created: v{new_version}
- Next steps: `git push && git push --tags`
