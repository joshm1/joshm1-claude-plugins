#!/usr/bin/env python3
"""Scan for component screenshots, build an interactive review gallery.

Usage:
    python build_review.py <project-dir> [--serve [PORT]] [--cosmos-url URL]

The script:
1. Scans project for ComponentName.__screenshots__/{dark,light}/*.png dirs
2. Finds matching .fixture.tsx files and extracts display names
3. Reads .ports.json for Cosmos URL (if available)
4. Validates generated data against JSON schema
5. Injects CSS, JS, and data into HTML template
6. Writes screenshot-review.html in the project dir
7. Optionally serves it locally
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
SCHEMA_PATH = ASSETS_DIR / "screenshot-data.schema.json"
TEMPLATE_PATH = ASSETS_DIR / "template.html"
STYLES_PATH = ASSETS_DIR / "styles.css"
APP_JS_PATH = ASSETS_DIR / "app.js"

SCREENSHOT_DIR_PATTERN = re.compile(r"^(.+)\.__screenshots__$")
FIXTURE_KEY_PATTERN = re.compile(r"""^\s+['"]([^'"]+)['"]\s*:""")

# Content detection (Pillow optional)
_has_pillow = False
try:
    from PIL import Image

    _has_pillow = True
except ImportError:
    pass

SOLID_TOLERANCE = 15  # max color distance for a row to be considered "solid"


def _detect_content_aspect(img_path: Path) -> float | None:
    """Detect content bounds and return a balanced-crop aspect ratio.

    Algorithm:
    1. Find dominant background color from center of image
    2. Detect border pixels at each edge (pixels that don't match bg)
    3. Scan from top to find first non-solid row (content start → top margin)
    4. Scan from bottom to find last non-solid row (content end)
    5. Set visible bottom = content_end + top_margin (balanced padding)
    6. Return aspect ratio of the balanced visible region
    """
    if not _has_pillow:
        return None
    try:
        img = Image.open(img_path).convert("RGB")
    except Exception:
        return None

    w, h = img.size
    pixels = img.load()
    sample_step = max(1, w // 50)

    # Step 1: Dominant background color (sample center-bottom area)
    bg = _sample_bg_color(pixels, w, h)

    # Step 2: Detect border on each edge (pixels that don't match bg)
    border_top = _edge_border(pixels, bg, "top", w, h)
    border_left = _edge_border(pixels, bg, "left", w, h)
    border_right = _edge_border(pixels, bg, "right", w, h)

    x_start = border_left
    x_end = w - border_right
    y_start = border_top

    # Step 3: Find content top (first non-solid row from top, after border)
    content_top = y_start
    for y in range(y_start, h):
        if not _is_solid_row(pixels, y, x_start, x_end, sample_step):
            content_top = y
            break

    # Step 4: Find content bottom (last non-solid row from bottom)
    content_bottom = h - 1
    for y in range(h - 1, y_start, -1):
        if not _is_solid_row(pixels, y, x_start, x_end, sample_step):
            content_bottom = y
            break

    # Step 5: Balance — bottom margin = top margin
    top_margin = content_top - y_start
    visible_bottom = min(content_bottom + top_margin, h)

    visible_w = x_end - x_start
    visible_h = visible_bottom - y_start

    if visible_h <= 0 or visible_w <= 0:
        return None

    # Skip if crop is negligible (< 5% saved)
    if visible_h > h * 0.95:
        return None

    return round(visible_w / visible_h, 4)


def _sample_bg_color(pixels, w: int, h: int) -> tuple[int, int, int]:
    """Sample the dominant background color from center-bottom of the image."""
    points = [
        (w // 3, h * 3 // 4),
        (w // 2, h * 3 // 4),
        (2 * w // 3, h * 3 // 4),
        (w // 3, h // 2),
        (w // 2, h // 2),
        (2 * w // 3, h // 2),
    ]
    r_sum, g_sum, b_sum = 0, 0, 0
    for x, y in points:
        r, g, b = pixels[x, y]
        r_sum += r
        g_sum += g
        b_sum += b
    n = len(points)
    return (r_sum // n, g_sum // n, b_sum // n)


def _edge_border(
    pixels, bg: tuple[int, int, int], edge: str, w: int, h: int, max_border: int = 10
) -> int:
    """Detect how many pixels at the given edge don't match the background."""
    for depth in range(max_border):
        if edge == "top":
            pixel = pixels[w // 2, depth]
        elif edge == "left":
            pixel = pixels[depth, h // 2]
        elif edge == "right":
            pixel = pixels[w - 1 - depth, h // 2]
        else:
            pixel = pixels[w // 2, h - 1 - depth]
        if abs(pixel[0] - bg[0]) + abs(pixel[1] - bg[1]) + abs(pixel[2] - bg[2]) <= SOLID_TOLERANCE:
            return depth
    return max_border


def _is_solid_row(pixels, y: int, x_start: int, x_end: int, step: int) -> bool:
    """Check if all sampled pixels in a row are the same solid dark or light color."""
    first = pixels[x_start, y]
    brightness = first[0] + first[1] + first[2]
    if not (brightness < 40 or brightness > 720):
        return False
    for x in range(x_start + step, x_end, step):
        r, g, b = pixels[x, y]
        if abs(r - first[0]) + abs(g - first[1]) + abs(b - first[2]) > SOLID_TOLERANCE:
            return False
    return True


def find_screenshots(project_dir: Path, *, auto_crop: bool = False) -> list[dict]:
    """Scan for __screenshots__ dirs and build screenshot entries."""
    screenshots = []
    screenshot_dirs = sorted(
        d
        for d in project_dir.rglob("*.__screenshots__")
        if d.is_dir() and "node_modules" not in d.parts
    )

    if not screenshot_dirs:
        print("No __screenshots__ directories found.", file=sys.stderr)
        return []

    for ss_dir in screenshot_dirs:
        match = SCREENSHOT_DIR_PATTERN.match(ss_dir.name)
        if not match:
            continue

        component = match.group(1)
        modes = sorted(
            d.name for d in ss_dir.iterdir() if d.is_dir() and d.name in ("dark", "light")
        )
        if not modes:
            continue

        # Collect variants from the first mode dir (they should be identical)
        variant_dir = ss_dir / modes[0]
        variants = sorted(p.stem for p in variant_dir.glob("*.png"))

        # Find matching fixture file for display names
        fixture_path = ss_dir.parent / f"{component}.fixture.tsx"
        display_names = _parse_fixture_keys(fixture_path) if fixture_path.exists() else {}
        fixture_rel = (
            str(fixture_path.relative_to(project_dir)) if fixture_path.exists() else None
        )

        for variant in variants:
            entry: dict = {
                "component": component,
                "variant": variant,
                "modes": modes,
            }
            # Match variant slug to fixture display name
            display_name = display_names.get(variant)
            if display_name:
                entry["displayName"] = display_name
            if fixture_rel:
                entry["fixturePath"] = fixture_rel

            # Auto-crop: detect content bounds (requires Pillow)
            if auto_crop and _has_pillow:
                img_path = ss_dir / modes[0] / f"{variant}.png"
                aspect = _detect_content_aspect(img_path)
                if aspect:
                    entry["contentAspectRatio"] = aspect

            screenshots.append(entry)

    return screenshots


def _parse_fixture_keys(fixture_path: Path) -> dict[str, str]:
    """Extract fixture export keys and map slugified versions to display names."""
    mapping = {}
    try:
        for line in fixture_path.read_text().splitlines():
            m = FIXTURE_KEY_PATTERN.match(line)
            if m:
                display_name = m.group(1)
                slug = _slugify(display_name)
                mapping[slug] = display_name
    except OSError:
        pass
    return mapping


def _slugify(text: str) -> str:
    """Convert display name to variant slug (matching Vitest/Cosmos convention)."""
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def detect_cosmos_url(project_dir: Path) -> str | None:
    """Read .ports.json for Cosmos URL."""
    ports_file = project_dir / ".ports.json"
    if not ports_file.exists():
        return None
    try:
        ports = json.loads(ports_file.read_text())
        cosmos_port = ports.get("cosmos")
        if cosmos_port:
            return f"http://localhost:{cosmos_port}"
    except (OSError, json.JSONDecodeError):
        pass
    return None


def compute_screenshot_base_dir(
    project_dir: Path, screenshot_dirs: list[dict]
) -> str:
    """Compute screenshotBaseDir relative from HTML output to screenshot parent."""
    if not screenshot_dirs:
        return "."

    # Find the common parent of all screenshot dirs
    parents = set()
    for ss_dir in project_dir.rglob("*.__screenshots__"):
        if ss_dir.is_dir() and "node_modules" not in ss_dir.parts:
            parents.add(ss_dir.parent)

    if len(parents) == 1:
        parent = parents.pop()
        return str(parent.relative_to(project_dir))

    # Multiple parents — use the common ancestor
    common = Path(*[p for p in min(parents, key=lambda x: len(x.parts)).parts])
    for parent in parents:
        while not str(parent).startswith(str(common)):
            common = common.parent
    return str(common.relative_to(project_dir))


def _detect_border_inset(
    project_dir: Path, screenshots: list[dict]
) -> dict[str, float] | None:
    """Detect border artifact from the first screenshot, return as CSS inset percentages."""
    if not _has_pillow or not screenshots:
        return None
    s = screenshots[0]
    for ss_dir in project_dir.rglob("*.__screenshots__"):
        if ss_dir.is_dir() and ss_dir.name == f"{s['component']}.__screenshots__":
            img_path = ss_dir / s["modes"][0] / f"{s['variant']}.png"
            if not img_path.exists():
                return None
            try:
                img = Image.open(img_path).convert("RGB")
            except Exception:
                return None
            w, h = img.size
            pixels = img.load()
            step = max(1, w // 50)
            bg = _sample_bg_color(pixels, w, h)
            top = _edge_border(pixels, bg, "top", w, h)
            left = _edge_border(pixels, bg, "left", w, h)
            right = _edge_border(pixels, bg, "right", w, h)
            bottom = _edge_border(pixels, bg, "bottom", w, h)
            if top == 0 and left == 0 and right == 0 and bottom == 0:
                return None
            inset = {
                "top": round(top / h * 100, 3),
                "right": round(right / w * 100, 3),
                "bottom": round(bottom / h * 100, 3),
                "left": round(left / w * 100, 3),
            }
            print(f"Border detected: {top}px top, {right}px right, {bottom}px bottom, {left}px left")
            return inset
    return None


def scan(project_dir: Path, cosmos_url: str | None, *, auto_crop: bool = False) -> dict:
    """Scan project and return complete review data."""
    screenshots = find_screenshots(project_dir, auto_crop=auto_crop)
    if not screenshots:
        print("No screenshots found.", file=sys.stderr)
        sys.exit(1)

    base_dir = compute_screenshot_base_dir(project_dir, screenshots)
    cosmos = cosmos_url or detect_cosmos_url(project_dir)

    # Detect border from first screenshot (only with --auto-crop)
    border_inset = _detect_border_inset(project_dir, screenshots) if auto_crop else None

    data = {
        "title": f"{project_dir.name} Screenshot Review",
        "cosmosBaseUrl": cosmos,
        "screenshotBaseDir": base_dir,
        "screenshots": screenshots,
    }
    if border_inset:
        data["borderInset"] = border_inset

    cropped = sum(1 for s in screenshots if "contentAspectRatio" in s)
    print(
        f"Found {len(screenshots)} screenshots across "
        f"{len(set(s['component'] for s in screenshots))} components"
    )
    if cropped:
        print(f"Auto-crop: detected content bounds for {cropped}/{len(screenshots)} screenshots")
    elif _has_pillow:
        print("Auto-crop: no blank space detected (all screenshots use full area)")
    else:
        print("Auto-crop: install Pillow for automatic blank space cropping (pip install Pillow)")
    return data


def validate_data(data: dict, tmp_dir: Path) -> bool:
    """Validate data dict against schema using uvx check-jsonschema."""
    tmp_file = tmp_dir / ".screenshot-data-tmp.json"
    tmp_file.write_text(json.dumps(data))
    try:
        result = subprocess.run(
            ["uvx", "check-jsonschema", "--schemafile", str(SCHEMA_PATH), str(tmp_file)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Schema validation failed:\n{result.stderr}", file=sys.stderr)
            return False
        print("Schema validation passed.")
        return True
    except FileNotFoundError:
        print("Warning: uvx not found, skipping schema validation.", file=sys.stderr)
        return True
    finally:
        tmp_file.unlink(missing_ok=True)


def build_html(data: dict, output_path: Path) -> None:
    """Inject CSS, JS, and JSON data into template and write output."""
    template = TEMPLATE_PATH.read_text()
    styles = STYLES_PATH.read_text()
    app_js = APP_JS_PATH.read_text()

    app_js_with_data = app_js.replace("__SCREENSHOT_DATA__", json.dumps(data, indent=2))
    html = template.replace("__STYLES__", styles)
    html = html.replace("__APP_JS__", app_js_with_data)
    output_path.write_text(html)
    print(f"Wrote {output_path}")


def serve(html_path: Path, port: int) -> None:
    """Serve the HTML file directory locally."""
    import http.server
    import os
    import webbrowser

    directory = html_path.parent
    filename = html_path.name
    url = f"http://localhost:{port}/{filename}"

    print(f"Serving at {url}")
    webbrowser.open(url)

    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer(("0.0.0.0", port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan for component screenshots and build a review gallery"
    )
    parser.add_argument("project_dir", type=Path, help="Project root directory to scan")
    parser.add_argument(
        "--output", "-o", type=Path, default=None, help="Output HTML path (default: <project>/screenshot-review.html)"
    )
    parser.add_argument(
        "--cosmos-url", type=str, default=None, help="Cosmos base URL (auto-detected from .ports.json)"
    )
    parser.add_argument(
        "--serve", nargs="?", const=8789, type=int, metavar="PORT",
        help="Serve the HTML after building (default port: 8789)",
    )
    parser.add_argument(
        "--auto-crop", action="store_true",
        help="Auto-detect and crop blank space / border artifacts (requires Pillow)",
    )
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    if not project_dir.is_dir():
        print(f"Error: {project_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Scan
    data = scan(project_dir, args.cosmos_url, auto_crop=args.auto_crop)

    # Validate
    if not validate_data(data, project_dir):
        sys.exit(1)

    # Build
    output = args.output or project_dir / "screenshot-review.html"
    build_html(data, output)

    # Serve
    if args.serve is not None:
        serve(output, args.serve)


if __name__ == "__main__":
    main()
