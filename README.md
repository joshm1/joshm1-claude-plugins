# joshm1-claude-plugins

My personal Claude Code plugins collection.

## Installation

### Using Claude Code Marketplace (Recommended)

The easiest way to install these plugins:

```bash
# Add this marketplace to Claude Code
/plugin marketplace add joshm1/joshm1-claude-plugins

# Install individual plugins
/plugin install python-dev@joshm1-claude-plugins
/plugin install git-public@joshm1-claude-plugins
/plugin install dev-utils@joshm1-claude-plugins
```

Then browse available plugins with:
```bash
/plugin
```

### Manual Installation

For local testing or development:

```bash
# Add local marketplace
/plugin marketplace add /path/to/joshm1-claude-plugins

# Or clone and link directly
git clone https://github.com/joshm1/joshm1-claude-plugins.git
ln -s /path/to/joshm1-claude-plugins/.claude your-project/.claude
```

## Available Plugins

### python-dev

Python development tools for testing and code quality.

**Subagents:**
- `pytest-fix` - Analyze and fix failing pytest tests
- `pytest-runner` - Run pytest tests, analyze failures, and fix broken tests
- `python-lint-fix` - Fix Python linting errors and warnings with pyright strict type checking

**Commands:**
- `/python-code-smell-audit` - Audit Python code for common AI coding agent mistakes

**Skills:**
- `pyright-strict-types` - Enforce strict Python typing standards with pyright type checking
- `python-code-smell-audit-updater` - Updates the Python code smell audit command when user gives feedback
- `python-scripts` - Standards for writing Python utility scripts

### git-public

Safe git workflows for public repositories with secret scanning and security checks.

**Commands:**
- `/commit` - Interactive git staging and semantic commit workflow
- `/safe-commit` - Safely commit changes with secret scanning and .gitignore validation
- `/review-safe-commit-history` - Review existing commit history for security issues and secret leaks

### dev-utils

General development utilities and helpers.

**Commands:**
- `/compact-instructions` - Compact instruction files
- `/list-skills` - List all available Claude Code skills
- `/update-mcp-token-usage` - Update MCP token usage statistics from /context output

**Skills:**
- `create-claude-code-extension` - Guide for creating Claude Code subagents, slash commands, or skills

## Creating New Extensions

See the [Claude Code documentation](https://code.claude.com/docs) for details on creating:
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Slash Commands](https://code.claude.com/docs/en/slash-commands)
- [Skills](https://code.claude.com/docs/en/skills)

## License

MIT
