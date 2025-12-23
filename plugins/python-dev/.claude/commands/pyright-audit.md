---
description: Analyze Python codebase for pyright type hint best practices and generate A+ improvement plan
---

Perform a comprehensive type hint quality analysis of the Python codebase following pyright strict typing standards.

## Analysis Steps

### 1. Scan for Type Violations

Search the codebase for common type hint anti-patterns:

**Any Type Usage:**
```bash
rg "\bAny\b" --type py apps/ packages/ templates/
```
- Every `Any` usage must be documented with justification
- Look for `dict[str, Any]`, `list[Any]`, `Any | SomeType`
- Check if TypedDict or Pydantic models could replace `Any`

**cast() and type: ignore:**
```bash
rg "cast\(|# type: ignore" --type py apps/ packages/ templates/
```
- All instances must have inline comments explaining why
- Check if underlying types can be fixed instead

**Old Typing Syntax:**
```bash
rg "from typing import.*\b(List|Dict|Optional|Tuple)\b" --type py
```
- Should use `list[]`, `dict[]`, `| None`, `tuple[]` instead

**Empty Collections Without Types:**
```bash
rg "= \[\]|= \{\}|= set\(\)" --type py apps/ packages/ templates/
```
- All should have explicit type annotations: `items: list[str] = []`

**Missing Function Types:**
```bash
rg "def \w+\([^)]*\):" --type py | rg -v "\->"
```
- All functions must have return type annotations

### 2. Run Pyright Checks

Execute pyright on all application code:
```bash
uv run pyright apps/ packages/ templates/ scripts/
```

Categorize results:
- **Errors** (must fix)
- **Warnings** (investigate - may be third-party library issues)
- **Informational** (optional improvements)

### 3. Generate Improvement Report

Create a structured report with:

**Section A: Metrics Summary**
- Total Python files analyzed
- Pyright errors count
- Pyright warnings count
- `Any` type usage count
- `cast()` usage count
- `type: ignore` count
- Missing function types count
- Old typing syntax count

**Section B: Violations by File**
- List each file with violations
- Show exact line numbers and issues
- Categorize by severity (HIGH/MEDIUM/LOW)

**Section C: Recommended Fixes**

For each HIGH priority issue:
1. **Location:** `file.py:line`
2. **Problem:** What the violation is
3. **Why it matters:** Impact on type safety
4. **Fix:** Specific code change needed
5. **Example:** Before/after code snippets

**Section D: Third-Party Library Issues**
- List warnings from external libraries (e.g., propelauth, stripe)
- Suggest using `cast()` with documentation when unavoidable
- Recommend creating type stubs if many issues

### 4. Priority Classification

**HIGH Priority (must fix for A+):**
- Any errors reported by pyright
- `Any` types without justification
- Unnecessary `type: ignore` comments
- Functions missing return type annotations

**MEDIUM Priority (should fix):**
- Old typing syntax (List, Dict, Optional)
- Empty collections without explicit types
- Overly broad union types

**LOW Priority (nice to have):**
- Add docstrings with type information
- Use more specific types (e.g., Literal, TypedDict)
- Create custom type aliases for complex types

### 5. Generate A+ Action Plan

If violations found, create numbered action items:

```markdown
## A+ Action Plan

1. [ ] Fix pyright error in auth.py:11 - add return type annotation
2. [ ] Replace `dict[str, Any]` in benchmark.py:20 with BenchmarkResults TypedDict
3. [ ] Add explicit types to empty collections in install.py:134, 188, 434
4. [ ] Fix third-party library warnings using cast() with documentation
5. [ ] Run final verification: `uv run pyright apps/ packages/ templates/`

**Target:** 0 errors, 0 warnings, 0 informations
```

### 6. Verification

After applying fixes:
```bash
uv run pyright apps/ packages/ templates/ scripts/ 2>&1 | tail -1
```

**A+ Criteria:**
- `0 errors, 0 warnings, 0 informations`
- All `Any` types documented
- All `cast()` usage documented
- All `type: ignore` comments necessary and documented
- Modern type syntax throughout
- Full function signature coverage

## Output Format

Present findings in a clear, actionable report with:
- ✅ for compliant patterns
- ⚠️ for warnings
- ❌ for errors
- 📊 for metrics
- 🎯 for recommendations

Grade the codebase: **F / D / C / B / A / A+**

Include both the analysis and the specific commands/fixes needed to reach A+.
