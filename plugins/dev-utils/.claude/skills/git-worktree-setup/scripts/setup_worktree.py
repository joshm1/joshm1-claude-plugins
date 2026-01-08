#!/usr/bin/env -S uv run
# /// script
# dependencies = ["click>=8.1.0", "rich>=13.0.0"]
# requires-python = ">=3.11"
# ///
"""
Setup environment isolation for Git worktrees.

Automates the process of configuring a Git worktree with:
- Port offset calculation to avoid conflicts
- Environment file copying with port transformation
- Claude Code settings isolation with path transformation
- Database URL generation with worktree suffix
- IDE config copying (.vscode, .idea)

Usage:
    # Setup current worktree (auto-detect source)
    uv run setup_worktree.py

    # Setup specific worktree with explicit source
    uv run setup_worktree.py --worktree ../project-feature --source .

    # Specify manual port offset
    uv run setup_worktree.py --offset 200

    # Preview without making changes
    uv run setup_worktree.py --dry-run

    # Force overwrite existing files
    uv run setup_worktree.py --force
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse, urlunparse

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class WorktreeConfig(TypedDict):
    """Configuration for worktree setup."""

    worktree_path: Path
    source_path: Path
    worktree_name: str
    port_offset: int


# Files to copy with port transformation
ENV_FILE_PATTERNS = [
    ".env",
    ".env.local",
    ".env.development.local",
    ".env.production.local",
    ".env.test.local",
]

# Claude files to copy
CLAUDE_FILES = [
    ".claude/settings.local.json",
]

# IDE config directories to copy
IDE_CONFIGS = [
    ".vscode",
    ".idea",
]

# MCP config file
MCP_CONFIG = ".mcp.json"

# Known port variable labels (for nice display names)
KNOWN_PORT_LABELS: dict[str, str] = {
    "PORT": "App",
    "VITE_PORT": "Vite",
    "DEV_PORT": "Dev Server",
    "WEBPACK_PORT": "Webpack",
    "NEXT_PORT": "Next.js",
    "API_PORT": "API",
    "BACKEND_PORT": "Backend",
    "FRONTEND_PORT": "Frontend",
    "SERVER_PORT": "Server",
    "DB_PORT": "Database",
    "POSTGRES_PORT": "PostgreSQL",
    "PG_PORT": "PostgreSQL",
    "MYSQL_PORT": "MySQL",
    "REDIS_PORT": "Redis",
    "MONGO_PORT": "MongoDB",
    "ELASTICSEARCH_PORT": "Elasticsearch",
    "RABBITMQ_PORT": "RabbitMQ",
    "KAFKA_PORT": "Kafka",
    "MINIO_PORT": "MinIO",
    "MAILHOG_PORT": "MailHog",
}

# Generic pattern to match ANY port variable (VAR_PORT=1234 or VAR_port=1234)
PORT_PATTERN = re.compile(r"^([A-Z_]*(?:PORT|port)[A-Z_]*)=(\d+)$", re.MULTILINE)


def calculate_port_offset(worktree_name: str) -> int:
    """Generate deterministic port offset (100-999) from worktree name.

    Uses MD5 hash to ensure same worktree always gets same offset.
    Range 100-999 avoids low ports and provides good distribution.
    """
    hash_digest = hashlib.md5(worktree_name.encode()).hexdigest()
    return 100 + (int(hash_digest[:4], 16) % 900)


def find_source_repo(worktree_path: Path) -> Path | None:
    """Find the main repository for this worktree.

    Git worktrees have a .git file (not directory) pointing to the main repo.
    """
    git_path = worktree_path / ".git"

    if git_path.is_file():
        # .git is a file pointing to the main repo's .git directory
        content = git_path.read_text().strip()
        if content.startswith("gitdir:"):
            main_git = Path(content.split("gitdir:")[1].strip())
            # Navigate from .git/worktrees/<name> to repo root
            # Path is like: /path/to/main/.git/worktrees/feature-x
            if "worktrees" in main_git.parts:
                return main_git.parent.parent.parent
    elif git_path.is_dir():
        # This is a regular repo, not a worktree
        console.print("[yellow]Warning:[/] This appears to be a main repo, not a worktree")
        return None

    return None


def get_port_label(var_name: str) -> str:
    """Get a human-readable label for a port variable.

    Uses known labels for common variables, otherwise derives from var name.
    """
    # Check known labels first
    if var_name in KNOWN_PORT_LABELS:
        return KNOWN_PORT_LABELS[var_name]

    # Derive label from variable name
    # e.g., CUSTOM_SERVICE_PORT -> Custom Service
    label = var_name.replace("_PORT", "").replace("_port", "").replace("_", " ").title()
    return label if label else var_name


def transform_ports_in_content(content: str, offset: int) -> tuple[str, dict[str, int]]:
    """Transform port numbers in env file content.

    Auto-detects any variable containing 'PORT' or 'port' and applies offset.
    Returns (modified_content, port_mapping).
    """
    ports: dict[str, int] = {}

    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        base_port = int(match.group(2))
        new_port = base_port + offset
        label = get_port_label(var_name)
        ports[label] = new_port
        return f"{var_name}={new_port}"

    content = PORT_PATTERN.sub(replacer, content)

    return content, ports


def add_worktree_vars(content: str, name: str, offset: int) -> str:
    """Add worktree identification variables to env content."""
    header = f"""# Worktree configuration (auto-generated by setup_worktree.py)
WORKTREE_NAME={name}
WORKTREE_OFFSET={offset}

"""
    # Check if already has worktree vars
    if "WORKTREE_NAME=" in content:
        # Update existing
        content = re.sub(r"^WORKTREE_NAME=.*$", f"WORKTREE_NAME={name}", content, flags=re.MULTILINE)
        content = re.sub(r"^WORKTREE_OFFSET=.*$", f"WORKTREE_OFFSET={offset}", content, flags=re.MULTILINE)
        return content

    return header + content


def transform_database_url(url: str, worktree_name: str, offset: int) -> str:
    """Transform DATABASE_URL with worktree suffix and port offset.

    Example:
        postgres://user:pass@localhost:5432/myapp
        -> postgres://user:pass@localhost:5532/myapp_feature_auth
    """
    if not url:
        return url

    parsed = urlparse(url)

    # Sanitize worktree name for database
    safe_name = re.sub(r"[^a-z0-9]", "_", worktree_name.lower())

    # Update database name (path component)
    new_path = f"{parsed.path.rstrip('/')}_{safe_name}"

    # Update port if present
    new_netloc = parsed.netloc
    if parsed.port:
        new_port = parsed.port + offset
        # Replace port in netloc
        new_netloc = re.sub(r":(\d+)$", f":{new_port}", parsed.netloc)

    return urlunparse(parsed._replace(path=new_path, netloc=new_netloc))


def transform_env_content(content: str, config: WorktreeConfig) -> tuple[str, dict[str, int]]:
    """Transform environment file content for worktree.

    - Adds worktree identification vars
    - Transforms port numbers
    - Transforms DATABASE_URL
    """
    # Add worktree vars
    content = add_worktree_vars(content, config["worktree_name"], config["port_offset"])

    # Transform ports
    content, ports = transform_ports_in_content(content, config["port_offset"])

    # Transform DATABASE_URL if present
    db_pattern = r"^(DATABASE_URL)=(.+)$"
    match = re.search(db_pattern, content, re.MULTILINE)
    if match:
        old_url = match.group(2)
        new_url = transform_database_url(old_url, config["worktree_name"], config["port_offset"])
        content = re.sub(db_pattern, f"DATABASE_URL={new_url}", content, flags=re.MULTILINE)

    return content, ports


def transform_claude_permissions(content: str, old_path: str, new_path: str) -> str:
    """Transform path-based permissions in Claude settings.

    Replaces absolute paths in permission strings.
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return content

    if "permissions" not in data:
        return content

    for key in ["allow", "deny", "ask"]:
        if key in data["permissions"]:
            data["permissions"][key] = [perm.replace(old_path, new_path) for perm in data["permissions"][key]]

    # Add worktree metadata
    data["worktree"] = {
        "name": Path(new_path).name,
        "source": old_path,
    }

    return json.dumps(data, indent=2)


def copy_env_file(source: Path, dest: Path, config: WorktreeConfig, *, dry_run: bool = False) -> dict[str, int]:
    """Copy and transform an environment file."""
    content = source.read_text()
    transformed, ports = transform_env_content(content, config)

    if dry_run:
        console.print(f"  [dim]Would copy:[/] {source.name} -> {dest}")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(transformed)
        console.print(f"  [green]Copied:[/] {source.name}")

    return ports


def copy_claude_settings(source: Path, dest: Path, config: WorktreeConfig, *, dry_run: bool = False) -> None:
    """Copy and transform Claude settings file."""
    content = source.read_text()
    transformed = transform_claude_permissions(content, str(config["source_path"]), str(config["worktree_path"]))

    if dry_run:
        console.print(f"  [dim]Would copy:[/] {source.relative_to(config['source_path'])} -> {dest}")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(transformed)
        console.print(f"  [green]Copied:[/] {source.relative_to(config['source_path'])}")


def copy_ide_config(source: Path, dest: Path, *, dry_run: bool = False) -> None:
    """Copy IDE configuration directory."""
    if dry_run:
        console.print(f"  [dim]Would copy:[/] {source.name}/ -> {dest}")
    else:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source, dest)
        console.print(f"  [green]Copied:[/] {source.name}/")


def copy_mcp_config(source: Path, dest: Path, config: WorktreeConfig, *, dry_run: bool = False) -> None:
    """Copy and transform MCP configuration file."""
    content = source.read_text()
    # Transform any path references
    transformed = content.replace(str(config["source_path"]), str(config["worktree_path"]))

    if dry_run:
        console.print(f"  [dim]Would copy:[/] {source.name}")
    else:
        dest.write_text(transformed)
        console.print(f"  [green]Copied:[/] {source.name}")


def validate_setup(config: WorktreeConfig) -> list[str]:
    """Validate the worktree setup is complete."""
    issues: list[str] = []

    # Check .env.local exists
    env_local = config["worktree_path"] / ".env.local"
    if not env_local.exists():
        issues.append(".env.local not created")
    else:
        content = env_local.read_text()
        if f"WORKTREE_OFFSET={config['port_offset']}" not in content:
            issues.append(f"WORKTREE_OFFSET not set to {config['port_offset']}")

    # Check .claude directory exists
    claude_dir = config["worktree_path"] / ".claude"
    if not claude_dir.exists():
        issues.append(".claude directory not found")

    return issues


@click.command()
@click.option(
    "--worktree",
    "-w",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to worktree (default: current directory)",
)
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to source repo (auto-detected if not provided)",
)
@click.option(
    "--offset",
    "-o",
    type=int,
    default=None,
    help="Manual port offset (auto-calculated if not provided)",
)
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
def main(
    worktree: Path | None,
    source: Path | None,
    offset: int | None,
    dry_run: bool,
    force: bool,
) -> int:
    """Setup environment isolation for a Git worktree.

    Copies environment files with port transformation, Claude settings with
    path transformation, and IDE configs. Calculates a deterministic port
    offset to avoid conflicts between worktrees.
    """
    # Determine worktree path
    worktree_path = (worktree or Path.cwd()).resolve()
    worktree_name = worktree_path.name

    # Find or validate source repo
    if source:
        source_path = source.resolve()
    else:
        source_path = find_source_repo(worktree_path)
        if not source_path:
            console.print("[bold red]Error:[/] Could not find source repository")
            console.print("Use --source to specify manually")
            return 1

    # Calculate port offset
    port_offset = offset if offset is not None else calculate_port_offset(worktree_name)

    config: WorktreeConfig = {
        "worktree_path": worktree_path,
        "source_path": source_path,
        "worktree_name": worktree_name,
        "port_offset": port_offset,
    }

    # Display configuration
    console.print(
        Panel(
            f"[bold]Worktree:[/] {worktree_path}\n"
            f"[bold]Source:[/] {source_path}\n"
            f"[bold]Port Offset:[/] {port_offset}",
            title="Worktree Setup",
            border_style="blue",
        )
    )

    if dry_run:
        console.print("\n[yellow]DRY RUN - no changes will be made[/]\n")

    all_ports: dict[str, int] = {}
    files_copied: list[str] = []
    files_skipped: list[str] = []

    # Copy environment files
    console.print("\n[bold]Environment Files[/]")
    for pattern in ENV_FILE_PATTERNS:
        source_file = source_path / pattern
        if source_file.exists():
            dest_file = worktree_path / pattern
            if dest_file.exists() and not force:
                files_skipped.append(pattern)
                console.print(f"  [yellow]Skipped:[/] {pattern} (exists, use --force)")
                continue
            ports = copy_env_file(source_file, dest_file, config, dry_run=dry_run)
            all_ports.update(ports)
            files_copied.append(pattern)

    # Copy Claude settings
    console.print("\n[bold]Claude Settings[/]")
    for pattern in CLAUDE_FILES:
        source_file = source_path / pattern
        if source_file.exists():
            dest_file = worktree_path / pattern
            if dest_file.exists() and not force:
                files_skipped.append(pattern)
                console.print(f"  [yellow]Skipped:[/] {pattern} (exists, use --force)")
                continue
            copy_claude_settings(source_file, dest_file, config, dry_run=dry_run)
            files_copied.append(pattern)
        else:
            console.print(f"  [dim]Not found:[/] {pattern}")

    # Copy IDE configs
    console.print("\n[bold]IDE Configuration[/]")
    for dirname in IDE_CONFIGS:
        source_dir = source_path / dirname
        if source_dir.exists() and source_dir.is_dir():
            dest_dir = worktree_path / dirname
            if dest_dir.exists() and not force:
                files_skipped.append(dirname)
                console.print(f"  [yellow]Skipped:[/] {dirname}/ (exists, use --force)")
                continue
            copy_ide_config(source_dir, dest_dir, dry_run=dry_run)
            files_copied.append(dirname)
        else:
            console.print(f"  [dim]Not found:[/] {dirname}/")

    # Copy MCP config
    console.print("\n[bold]MCP Configuration[/]")
    mcp_source = source_path / MCP_CONFIG
    if mcp_source.exists():
        mcp_dest = worktree_path / MCP_CONFIG
        if mcp_dest.exists() and not force:
            files_skipped.append(MCP_CONFIG)
            console.print(f"  [yellow]Skipped:[/] {MCP_CONFIG} (exists, use --force)")
        else:
            copy_mcp_config(mcp_source, mcp_dest, config, dry_run=dry_run)
            files_copied.append(MCP_CONFIG)
    else:
        console.print(f"  [dim]Not found:[/] {MCP_CONFIG}")

    # Summary
    console.print()
    if all_ports:
        table = Table(title="Port Assignments")
        table.add_column("Service", style="cyan")
        table.add_column("Port", style="green")
        for service, port in sorted(all_ports.items()):
            table.add_row(service, str(port))
        console.print(table)

    # Validation (only in non-dry-run mode)
    if not dry_run:
        console.print("\n[bold]Validation[/]")
        issues = validate_setup(config)
        if issues:
            for issue in issues:
                console.print(f"  [red]Issue:[/] {issue}")
        else:
            console.print("  [green]All checks passed[/]")

    # Final summary
    status = "[yellow]DRY RUN COMPLETE[/]" if dry_run else "[bold green]SETUP COMPLETE[/]"
    console.print(f"\n{status}")
    console.print(f"  Files copied: {len(files_copied)}")
    if files_skipped:
        console.print(f"  Files skipped: {len(files_skipped)} (use --force to overwrite)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
