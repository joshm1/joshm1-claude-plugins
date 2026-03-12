---
name: e2e-documentation-qa
description: Walk through a web application with agent-browser, capture screenshots, inspect for issues, and produce stakeholder-ready markdown documentation of the user journey. Use this skill whenever the user asks to document a user flow, QA a website, create visual walkthroughs, click through an app to verify it works, find UI bugs, or generate E2E documentation with screenshots. Even if the user just says "test this page" or "check this URL for issues", this skill applies.
---

# E2E Documentation & QA

Walk through a web application using `agent-browser`, capture screenshots at meaningful states, inspect for visual and functional issues, and produce a polished markdown document with embedded screenshots.

## Before You Start

Extract from the user's request:
- **URL** - where to start
- **Flow name** - for file naming (e.g., "login-flow", "checkout-process"). Infer from context if not stated.
- **Steps** - specific actions to follow, or explore the natural user path

Output goes to:
- `docs/user-flows/<flow-name>.md`
- `docs/user-flows/screenshots/<flow-name>/`

## Core Loop

For each meaningful step in the journey:

```
1. SNAPSHOT  →  agent-browser snapshot -i
2. SCREENSHOT  →  agent-browser screenshot <path>
3. INSPECT  →  Examine the screenshot (see visual-inspection-guide.md)
4. DOCUMENT  →  Add step to the markdown file
5. ACT  →  Perform the next user action
6. WAIT  →  agent-browser wait --load networkidle
7. RE-SNAPSHOT  →  agent-browser snapshot -i (refs are invalidated after navigation)
```

### What counts as a "meaningful step"

Screenshot at state changes that matter: landing on a new page, a form filled out, a submission result, an error state, a modal opening. You don't need a screenshot for every individual field fill or button hover. Think about what a stakeholder reading the document would want to see.

### Navigate and wait

```bash
agent-browser open <url> && agent-browser wait --load networkidle
```

### Snapshot and interact

```bash
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Sign in"
agent-browser fill @e1 "user@test.com"
agent-browser fill @e2 "password"
agent-browser click @e3
agent-browser wait --load networkidle
```

Refs (`@e1`, `@e2`) are invalidated whenever the page navigates or the DOM changes significantly. Always re-snapshot after clicking something that loads a new page.

### Screenshot

```bash
agent-browser screenshot docs/user-flows/screenshots/<flow-name>/01-description.png
```

Use sequential numbering with descriptive suffixes: `01-homepage.png`, `02-login-form-filled.png`, `03-dashboard-after-login.png`.

### Verify changes

After performing an action, `diff snapshot` shows what changed on the page without needing to re-read the full snapshot:

```bash
agent-browser diff snapshot
```

### Responsive testing

If relevant to the user's request:

```bash
agent-browser set viewport 375 812
agent-browser screenshot docs/user-flows/screenshots/<flow-name>/05-mobile-view.png
```

## Visual Inspection

After each screenshot, examine it for issues. See [references/visual-inspection-guide.md](references/visual-inspection-guide.md) for the full checklist. The short version:

- **Layout** - alignment, spacing, overflow, overlap
- **Styling** - colors, fonts, images, borders
- **Text** - truncation, "undefined"/"null" showing, missing labels
- **Error states** - unexpected error messages, stack traces, error toasts

## Handling Issues

When you find a problem, decide based on confidence:

### Obvious fix (high confidence)
Fix it directly. Examples: CSS typo, wrong color value, missing alt text, obvious off-by-one in padding. After fixing, refresh and re-screenshot to confirm.

```bash
# Fix the code, then verify
agent-browser open <same-url> && agent-browser wait --load networkidle
agent-browser screenshot docs/user-flows/screenshots/<flow-name>/issue-01-after.png
```

### Uncertain fix
Document the issue with a screenshot and ask the user before proceeding. Describe what you see, what you think the problem might be, and suggest options.

### Complex/risky fix
Document it in the report's "Issues Found" section with:
- Screenshot showing the problem
- Steps to reproduce
- What you think is wrong
- Suggested fix approach

Let the user decide whether to fix now or later.

## Writing the Documentation

Follow the template in [references/documentation-template.md](references/documentation-template.md).

Key principles:
- Every step gets an embedded screenshot
- Write in present tense: "The user sees...", "Click the **Submit** button..."
- Highlight interactive elements in **bold**
- Keep descriptions concise — a sentence or two per step, not paragraphs
- Use `---` between steps for visual separation

Build the document incrementally as you go through the flow. Write each step's section right after capturing it, rather than saving everything for the end.

## Finishing Up

1. Write the final documentation file
2. Close the browser:
   ```bash
   agent-browser close
   ```
3. Validate the documentation (checks for broken image links, missing sections):
   ```bash
   uv run scripts/validate_documentation.py <flow-name>
   ```
4. Report to the user:
   - How many steps documented
   - Issues found (and whether they were fixed or need attention)
   - Path to the documentation file
