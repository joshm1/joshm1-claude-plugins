#!/usr/bin/env python3
"""
Generate index of all E2E documented flows.

Creates an index.md file in docs/user-flows/ that catalogs all documented
flows with metadata, status, and quick navigation links.

Exit codes:
  0 - Index generated successfully
  1 - General error
  10 - No flows found to index
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class FlowMetadata:
    """Metadata extracted from a flow documentation file."""

    name: str
    path: Path
    title: Optional[str] = None
    status: Optional[str] = None
    last_verified: Optional[str] = None
    url: Optional[str] = None
    steps_count: int = 0
    issues_count: int = 0
    screenshot_count: int = 0
    size_bytes: int = 0


@dataclass
class IndexResult:
    """Result of index generation."""

    success: bool
    index_path: Optional[Path] = None
    flows_indexed: int = 0
    errors: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "index_path": str(self.index_path) if self.index_path else None,
            "flows_indexed": self.flows_indexed,
            "errors": self.errors,
        }


def extract_metadata(doc_path: Path, screenshots_dir: Optional[Path]) -> FlowMetadata:
    """Extract metadata from a flow documentation file."""
    meta = FlowMetadata(name=doc_path.stem, path=doc_path)

    try:
        content = doc_path.read_text(encoding="utf-8")
        meta.size_bytes = len(content.encode("utf-8"))
    except Exception:
        return meta

    # Extract title (first H1)
    title_match = re.search(r"^#\s+(.+?)(?:\s*[-–]\s*.+)?$", content, re.MULTILINE)
    if title_match:
        meta.title = title_match.group(1).strip()

    # Extract status from overview table
    status_match = re.search(
        r"\*\*Status\*\*\s*\|\s*(.+?)(?:\s*\||\s*$)", content, re.MULTILINE
    )
    if status_match:
        meta.status = status_match.group(1).strip()

    # Extract last verified date
    date_match = re.search(
        r"\*\*Last Verified\*\*\s*\|\s*(.+?)(?:\s*\||\s*$)", content, re.MULTILINE
    )
    if date_match:
        meta.last_verified = date_match.group(1).strip()

    # Extract URL
    url_match = re.search(
        r"\*\*URL\*\*\s*\|\s*(.+?)(?:\s*\||\s*$)", content, re.MULTILINE
    )
    if url_match:
        meta.url = url_match.group(1).strip()

    # Count steps (H3 headings under User Flow that start with "Step")
    meta.steps_count = len(re.findall(r"^###\s+Step\s+\d+", content, re.MULTILINE))
    if meta.steps_count == 0:
        # Alternative: count all H3 headings
        meta.steps_count = len(re.findall(r"^###\s+", content, re.MULTILINE))

    # Count issues
    issues_section = re.search(
        r"##\s+Issues Found.*?(?=^##|\Z)", content, re.MULTILINE | re.DOTALL
    )
    if issues_section:
        meta.issues_count = len(
            re.findall(r"^###\s+Issue\s+\d+", issues_section.group(0), re.MULTILINE)
        )

    # Count screenshots
    if screenshots_dir and screenshots_dir.exists():
        screenshots = list(screenshots_dir.glob("*.png")) + list(
            screenshots_dir.glob("*.jpg")
        )
        meta.screenshot_count = len(screenshots)

    return meta


def generate_index_content(flows: list[FlowMetadata], base_path: Path) -> str:
    """Generate markdown content for the index file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# E2E Documentation Index",
        "",
        "> Catalog of all documented user flows and QA reports.",
        "",
        "## Overview",
        "",
        f"| Property | Value |",
        f"|----------|-------|",
        f"| **Total Flows** | {len(flows)} |",
        f"| **Last Updated** | {now} |",
        "",
        "## Documented Flows",
        "",
        "| Flow | Status | Steps | Issues | Last Verified |",
        "|------|--------|-------|--------|---------------|",
    ]

    for flow in sorted(flows, key=lambda f: f.name):
        title = flow.title or flow.name.replace("-", " ").title()
        status = flow.status or "Unknown"
        steps = str(flow.steps_count) if flow.steps_count > 0 else "-"
        issues = str(flow.issues_count) if flow.issues_count > 0 else "-"
        last_verified = flow.last_verified or "-"

        # Status emoji
        if "working" in status.lower() or "pass" in status.lower():
            status_icon = "working"
        elif "issue" in status.lower() or "fail" in status.lower():
            status_icon = "has issues"
        else:
            status_icon = status

        lines.append(
            f"| [{title}](./{flow.name}.md) | {status_icon} | {steps} | {issues} | {last_verified} |"
        )

    lines.extend(
        [
            "",
            "## Quick Stats",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Steps Documented | {sum(f.steps_count for f in flows)} |",
            f"| Total Issues Recorded | {sum(f.issues_count for f in flows)} |",
            f"| Total Screenshots | {sum(f.screenshot_count for f in flows)} |",
            "",
            "---",
            "",
            f"*Index generated on {now}*",
        ]
    )

    return "\n".join(lines)


def generate_index(base_path: Path, dry_run: bool = False) -> IndexResult:
    """Generate the index file for all documented flows."""
    result = IndexResult(success=True)
    user_flows_dir = base_path / "docs" / "user-flows"

    if not user_flows_dir.exists():
        result.add_error(f"User flows directory not found: {user_flows_dir}")
        result.success = False
        return result

    # Find all flow documentation files
    flows: list[FlowMetadata] = []
    for md_file in user_flows_dir.glob("*.md"):
        if md_file.name == "index.md":
            continue

        flow_name = md_file.stem
        screenshots_dir = user_flows_dir / "screenshots" / flow_name

        meta = extract_metadata(
            md_file, screenshots_dir if screenshots_dir.exists() else None
        )
        flows.append(meta)

    if not flows:
        result.add_error("No documented flows found")
        result.success = False
        return result

    result.flows_indexed = len(flows)

    # Generate index content
    content = generate_index_content(flows, base_path)

    # Write or display
    index_path = user_flows_dir / "index.md"
    result.index_path = index_path

    if dry_run:
        print(content)
    else:
        try:
            index_path.write_text(content, encoding="utf-8")
        except Exception as e:
            result.add_error(f"Failed to write index: {e}")
            result.success = False

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate index of E2E documented flows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --base-path /path/to/project
  %(prog)s --dry-run
  %(prog)s --json
        """,
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path.cwd(),
        help="Base path for documentation (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print index content without writing file",
    )
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    result = generate_index(args.base_path, dry_run=args.dry_run)

    if args.json:
        import json

        print(json.dumps(result.to_dict(), indent=2))
    elif not args.dry_run:
        if result.success:
            print(f"Index generated: {result.index_path}")
            print(f"Flows indexed: {result.flows_indexed}")
        else:
            print("Index generation failed:")
            for err in result.errors:
                print(f"  - {err}")

    if not result.success:
        return 10 if result.flows_indexed == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
