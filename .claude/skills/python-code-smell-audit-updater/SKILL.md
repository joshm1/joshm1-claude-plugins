---
name: python-code-smell-audit-updater
description: Updates the Python code smell audit command when user gives feedback about Python code being a code smell, bad practice, nasty hack, anti-pattern, or mistake. Trigger when user says things like "that's a code smell", "don't do that", "that's bad", "that's a hack", "that's wrong", "fix that pattern" about Python code.
---

# Python Code Smell Audit Updater

When the user identifies a Python code pattern as bad, wrong, or a code smell, update the audit command file.

## Steps

1. Read `~/.claude/commands/python-code-smell-audit.md`
2. Identify the next section number (look for `## N.` pattern)
3. Add a new section for the identified code smell with:
   - Clear title
   - **Bad:** example showing the anti-pattern
   - **Good:** example showing the correct approach (if applicable)
   - Brief explanation of why it's problematic
4. Keep entries concise (3-6 lines each)

## Format for New Entries

```markdown
## N. [Smell Name]
Brief description of what to check for.

**Bad:**
```python
# anti-pattern code
```

**Good:**
```python
# correct approach
```
```

## Important

- Only add genuinely problematic patterns, not style preferences
- Deduplicate: don't add if a similar smell already exists
- Keep examples minimal and focused
