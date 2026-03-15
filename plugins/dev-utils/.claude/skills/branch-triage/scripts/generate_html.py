#!/usr/bin/env python3
"""Generate a branch triage HTML dashboard from a JSON data file.

Reads branch data JSON and injects it into the template.html to produce
a self-contained HTML file with embedded data. No external dependencies.

Usage:
    python3 generate_html.py branch_data.json                    # writes branch_triage.html
    python3 generate_html.py branch_data.json -o output.html     # custom output path
    python3 generate_html.py branch_data.json --template /path/to/template.html
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = SCRIPT_DIR.parent / "template.html"
SENTINEL = "const EMBEDDED_DATA = null;"


def generate(data_path: str, template_path: str, output_path: str) -> None:
    # Read the JSON data
    data_file = Path(data_path)
    if not data_file.exists():
        print(f"Error: data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    with open(data_file) as f:
        data = json.load(f)

    # Validate structure
    if isinstance(data, list):
        data = {"repo": "", "branches": data}
    elif not isinstance(data, dict) or "branches" not in data:
        print("Error: JSON must be an array of branches or an object with a 'branches' array.", file=sys.stderr)
        sys.exit(1)

    if not data["branches"]:
        print("Error: branches array is empty.", file=sys.stderr)
        sys.exit(1)

    # Read the template
    tmpl = Path(template_path)
    if not tmpl.exists():
        print(f"Error: template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    html = tmpl.read_text()

    # Inject the data by replacing the sentinel
    if SENTINEL not in html:
        print(f"Error: template is missing the sentinel line: {SENTINEL!r}", file=sys.stderr)
        print("Make sure the template has this exact line in its <script> section.", file=sys.stderr)
        sys.exit(1)

    data_json = json.dumps(data, indent=2)
    replacement = f"const EMBEDDED_DATA = {data_json};"
    html = html.replace(SENTINEL, replacement, 1)

    # Update the page title if we have a repo name
    if data.get("repo"):
        html = html.replace("<title>Branch Triage</title>", f"<title>Branch Triage — {data['repo']}</title>")

    # Write the output
    out = Path(output_path)
    out.write_text(html)
    print(f"✅ Generated {out} ({len(data['branches'])} branches)", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate branch triage HTML from JSON data"
    )
    parser.add_argument("data", help="Path to branch data JSON file")
    parser.add_argument(
        "-o", "--output",
        default="branch_triage.html",
        help="Output HTML file path (default: branch_triage.html)",
    )
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help=f"Path to template.html (default: {DEFAULT_TEMPLATE})",
    )
    args = parser.parse_args()
    generate(args.data, args.template, args.output)


if __name__ == "__main__":
    main()
