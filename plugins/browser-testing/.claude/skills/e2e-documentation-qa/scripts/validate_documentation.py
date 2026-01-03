#!/usr/bin/env python3
"""
Validate E2E documentation output.

Verifies that generated documentation meets quality standards:
- Markdown file exists and is non-empty
- All referenced screenshots exist
- Required sections are present
- No broken image links

Exit codes:
  0 - All validations passed
  1 - General error
  10 - Validation failed (documentation issues found)
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    """Result of documentation validation."""

    success: bool
    flow_name: str
    doc_path: Optional[Path] = None
    screenshots_dir: Optional[Path] = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.success = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "flow_name": self.flow_name,
            "doc_path": str(self.doc_path) if self.doc_path else None,
            "screenshots_dir": str(self.screenshots_dir) if self.screenshots_dir else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
        }


def find_documentation(base_path: Path, flow_name: str) -> tuple[Optional[Path], Optional[Path]]:
    """Find documentation file and screenshots directory for a flow."""
    doc_path = base_path / "docs" / "user-flows" / f"{flow_name}.md"
    screenshots_dir = base_path / "docs" / "user-flows" / "screenshots" / flow_name

    return (
        doc_path if doc_path.exists() else None,
        screenshots_dir if screenshots_dir.exists() else None,
    )


def extract_image_references(content: str) -> list[str]:
    """Extract all image references from markdown content."""
    # Match both ![alt](path) and <img src="path"> patterns
    md_pattern = r"!\[.*?\]\(([^)]+)\)"
    html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'

    refs = re.findall(md_pattern, content)
    refs.extend(re.findall(html_pattern, content))

    return refs


def validate_image_references(
    doc_path: Path, content: str, screenshots_dir: Optional[Path]
) -> tuple[list[str], list[str]]:
    """Validate that all image references resolve to existing files."""
    errors = []
    warnings = []

    refs = extract_image_references(content)

    for ref in refs:
        # Handle relative paths
        if ref.startswith("./"):
            img_path = doc_path.parent / ref[2:]
        elif ref.startswith("../"):
            img_path = doc_path.parent / ref
        elif ref.startswith("/"):
            # Absolute path from project root - skip validation
            warnings.append(f"Absolute image path (cannot validate): {ref}")
            continue
        elif ref.startswith("http://") or ref.startswith("https://"):
            # External URL - skip validation
            continue
        else:
            img_path = doc_path.parent / ref

        if not img_path.exists():
            errors.append(f"Missing image: {ref}")

    return errors, warnings


def check_required_sections(content: str) -> list[str]:
    """Check that required sections are present in the documentation."""
    required = [
        (r"^#\s+.+", "Title (H1 heading)"),
        (r"^##\s+Overview", "Overview section"),
        (r"^##\s+(User Flow|Steps|Flow)", "User Flow/Steps section"),
        (r"^##\s+Summary", "Summary section"),
    ]

    missing = []
    for pattern, name in required:
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            missing.append(f"Missing required section: {name}")

    return missing


def validate_flow(base_path: Path, flow_name: str) -> ValidationResult:
    """Validate documentation for a specific flow."""
    result = ValidationResult(success=True, flow_name=flow_name)

    # Find documentation
    doc_path, screenshots_dir = find_documentation(base_path, flow_name)
    result.doc_path = doc_path
    result.screenshots_dir = screenshots_dir

    if not doc_path:
        result.add_error(f"Documentation file not found: docs/user-flows/{flow_name}.md")
        return result

    # Read content
    try:
        content = doc_path.read_text(encoding="utf-8")
    except Exception as e:
        result.add_error(f"Failed to read documentation: {e}")
        return result

    if not content.strip():
        result.add_error("Documentation file is empty")
        return result

    # Validate structure
    section_errors = check_required_sections(content)
    for err in section_errors:
        result.add_warning(err)  # Warnings, not errors - structure can vary

    # Validate images
    img_errors, img_warnings = validate_image_references(doc_path, content, screenshots_dir)
    for err in img_errors:
        result.add_error(err)
    for warn in img_warnings:
        result.add_warning(warn)

    # Collect stats
    result.stats = {
        "doc_size_bytes": len(content.encode("utf-8")),
        "line_count": len(content.splitlines()),
        "image_references": len(extract_image_references(content)),
        "h2_sections": len(re.findall(r"^##\s+", content, re.MULTILINE)),
        "h3_sections": len(re.findall(r"^###\s+", content, re.MULTILINE)),
    }

    # Check screenshot count
    if screenshots_dir and screenshots_dir.exists():
        screenshots = list(screenshots_dir.glob("*.png")) + list(screenshots_dir.glob("*.jpg"))
        result.stats["screenshot_files"] = len(screenshots)

        if len(screenshots) == 0:
            result.add_warning("Screenshots directory exists but contains no images")
    else:
        result.stats["screenshot_files"] = 0
        if result.stats["image_references"] > 0:
            result.add_warning("Image references found but no screenshots directory")

    return result


def validate_all_flows(base_path: Path) -> list[ValidationResult]:
    """Validate all documented flows in the base path."""
    results = []
    user_flows_dir = base_path / "docs" / "user-flows"

    if not user_flows_dir.exists():
        return results

    for md_file in user_flows_dir.glob("*.md"):
        if md_file.name == "index.md":
            continue
        flow_name = md_file.stem
        results.append(validate_flow(base_path, flow_name))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate E2E documentation output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s login-flow
  %(prog)s checkout-process --base-path /path/to/project
  %(prog)s --all
  %(prog)s --all --json
        """,
    )
    parser.add_argument("flow_name", nargs="?", help="Name of the flow to validate")
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path.cwd(),
        help="Base path for documentation (default: current directory)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Validate all documented flows"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )

    args = parser.parse_args()

    if args.all:
        results = validate_all_flows(args.base_path)
        if not results:
            print("No documented flows found in docs/user-flows/")
            return 1
    elif args.flow_name:
        results = [validate_flow(args.base_path, args.flow_name)]
    else:
        parser.error("Either flow_name or --all is required")

    # Output results
    if args.json:
        import json

        output = {
            "results": [r.to_dict() for r in results],
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.success),
                "failed": sum(1 for r in results if not r.success),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        all_passed = True
        for result in results:
            status = "PASS" if result.success else "FAIL"
            print(f"\n{'='*60}")
            print(f"Flow: {result.flow_name} [{status}]")
            print(f"{'='*60}")

            if result.doc_path:
                print(f"  Doc: {result.doc_path}")
            if result.screenshots_dir:
                print(f"  Screenshots: {result.screenshots_dir}")

            if result.stats:
                print(f"\n  Stats:")
                for key, value in result.stats.items():
                    print(f"    {key}: {value}")

            if result.errors:
                print(f"\n  Errors:")
                for err in result.errors:
                    print(f"    - {err}")
                all_passed = False

            if result.warnings:
                print(f"\n  Warnings:")
                for warn in result.warnings:
                    print(f"    - {warn}")

        print(f"\n{'='*60}")
        passed = sum(1 for r in results if r.success)
        print(f"Summary: {passed}/{len(results)} flows passed validation")

        if not all_passed:
            return 10  # Validation failed

    return 0


if __name__ == "__main__":
    sys.exit(main())
