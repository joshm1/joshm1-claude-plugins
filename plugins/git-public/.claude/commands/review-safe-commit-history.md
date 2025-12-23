---
description: Review existing commit history for security issues and secret leaks
---

# Review Safe Commit History

**THIS REVIEWS EXISTING COMMITS - IT DOES NOT CREATE NEW COMMITS**

Review past commits to check for accidentally committed secrets, sensitive data, or security issues in commit history.

## Instructions

$ARGUMENTS

1. **Review Recent Commit History**
   - Look back at the last 10 commits (or whatever number specified in instructions above)
   - If the repo has fewer commits, show all available commits
   - Use `git log -n 10 --oneline` to show recent commit history
   - List each commit with its hash and message

2. **Analyze Each Commit for Secrets**
   For each commit in the range:
   - Use `git show <commit-hash>` to see the full diff
   - Scan all changes in that commit for secret patterns

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
   - `.env` files (scan for actual secrets - it's OK to have .env with placeholders)
   - Any file with `.local` in the name
   - Files containing actual JWT tokens (long base64 strings)
   - Certificate files: `.pem`, `.key`, `.p12`, `.pfx`

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

3. **Report Findings**
   - If secrets found in any commit:
     - Show commit hash and message
     - Show file path and line numbers
     - Display the concerning lines (with partial redaction)
     - Explain the severity and risk
     - Provide remediation steps (rewrite history, rotate secrets, etc.)
   - If no secrets found:
     - Confirm that the reviewed commits appear safe
     - Show summary of what was checked

4. **Check .gitignore**
   - Review current `.gitignore` file
   - Suggest additions if common secret files aren't listed:
     - `.env.local`
     - `settings.local.json`
     - `*.env.local`
     - `*.local`
     - Certificate files

## Expected Behavior

- 📜 Reviews EXISTING commit history (does not create new commits)
- ✅ Clean history → confirm no secrets found
- ❌ Secrets detected → report findings with commit hashes and remediation steps
- ⚠️ Missing .gitignore entries → suggest additions
- ℹ️ Always provide clear feedback about what was checked and what was found
- 🔍 Focus on security audit, not making changes
