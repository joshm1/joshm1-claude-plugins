#!/usr/bin/env python3
"""
Merge and analyze Claude Code permissions from .claude/settings*.json files.

Scans a directory tree for Claude Code settings files, extracts permissions,
and compares them against your user-level settings to identify candidates
for global configuration.

Usage:
    # Scan ~/projects and compare with user settings
    python merge_claude_permissions.py

    # Scan a specific directory
    python merge_claude_permissions.py --search-dir /path/to/projects

    # Use a different user settings file
    python merge_claude_permissions.py --user-settings ~/.claude/settings.json

    # Output only the new permissions as JSON
    python merge_claude_permissions.py --json-only
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import TypedDict


class Permissions(TypedDict):
    allow: list[str]
    deny: list[str]
    ask: list[str]


def find_claude_settings(search_dir: Path) -> list[Path]:
    """Find all .claude/settings*.json files in the search directory."""
    # Try using fd for speed, fall back to pure Python
    if shutil.which("fd"):
        result = subprocess.run(
            [
                "fd",
                "-H",
                "-t",
                "f",
                r"settings\.json$|settings\.local\.json$",
                str(search_dir),
            ],
            capture_output=True,
            text=True,
        )
        paths = []
        for line in result.stdout.strip().split("\n"):
            if line and ".claude/" in line and not line.endswith(".jinja"):
                paths.append(Path(line))
        return paths

    # Fallback: pure Python search
    paths = []
    for settings_file in search_dir.rglob(".claude/settings*.json"):
        if settings_file.suffix == ".json" and not settings_file.name.endswith(
            ".jinja"
        ):
            paths.append(settings_file)
    return paths


def extract_permissions(path: Path) -> Permissions:
    """Extract allow/deny/ask permissions from a settings file."""
    try:
        with open(path) as f:
            data = json.load(f)
        perms = data.get("permissions", {})
        return {
            "allow": perms.get("allow", []),
            "deny": perms.get("deny", []),
            "ask": perms.get("ask", []),
        }
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        print(f"Warning: Could not read {path}: {e}", file=sys.stderr)
        return {"allow": [], "deny": [], "ask": []}


def categorize_permission(perm: str) -> str:
    """Categorize a permission for display grouping."""
    if perm.startswith("Bash("):
        return "Bash Commands"
    elif perm.startswith("mcp__"):
        return "MCP Tools"
    elif perm.startswith("Skill("):
        return "Skills"
    elif perm.startswith("WebFetch") or perm == "WebSearch":
        return "Web Access"
    elif perm.startswith("Read("):
        return "File Read"
    else:
        return "Other"


def print_section(title: str, width: int = 80) -> None:
    """Print a section header."""
    print()
    print("=" * width)
    print(title)
    print("=" * width)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge and analyze Claude Code permissions across projects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--search-dir",
        type=Path,
        default=Path.home() / "projects",
        help="Directory to search for .claude settings files (default: ~/projects)",
    )
    parser.add_argument(
        "--user-settings",
        type=Path,
        default=Path.home() / ".claude" / "settings.json",
        help="Path to user-level settings file (default: ~/.claude/settings.json)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output only the new permissions as JSON array",
    )
    args = parser.parse_args()

    # Validate paths
    if not args.search_dir.exists():
        print(f"Error: Search directory does not exist: {args.search_dir}", file=sys.stderr)
        return 1

    # Find all settings files
    settings_files = find_claude_settings(args.search_dir)

    if not settings_files:
        print(f"No .claude settings files found in {args.search_dir}", file=sys.stderr)
        return 1

    # Track permissions and their sources
    permission_sources: dict[str, list[str]] = defaultdict(list)
    all_allow: set[str] = set()
    all_deny: set[str] = set()
    all_ask: set[str] = set()

    for path in settings_files:
        perms = extract_permissions(path)
        # Create a relative path for display
        try:
            rel_path = str(path.relative_to(args.search_dir))
        except ValueError:
            rel_path = str(path)

        for p in perms["allow"]:
            all_allow.add(p)
            permission_sources[p].append(rel_path)
        for p in perms["deny"]:
            all_deny.add(p)
        for p in perms["ask"]:
            all_ask.add(p)

    # Load user settings for comparison
    user_allow: set[str] = set()
    if args.user_settings.exists():
        user_perms = extract_permissions(args.user_settings)
        user_allow = set(user_perms["allow"])

    # Calculate new permissions
    new_perms = sorted(all_allow - user_allow)

    # JSON-only output mode
    if args.json_only:
        print(json.dumps(new_perms, indent=2))
        return 0

    # Full report
    print(f"Found {len(settings_files)} .claude settings files in {args.search_dir}:\n")
    for f in sorted(settings_files):
        try:
            rel = f.relative_to(args.search_dir)
        except ValueError:
            rel = f
        print(f"  • {rel}")

    print_section("ALL ALLOWED PERMISSIONS (sorted)")

    # Group by category for better readability
    by_category: dict[str, list[str]] = defaultdict(list)
    for perm in sorted(all_allow):
        by_category[categorize_permission(perm)].append(perm)

    for category in sorted(by_category.keys()):
        print(f"\n  {category}:")
        for perm in by_category[category]:
            in_user = "✓" if perm in user_allow else " "
            sources = ", ".join(permission_sources[perm])
            print(f"    [{in_user}] {perm}")
            print(f"         └─ {sources}")

    print_section("NEW PERMISSIONS (not in user settings)")

    if new_perms:
        for perm in new_perms:
            sources = ", ".join(permission_sources[perm])
            print(f"  {perm}")
            print(f"     └─ {sources}")
    else:
        print("  (none - all permissions already in user settings)")

    print_section("SUMMARY")
    print(f"  Total unique permissions across projects: {len(all_allow)}")
    print(f"  Already in user settings: {len(all_allow & user_allow)}")
    print(f"  New (not in user settings): {len(new_perms)}")

    if all_deny:
        print(f"\n  Deny rules found: {sorted(all_deny)}")
    if all_ask:
        print(f"\n  Ask rules found: {sorted(all_ask)}")

    print_section("NEW PERMISSIONS AS JSON")
    print(json.dumps(new_perms, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
