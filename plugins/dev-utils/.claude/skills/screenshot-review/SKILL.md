---
name: screenshot-review
description: Generate an interactive HTML gallery to review component screenshots. Use when the user asks to review screenshots, view component screenshots, build a screenshot gallery, QA visual regression screenshots, or after running screenshot tests (e.g., `mise run test:screenshots`). Also use when the user mentions "__screenshots__" directories, "visual review", "screenshot QA", or wants to see all component variants side by side. Even if the user just says "review the screenshots" or "show me the screenshots", this skill applies.
---

# Screenshot Review Gallery

Build an interactive HTML gallery for reviewing component screenshots (`ComponentName.__screenshots__/{dark,light}/variant.png`).

## Usage

One command — the script scans for screenshots, parses fixture files for display names, auto-detects Cosmos URL from `.ports.json`, and builds the gallery:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/screenshot-review/scripts/build_review.py <project-dir> --serve [PORT]
```

Options:

- `--serve [PORT]` — serve immediately (default port: 8789), prints localhost + Tailscale URLs
- `--cosmos-url URL` — override Cosmos base URL (auto-detected from `.ports.json`)
- `--auto-crop` — detect and crop blank space / border artifacts (requires Pillow)
- `--output DIR` — output directory (default: `<project>/.screenshot-review/`)

Output goes to `<project>/.screenshot-review/` with separate HTML, CSS, JS, and data files. The server maps `/` to the gallery while resolving screenshot image paths from the project root.

## What the script does

1. Recursively finds `*.__screenshots__/` directories (skips node_modules)
2. Extracts component names, variant slugs (PNG filenames), and available modes (dark/light)
3. Finds matching `.fixture.tsx` files and parses exported object keys for human-readable display names
4. Reads `.ports.json` for Cosmos URL (or uses `--cosmos-url`)
5. Validates the generated data against the JSON schema
6. Copies static assets (HTML, CSS, JS) and writes `screenshot-data.js` to output directory

## Gallery features

- Dark/Light theme toggle for both screenshots and page chrome
- Component filter tabs with counts, issues-only filter
- Grid and list (grouped by component) views
- Lightbox with arrow key navigation
- Issue tracking with inline comments, Cmd+click batch selection
- AI fix prompt generator (copies component, variant, fixture path, screenshots, and comments)
- Cosmos deep-links to open fixtures directly (when URL available)
- Mobile-responsive layout with horizontal-scroll tabs
- Repo + worktree pills with clipboard copy for project path
