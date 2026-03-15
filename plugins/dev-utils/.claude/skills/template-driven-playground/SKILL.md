---
name: template-driven-playground
description: >
  Architecture pattern for building deterministic, maintainable interactive HTML playgrounds where the
  agent outputs structured JSON (never HTML) and a build script validates and injects it into a pre-built
  Vue 3 template. Use this skill whenever building a skill or tool that produces interactive HTML output,
  refactoring an existing HTML-generating skill into a template-driven architecture, creating analysis or
  review tools that render results in the browser, or when the user mentions "template-driven",
  "JSON schema + HTML", "deterministic playground", or wants to stop agents from generating inconsistent
  HTML across runs. Also use when building any multi-persona or multi-section analysis tool where
  sub-agents can work in parallel and their outputs get merged into a single view.
---

# Template-Driven Playground

Build interactive HTML playgrounds where agents output structured JSON — never HTML — and a build pipeline validates and renders it deterministically.

## Why this exists

When agents generate full HTML directly, every run produces slightly different markup. CSS class names drift, JS patterns change, styling regresses. Over multiple iterations this becomes unmanageable — you fix a bug in one run and it reappears in the next because the agent regenerated everything from scratch.

The template-driven pattern eliminates this entirely: the HTML template is written once and improved over time, while agents focus purely on analysis quality. Same data in = same HTML out, every time.

## Architecture

```
Agent(s) analyze input → output JSON → build script validates → injects into HTML template → browser
```

Three files, clear separation of concerns:

| File | Who writes it | What it does |
|------|--------------|--------------|
| `schema/<name>.schema.json` | You, once | Defines the contract between agent output and template |
| `scripts/build_<name>.py` | You, once | Validates JSON + injects into template |
| `assets/template.html` | You, iterated | Pre-built Vue 3 playground that renders the data |

The agent's job is reduced to: read input, analyze it, output JSON matching the schema. Zero context spent on HTML, CSS, or JS.

## Step 1: Design the data model

Before writing any code, look at what the HTML needs to render and work backwards to the minimal JSON structure. Ask:

- What are the **entities**? (concerns, steps, sections, findings, comparisons)
- What are the **categories/variants**? (severity levels, personas, statuses) — these become enums
- What **metadata** is needed? (source file, title, timestamps)
- What enables **interactivity**? (IDs for cross-referencing, search strings for highlight injection, line numbers for code view)

Design the JSON so that **merging is simple** — arrays that can be concatenated, keyed objects that can be spread. This matters when sub-agents work in parallel.

## Step 2: Write the JSON Schema

Create `schema/<name>.schema.json` using JSON Schema draft 2020-12. This is the single source of truth.

### Schema design principles

**Lock everything down.** Every object gets `additionalProperties: false` and explicit `required`. The schema should reject anything the template doesn't know how to render. An agent producing invalid JSON should fail at validation, not produce a broken page.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["metadata", "sections", "items"],
  "additionalProperties": false,
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["title", "sourceFile"],
      "additionalProperties": false,
      "properties": {
        "title": { "type": "string" },
        "sourceFile": { "type": "string" }
      }
    }
  }
}
```

**Use enums for known value sets.** Severities, statuses, verdict types, view modes — if the template switches on it, it's an enum. This prevents typos from silently producing broken rendering.

```json
"severity": {
  "type": "string",
  "enum": ["critical", "warning", "info"]
}
```

**Use patterns for format constraints.** Hex colors, lowercase IDs, date formats:

```json
"id": { "type": "string", "pattern": "^[a-z][a-z0-9_]*$" },
"color": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$" }
```

**Design IDs for cross-referencing.** If items reference categories, use a consistent `{category}-{n}` pattern (e.g., `cto-1`, `security-3`). This makes the relationship readable in raw JSON and easy to validate.

**Keep arrays flat.** Prefer a flat array of items with a `category` field over nested `{ category: { items: [...] } }`. Flat arrays are easier to filter, sort, merge, and validate.

## Step 3: Write the build script

Create `scripts/build_<name>.py` — a Python script with two validation layers and simple string injection.

### Layer 1: Schema validation

```python
import subprocess
result = subprocess.run(
    ["uvx", "check-jsonschema", "--schemafile", str(schema_path), str(data_path)],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"Schema validation FAILED:\n{result.stderr or result.stdout}", file=sys.stderr)
    sys.exit(1)
```

No Python JSON Schema library needed — `uvx check-jsonschema` handles it with zero dependencies.

### Layer 2: Semantic validation

Things JSON Schema can't express. Write a `validate_data_integrity(data)` function that returns a list of error strings:

- **Referential integrity**: If an item's `category` field references a category ID, that ID must exist in the categories array
- **Unique IDs**: No duplicate IDs within any array
- **Substring existence**: If a field is meant to match text in a source document (e.g., for highlight injection), verify the substring actually exists in the source
- **Cross-field consistency**: `endLine >= startLine`, summary keys match all category IDs plus an "all" key
- **Bounds checking**: Line numbers within document length, indices within array bounds

Every semantic check should produce a specific, actionable error message:
```python
errors.append(f"Item {item['id']}: references unknown category '{item['category']}'. Valid: {valid_ids}")
```

### Injection

Simple string replacement. Place a `__PLACEHOLDER__` token in the template and replace it:

```python
PLACEHOLDER = "__DATA_PLACEHOLDER__"
template = template_path.read_text()
html = template.replace(PLACEHOLDER, json.dumps(data))
output_path.write_text(html)
```

No Jinja, no Mustache, no templating engine. The template is a complete HTML file with a JS variable assignment that gets its value replaced.

### CLI interface

```python
parser = argparse.ArgumentParser()
parser.add_argument("data", type=Path, help="Path to JSON data file")
parser.add_argument("-o", "--output", type=Path, default=None)
parser.add_argument("--open", action="store_true", help="Open in browser")
parser.add_argument("--skip-validation", action="store_true")
```

Run with: `uv run python scripts/build_<name>.py data.json --open`

### Merging multiple JSON files

If sub-agents produce separate files, add merge logic before validation:

```python
parser.add_argument("data", nargs="+", type=Path, help="One or more JSON files to merge")
```

Merge strategy: concatenate arrays, spread keyed objects, take metadata from the first file. Validate the **merged** result, not individual files.

## Step 4: Build the Vue 3 template

Create `assets/template.html` — a single self-contained HTML file.

### Foundation

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
<style>/* all CSS inline */</style>
</head>
<body>
<div id="app">
  <!-- template here -->
</div>
<script>
const DATA = __DATA_PLACEHOLDER__;
const { createApp, ref, computed, watch, nextTick, onMounted } = Vue;
createApp({
  setup() {
    // all logic here
    return { /* everything the template needs */ };
  }
}).mount('#app');
</script>
</body>
</html>
```

Everything inline — CSS in `<style>`, JS in `<script>`. No external dependencies except Vue 3 CDN (and optionally marked.js + highlight.js if rendering markdown).

### Data-driven rendering

Everything the template renders comes from `DATA`. No hardcoded labels, colors, or categories.

```javascript
// Categories/tabs generated from data
const categories = DATA.categories;

// Colors come from data, applied via computed styles
function categoryStyle(catId) {
  const color = categoryColors[catId] || '#8b949e';
  return { background: color + '22', color: color, border: '1px solid ' + color + '55' };
}
```

If you're tempted to write `if (category === 'security')` in the template, stop — that's a hardcoded value. Use `DATA.categories.find(c => c.id === item.category)` instead.

### CSS patterns

**Dark theme variables** — define once, use everywhere:

```css
:root {
  --bg: #0d1117; --surface: #161b22; --surface2: #21262d;
  --border: #30363d; --text: #e6edf3; --text-muted: #8b949e;
  --red: #f85149; --red-bg: rgba(248,81,73,0.12);
  --yellow: #d29922; --yellow-bg: rgba(210,153,34,0.12);
  --blue: #58a6ff; --blue-bg: rgba(88,166,255,0.12);
  --green: #3fb950; --green-bg: rgba(63,185,80,0.12);
}
```

**Two-class pattern for variant styling.** When items have a base state plus a variant (severity, status, type), use two CSS classes instead of one concatenated class:

```css
/* Good: two classes, independently styleable */
.item.has-status { border-left: 3px solid var(--yellow); cursor: pointer; }
.item.has-status.critical { border-left-color: var(--red); background: var(--red-bg); }
.item.has-status.warning { border-left-color: var(--yellow); background: var(--yellow-bg); }

/* Bad: concatenated, fragile */
.item.status-critical { ... }
```

The JS returns both classes as a space-separated string:
```javascript
function itemClass(item) {
  return item.status ? 'has-status ' + item.status : '';
}
```

### Interactivity patterns

**localStorage persistence** — user decisions (approve/reject, comments, collapsed state) survive page refresh:

```javascript
const STORAGE_KEY = 'tool-name-' + DATA.metadata.sourceFile.replace(/[^a-z0-9]/gi, '-').toLowerCase();
function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ decisions: decisions.value, comments: comments.value }));
}
// Call persist() on every mutation. Load before first render.
```

**URL state via replaceState** — active tab, view mode, selected item:

```javascript
watch([activeTab, viewMode], () => {
  const url = new URL(window.location);
  url.searchParams.set('tab', activeTab.value);
  url.searchParams.set('view', viewMode.value);
  history.replaceState(null, '', url);
});
```

**Bidirectional navigation** — click an item in the document to scroll to its detail card, click a detail card to scroll to the item in the document. Use `data-*` attributes to link them:

```javascript
function focusElement(selector) {
  nextTick(() => {
    const el = document.querySelector(selector);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('focus-highlight');
      setTimeout(() => el.classList.remove('focus-highlight'), 2000);
    }
  });
}
```

With a gold pulse animation:
```css
@keyframes focus-pulse {
  0% { box-shadow: 0 0 0 4px rgba(255,215,0,0.8); background-color: rgba(255,215,0,0.25); }
  100% { box-shadow: 0 0 0 0 transparent; background-color: transparent; }
}
.focus-highlight { animation: focus-pulse 2s ease-out forwards; }
```

### Markdown rendering (when needed)

If the data includes markdown content, use marked.js + highlight.js:

```html
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11/lib/core.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11/styles/github-dark.min.css">
```

Strip YAML frontmatter before rendering:
```javascript
const content = rawMarkdown.replace(/^---\n[\s\S]*?\n---\n?/, '');
const html = marked.parse(content);
```

For highlight injection into rendered markdown, wrap matched substrings with `<span>` tags **before** calling `marked.parse()`, sorting by length descending to avoid partial replacements.

## Step 5: Update agent instructions

In the skill's SKILL.md, tell the agent to output JSON instead of HTML. Include:

1. The schema location: "Read the schema at `schema/<name>.schema.json`"
2. A condensed example of the JSON structure (not the full schema — the agent should read it)
3. Where to save: "Write the JSON to `/tmp/<descriptive_name>.json`"
4. The build command: `uv run python <skill_dir>/scripts/build_<name>.py /tmp/data.json --open`
5. What to tell the user after building

The agent should never need to see or think about the template HTML.

## Parallel sub-agent pattern

When analysis can be split by category, persona, or section:

1. Each sub-agent receives its section of work + the schema to follow
2. Sub-agents run in parallel (no shared state)
3. Each outputs a JSON file for its section
4. The controller merges all JSON files
5. Build script validates the merged result and injects into template

Design the schema so merging is trivial:
- Items in flat arrays with a `category` field → concatenate arrays
- Keyed summaries → spread objects
- Metadata → take from controller, not sub-agents

## Common mistakes

- **Agent writes HTML "just this once"** — it never stops at once. If the agent generates any HTML, the template becomes stale immediately.
- **Schema too permissive** — `additionalProperties: true` or missing `required` fields let garbage through silently. Lock it down from the start.
- **Hardcoded values in template** — if you write the category name in CSS or a conditional, it breaks when categories change. Always derive from data.
- **Skipping semantic validation** — schema validation catches structural issues, but semantic bugs (dangling references, impossible line numbers) only surface when the page renders wrong. Catch them in the build script.
- **Complex templating** — Jinja/Mustache/etc. add a dependency and a layer of indirection. `str.replace()` is all you need for injecting a single JSON blob.
