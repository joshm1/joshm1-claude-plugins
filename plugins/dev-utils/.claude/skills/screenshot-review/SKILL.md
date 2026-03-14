---
name: screenshot-review
description: Generate an interactive HTML gallery to review component screenshots. Use when the user asks to review screenshots, view component screenshots, build a screenshot gallery, QA visual regression screenshots, or after running screenshot tests (e.g., `mise run test:screenshots`). Also use when the user mentions "__screenshots__" directories, "visual review", "screenshot QA", or wants to see all component variants side by side. Even if the user just says "review the screenshots" or "show me the screenshots", this skill applies.
---

# Screenshot Review Gallery

Build an interactive HTML gallery for reviewing component screenshots (`ComponentName.__screenshots__/{dark,light}/variant.png`).

## Usage

One command — the script scans for screenshots, parses fixture files for display names, auto-detects Cosmos URL from `.ports.json`, and builds the HTML:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_review.py <project-dir> [--serve [PORT]] [--cosmos-url URL]
```

To build and serve immediately:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_review.py /path/to/project --serve 8789
```

The output HTML is written to `<project-dir>/screenshot-review.html`. It uses relative paths to reference the screenshot PNGs, so it must be served from the project directory.

If not using `--serve`, use the `serve-html` skill to serve `screenshot-review.html` from the project directory.

## What the script does

1. Recursively finds `*.__screenshots__/` directories (skips node_modules)
2. Extracts component names, variant slugs (PNG filenames), and available modes (dark/light)
3. Finds matching `.fixture.tsx` files and parses exported object keys for human-readable display names
4. Reads `.ports.json` for Cosmos URL (or uses `--cosmos-url`)
5. Validates the generated data against `assets/screenshot-data.schema.json`
6. Injects CSS (`assets/styles.css`), JS (`assets/app.js`), and data into `assets/template.html`
7. Writes the self-contained HTML output

## Gallery features

- Dark/Light toggle between color mode screenshots
- Component filter pills with counts
- Grid and list (grouped by component) views
- Lightbox with arrow key navigation
- Pass/Issue buttons persisted to localStorage
- Cosmos deep-links to open fixtures directly (when URL available)
- Component filter synced to URL params
