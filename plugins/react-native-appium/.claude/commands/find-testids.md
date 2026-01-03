---
name: find-testids
description: Find and audit testIDs in the React Native codebase
args: [path]
---

# Find and Audit testIDs

Analyze the React Native codebase for testID usage, coverage, and naming convention compliance.

## Arguments
- `path` (optional): Specific path to analyze (defaults to `src/` or `app/`)

## Analysis Steps

1. **Find all testIDs in the codebase**
   ```bash
   grep -rn "testID=" --include="*.tsx" --include="*.jsx" ${path:-src/}
   ```

2. **Count testID coverage**
   - Total interactive elements (buttons, inputs, pressables)
   - Elements with testIDs
   - Coverage percentage

3. **Validate naming convention**
   - Expected: `{screen}-{element}-{type}`
   - Flag non-compliant names

4. **Find duplicates** (testIDs should be unique)
   ```bash
   grep -roh 'testID="[^"]*"' --include="*.tsx" ${path:-src/} | sort | uniq -d
   ```

5. **Identify missing testIDs on critical elements**
   - TouchableOpacity/Pressable without testID
   - TextInput without testID
   - Buttons without testID

## Output Format

Generate a markdown report:

```markdown
# testID Audit Report

## Summary
- **Total testIDs Found**: X
- **Unique testIDs**: Y
- **Duplicate testIDs**: Z (list them)
- **Coverage**: A%

## By File

| File | testIDs | Missing | Coverage |
|------|---------|---------|----------|
| LoginScreen.tsx | 5 | 0 | 100% |
| HomeScreen.tsx | 3 | 2 | 60% |

## Issues Found

### Critical: Missing testIDs
- `src/screens/Profile.tsx:45` - Pressable (save button)
- `src/components/Input.tsx:12` - TextInput

### Warning: Naming Convention
- `emailInput` should be `login-email-input`
- `btn1` should be `{screen}-{action}-button`

### Error: Duplicates
- `submit-button` used in 3 files

## Recommendations
1. Add testIDs to X critical elements
2. Rename Y testIDs to follow convention
3. Resolve Z duplicate testIDs
```

## When to Use This vs testid-inspector Agent

| Use `/find-testids` When | Use `testid-inspector` Agent When |
|-------------------------|----------------------------------|
| Quick audit of a specific path | Comprehensive codebase analysis |
| You want a summary report | You need detailed file-by-file breakdown |
| Running before a commit | Planning testID improvements |
| CI/CD validation | Interactive exploration |

## Quick Commands

After running this command, you can use:

- `/new-appium-test <screen>` - Create tests for a specific screen
- Use the testid-inspector agent for deeper, interactive analysis
