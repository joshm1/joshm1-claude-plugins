---
name: create-claude-code-extension
description: Guide for creating Claude Code subagents, slash commands, or skills. Use when user asks to create or write a new subagent, command, or skill.
allowed-tools: WebFetch, Write, Read, Bash
---

# Create Claude Code Extension Skill

This skill guides you through creating Claude Code subagents, slash commands, and skills with proper formatting and documentation.

## When to Use This Skill

Use this skill when the user asks to:
- "Create a subagent for..."
- "Write a slash command to..."
- "Make a skill that..."
- "Add a new agent/command/skill..."

## Step 1: Determine Extension Type

Ask yourself what the user needs:

### Subagents (`.claude/agents/*.md`)
**Use when**: Autonomous task execution needed
- Complex multi-step workflows
- Code review, debugging, testing
- Research and analysis tasks
- Background processing

**Example**: code-quality-check, debugger, test-runner

### Slash Commands (`.claude/commands/*.md`)
**Use when**: User-invoked explicit actions
- Quick utilities the user triggers
- Custom shortcuts for common tasks
- Commands with specific arguments

**Example**: /quality-check, /fix-issue, /optimize

### Skills (`.claude/skills/*/SKILL.md`)
**Use when**: Context-aware autonomous assistance
- Claude should invoke automatically based on context
- Providing guidance for specific patterns
- Domain-specific expertise

**Example**: Database migration guidance, API design patterns

## Step 2: Read Official Documentation

**ALWAYS fetch the latest documentation before creating:**

```bash
# For Subagents
WebFetch https://code.claude.com/docs/en/sub-agents

# For Slash Commands
WebFetch https://code.claude.com/docs/en/slash-commands

# For Skills
WebFetch https://code.claude.com/docs/en/skills
```

**Prompt for WebFetch**: "Extract the complete structure, required fields, examples, and best practices"

## Step 3: Create the Extension

### For Subagents (`.claude/agents/*.md`)

**File location**: `.claude/agents/<name>.md`

**Format**:
```markdown
---
name: unique-agent-name
description: When this subagent should be invoked
tools: Bash, Read, Write  # Optional, inherits all if omitted
model: sonnet  # Optional: sonnet, haiku, opus
---

# Agent Name

You are a [role] agent. Your job is to [purpose].

## Your Task

[Detailed instructions on what the agent should do]

## Approach

[Step-by-step guidance]

## Reporting

[How to report results]
```

### For Slash Commands (`.claude/commands/*.md`)

**File location**: `.claude/commands/<name>.md`

**Format**:
```markdown
---
description: Brief command description
argument-hint: <optional-args>  # Optional
model: sonnet  # Optional
---

[Command prompt content - what Claude should do when this command is invoked]

Can use:
- $ARGUMENTS or $1, $2 for arguments
- @filename to reference files
- !command for bash execution
```

### For Skills (`.claude/skills/<name>/SKILL.md`)

**🚨 CRITICAL: Skills require a DIRECTORY with SKILL.md inside!**

**File location**: `.claude/skills/<name>/SKILL.md`
- Create directory: `.claude/skills/<name>/`
- Create file: `SKILL.md` inside that directory
- ❌ NOT `.claude/skills/<name>.md` (this won't work!)
- ✅ YES `.claude/skills/<name>/SKILL.md`

**Format**:
```markdown
---
name: skill-name
description: Brief (1-2 sentences) but descriptive explanation of what this skill does and WHEN Claude should use it. Include keywords that trigger the skill. Max 1024 chars.
allowed-tools: Bash, Read, Write, Grep  # Optional - only if skill needs specific tools
---

# Skill Name

[Detailed instructions for Claude on how to use this skill]

## When to Use

[Specific contexts where this skill applies]

## Approach

[Step-by-step guidance]
```

**Writing the Description (CRITICAL for Auto-Invocation)**

The `description` field determines when Claude automatically invokes the skill. Make it:

1. **Brief** - 1-2 sentences, under 200 chars if possible
2. **Specific** - Include concrete keywords and use cases
3. **Actionable** - Describe WHEN to use it (not just what it is)
4. **Context-rich** - Mention related terms Claude might see

**Examples of GOOD descriptions:**
```yaml
# ✅ GOOD - Specific keywords and triggers
description: Guide for writing and reviewing tests (unit tests with Vitest, E2E tests with Playwright). Use when user asks to write tests, or when you're writing tests yourself. Emphasizes running tests to verify they pass, using real data, and merging E2E tests with shared setup for performance.

# ✅ GOOD - Clear trigger words
description: Guidelines for testing features with Playwright MCP browser automation. Use when implementing UI features that need validation - emphasizes mobile-first testing, taking screenshots for visual verification, and actually clicking through the UI to ensure everything works and looks correct.

# ✅ GOOD - Specific domain keywords
description: Start all necessary development servers for the Greenlight Clone monorepo including shared package watch mode, client Vite dev server, and optional Supabase functions. Use when beginning development or when servers need to be restarted.
```

**Examples of BAD descriptions:**
```yaml
# ❌ BAD - Too vague, no triggers
description: Help with tests

# ❌ BAD - Doesn't say WHEN to use it
description: This skill provides guidance on writing unit and E2E tests

# ❌ BAD - Missing keywords and context
description: Testing helper
```

**Testing Your Description:**
Ask yourself: "If I mentioned [X], would Claude know to invoke this skill?"
- Writing tests → Should trigger "writing-tests" skill
- Start dev server → Should trigger "dev-server" skill
- Create skill → Should trigger "create-claude-code-extension" skill

**Directory Creation Workflow:**
```bash
# 1. Create the directory
mkdir -p .claude/skills/my-skill-name

# 2. Create SKILL.md inside
# Write the file to .claude/skills/my-skill-name/SKILL.md

# 3. Verify structure
ls -la .claude/skills/my-skill-name/
# Should show: SKILL.md
```

## Step 4: Validate Format

**Check**:
- ✅ YAML frontmatter uses `---` delimiters (both opening and closing)
- ✅ Required fields present (name, description)
- ✅ Name uses lowercase, numbers, hyphens only (no underscores, spaces, or capitals)
- ✅ Description is clear, actionable, and includes trigger keywords
- ✅ Description explains WHEN to use the extension
- ✅ Description is under 1024 chars (ideally under 200)
- ✅ File in correct directory:
  - Subagents: `.claude/agents/<name>.md`
  - Commands: `.claude/commands/<name>.md`
  - Skills: `.claude/skills/<name>/SKILL.md` (directory + file!)
- ✅ For skills: Directory exists with `SKILL.md` inside (not a single `.md` file)
- ✅ Markdown formatting correct

## Step 5: Test the Extension

**For subagents**:
```bash
# Invoke explicitly
"Use the <name> subagent to [task]"
```

**For commands**:
```bash
# User types
/<command-name> [arguments]
```

**For skills**:
```bash
# Should invoke automatically based on context
# Verify description triggers correctly by testing with relevant keywords

# Test by asking questions that match the description:
# - If skill is about "writing tests", ask "how do I write a test?"
# - If skill is about "dev server", say "start the dev server"
# - Verify Claude mentions or uses the skill in response
```

## Examples from This Project

### Subagent Example
```markdown
---
name: code-quality-check
description: Run comprehensive quality checks after writing or modifying code
tools: Bash, Read, Grep
model: haiku
---

# Code Quality Check Agent
[Instructions...]
```

### Command Example
```markdown
---
description: Run comprehensive code quality checks on the codebase
---

Run comprehensive code quality checks...
[Detailed prompt...]
```

### Skill Example - writing-tests
```markdown
---
name: writing-tests
description: Guide for writing and reviewing tests (unit tests with Vitest, E2E tests with Playwright). Use when user asks to write tests, or when you're writing tests yourself. Emphasizes running tests to verify they pass, using real data, and merging E2E tests with shared setup for performance.
allowed-tools: Bash, Read, Write, Grep
---

# Writing Tests Skill

[Detailed instructions for test writing best practices...]
```

**File location**: `.claude/skills/writing-tests/SKILL.md`

**Why this description works:**
- ✅ Mentions "writing" and "reviewing tests" - key trigger words
- ✅ Specifies tools: "Vitest" and "Playwright"
- ✅ Says WHEN to use: "when user asks to write tests, or when you're writing tests yourself"
- ✅ Includes key concepts: "running tests", "real data", "merging E2E tests"

## Common Mistakes to Avoid

❌ **Missing frontmatter** - All files need YAML frontmatter with `---` delimiters
❌ **Wrong directory** - Subagents in `.claude/agents/`, commands in `.claude/commands/`, skills in `.claude/skills/<name>/`
❌ **Incorrect skill structure** - Skills MUST be in a directory with `SKILL.md` inside, NOT a single `.md` file
❌ **Vague descriptions** - Be specific about when to use the extension, include trigger keywords
❌ **Description too long** - Keep descriptions under 200 chars when possible, max 1024 chars
❌ **Description missing WHEN** - Always explain WHEN Claude should invoke the skill
❌ **Not reading docs** - Always fetch latest documentation first
❌ **Wrong file name** - Skills must be named `SKILL.md` (uppercase), not `skill.md` or `<name>.md`

## Workflow Summary

1. **Determine type** (subagent vs command vs skill)
2. **Fetch documentation** (WebFetch the official docs)
3. **Create file** in correct location with proper format
4. **Validate** frontmatter and content
5. **Test** the extension works as expected
6. **Commit** to git (project-level extensions)

## Documentation URLs

- **Subagents**: https://code.claude.com/docs/en/sub-agents
- **Slash Commands**: https://code.claude.com/docs/en/slash-commands
- **Skills**: https://code.claude.com/docs/en/skills
- **Claude Code Docs**: https://code.claude.com/docs
