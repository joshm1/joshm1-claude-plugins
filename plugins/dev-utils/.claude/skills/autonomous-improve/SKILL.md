---
name: autonomous-improve
description: Autonomously make one meaningful improvement to a codebase per session. Use this skill whenever the user asks to "improve the project", "find something to fix", "make an autonomous improvement", "run auto-improve", "auto-improve", "autonomous improvement", runs "/autonomous-improve", or wants Claude to independently find and implement a valuable change. Also triggers on cron-driven autonomous contributor sessions, or when the user says "pick something to work on" or "find something useful to do in this codebase". Even if the user just says "improve something" or "make this project better", this skill applies.
---

# Autonomous Improvement

Make **one** meaningful improvement per invocation — something a thoughtful senior engineer would appreciate in code review. Leave the project strictly better than found, or commit nothing and exit cleanly.

## Phase 1: Orient

Do not skip this phase. Understanding the project prevents wasted effort.

1. Read the project's README, CLAUDE.md, CONTRIBUTING.md, or equivalent docs.
2. Explore the codebase structure, test suite, and CI configuration to understand conventions.
3. Run the existing test/lint/typecheck suite. If it already fails, fixing that is the highest-priority improvement — skip to Phase 3.
4. Review recent git history (last ~20 commits) to understand what's actively changing and avoid conflicting with in-flight work.
5. Detect branching strategy:
   ```bash
   which gt >/dev/null 2>&1 && test -f "$(git rev-parse --git-common-dir)/.graphite_repo_config" && echo "graphite" || echo "standard"
   ```
   If both checks pass, use Graphite mode throughout. Otherwise use standard git.
   Note: `--git-common-dir` is used instead of `--git-dir` because in worktrees, `--git-dir` returns the worktree-specific dir while Graphite config lives in the shared `.git/` root.

## Phase 2: Choose one improvement

Pick **exactly one** category. Prefer whichever delivers the most value:

| Category | Examples |
|----------|----------|
| **Fix a real bug** | A bug discovered during exploration — not a hypothetical one |
| **Improve code quality** | Eliminate duplication, clarify confusing logic, simplify overly complex code |
| **Strengthen the test suite** | Add missing coverage for untested edge cases or critical paths |
| **Improve developer experience** | Better error messages, faster builds, clearer logs |
| **Small feature enhancement** | Well-scoped, clearly fits the project's direction |

### Out of scope

These carry disproportionate risk for a single unreviewed session:

- Adding dependencies without strong justification
- Rewriting large subsystems
- Changing public APIs without backwards compatibility
- Modifying CI/CD pipelines
- Purely cosmetic changes (whitespace, import sorting) as the primary contribution

## Phase 3: Implement

### Branch creation

**Standard mode:**
Create a branch named `auto/improve-<short-description>` from the default branch.

**Graphite mode:**
Run `gt create 'auto/improve-<short-description>' -am "<initial commit message>"`. This stacks on whatever branch is currently checked out — which is exactly right when running in a loop, because each improvement builds on the previous one. No need to checkout trunk first.

### Development loop

1. Make changes in focused, logical commits.
   - Standard: normal `git add` + `git commit`
   - Graphite: `gt modify -acm "<message>"` for additional commits on the current branch
2. After every meaningful change, run the full test/lint/typecheck suite. Fix failures before moving on.
3. If mid-implementation the change turns out larger or riskier than expected, scale back to the simplest valuable version. An incomplete refactor is worse than no refactor.

## Phase 4: Verify and ship

1. Run the complete verification suite one final time. Every check must pass.
2. Ensure no untracked or uncommitted files.
3. Final commit message structure:
   ```
   <type>: <concise summary>

   **What:** Description of the change.
   **Why:** What motivated this — the problem, smell, or opportunity found.
   **Verification:** What was run to confirm correctness.
   ```
4. Ship it:
   - **Standard:** Push the branch. If `gh` CLI is available, open a draft PR.
   - **Graphite:** Run `gt submit` to push and create/update the PR. The PR is automatically stacked on any previous improvement's PR.

## Guiding principles

- **Scope to one invocation.** Pick something that can be completed fully. Half-done work creates burden.
- **Respect existing conventions** even if disagreed with. Consistency beats preference.
- **Confidence threshold.** If not confident the change is strictly better, commit nothing and explain what was considered and why it was held back. That's a valid outcome.
- **Loop-friendly.** When run repeatedly (e.g., via `/loop`), each invocation should produce an independent, reviewable improvement. With Graphite, these stack naturally. Without it, each branches from trunk independently.
