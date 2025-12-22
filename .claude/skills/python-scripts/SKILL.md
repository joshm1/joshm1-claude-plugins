---
name: python-scripts
description: Standards for writing Python utility scripts
---

# Python Scripts Skill

Standards for writing Python utility scripts in this project, based on the patterns in `scripts/manage-users.py`.

## Core Principles

1. **Use `uv run` for execution** - No virtual environment management needed
2. **PEP 723 inline script metadata** - Dependencies declared in the script file
3. **Click for CLI framework** - Simple, composable command-line interfaces
4. **Rich for output** - Beautiful terminal output with colors and tables
5. **Type hints throughout** - Full type annotations for all functions
6. **Proper error handling** - Graceful failures with clear error messages

## Script Template

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "click>=8.1.0",
#   "rich>=13.0.0",
# ]
# ///
"""Brief description of what this script does."""

import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.group()
def cli():
    """Main CLI group description."""
    pass


@cli.command()
@click.option('--flag', is_flag=True, help='Example flag option')
@click.argument('arg')
def command_name(flag: bool, arg: str):
    """Command description."""
    try:
        # Command logic here
        console.print("[bold green]✓[/] Success message")
        return 0
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(cli())
```

## Shebang Line

**Always use:**
```python
#!/usr/bin/env -S uv run
```

**Why:**
- `-S` flag allows passing arguments to the interpreter
- `uv run` automatically handles dependencies from PEP 723 metadata
- No need for separate virtual environment activation

**Make executable:**
```bash
chmod +x script.py
```

## PEP 723 Inline Script Metadata

**Format:**
```python
# /// script
# dependencies = [
#   "package-name>=version",
#   "another-package>=version",
# ]
# ///
```

**Common dependencies:**
- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Terminal output
- `python-dotenv>=1.0.0` - Environment variables
- `supabase>=2.10.0` - Supabase client

**Rules:**
- Must appear at top of file after shebang
- Must use exact format with `# ///` delimiters
- Pin minimum versions with `>=`
- Keep alphabetically sorted

## Click Framework Standards

### Basic Command

```python
@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.argument('input_file')
def process(verbose: bool, input_file: str):
    """Process the input file."""
    if verbose:
        console.print(f"Processing {input_file}...")
```

### Command Groups

```python
@click.group()
def cli():
    """Main command description."""
    pass

@cli.command()
def subcommand():
    """Subcommand description."""
    pass
```

**Usage:** `./script.py subcommand`

### Options vs Arguments

**Options** (optional, named):
```python
@click.option('--count', '-c', default=1, help='Number of iterations')
@click.option('--json-output', is_flag=True, help='Output as JSON')
```

**Arguments** (required, positional):
```python
@click.argument('filename')
@click.argument('output', type=click.Path())
```

### Type Hints with Click

```python
@click.option('--count', type=int, default=1)
def command(count: int):  # Type hint matches Click type
    """Command with typed parameter."""
    pass
```

## Rich Console Output

### Basic Usage

```python
from rich.console import Console

console = Console()

# Success messages
console.print("[bold green]✓[/] Operation successful")

# Error messages
console.print("[bold red]Error:[/] Something went wrong")

# Info messages
console.print("[blue]ℹ[/] Information message")

# Warning messages
console.print("[yellow]⚠[/] Warning message")
```

### Tables

```python
from rich.table import Table

table = Table(show_header=True)
table.add_column("Name", style="cyan")
table.add_column("Value", style="green")

table.add_row("Key 1", "Value 1")
table.add_row("Key 2", "Value 2")

console.print(table)
```

**For simple key-value pairs:**
```python
table = Table(show_header=False)
table.add_row("ID", user_data["id"])
table.add_row("Email", user_data["email"])
console.print(table)
```

### JSON Output Option

**Always provide a `--json-output` flag for machine-readable output:**

```python
@click.option('--json-output', is_flag=True, help='Output as JSON')
def command(json_output: bool):
    """Command with JSON output option."""
    data = {"key": "value"}

    if json_output:
        print(json.dumps(data, indent=2))  # Use print, not console
    else:
        console.print("[bold]Pretty output:[/]")
        console.print(data)
```

## Environment Variables

### Using python-dotenv

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load from specific .env file
env_path = Path(__file__).parent.parent / "packages" / "client" / ".env.local"
load_dotenv(env_path)

# Access variables
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_SERVICE_KEY")

# Validate required variables
if not SUPABASE_URL or not SUPABASE_KEY:
    console.print("[bold red]Error:[/] Missing required environment variables")
    sys.exit(1)
```

## Type Hints

**Always use type hints for:**
- Function parameters
- Return types
- Variables when not obvious

```python
def generate_password(length: int = 16) -> str:
    """Generate a random secure password."""
    chars: str = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def process_data(items: list[dict[str, str]]) -> None:
    """Process a list of data items."""
    for item in items:
        console.print(f"Processing {item['name']}")
```

## Error Handling

### Pattern

```python
@cli.command()
def command():
    """Command that might fail."""
    try:
        # Main logic
        result = do_something()
        console.print("[bold green]✓[/] Success")
        return 0
    except SpecificError as e:
        console.print(f"[bold red]Error:[/] {e}")
        return 1
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/] {e}")
        return 1
```

### Exit Codes

```python
if __name__ == "__main__":
    sys.exit(cli())  # Click returns exit code from commands
```

**Standard codes:**
- `0` - Success
- `1` - General error
- `2` - Invalid usage (Click handles this)

## File Paths

**Use pathlib.Path:**
```python
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent
config_file = project_root / "config" / "settings.json"

# Check existence
if config_file.exists():
    with open(config_file) as f:
        data = json.load(f)
```

## Docstrings

### Module Docstring

```python
#!/usr/bin/env -S uv run
# ... dependencies ...
"""Brief one-line description.

Longer description if needed, explaining what the script does,
when to use it, and any important notes.
"""
```

### Function Docstrings

```python
def process_item(item: dict, verbose: bool = False) -> dict:
    """Process a single item and return the result.

    Args:
        item: Dictionary containing item data
        verbose: Enable verbose output

    Returns:
        Processed item dictionary

    Raises:
        ValueError: If item is missing required fields
    """
    pass
```

## Common Patterns

### Random ID Generation

```python
import random
import string

# Short random ID
random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# Timestamp-based unique ID
timestamp = int(random.random() * 1000000)
unique_id = f"item-{timestamp}-{random_id}"
```

### Supabase Admin Operations

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Create user with admin API
response = supabase.auth.admin.create_user({
    "email": email,
    "password": password,
    "email_confirm": True,
})

# Direct database queries
result = supabase.from_('table_name').select('*').execute()
```

## Script Naming

- Use `kebab-case` for script names: `manage-users.py`, `create-test-data.py`
- Place in `scripts/` directory at project root
- Make executable: `chmod +x scripts/script-name.py`

## Running Scripts

```bash
# Direct execution (preferred)
./scripts/manage-users.py --help

# Via uv (alternative)
uv run scripts/manage-users.py --help

# Commands and subcommands
./scripts/manage-users.py create --json-output
```

## Example: Complete Script

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "click>=8.1.0",
#   "rich>=13.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///
"""Manage configuration for the application."""

import json
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

console = Console()

# Load environment
env_path = Path(__file__).parent.parent / "packages" / "client" / ".env.local"
load_dotenv(env_path)


@click.group()
def cli():
    """Configuration management tool."""
    pass


@cli.command()
@click.option('--json-output', is_flag=True, help='Output as JSON')
def list(json_output: bool):
    """List all configuration values."""
    try:
        config = {
            "env": os.getenv("NODE_ENV", "development"),
            "api_url": os.getenv("VITE_API_URL"),
        }

        if json_output:
            print(json.dumps(config, indent=2))
        else:
            table = Table(title="Configuration")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")

            for key, value in config.items():
                table.add_row(key, value or "[dim]not set[/]")

            console.print(table)

        return 0
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        return 1


@cli.command()
@click.argument('key')
@click.argument('value')
def set(key: str, value: str):
    """Set a configuration value."""
    try:
        console.print(f"[blue]ℹ[/] Setting {key} = {value}")
        # Implementation here
        console.print("[bold green]✓[/] Configuration updated")
        return 0
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(cli())
```

## Testing Scripts

**Manual testing:**
```bash
# Test all commands
./script.py --help
./script.py command --help
./script.py command --json-output

# Test error cases
./script.py command --invalid-option
```

**No automated tests required for utility scripts** - manual testing is sufficient.

## When to Create Scripts

**Create Python scripts for:**
- Database seeding/management
- User creation/management
- Data migration
- Cleanup tasks
- Development utilities
- CI/CD helpers

**Don't create scripts for:**
- Tasks that are part of the application runtime
- Features that should be in the web UI
- One-time operations (use the REPL instead)

## Key Takeaways

1. ✅ **Use `uv run`** - No venv management needed
2. ✅ **PEP 723 metadata** - Dependencies in the script
3. ✅ **Click for CLI** - Simple, composable commands
4. ✅ **Rich for output** - Beautiful terminal formatting
5. ✅ **Type hints** - Full type coverage
6. ✅ **JSON output option** - For programmatic use
7. ✅ **Proper error handling** - Graceful failures
8. ✅ **Exit codes** - 0 for success, 1 for errors

**Follow these standards for all Python utility scripts in this project!**
