# Python Zero-Tolerance Reference

## Type Checking (pyright)

### Common Excuses and Fixes

| Error Pattern | Excuse | Fix |
|--------------|--------|-----|
| `reportGeneralClassIssues` | "The library isn't typed" | Add a typed wrapper or use `TYPE_CHECKING` imports |
| `reportMissingTypeStubs` | "No stubs available" | Install stubs (`pip install types-X`) or create a stub file |
| `reportUnknownMemberType` | "It works at runtime" | Add type annotations or use `TYPE_CHECKING` guard |
| `reportReturnType` | "The return type is obvious" | Annotate it. Obvious to humans ≠ obvious to the checker. |
| `reportArgumentType` | "The types changed upstream" | Update the call site to match the new signature |
| `reportIncompatibleMethodOverride` | "The override is correct" | Fix the signature to match the base class |

### Forbidden Shortcuts

- **`# type: ignore`** — Never without a specific error code and comment explaining why.
- **`cast()`** — Avoid. Prefer `isinstance()` narrowing or `TypeGuard`.
- **`Any`** — Never as a return type or parameter type. Use `object` or a proper generic.
- **Untyped `dict`** — Use `TypedDict` or Pydantic models instead of `dict[str, Any]`.

### Strict Mode Patterns

```python
# BAD: raw dict
def get_config() -> dict[str, str]:
    ...

# GOOD: typed model
class Config(TypedDict):
    host: str
    port: int

def get_config() -> Config:
    ...
```

## Linting (ruff)

### Common Excuses and Fixes

| Rule | Excuse | Fix |
|------|--------|-----|
| `F401` unused import | "I might need it later" | Delete it. Git has history. |
| `E501` line too long | "Reformatting breaks readability" | Run `ruff format`. It knows better. |
| `B006` mutable default argument | "It works fine in practice" | Use `None` default with `if arg is None: arg = []` |
| `S101` use of `assert` | "It's just for debugging" | Use proper validation or remove it |
| `UP` upgrade rules | "The old syntax works" | Use modern syntax. The linter knows the minimum Python version. |

### ruff format

Always run `ruff format` before committing. No manual formatting overrides.

Only acceptable `noqa` with a clear external constraint:
```python
x = long_function_name(  # noqa: E501 — URL cannot be split
    "https://very-long-url-that-cannot-be-broken.example.com/path"
)
```

## Testing (pytest)

### Common Excuses and Fixes

| Failure | Excuse | Fix |
|---------|--------|-----|
| `AssertionError` | "The expected value changed" | Verify the new behavior is correct, then update the assertion |
| `fixture not found` | "Works in my local env" | Check conftest.py scope and imports |
| `ImportError` | "The module moved" | Update the import path |
| Database/network errors | "The test env is broken" | Fix the env setup or mock properly |

### Forbidden Test Shortcuts

- **`@pytest.mark.skip`** — Never to defer a broken test. Fix it or delete it.
- **`@pytest.mark.xfail`** — Only for documenting known upstream bugs with a link to the issue.
- **Broad `except Exception`** — Never in test code. Let errors propagate.
- **`# pragma: no cover`** — Never on code that should be tested.

## Build & Packaging

### Common Excuses and Fixes

| Error | Excuse | Fix |
|-------|--------|-----|
| `ModuleNotFoundError` | "It's installed locally" | Add to pyproject.toml dependencies |
| Version conflicts | "It works with the old version" | Resolve the conflict. Pin if necessary. |
| `uv sync` failures | "The lock file is stale" | Run `uv lock` and commit the updated lock file |
