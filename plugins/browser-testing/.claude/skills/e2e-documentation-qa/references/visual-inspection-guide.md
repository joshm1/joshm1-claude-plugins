# Visual Inspection Guide

Systematic checklist for examining screenshots during E2E documentation.

## Layout & Positioning

| Check | What to Look For |
|-------|------------------|
| Alignment | Elements centered correctly, consistent left/right margins |
| Spacing | Even gaps between elements, no cramped or floating items |
| Overflow | Content not clipped or cut off at edges |
| Z-index | Correct layering, no unexpected overlaps |
| Responsive | Elements adapt properly at different viewport sizes |

## Styling & Appearance

| Check | What to Look For |
|-------|------------------|
| Colors | Brand colors correct, sufficient contrast for readability |
| Images | All images load, correct size, no broken placeholders |
| Icons | Icons visible, correctly sized, proper color |
| Fonts | Correct typeface, readable size, consistent weights |
| Borders/Shadows | Consistent styling, no missing decorations |

## Text & Content

| Check | What to Look For |
|-------|------------------|
| Truncation | Text not cut off unexpectedly |
| Placeholders | No "undefined", "null", "[object Object]" visible |
| Labels | All form fields have labels, buttons have text |
| Wrapping | Text wraps naturally, no orphaned words |
| Localization | No untranslated strings if i18n expected |

## Interactive Elements

| Check | What to Look For |
|-------|------------------|
| Buttons | Look clickable, proper hover/focus states |
| Links | Distinguished from regular text |
| Forms | Inputs visible, labels associated |
| Disabled states | Clearly indicate non-interactive |
| Loading states | Spinners/skeletons show during async ops |

## Error States

| Check | What to Look For |
|-------|------------------|
| Error messages | User-friendly, no stack traces |
| Empty states | Graceful handling, helpful guidance |
| 404/500 pages | Styled, not raw error text |
| Form validation | Clear indication of invalid fields |
| Toast/alerts | Positioned correctly, dismissible |

## Severity Classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Blocks user journey | Login button invisible, form unsubmittable |
| **High** | Major usability impact | Text unreadable, layout broken |
| **Medium** | Noticeable quality issue | Alignment off, colors wrong |
| **Low** | Minor polish issue | Slight spacing, minor inconsistency |

## Inspection Workflow

```
FOR EACH screenshot:
  1. Overall impression (2 seconds)
     - Does it look "right" at a glance?

  2. Systematic scan (top → bottom, left → right)
     - Check each section against checklist

  3. Compare to expected
     - Does this match design/previous state?

  4. Edge cases
     - What if text was longer?
     - What if data was missing?

  5. Document findings
     - Screenshot location
     - Issue description
     - Severity
     - Suggested fix
```
