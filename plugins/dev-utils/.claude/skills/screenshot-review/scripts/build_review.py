#!/usr/bin/env python3
"""Build the screenshot review HTML from a JSON data file + template.

Usage:
    python build_review.py <data.json> [--output <output.html>] [--serve [PORT]]

The script:
1. Validates data.json against the schema (using uvx check-jsonschema)
2. Reads the HTML template
3. Injects the JSON data into the template
4. Writes the output HTML
5. Optionally serves it locally
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = SKILL_DIR / "assets" / "screenshot-data.schema.json"
TEMPLATE_PATH = SKILL_DIR / "assets" / "template.html"


def validate_json(data_path: Path) -> bool:
    """Validate JSON against schema using uvx check-jsonschema."""
    try:
        result = subprocess.run(
            [
                "uvx",
                "check-jsonschema",
                "--schemafile",
                str(SCHEMA_PATH),
                str(data_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Schema validation failed:\n{result.stderr}", file=sys.stderr)
            return False
        print("Schema validation passed.")
        return True
    except FileNotFoundError:
        print(
            "Warning: uvx not found, skipping schema validation.", file=sys.stderr
        )
        return True


def build_html(data_path: Path, output_path: Path) -> None:
    """Inject JSON data into template and write output."""
    data = json.loads(data_path.read_text())
    template = TEMPLATE_PATH.read_text()

    # Replace the placeholder with actual data
    html = template.replace("__SCREENSHOT_DATA__", json.dumps(data, indent=2))
    output_path.write_text(html)
    print(f"Wrote {output_path} ({len(data.get('screenshots', []))} screenshots)")


def serve(html_path: Path, port: int) -> None:
    """Serve the HTML file directory locally."""
    import webbrowser

    directory = html_path.parent
    filename = html_path.name
    url = f"http://localhost:{port}/{filename}"

    print(f"Serving at {url}")
    webbrowser.open(url)

    import http.server
    import os

    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer(("0.0.0.0", port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build screenshot review HTML")
    parser.add_argument("data", type=Path, help="Path to screenshot-data.json")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output HTML path (default: same dir as data.json)",
    )
    parser.add_argument(
        "--serve",
        nargs="?",
        const=8789,
        type=int,
        metavar="PORT",
        help="Serve the HTML after building (default port: 8789)",
    )
    args = parser.parse_args()

    if not args.data.exists():
        print(f"Error: {args.data} not found", file=sys.stderr)
        sys.exit(1)

    # Validate
    if not validate_json(args.data):
        sys.exit(1)

    # Build
    output = args.output or args.data.parent / "screenshot-review.html"
    build_html(args.data, output)

    # Serve
    if args.serve is not None:
        serve(output, args.serve)


if __name__ == "__main__":
    main()
