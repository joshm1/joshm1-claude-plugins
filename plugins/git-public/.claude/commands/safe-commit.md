---
description: Safely commit changes with secret scanning and .gitignore validation
---

# Safe Git Commit

Perform a git add and commit with comprehensive secret scanning for public GitHub projects.

## Instructions

$ARGUMENTS

1. **Check .gitignore File**
   - Verify `.gitignore` exists
   - Ensure it includes:
     - `.env.local`
     - `settings.local.json`
     - `.env` (if not already present)
     - `*.env.local`
     - `*.local`
     - Common secret patterns
   - If missing entries, add them and notify the user

2. **Scan Staged Files for Secrets**
   Check staged files by default (files added with `git add`). Scan all staged files for common secret patterns:

   **Critical Patterns to Detect:**
   - API keys: `api[_-]?key`, `apikey`, patterns like `sk-`, `pk-`
   - Tokens: `token`, `auth[_-]?token`, `access[_-]?token`, `bearer`
   - Passwords: `password`, `passwd`, `pwd` (in assignments)
   - Private keys: `-----BEGIN.*PRIVATE KEY-----`, `private[_-]?key`
   - AWS credentials: `aws[_-]?(access[_-]?)?key`, `AKIA[0-9A-Z]{16}`
   - Database URLs: `postgres://`, `mongodb://`, `mysql://` (with credentials)
   - GitHub tokens: `gh[pousr]_[A-Za-z0-9]{36,}`
   - OAuth secrets: `client[_-]?secret`, `oauth`
   - Supabase keys: `eyJ[A-Za-z0-9_-]{30,}\.eyJ[A-Za-z0-9_-]{30,}`
   - Generic secrets: `secret[_-]?(key|token)?`, `credentials`
   - Email/SMTP: `smtp[_-]?(password|pass)`, `mail[_-]?password`
   - Hardcoded credentials: `user.*=.*password`, quoted connection strings

   **Files to Check Carefully:**
   - `.env` files (scan for actual secrets - it's OK to commit .env with placeholders)
   - Any file with `.local` in the name (should be in .gitignore)
   - Files containing actual JWT tokens (long base64 strings)
   - Certificate files: `.pem`, `.key`, `.p12`, `.pfx` (should be in .gitignore)

   **Safe Patterns (Don't Flag):**
   - Variable names like `API_KEY` or `PASSWORD` in:
     - `.env.example`
     - `.env.template`
     - Documentation files
     - Configuration schemas
     - Jinja2 templates (`.jinja` files)
   - Placeholder values: `your-api-key-here`, `<YOUR_KEY>`, `xxx`, `***`
   - Comments explaining what a key should be
   - Test/mock values clearly marked as such

3. **Secret Detection Process**
   - First, run `git diff --cached` to see the FULL diff of what's being committed
   - Analyze the actual changes being made, not just the final file state
   - Get list of staged files with `git diff --cached --name-only`
   - For each staged file (excluding binary files):
     - Read the actual file contents using the Read tool
     - Read the git diff for that specific file with `git diff --cached <file>`
     - Check for secret patterns using regex AND manual inspection
     - **DO NOT RELY SOLELY ON REGEX** - actually look at the content
     - Look for:
       - Actual API keys, tokens, passwords (not just the words)
       - Long random strings that look like secrets
       - Connection strings with embedded credentials
       - Private keys and certificates
       - JWT tokens and bearer tokens
       - Any hardcoded sensitive values
     - Identify line numbers where secrets appear
     - Distinguish between actual secrets and safe references
   - If secrets found:
     - Show file path and line numbers
     - Display the concerning lines (with partial redaction)
     - **UNSTAGE the unsafe files** using `git reset HEAD <file>`
     - **DO NOT DELETE OR REMOVE the files** - only unstage them
     - Explain the issue clearly
     - Suggest moving secrets to `.env.local`
     - Provide example of how to use environment variables instead
     - List which files were unstaged and why

4. **If No Secrets Found and 100% Safe**
   - Show summary of staged files to be committed
   - Automatically create a semantic git commit message based on the changes
   - Execute: `git commit -m "<semantic-message>"` (no need for git add, files are already staged)
   - Show commit hash and summary

   **Semantic Commit Format:**
   - Use conventional commits format: `type(scope): description`
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`
   - Example: `feat(auth): add user login validation`
   - Example: `fix(api): resolve null pointer in user endpoint`
   - Example: `docs(readme): update installation instructions`

5. **Guidance for Users**
   - If secrets detected: "Found potential secrets in files. Please move sensitive values to `.env.local` and use environment variables instead."
   - Provide example:
     ```
     # .env.local (never committed)
     API_KEY=sk-actual-secret-key-here

     # In your code
     const apiKey = process.env.API_KEY;
     ```
   - Remind: "Make sure `.env.local` is in `.gitignore`"

6. **Additional Safety Checks**
   - Warn if committing to `main` or `master` branch without explicit confirmation
   - Check if there are uncommitted changes to `.gitignore` and commit those first
   - Verify the repository has a remote configured (confirms it's meant to be shared)

## Expected Behavior

- ✅ Safe staged files → commit proceeds with semantic message
- ⚠️ Missing .gitignore entries → add them, then proceed
- ❌ Secrets detected → unstage unsafe files (DO NOT delete), explain, suggest fixes
- ℹ️ Always provide clear feedback about what was found and what action was taken
- 🔒 Files are only unstaged, never deleted or modified
