---
description: Create a GitHub release with intelligent semantic version inference from commits
allowed-tools: Bash, Read, Glob, Grep, mcp__github__create_branch, mcp__github__list_tags, mcp__github__get_tag
arguments:
  - name: version
    description: "Override version bump: patch, minor, major, or explicit version (e.g., 1.2.3). If omitted, infers from commits."
    required: false
  - name: options
    description: "--dry-run (show what would happen), --base BRANCH (compare against, default: main), --prefix PREFIX (tag prefix, e.g., 'v'), --ref COMMIT (release from specific commit/SHA instead of HEAD)"
    required: false
---

# GitHub Release Command

Create a GitHub release with semantic versioning inferred from conventional commits.

## Arguments

`$ARGUMENTS`

## Core Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: ANALYZE COMMITS                                        │
│  • Get commits since base branch (default: main)                │
│  • Parse conventional commit prefixes                           │
│  • Determine version bump type                                  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: DETERMINE VERSION                                      │
│  • Find current version from tags/package.json/pyproject.toml  │
│  • Calculate new version based on bump type                    │
│  • Allow override via explicit version argument                │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: CREATE RELEASE                                         │
│  • Create annotated git tag                                     │
│  • Generate release notes from commits                          │
│  • Create GitHub release via `gh release create`                │
└─────────────────────────────────────────────────────────────────┘
```

## Step 1: Analyze Commits

Parse options:

```bash
# Get the base branch
BASE_BRANCH="${base_option:-main}"

# Get the target ref (default: HEAD)
TARGET_REF="${ref_option:-HEAD}"

# If using a specific ref, resolve it to a full SHA
if [ "$TARGET_REF" != "HEAD" ]; then
  TARGET_SHA=$(git rev-parse "$TARGET_REF")
  echo "Releasing from: $TARGET_REF ($TARGET_SHA)"
fi

# Get commits between base and target ref
git log ${BASE_BRANCH}..${TARGET_REF} --oneline
```

**When using `--ref`:**
- Commits analyzed are those between `--base` and `--ref`
- The tag will be created pointing to that specific commit
- Useful for retroactively tagging releases you forgot to tag

### Conventional Commit Inference

Scan commit messages for conventional commit prefixes:

| Prefix Pattern | Version Bump |
|----------------|--------------|
| `BREAKING CHANGE:` in body | **major** |
| `feat!:` or `fix!:` (with `!`) | **major** |
| `feat:` or `feat(scope):` | **minor** |
| `fix:`, `perf:`, `refactor:` | **patch** |
| `docs:`, `style:`, `test:`, `chore:`, `ci:`, `build:` | **patch** |

**Priority:** major > minor > patch (use highest found)

```bash
# Check for breaking changes
git log ${BASE_BRANCH}..HEAD --grep="BREAKING CHANGE" --oneline
git log ${BASE_BRANCH}..HEAD --grep="^feat!:" --oneline
git log ${BASE_BRANCH}..HEAD --grep="^fix!:" --oneline

# Check for features (minor)
git log ${BASE_BRANCH}..HEAD --grep="^feat" --oneline

# All other conventional commits are patch
```

**Show analysis to user:**
```
## Commit Analysis

Commits since ${BASE_BRANCH}: 5
- 2 feat: commits (minor bump)
- 3 fix: commits (patch bump)
- 0 breaking changes

Inferred bump: **minor**
```

## Step 2: Determine Version

### Find Current Version

Try these sources in order:

1. **Git tags** (most reliable for releases):
   ```bash
   # Get latest semver tag
   git tag --sort=-v:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+' | head -1
   ```

2. **package.json** (Node.js projects):
   ```bash
   cat package.json | grep '"version"'
   ```

3. **pyproject.toml** (Python projects):
   ```bash
   grep '^version' pyproject.toml
   ```

4. **VERSION file**:
   ```bash
   cat VERSION
   ```

5. **Default:** If no version found, start at `0.1.0`

### Calculate New Version

If user provided explicit version, use it. Otherwise:

| Current Version | Bump Type | New Version |
|-----------------|-----------|-------------|
| 1.2.3 | patch | 1.2.4 |
| 1.2.3 | minor | 1.3.0 |
| 1.2.3 | major | 2.0.0 |

### Handle Tag Prefix

Parse `--prefix` option (default: `v` if existing tags use it, empty otherwise):

```bash
# Detect existing prefix style
EXISTING_PREFIX=$(git tag --sort=-v:refname | head -1 | grep -oE '^v?' || echo "")
PREFIX="${prefix_option:-${EXISTING_PREFIX}}"
```

## Step 3: Create Release

### Generate Release Notes

Extract from commits:

```bash
# Generate release notes from conventional commits
git log ${BASE_BRANCH}..HEAD --pretty=format:"- %s" | head -20
```

Group by type for clean release notes:

```markdown
## What's Changed

### Features
- feat: Add user authentication (#123)
- feat(api): New endpoint for metrics

### Bug Fixes
- fix: Resolve memory leak in cache
- fix(ui): Button alignment issue

### Other Changes
- docs: Update README
- refactor: Simplify database queries
```

### Dry Run Mode

If `--dry-run` is specified, show what would happen without executing:

```
## Dry Run - GitHub Release

Current version: 1.2.3
New version: 1.3.0
Tag: v1.3.0
Bump type: minor (inferred from 2 feat: commits)

Would create release with:
- Tag: v1.3.0
- Title: v1.3.0
- Release notes: [generated notes]

Run without --dry-run to execute.
```

### Create Tag and Release

```bash
# Create annotated tag (at specific ref if provided, otherwise HEAD)
if [ -n "$TARGET_SHA" ]; then
  # Tag a specific commit
  git tag -a "${PREFIX}${NEW_VERSION}" "${TARGET_SHA}" -m "Release ${PREFIX}${NEW_VERSION}

${RELEASE_NOTES}"
else
  # Tag HEAD
  git tag -a "${PREFIX}${NEW_VERSION}" -m "Release ${PREFIX}${NEW_VERSION}

${RELEASE_NOTES}"
fi

# Push tag
git push origin "${PREFIX}${NEW_VERSION}"

# Create GitHub release using gh CLI
# --target specifies which commit the release points to
# IS_LATEST is set based on version comparison (see below)
gh release create "${PREFIX}${NEW_VERSION}" \
  --title "${PREFIX}${NEW_VERSION}" \
  --notes "${RELEASE_NOTES}" \
  ${TARGET_SHA:+--target "$TARGET_SHA"} \
  $IS_LATEST
```

**Smart `--latest` handling:** When releasing, check if there are already tags with higher version numbers. If so, omit `--latest` automatically since this is a backfill release.

```bash
# Check if any existing tags have a higher version
LATEST_TAG=$(git tag --sort=-v:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+' | head -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

# Compare versions: if NEW_VERSION < LATEST_VERSION, this is a backfill
if version_less_than "$NEW_VERSION" "$LATEST_VERSION"; then
  IS_LATEST=""  # Don't mark as latest
  echo "Note: Backfill release detected (v$NEW_VERSION < v$LATEST_VERSION). Not marking as latest."
else
  IS_LATEST="--latest"
fi
```

## Output

After successful release:

```
## Release Created

Version: 1.2.3 → 1.3.0
Tag: v1.3.0
Bump: minor (inferred from commits)
Ref: HEAD (or specific SHA if --ref was used)
URL: https://github.com/owner/repo/releases/tag/v1.3.0

### Commits Included
- feat: Add new feature X
- fix: Resolve issue Y
- docs: Update documentation

Next steps:
- Verify release at the URL above
- Announce the release if needed
```

When using `--ref`, also show:
```
Note: This release was created from commit abc123f, not the current HEAD.
```

## Error Handling

| Scenario | Action |
|----------|--------|
| No commits since base | Warn user, ask if they want to proceed anyway |
| Can't determine current version | Ask user to provide explicit version |
| Tag already exists | Error with suggestion to use different version |
| gh CLI not available | Fall back to just creating git tag, provide manual release URL |
| Not on a feature branch | Warn but allow (user may be releasing from main) |

## Examples

```bash
# Infer version from commits
/github-release

# Force a minor bump
/github-release minor

# Explicit version
/github-release 2.0.0

# Dry run to see what would happen
/github-release --dry-run

# Use different base branch
/github-release --base develop

# Custom tag prefix
/github-release --prefix release-

# Release from a specific commit (retroactive tagging)
/github-release 1.0.0 --ref abc123f

# Release from a branch tip
/github-release --ref feature-branch

# Backfill a forgotten release from 3 commits ago
/github-release 0.9.0 --ref HEAD~3
```

## Begin

Parse the arguments and start with Step 1: Analyze Commits.
