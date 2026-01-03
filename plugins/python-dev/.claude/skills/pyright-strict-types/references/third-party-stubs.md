# Third-Party Type Stubs Guide

How to work with type stubs for third-party libraries.

---

## Finding Type Stubs

### Official Typeshed Stubs

Most popular libraries have stubs in [typeshed](https://github.com/python/typeshed).

```bash
# Search for available stubs
uv search types-

# Common stubs
uv add types-requests
uv add types-pyyaml
uv add types-redis
uv add types-boto3
uv add types-python-dateutil
uv add types-pillow
uv add types-protobuf
```

### Check if Library is Already Typed

Many modern libraries include inline types (py.typed marker):

```bash
# Check if package has py.typed
python -c "import pkg; print(pkg.__path__)"
ls /path/to/package/py.typed
```

**Libraries with inline types (no stubs needed):**
- pydantic
- fastapi
- httpx
- attrs
- sqlalchemy (2.0+)
- typer
- rich

---

## Installing Stubs

### With uv

```bash
# Add type stubs
uv add types-requests

# Add multiple
uv add types-requests types-pyyaml types-redis

# Add as dev dependency
uv add --dev types-requests
```

### With pip

```bash
pip install types-requests
```

### Pyright Auto-Install

Pyright can auto-install stubs. In pyrightconfig.json:

```json
{
  "useLibraryCodeForTypes": true
}
```

---

## Common Stub Packages

| Library | Stub Package |
|---------|-------------|
| requests | types-requests |
| PyYAML | types-pyyaml |
| redis | types-redis |
| boto3 | types-boto3 |
| Pillow | types-pillow |
| protobuf | types-protobuf |
| python-dateutil | types-python-dateutil |
| beautifulsoup4 | types-beautifulsoup4 |
| selenium | types-selenium |
| paramiko | types-paramiko |
| Flask | types-flask |
| Jinja2 | types-jinja2 |
| Markdown | types-markdown |
| psutil | types-psutil |
| docutils | types-docutils |
| toml | types-toml |

---

## Creating Local Stubs

When no stubs exist, create your own.

### Directory Structure

```
myproject/
├── stubs/
│   └── untyped_lib/
│       ├── __init__.pyi
│       └── module.pyi
├── src/
└── pyrightconfig.json
```

### Configure Pyright

```json
{
  "stubPath": "./stubs"
}
```

### Stub File Syntax

```python
# stubs/untyped_lib/__init__.pyi
from typing import Any

def some_function(arg: str, count: int = ...) -> list[str]: ...

class SomeClass:
    name: str
    value: int

    def __init__(self, name: str, value: int = ...) -> None: ...
    def process(self, data: bytes) -> str: ...

# Use ... for implementation (not pass)
```

### Partial Stubs

For large libraries, stub only what you use:

```python
# stubs/big_lib/__init__.pyi
from typing import Any

# Only stub functions you actually use
def function_i_use(x: int) -> str: ...

# Everything else is Any
def __getattr__(name: str) -> Any: ...
```

---

## Handling Untyped Libraries

### Strategy 1: Ignore Type Stubs Warning

```json
{
  "reportMissingTypeStubs": false
}
```

### Strategy 2: Suppress Per-Import

```python
import untyped_lib  # type: ignore[import-untyped]
```

### Strategy 3: Create Minimal Stubs

```python
# stubs/untyped_lib/__init__.pyi
from typing import Any

def __getattr__(name: str) -> Any: ...
```

### Strategy 4: Type the Usage

```python
from typing import Any

import untyped_lib

# Add types at point of use
result: str = untyped_lib.get_string()
data: dict[str, int] = untyped_lib.get_data()
```

---

## Verifying Stub Installation

### Check Pyright Finds Stubs

```bash
# Run pyright in verbose mode
uv run pyright --verifytypes mypackage

# Check for stub resolution
uv run pyright --outputjson file.py | jq '.generalDiagnostics'
```

### Test Import

```python
# tmp/test_stubs.py
import requests

# If stubs work, pyright knows response is Response
response = requests.get("https://example.com")
reveal_type(response)  # Should show: Response
```

---

## Stub Quality Issues

### Overly Permissive Stubs

Some stubs use too much `Any`:

```python
# Bad stub
def get_data() -> Any: ...

# Better stub
def get_data() -> dict[str, str]: ...
```

**Solution:** Create local override stubs.

### Missing Overloads

```python
# Stub missing overloads
def process(data: str | bytes) -> str | bytes: ...

# Better with overloads
@overload
def process(data: str) -> str: ...
@overload
def process(data: bytes) -> bytes: ...
```

### Outdated Stubs

```bash
# Update stubs
uv add --upgrade types-requests
```

---

## Contributing Stubs

If you create quality stubs, consider contributing to typeshed:

1. Fork [python/typeshed](https://github.com/python/typeshed)
2. Add stubs following their format
3. Test with `python tests/check_new_syntax.py`
4. Submit PR

---

## Pyright Configuration for Stubs

```json
{
  "stubPath": "./stubs",
  "reportMissingTypeStubs": true,
  "useLibraryCodeForTypes": true,
  "typeshedPath": null,
  "extraPaths": ["./src"]
}
```

| Option | Purpose |
|--------|---------|
| `stubPath` | Local stubs directory |
| `reportMissingTypeStubs` | Warn about missing stubs |
| `useLibraryCodeForTypes` | Infer from source if no stubs |
| `typeshedPath` | Custom typeshed location |
| `extraPaths` | Additional paths for imports |

---

## Troubleshooting

### "Stub file not found"

1. Check package is installed: `uv pip show types-xxx`
2. Check correct name: `types-pyyaml` not `types-yaml`
3. Verify venv is active

### "Partially unknown type"

1. Stub exists but is incomplete
2. Create local override stub
3. Or suppress: `reportUnknownMemberType: false`

### "Import could not be resolved"

1. Package not installed
2. Wrong Python path
3. Add to `extraPaths` in pyrightconfig.json

### Stubs Conflict with Source

If library has inline types AND you have stubs:

```json
{
  "stubPath": "./stubs",
  "useLibraryCodeForTypes": false
}
```

This prefers stubs over inline types.

---

## Quick Reference

```bash
# Find stubs
uv search types-libraryname

# Install stubs
uv add types-libraryname

# Create local stub
mkdir -p stubs/libraryname
touch stubs/libraryname/__init__.pyi

# Test stub resolution
uv run pyright --verbose file.py
```
