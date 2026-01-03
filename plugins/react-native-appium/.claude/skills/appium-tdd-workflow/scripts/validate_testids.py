#!/usr/bin/env python3
"""
Validate testID usage in React Native codebase.

Checks for:
- Missing testIDs on interactive elements
- Naming convention compliance
- Duplicate testIDs
- Coverage metrics
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


@dataclass
class Result:
    """Standard result container."""
    success: bool
    message: str
    data: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


@dataclass
class TestIdInfo:
    """Information about a testID."""
    value: str
    file: str
    line: int
    element_type: str


@dataclass
class MissingTestId:
    """Information about a missing testID."""
    file: str
    line: int
    element_type: str
    suggested_id: str


# Patterns for finding interactive elements
INTERACTIVE_PATTERNS = [
    (r'<TouchableOpacity[^>]*>', 'TouchableOpacity'),
    (r'<TouchableHighlight[^>]*>', 'TouchableHighlight'),
    (r'<TouchableWithoutFeedback[^>]*>', 'TouchableWithoutFeedback'),
    (r'<Pressable[^>]*>', 'Pressable'),
    (r'<Button[^>]*>', 'Button'),
    (r'<TextInput[^>]*>', 'TextInput'),
    (r'<Switch[^>]*>', 'Switch'),
    (r'<Slider[^>]*>', 'Slider'),
]

# Pattern for extracting testID
TESTID_PATTERN = re.compile(r'testID=["\']([^"\']+)["\']')

# Valid naming convention: lowercase with hyphens
NAMING_CONVENTION = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')


def find_files(root_path: Path, extensions: tuple = ('.tsx', '.jsx')) -> list[Path]:
    """Find all React Native source files."""
    files = []
    for ext in extensions:
        files.extend(root_path.rglob(f'*{ext}'))
    return [f for f in files if 'node_modules' not in str(f)]


def extract_testids(content: str, file_path: str) -> list[TestIdInfo]:
    """Extract all testIDs from file content."""
    testids = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        matches = TESTID_PATTERN.findall(line)
        for match in matches:
            # Try to determine element type
            element_type = 'Unknown'
            for pattern, etype in INTERACTIVE_PATTERNS:
                if re.search(pattern, line):
                    element_type = etype
                    break

            testids.append(TestIdInfo(
                value=match,
                file=file_path,
                line=i,
                element_type=element_type
            ))

    return testids


def find_missing_testids(content: str, file_path: str) -> list[MissingTestId]:
    """Find interactive elements without testIDs."""
    missing = []
    lines = content.split('\n')

    # Track multi-line elements
    in_element = False
    element_start_line = 0
    element_type = ''
    element_content = ''

    for i, line in enumerate(lines, 1):
        # Check for interactive element start
        for pattern, etype in INTERACTIVE_PATTERNS:
            if re.search(pattern, line):
                # Check if element has testID on same line or within next few lines
                # Simple check: look ahead 5 lines
                context = '\n'.join(lines[i-1:min(i+4, len(lines))])
                if 'testID=' not in context:
                    # Generate suggested ID
                    screen_name = extract_screen_name(file_path)
                    suggested = f"{screen_name}-{etype.lower()}"

                    missing.append(MissingTestId(
                        file=file_path,
                        line=i,
                        element_type=etype,
                        suggested_id=suggested
                    ))
                break

    return missing


def extract_screen_name(file_path: str) -> str:
    """Extract screen name from file path."""
    name = Path(file_path).stem
    # Remove common suffixes
    for suffix in ['Screen', 'Component', 'View']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    # Convert to kebab-case
    name = re.sub(r'([A-Z])', r'-\1', name).lower().strip('-')
    return name or 'component'


def validate_naming(testids: list[TestIdInfo]) -> list[tuple[TestIdInfo, str]]:
    """Validate testID naming convention."""
    issues = []
    for testid in testids:
        if not NAMING_CONVENTION.match(testid.value):
            suggestion = testid.value.lower()
            # Convert camelCase to kebab-case
            suggestion = re.sub(r'([A-Z])', r'-\1', suggestion).lower()
            suggestion = re.sub(r'_', '-', suggestion)
            suggestion = re.sub(r'-+', '-', suggestion).strip('-')
            issues.append((testid, suggestion))
    return issues


def find_duplicates(testids: list[TestIdInfo]) -> dict[str, list[TestIdInfo]]:
    """Find duplicate testID values."""
    by_value = defaultdict(list)
    for testid in testids:
        by_value[testid.value].append(testid)

    return {k: v for k, v in by_value.items() if len(v) > 1}


def analyze_codebase(root_path: Path) -> Result:
    """Analyze React Native codebase for testID issues."""
    files = find_files(root_path)

    if not files:
        return Result(
            success=False,
            message=f"No React Native files found in {root_path}",
            errors=["No .tsx or .jsx files found"]
        )

    all_testids = []
    all_missing = []
    files_analyzed = 0

    for file_path in files:
        try:
            content = file_path.read_text(encoding='utf-8')
            file_str = str(file_path)

            testids = extract_testids(content, file_str)
            all_testids.extend(testids)

            missing = find_missing_testids(content, file_str)
            all_missing.extend(missing)

            files_analyzed += 1
        except Exception as e:
            # Skip files that can't be read
            continue

    # Validate naming
    naming_issues = validate_naming(all_testids)

    # Find duplicates
    duplicates = find_duplicates(all_testids)

    # Calculate coverage
    total_interactive = len(all_missing) + len(all_testids)
    coverage = (len(all_testids) / total_interactive * 100) if total_interactive > 0 else 100

    # Build result
    errors = []
    warnings = []

    if duplicates:
        for value, locations in duplicates.items():
            errors.append(f"Duplicate testID '{value}' in {len(locations)} locations")

    if all_missing:
        for m in all_missing[:10]:  # Limit to 10
            warnings.append(f"Missing testID: {m.file}:{m.line} ({m.element_type})")
        if len(all_missing) > 10:
            warnings.append(f"... and {len(all_missing) - 10} more")

    if naming_issues:
        for testid, suggestion in naming_issues[:10]:
            warnings.append(f"Naming issue: '{testid.value}' should be '{suggestion}'")

    success = len(errors) == 0 and coverage >= 80

    return Result(
        success=success,
        message=f"Analyzed {files_analyzed} files. Coverage: {coverage:.1f}%",
        data={
            'files_analyzed': files_analyzed,
            'total_testids': len(all_testids),
            'missing_testids': len(all_missing),
            'coverage_percent': round(coverage, 1),
            'duplicates_count': len(duplicates),
            'naming_issues_count': len(naming_issues),
            'testids': [{'value': t.value, 'file': t.file, 'line': t.line} for t in all_testids],
            'missing': [{'file': m.file, 'line': m.line, 'type': m.element_type, 'suggested': m.suggested_id} for m in all_missing],
        },
        errors=errors,
        warnings=warnings
    )


def generate_report(result: Result) -> str:
    """Generate markdown report from result."""
    lines = ["# testID Validation Report", ""]

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Files Analyzed**: {result.data.get('files_analyzed', 0)}")
    lines.append(f"- **Total testIDs**: {result.data.get('total_testids', 0)}")
    lines.append(f"- **Missing testIDs**: {result.data.get('missing_testids', 0)}")
    lines.append(f"- **Coverage**: {result.data.get('coverage_percent', 0)}%")
    lines.append(f"- **Duplicates**: {result.data.get('duplicates_count', 0)}")
    lines.append(f"- **Naming Issues**: {result.data.get('naming_issues_count', 0)}")
    lines.append("")

    # Status
    status = "PASS" if result.success else "FAIL"
    lines.append(f"## Status: {status}")
    lines.append("")

    # Errors
    if result.errors:
        lines.append("## Errors (Must Fix)")
        lines.append("")
        for error in result.errors:
            lines.append(f"- {error}")
        lines.append("")

    # Warnings
    if result.warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in result.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    # Missing testIDs detail
    missing = result.data.get('missing', [])
    if missing:
        lines.append("## Missing testIDs")
        lines.append("")
        lines.append("| File | Line | Element | Suggested testID |")
        lines.append("|------|------|---------|------------------|")
        for m in missing[:20]:
            lines.append(f"| {m['file']} | {m['line']} | {m['type']} | `{m['suggested']}` |")
        if len(missing) > 20:
            lines.append(f"| ... | ... | ... | ({len(missing) - 20} more) |")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Validate testID usage in React Native codebase'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to scan (default: current directory)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON instead of markdown'
    )
    parser.add_argument(
        '--min-coverage',
        type=float,
        default=80.0,
        help='Minimum coverage percentage to pass (default: 80)'
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}", file=sys.stderr)
        sys.exit(1)

    result = analyze_codebase(root_path)

    # Override success based on min coverage
    if result.data.get('coverage_percent', 0) < args.min_coverage:
        result.success = False

    if args.json:
        output = {
            'success': result.success,
            'message': result.message,
            'data': result.data,
            'errors': result.errors,
            'warnings': result.warnings
        }
        print(json.dumps(output, indent=2))
    else:
        print(generate_report(result))

    sys.exit(0 if result.success else 1)


if __name__ == '__main__':
    main()
