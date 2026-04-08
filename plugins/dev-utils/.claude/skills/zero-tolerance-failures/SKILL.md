---
name: zero-tolerance-failures
description: This skill should be used when ANY errors exist — test failures, type check errors, lint warnings, or build failures — and a decision is needed on whether to fix them or move on. Especially use when errors are labeled "pre-existing", "not my problem", "from another branch", "unrelated to my changes", "just a warning", "infrastructure issue", or "flaky". Also use when asking "is that good enough to merge?", "can I skip these?", "should I defer to a follow-up?", "can I commit with --no-verify?", or before claiming any implementation work is done. Use after rebases or merges when new failures appear, when categorizing failures as "mine vs not mine", or when considering filing separate tickets for existing errors instead of fixing them now.
---

# Zero Tolerance for Errors

**ALL tests must pass. ALL type checks must pass. ALL lints must be clean. 100%. No exceptions. No excuses.**

If anything fails — tests, types, lint, build — it is the current agent's responsibility. Fix it before claiming work is complete.

## The Rule

```
Every error is your responsibility to fix.
"Not my problem" is NEVER an acceptable excuse.
```

This covers:
- **Test failures** — unit tests, E2E tests, integration tests
- **Type errors** — any configured type checker
- **Lint errors** — any configured linter
- **Build errors** — compilation, bundling failures
- **Quality check failures** — anything the project's check command catches

This applies after:
- Completing a feature or spec implementation
- Rebasing or merging branches
- Refactoring code
- ANY change, no matter how small

## "Not My Problem" is Never Acceptable

The most dangerous rationalization is classifying failures as someone else's problem:

| Excuse | Why It's Wrong |
|--------|---------------|
| "These failures are pre-existing" | The branch is yours. The failures are yours. |
| "Main branch introduced these" | Rebasing means accepting the result. Fix it. |
| "I only changed CSS/styles" | If tests broke, the change broke them. |
| "The test was already flaky" | Fix the flake. Don't ignore it. |
| "That's a different feature area" | All checks must pass. Not just yours. |
| "I'll categorize which are mine vs not" | Stop categorizing. Start fixing. |
| "It's a test environment issue" | Prove it. Then fix the environment. |
| "The type errors are in files I didn't touch" | They're on your branch. Fix them. |
| "It's just a warning, not an error" | Warnings are errors you haven't fixed yet. |

## After Every Phase of Work

```
1. Run ALL checks (not just ones "related" to changes)
2. Count: how many errors? How many warnings?
3. If ANY exist → FIX THEM before proceeding
4. Only claim "done" when error count is 0
```

Run the project's full quality check command before and after every phase.

## After Rebases and Merges

Rebases are the #1 source of "not my problem" rationalization:

1. **The merge result was accepted.** Every conflict resolution is a decision.
2. **Behavior changes from the base branch are now yours.** Fix tests and types to match.
3. **Never report "X passed, Y failed, but the Y aren't from our changes."** Report: "X passed, Y failed. Fixing the Y now."

## Red Flags — STOP Immediately

- Sorting failures into "mine" vs "not mine" → **STOP. Fix all of them.**
- Reporting failures without a plan to fix → **STOP. Make a plan.**
- Suggesting "defer to follow-up" for test or type fixes → **STOP. Fix now.**
- Writing a summary that mentions unfixed errors → **STOP. Fix first, summarize after.**
- Claiming errors are "in unrelated files" → **STOP. They're on the branch.**

## What "Done" Means

Work is **NOT done** until:
- [ ] ALL type checks pass (0 errors)
- [ ] ALL lint checks pass (0 errors, 0 warnings)
- [ ] ALL tests pass (0 failures)
- [ ] Quality checks pass (full check suite)

Work is done when every check is green. Not "all the checks related to my changes." ALL checks.

## Stack-Specific Guidance

For tool-specific error patterns, common excuses, and fix strategies:

- **`references/typescript.md`** — tsc, Biome, Vitest, Vite build errors
- **`references/python.md`** — pyright, ruff, pytest errors

## The Bottom Line

The role is not to report errors. The role is to fix errors. When anything fails, the only acceptable response is: **"Fixing them now."**
