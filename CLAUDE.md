# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

An opinionated collection of Claude Code plugins that encode engineering team practices into automated tooling. Each plugin enforces a specific engineering opinion — strict types, secret scanning, test discipline — as the default behavior inside Claude Code. Plugins are installed via `/plugin marketplace add joshm1/claude-eng-toolkit`.

## Repository Structure

```
.claude-plugin/marketplace.json   # Central plugin registry (versions, sources)
.claude/commands/                  # Repo-level commands (e.g., /release-plugin)
plugins/
  <plugin-name>/
    .claude/
      agents/        # Subagent definitions (.md with YAML frontmatter)
      commands/      # Slash commands (.md with YAML frontmatter)
      skills/        # Each skill is a directory:
        <skill-name>/
          SKILL.md        # Main skill content
          references/     # Supporting docs
          scripts/        # Automation scripts (.py)
      hooks/          # Event-driven hooks
```

## Plugin Component Formats

All components are **Markdown files with YAML frontmatter**. Claude Code auto-discovers them from the `.claude/` subdirectories (no manual registration needed).

**Agents** — autonomous subagents with specified tools and model:
```yaml
---
name: agent-name
description: When and what this agent does
tools: Bash, Read, Edit, Grep, Glob   # or YAML array
model: haiku                            # haiku | sonnet | opus
---
```

**Commands** — user-invocable slash commands:
```yaml
---
description: What the command does
argument-hint: <required> [optional]
arguments:
  - name: arg_name
    description: What it is
    required: true
allowed-tools: Task, Read, Bash        # restrict available tools
---
```
Commands reference arguments via `$ARGUMENTS` in the body.

**Skills** — knowledge bases invoked by the Skill tool. The `SKILL.md` frontmatter has `name` and `description` (the description controls when Claude auto-invokes it). Supporting files go in `references/` and `scripts/` subdirs.

## Versioning & Releases

Each plugin has a semantic version in `.claude-plugin/marketplace.json`. To release:
```
/release-plugin <plugin-name> [patch|minor|major]
```
This stages changes, bumps version, commits (with descriptive message — not just "Release vX.Y.Z"), and creates an annotated git tag `<plugin>-v<version>`.

## Current Plugins

| Plugin | Description |
|--------|-------------|
| `python-dev` | Strict Python type safety (no Any, no cast), pytest workflows, code smell audit |
| `typescript-dev` | Post-edit type checking and Biome linting in under 30 seconds |
| `browser-testing` | Headless browser QA with screenshots and documented evidence |
| `git-public` | Secret scanning before commit, semantic commits, history audit |
| `git-worktrees` | Worktree environment isolation with port offsets, env copying, database naming |
| `ci-automation` | Autonomous PR babysitting, branch triage dashboards, semantic GitHub releases |
| `parallel-agents` | Wave-planned parallel implementation across concurrent subagents |
| `testing` | Zero-tolerance test failure and error investigation discipline |
| `react-native-appium` | TDD workflow for Appium E2E with Page Object patterns |
| `openclaw` | OpenClaw skill authoring standards and SKILL.md format |
| `audio-transcripts` | Text-side speaker diarization for Whisper ASR transcripts (paired with pyannote in polyphony) |
| `dev-utils` | Meta utilities: instruction compacting, permission syncing, screenshot galleries |

## Conventions

- **Kebab-case** for all directory and file names
- **Model selection**: haiku for fast/lightweight checks, sonnet for standard tasks, opus for complex reasoning
- Skills that include Python scripts use `uv run` to execute them
- Commit messages follow conventional commits: `feat(plugin-name): describe what changed`
- Tags follow pattern: `plugin-name-vX.Y.Z`
