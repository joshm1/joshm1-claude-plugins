---
name: e2e-documentation-qa
description: E2E documentation and QA skill using Playwright MCP. Use when asked to document user journeys, create E2E documentation with screenshots, QA a website, find UI bugs, check for console/network errors, or generate visual walkthroughs. Produces professional step-by-step markdown documentation of the real user flow with embedded screenshots.
---

# E2E Documentation & QA Skill

This skill performs comprehensive end-to-end documentation and quality assurance for web applications using Playwright MCP browser automation.

## How to Use

**Spawn the `e2e-documenter` agent** to perform E2E documentation:

```
Task(subagent_type="e2e-documenter", prompt="Document the [flow-name] flow starting at [URL]")
```

**Examples:**
```
Task(subagent_type="e2e-documenter", prompt="Document the login-flow starting at http://localhost:3000")

Task(subagent_type="e2e-documenter", prompt="Document the checkout-process flow starting at http://localhost:3000/cart. Follow these steps: 1) View cart 2) Click checkout 3) Fill shipping info 4) Complete payment")

Task(subagent_type="e2e-documenter", prompt="QA the user-settings flow at http://localhost:3000/settings - look for visual issues and console errors")
```

**Output location:** `docs/user-flows/[flow-name].md` with screenshots in `docs/user-flows/screenshots/[flow-name]/`

The agent handles all the heavy lifting (screenshots, inspection, issue detection) and returns a concise summary when done.

---

## Primary Output: Professional User Flow Documentation

**Your main deliverable is a polished, step-by-step markdown document** that captures the real and correct user flow with embedded screenshots. This documentation should be:

- **Professional quality** - Ready to share with stakeholders, put in a wiki, or use as onboarding material
- **Accurate** - Documents what actually happens, not what should happen
- **Visual** - Every significant step has an embedded screenshot
- **Complete** - Covers the full journey from start to finish
- **Actionable** - Clear descriptions of what the user does at each step

The documentation serves as both a **verification that the flow works correctly** and a **reference for how the feature is intended to be used**.

## When to Use This Skill

Activate this skill when the user asks to:
- **Document user journeys** - "Document the login flow", "Create a walkthrough of the checkout process"
- **QA a website** - "Test this website", "Check for issues on our app"
- **Visual documentation** - "Take screenshots of the user flow", "Create visual docs"
- **Find bugs** - "Look for UI issues", "Check for console errors"
- **E2E testing** - "Click through the app and verify it works"

## Core Workflow

### Phase 1: Setup & Initial Assessment

1. **Navigate to the starting URL**
   ```
   mcp__playwright__browser_navigate: <url>
   ```

2. **Take initial snapshot and screenshot**
   ```
   mcp__playwright__browser_snapshot
   mcp__playwright__browser_take_screenshot:
     filename: "01-initial-page.png"
   ```

3. **Check for immediate issues**
   ```
   mcp__playwright__browser_console_messages:
     level: "error"
   mcp__playwright__browser_network_requests
   ```

### Phase 2: Interactive Journey Documentation

For each step in the user journey:

1. **Document current state**
   - Take accessibility snapshot to understand page structure
   - **ALWAYS take a screenshot** - every step gets documented visually
   - Note key elements visible and their refs

2. **Visually inspect the screenshot for issues**
   - Look at alignment and positioning - are elements properly aligned?
   - Check spacing and margins - is anything too cramped or too spread out?
   - Examine colors and contrast - do colors look correct? Is text readable?
   - Look for overlap - are elements overlapping unexpectedly?
   - Check for clipping or overflow - is content cut off?
   - Verify visual hierarchy - does the layout make sense?
   - Look for broken/missing images or icons
   - Check text for issues - truncation, orphaned words, weird wrapping

3. **Perform user action**
   - Click buttons, links, or interactive elements
   - Fill forms when needed
   - Navigate through flows

4. **Capture results**
   - **Screenshot after EVERY significant action** (regardless of errors)
   - Record any state changes
   - Note loading states and transitions

5. **Monitor for issues (both visual AND technical)**
   - Check console for errors after each action
   - Watch network requests for failures (4xx, 5xx)
   - **Critically examine the screenshot** for visual problems
   - Note ANY visual oddity, even minor ones

### Phase 3: Issue Detection & Delegation

When issues are found:

1. **Document the issue**
   - Screenshot showing the problem
   - Console/network error details
   - Steps to reproduce

2. **Classify the issue**
   - **Console Error** - JavaScript runtime error
   - **Network Error** - Failed API calls, 404s, timeouts
   - **Visual/CSS Issue** - Alignment, positioning, colors, overlap, spacing, styling problems
   - **UI Issue** - Broken elements, missing images, unexpected error messages on page
   - **UX Issue** - Confusing flows, missing feedback, poor states

3. **Delegate to appropriate subagent**
   ```
   Use Task tool to spawn fix agent:
   - For frontend bugs: "Fix the [issue] in [component/file]"
   - For API errors: "Investigate and fix the API error at [endpoint]"
   - For styling issues: "Fix the CSS issue causing [problem]"
   ```

4. **Wait for fix and re-evaluate**
   - After subagent reports completion
   - Refresh or re-navigate to the affected area
   - Verify the fix worked
   - Continue if fixed, escalate if not

## Screenshot Naming Convention

Use descriptive, sequential names:
```
01-homepage-initial.png
02-homepage-click-login.png
03-login-form-empty.png
04-login-form-filled.png
05-login-submit-loading.png
06-dashboard-after-login.png
```

## Documentation Output Format

**Create a professional, stakeholder-ready markdown document** with embedded screenshots. Save this to a file like `docs/user-flows/[flow-name].md`.

```markdown
# [Flow Name] - User Journey Documentation

> Step-by-step guide showing the complete [flow name] process with screenshots.

## Overview

| Property | Value |
|----------|-------|
| **Application** | [app name] |
| **URL** | [starting url] |
| **Last Verified** | [date] |
| **Status** | Working / Has Issues |

## User Flow

### Step 1: [Starting Point]

Navigate to the starting page.

![Step 1 - Starting page](./screenshots/01-starting-page.png)

The user sees [describe key elements visible]. From here, they can [describe available actions].

---

### Step 2: [Action Description]

Click the **[Button/Link Name]** to proceed.

![Step 2 - After clicking](./screenshots/02-after-click.png)

The page now shows [describe what changed]. Notice that [highlight important elements].

---

### Step 3: [Form/Input Step]

Fill in the required information:
- **Field 1**: [what to enter]
- **Field 2**: [what to enter]

![Step 3 - Form filled](./screenshots/03-form-filled.png)

---

### Step 4: [Completion]

Click **Submit** to complete the process.

![Step 4 - Success state](./screenshots/04-success.png)

The user sees a confirmation message indicating [describe success state].

---

## Issues Found During Testing

### Issue 1: [Title]

| Property | Value |
|----------|-------|
| **Type** | Console Error / Network Error / UI Issue |
| **Severity** | Critical / High / Medium / Low |
| **Status** | Fixed / Pending / Delegated |

**Description**: [detailed description]

![Issue screenshot](./screenshots/issue-01.png)

**Resolution**: [how it was fixed or what action was taken]

---

## Improvement Suggestions

1. **[Suggestion Title]** - [rationale and expected benefit]
2. **[Suggestion Title]** - [rationale and expected benefit]

## Summary

| Metric | Value |
|--------|-------|
| Steps Documented | [count] |
| Issues Found | [count] |
| Issues Resolved | [count] |
| Overall Status | [Pass/Fail with notes] |

---

*Documentation generated via E2E walkthrough on [date]*
```

**Key principles for the documentation:**
- Every step MUST have an embedded screenshot
- Use horizontal rules (`---`) between steps for visual separation
- Write in present tense, describing what the user sees and does
- Highlight interactive elements in **bold**
- Keep descriptions concise but complete

## Playwright MCP Tools Reference

### Navigation & State
- `mcp__playwright__browser_navigate` - Go to URL
- `mcp__playwright__browser_navigate_back` - Go back
- `mcp__playwright__browser_snapshot` - Get accessibility tree (CRITICAL for finding element refs)
- `mcp__playwright__browser_take_screenshot` - Capture visual screenshot

### Interaction (requires ref from snapshot)
- `mcp__playwright__browser_click` - Click element
- `mcp__playwright__browser_type` - Type into input
- `mcp__playwright__browser_fill_form` - Fill multiple fields
- `mcp__playwright__browser_hover` - Hover over element
- `mcp__playwright__browser_select_option` - Select dropdown
- `mcp__playwright__browser_press_key` - Press keyboard key

### Monitoring
- `mcp__playwright__browser_console_messages` - Get console logs/errors
- `mcp__playwright__browser_network_requests` - Get network activity

### Utilities
- `mcp__playwright__browser_wait_for` - Wait for text/element/time
- `mcp__playwright__browser_resize` - Test responsive layouts
- `mcp__playwright__browser_tabs` - Manage tabs
- `mcp__playwright__browser_close` - Close browser

## Issue Detection Checklist

### Console Errors to Watch
- JavaScript runtime errors
- Unhandled promise rejections
- React/Vue/framework errors
- Missing resources (404 for scripts/styles)
- CORS errors

### Network Issues to Catch
- Failed API calls (4xx, 5xx status)
- Slow requests (> 3 seconds)
- Missing authentication errors (401, 403)
- Timeouts
- CORS failures

### UI/Visual Issues to Identify

**Always visually inspect screenshots for these issues:**

**Layout & Positioning**
- Elements misaligned (not centered, uneven spacing)
- Content overflow or clipping
- Elements overlapping unexpectedly
- Incorrect z-index (wrong element on top)
- Responsive breakpoint issues
- Uneven gutters or margins

**Styling & Appearance**
- Incorrect colors (wrong brand colors, poor contrast)
- Missing or broken images/icons
- Wrong fonts or font sizes
- Inconsistent styling between similar elements
- Flash of unstyled content (FOUC)
- Borders, shadows, or rounded corners missing/wrong

**Text & Content**
- Text truncation cutting off important info
- Orphaned words or bad text wrapping
- "undefined", "null", or placeholder text showing
- Missing labels or descriptions
- Unreadable text (too small, poor contrast)

**Interactive Elements**
- Buttons that look unclickable
- Missing hover/focus states
- Disabled states that look enabled (or vice versa)
- Missing loading indicators

**Error States**
- **Unexpected error messages displayed on the page**
- API errors shown to user
- Stack traces visible
- Error toasts that shouldn't appear
- Generic "Something went wrong" without context

### UX Issues to Note
- Confusing navigation
- Missing feedback after actions
- Unclear error messages
- Dead-end states
- Missing confirmation dialogs
- Inconsistent behavior

## Delegation Patterns

### For Frontend Code Issues
```
Use Task tool with prompt:
"There's a [type] issue in the application:
- URL: [url]
- Problem: [description]
- Console error: [if applicable]
- Screenshot shows: [what's visible]

Please investigate and fix the root cause in the codebase."
```

### For API/Backend Issues
```
Use Task tool with prompt:
"API error detected:
- Endpoint: [url/path]
- Status: [code]
- Response: [error message]
- Triggered by: [user action]

Please investigate the backend and fix this endpoint."
```

### For Visual/CSS Issues
```
Use Task tool with prompt:
"Visual/CSS issue found:
- Page: [url]
- Element: [description of affected element]
- Problem: [specific issue - alignment, color, overlap, spacing, etc.]
- Screenshot shows: [describe what's visible in the screenshot]
- Expected: [how it should look]

Please find the component/styles responsible and fix this visual issue."
```

**Examples of visual issues to delegate:**
- "The submit button is not vertically centered with the input field"
- "There's 30px gap on the left but only 15px on the right"
- "The card shadow is missing compared to other cards"
- "Text is getting clipped on the right side of the container"
- "The header overlaps the main content when scrolling"

## Re-evaluation After Fixes

After a fix is applied:

1. **Hard refresh the page**
   ```
   mcp__playwright__browser_navigate: [same url]
   ```

2. **Reproduce the original action**
   - Follow the same steps that triggered the issue

3. **Verify the fix**
   - Check console is clean
   - Check network requests succeed
   - Take comparison screenshot
   - Confirm visual appearance is correct

4. **Document the resolution**
   - Update issue status in report
   - Add "after" screenshot if relevant
   - Note any remaining concerns

## Best Practices

1. **Always snapshot before clicking** - Get fresh refs for interaction
2. **Screenshot EVERY step** - Not just when errors occur; every action gets a screenshot
3. **Visually examine each screenshot** - Look for alignment, colors, overlap, spacing issues
4. **Check console after every action** - Catch technical issues immediately
5. **Use descriptive filenames** - Makes documentation clear
6. **Test responsive** - Use `browser_resize` for mobile/tablet
7. **Test error states** - Try invalid inputs, empty states
8. **Document both happy and sad paths** - Real users make mistakes
9. **Be systematic** - Follow consistent patterns for reproducibility
10. **Report even minor visual issues** - Small alignment problems matter for polish

## Example Session

```
User: "Document and QA the login flow on localhost:3000"

1. Navigate to localhost:3000
2. Screenshot: 01-homepage.png
3. Snapshot page, find login button (ref: e15)
4. Click login button
5. Screenshot: 02-login-page.png
6. Check console - no errors
7. Snapshot form, find email/password fields
8. Fill form with test credentials
9. Screenshot: 03-form-filled.png
10. Submit form
11. Screenshot: 04-submitting.png
12. Wait for navigation
13. Check console - ERROR: "TypeError: Cannot read property 'user' of undefined"
14. Screenshot: 05-error-state.png
15. Delegate to subagent: "Fix undefined user error in login handler"
16. Wait for fix confirmation
17. Re-navigate to login page
18. Repeat login flow
19. Screenshot: 06-login-success.png
20. Verify dashboard loads correctly
21. Generate final documentation report
```

## Output Artifacts

This skill produces:
- **Screenshots folder** - All captured images
- **Journey document** - Markdown walkthrough with embedded images
- **Issues list** - All problems found with status
- **Suggestions list** - UX/UI improvement recommendations

---

## Scripts (Agentic Capabilities)

This skill includes automation scripts for self-verification and catalog management.

### validate_documentation.py

Verifies that generated documentation meets quality standards.

```bash
# Validate a specific flow
python scripts/validate_documentation.py login-flow

# Validate all documented flows
python scripts/validate_documentation.py --all

# JSON output for automation
python scripts/validate_documentation.py --all --json
```

**What it checks:**
- Markdown file exists and is non-empty
- All referenced screenshots exist
- Required sections present (Overview, User Flow, Summary)
- No broken image links

**Exit codes:**
- `0` - All validations passed
- `1` - General error
- `10` - Validation failed (issues found)

### generate_index.py

Creates a catalog of all documented flows.

```bash
# Generate index
python scripts/generate_index.py

# Preview without writing
python scripts/generate_index.py --dry-run

# Custom base path
python scripts/generate_index.py --base-path /path/to/project
```

**Output:** `docs/user-flows/index.md` with:
- Table of all flows with status
- Step counts and issue counts
- Last verified dates
- Quick navigation links

---

## Validation Workflow

After generating documentation, always validate:

```
┌─────────────────────────────────────────┐
│ 1. Documentation Generated              │
│    docs/user-flows/[flow-name].md       │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ 2. Run Validation                       │
│    python scripts/validate_documentation│
│           .py [flow-name]               │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   [PASS]                  [FAIL]
        │                       │
        ▼                       ▼
┌───────────────┐     ┌─────────────────┐
│ 3a. Update    │     │ 3b. Fix Issues  │
│ Index         │     │ - Add missing   │
│               │     │   screenshots   │
│ python scripts│     │ - Fix image     │
│ /generate_    │     │   references    │
│ index.py      │     │ - Add sections  │
└───────────────┘     └─────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────────────────────────────┐
│ 4. Documentation Complete               │
│    - Flow doc validated                 │
│    - Index updated                      │
│    - Ready for stakeholders             │
└─────────────────────────────────────────┘
```

**Best practice:** Run validation automatically after every documentation session:

```bash
# Full workflow
python scripts/validate_documentation.py [flow-name] && \
python scripts/generate_index.py
```

---

## Directory Structure

```
docs/user-flows/
├── index.md                    # Auto-generated catalog
├── login-flow.md               # Flow documentation
├── checkout-process.md         # Flow documentation
├── user-settings.md            # Flow documentation
└── screenshots/
    ├── login-flow/
    │   ├── 01-homepage.png
    │   ├── 02-login-form.png
    │   └── 03-dashboard.png
    ├── checkout-process/
    │   └── ...
    └── user-settings/
        └── ...
```

---

## References

- [Visual Inspection Guide](references/visual-inspection-guide.md) - Systematic checklist for examining screenshots

---

## Extension Points

1. **Baseline comparison** - Add `compare_baselines.py` for visual regression detection
2. **Staleness detection** - Add `check_staleness.py` to flag outdated docs
3. **CI/CD integration** - Scripts already return exit codes for automation
4. **Custom templates** - Add templates to `assets/templates/` for different output formats
5. **Accessibility testing** - Integrate WCAG checks into the workflow

---

## Changelog

### v2.0.0 (Current)
- Added `scripts/` directory with automation capabilities
- Added `validate_documentation.py` for self-verification
- Added `generate_index.py` for flow catalog generation
- Added `references/visual-inspection-guide.md`
- Added Validation Workflow section
- Added Extension Points for future enhancements
- Skill now supports agentic operation with exit codes

### v1.0.0
- Initial release with core documentation and QA workflow
- Playwright MCP integration
- Issue detection and delegation
- Professional markdown output format
