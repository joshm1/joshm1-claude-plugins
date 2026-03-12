# Documentation Template

Use this template for E2E user flow documentation. Save to `docs/user-flows/<flow-name>.md`.

---

```markdown
# <Flow Name> — User Journey

> Step-by-step walkthrough of the <flow name> with screenshots.

| Property | Value |
|----------|-------|
| **URL** | <starting url> |
| **Last Verified** | <date> |
| **Status** | Working / Has Issues |

## Flow

### Step 1: <Starting Point>

Navigate to the application.

![Step 1 — Starting page](./screenshots/<flow-name>/01-starting-page.png)

The user sees <describe key elements>. From here, they can <available actions>.

---

### Step 2: <Action>

Click **<Button Name>** to proceed.

![Step 2 — After clicking](./screenshots/<flow-name>/02-after-click.png)

<Describe what changed and what's now visible.>

---

### Step 3: <Form/Input>

Fill in the required fields:
- **Email**: user's email address
- **Password**: account password

![Step 3 — Form filled](./screenshots/<flow-name>/03-form-filled.png)

---

### Step 4: <Completion>

Click **Submit** to complete the process.

![Step 4 — Success](./screenshots/<flow-name>/04-success.png)

The user sees a confirmation indicating <success state>.

---

## Issues Found

### Issue 1: <Title>

| Property | Value |
|----------|-------|
| **Type** | Visual / UI / Network |
| **Severity** | Critical / High / Medium / Low |
| **Status** | Fixed / Needs Attention |

**Problem**: <what was wrong>

![Issue screenshot](./screenshots/<flow-name>/issue-01.png)

**Resolution**: <how it was fixed, or what action is recommended>

---

## Summary

| Metric | Value |
|--------|-------|
| Steps Documented | <count> |
| Issues Found | <count> |
| Issues Fixed | <count> |
| Status | Pass / Fail |

---
*Generated via E2E walkthrough on <date>*
```

## Notes on the template

- Adapt the number of steps to the actual flow — don't force it into exactly 4 steps
- Omit the "Issues Found" section entirely if there were no issues
- The Overview table is intentionally minimal — add rows only if they're useful (e.g., "Test Account" for authenticated flows)
- Screenshot paths use relative paths from the markdown file's location
