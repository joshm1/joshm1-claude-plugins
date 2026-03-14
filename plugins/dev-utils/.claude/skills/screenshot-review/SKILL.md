---
name: screenshot-review
description: Generate an interactive HTML gallery to review component screenshots. Use when the user asks to review screenshots, view component screenshots, build a screenshot gallery, QA visual regression screenshots, or after running screenshot tests (e.g., `mise run test:screenshots`). Also use when the user mentions "__screenshots__" directories, "visual review", "screenshot QA", or wants to see all component variants side by side. Even if the user just says "review the screenshots" or "show me the screenshots", this skill applies.
---

# Screenshot Review Gallery

Generate an interactive HTML gallery for reviewing component screenshots captured by Vitest browser mode (or any tool that produces `ComponentName.__screenshots__/{dark,light}/variant-slug.png`).

## Architecture

Three-piece pipeline — the subagent generates data, a script validates and builds, the HTML renders it:

```
Subagent scans codebase → screenshot-data.json → build_review.py → screenshot-review.html
                                                       ↑
                                            validates against schema
                                            injects into HTML template
```

## Step 1: Generate screenshot-data.json

Scan the codebase for `__screenshots__/` directories and fixture files. Generate a JSON file conforming to the schema at `assets/screenshot-data.schema.json`.

Read the schema file first to understand the exact structure. Key fields:

```json
{
  "title": "Component Screenshot Review",
  "cosmosBaseUrl": "http://localhost:5000",
  "screenshotBaseDir": ".",
  "screenshots": [
    {
      "component": "ChoreCard",
      "variant": "daily-chore",
      "displayName": "Daily chore",
      "fixturePath": "src/components/ChoreCard.fixture.tsx",
      "modes": ["dark", "light"]
    }
  ]
}
```

**How to populate each field:**

- **component**: Directory name prefix before `.__screenshots__/` (e.g., `ChoreCard` from `ChoreCard.__screenshots__/`)
- **variant**: PNG filename without extension (e.g., `daily-chore` from `dark/daily-chore.png`)
- **displayName**: Read from the matching `.fixture.tsx` file — the object key for this variant (e.g., `'Daily chore'`). This is needed for Cosmos deep-links.
- **fixturePath**: Relative path from project root to the `.fixture.tsx` file
- **modes**: Which subdirectories exist (`dark`, `light`, or both)
- **cosmosBaseUrl**: Read from `.ports.json` if available (`cosmos` key), or ask the user. Set to `null` if Cosmos isn't set up.
- **screenshotBaseDir**: Relative path from where the output HTML will be placed to the directory containing `ComponentName.__screenshots__/` dirs. Usually `.` if HTML is co-located.

**Finding fixture display names:**

```bash
# Find fixture files near screenshot dirs
fd '\.fixture\.tsx$' src/components/

# Extract variant names (the object keys in the default export)
grep -E "^\s+'[^']+'" src/components/ChoreCard.fixture.tsx
```

The fixture file exports an object like:
```tsx
export default {
  'Daily chore': <ChoreCard ... />,
  'Completed chore': <ChoreCard ... />,
}
```

The keys become `displayName`, their slugified forms become `variant`.

## Step 2: Validate and Build

Write the JSON to a file, then run the build script:

```bash
python3 ~/.claude/skills/screenshot-review/scripts/build_review.py screenshot-data.json --output screenshot-review.html
```

This validates against the schema (via `uvx check-jsonschema`), injects the data into the HTML template, and writes the output.

To also serve it immediately:

```bash
python3 ~/.claude/skills/screenshot-review/scripts/build_review.py screenshot-data.json --serve 8789
```

## Step 3: Serve

If not using `--serve`, use the `/serve-html` skill to serve the output HTML. The HTML must be served from a directory where the relative `screenshotBaseDir` path resolves to the actual screenshot files — image tags use relative paths.

## Cosmos Deep-Linking

The gallery generates Cosmos URLs in this format (when `cosmosBaseUrl` is set):

```
http://localhost:18830/?fixture={"path":"src/components/ChoreCard.fixture.tsx","name":"Daily chore"}
```

This requires `fixturePath` and `displayName` in the data. If either is missing for a screenshot, the Cosmos link is hidden for that entry.

## Gallery Features

- **Dark/Light toggle**: Switch between color mode screenshots
- **Component filter pills**: Filter by component
- **Grid / List view**: Grid shows all screenshots; List groups by component
- **Lightbox**: Click any screenshot for full-size view with arrow key navigation
- **Pass/Issue buttons**: Mark screenshots as passing or having issues (persisted to localStorage)
- **Cosmos links**: Open the fixture variant directly in React Cosmos (new tab)
- **URL state**: Component filter synced to URL params for sharing

## File Locations

| File | Purpose |
|------|---------|
| `assets/screenshot-data.schema.json` | JSON Schema for the data file |
| `assets/template.html` | Vue 3 HTML template with `__SCREENSHOT_DATA__` placeholder |
| `scripts/build_review.py` | Validates JSON + injects into template + optional serve |
