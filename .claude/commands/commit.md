---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git branch:*), Bash(git log:*)
argument-hint: [optional additional instructions]
description: Interactive git staging and semantic commit workflow
---

# Git Commit Command

Create a well-structured git commit using an interactive staging workflow with semantic commit messages.

## Current Context

**Branch:** !`git branch --show-current`

**Recent commits (for style reference):**
!`git log --oneline -5 2>/dev/null || echo "No commits yet"`

## Your Task

Follow this systematic workflow to stage changes and create a semantic commit.

$ARGUMENTS

---

## Staging and Committing Workflow

### Step 1: Check Status

Run `git status` to assess the repository state. Identify:
- Modified tracked files ("Changes not staged for commit")
- Deleted tracked files
- Untracked files

### Step 2: Handle Tracked Changes

For files under "Changes not staged for commit":

1. List all modified/deleted tracked files
2. **Ask the user**: "Stage all tracked changes? (y/n)" or allow selection of specific files
3. If yes, stage each file **individually** using `git add <file-path>`
4. **CRITICAL**: Never use `git add .` - this is a non-negotiable safety rule

### Step 3: Handle Untracked Files

**CRITICAL**: Never automatically add untracked files.

1. List all untracked files for the user
2. **Special Check for Code Files**: If any untracked files are source code (`.py`, `.ts`, `.js`, `.go`, `.rs`, etc.), this may indicate incomplete work. Ask the user: "Untracked source files found. Continue with commit? (y/n)"
3. If the user wants to include specific untracked files, add them individually
4. If the user declines to continue, halt the process

### Step 4: Create Semantic Commit

Once staging is complete, generate a semantic commit message.

**Format**: `type(scope): description`

**Types:**
- `feat`: New feature or capability
- `fix`: Bug fix
- `refactor`: Code restructuring without behavior change
- `test`: Adding or modifying tests
- `docs`: Documentation changes
- `chore`: Maintenance tasks, dependency updates
- `perf`: Performance improvements
- `style`: Code style/formatting changes

**Scope**: The area of the codebase affected (e.g., `auth`, `api`, `forms`, `cli`)

**Examples:**
- `feat(auth): add two-factor authentication support`
- `fix(api): resolve null pointer in user endpoint`
- `refactor(forms): extract validation logic to separate module`
- `test(auth): add unit tests for password reset flow`
- `docs(readme): update installation instructions`

**CRITICAL**: Never use `--no-verify` flag unless the user explicitly requests it. Pre-commit hooks perform important checks.

### Step 5: Execute Commit

1. Show the staged changes summary
2. Present the proposed commit message
3. Execute `git commit -m "<message>"`
4. Confirm success with the commit hash

---

## Key Safety Rules

1. **No `git add .`**: Stage files explicitly by their full path
2. **No `--no-verify`**: Never bypass pre-commit hooks unless explicitly instructed
3. **User approval required**: Always ask before staging tracked files
4. **Untracked code files are a red flag**: Require explicit confirmation
5. **Halt on user decline**: If the user says no at any step, stop the process
6. **Semantic commits are mandatory**: Use the `type(scope): description` format

---

## When to Use This vs /safe-commit

- Use `/commit` for the standard interactive staging workflow with semantic commits
- Use `/safe-commit` when you specifically want secret scanning and .gitignore validation
