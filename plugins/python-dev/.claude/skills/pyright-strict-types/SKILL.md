---
name: pyright-strict-types
description: Enforce strict Python typing standards with pyright type checking. Use when user mentions pyright, type checking, strict types, type safety, type hints, type annotations, type errors, typing issues, Any, cast(), type ignore, Protocol, Generic, TypeVar, or TypedDict.
license: MIT
metadata:
  version: 2.0.0
  model: claude-opus-4-5-20251101
---

# Pyright Strict Types

Enforce strict Python typing standards with pyright type checking.

---

## Quick Start

```bash
# Check a single file
uv run pyright path/to/file.py

# Check entire project
uv run pyright .

# Find type violations
rg "\bAny\b|cast\(|# type: ignore" --type py
```

---

## Triggers

This skill activates when the user mentions:
- **pyright**, type checking, strict types
- **type safety**, type hints, type annotations
- **type errors**, typing issues
- **Any**, **cast()**, **type: ignore**
- **Protocol**, **Generic**, **TypeVar**
- **TypedDict**, **Literal**, **Callable**

---

## Quick Reference

| Category | Do | Don't |
|----------|------|-------|
| **Generics** | `list[str]`, `dict[str, int]` | `List[str]`, `Dict[str, int]` |
| **Optionals** | `str \| None` | `Optional[str]` |
| **Empty collections** | `items: list[str] = []` | `items = []` |
| **Functions** | `def foo(x: int) -> str:` | `def foo(x):` |
| **Data** | Pydantic models, TypedDict | `dict[str, Any]` |
| **Workarounds** | Fix root cause | `Any`, `cast()`, `# type: ignore` |

---

## Core Principles

**Type Safety is Non-Negotiable**
- All code must pass strict pyright before being considered complete
- Type errors are bugs - fix them, don't bypass them

**No Type Shortcuts**
- Never use `Any` without documented justification
- Never use `cast()` without documented justification
- Never use `# type: ignore` without documented justification
- Treat any type workaround as a code smell requiring explanation

**Modern Python Type Syntax**
- Use `list[str]` not `List[str]`
- Use `dict[str, int]` not `Dict[str, int]`
- Use `str | None` not `Optional[str]`
- Use native Python types over typing module imports

**Explicit Over Implicit**
- Always add explicit type hints for function parameters
- Always add explicit type hints for return types
- Always specify types for empty collections

---

## Pyright Configuration

Create `pyrightconfig.json` in your project root:

```json
{
  "include": ["src", "apps", "packages"],
  "exclude": ["**/node_modules", "**/__pycache__", ".venv"],
  "typeCheckingMode": "strict",
  "pythonVersion": "3.11",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "reportUnknownMemberType": false,
  "reportUnknownArgumentType": false,
  "reportUnknownVariableType": false,
  "reportUnknownParameterType": false
}
```

| Mode | Use Case |
|------|----------|
| `"basic"` | Legacy codebases, gradual adoption |
| `"standard"` | Normal projects, balanced strictness |
| `"strict"` | **Recommended** - Full type safety |
| `"all"` | Maximum strictness, may be noisy |

---

## Validation Commands

```bash
# Find Any, cast, or type: ignore
rg "\bAny\b|cast\(|# type: ignore" --type py

# Find untyped functions
rg "def \w+\([^)]*\):" --type py | rg -v "->"

# Find loose dicts
rg "dict\[str,\s*Any\]" --type py

# Find empty collections without types
rg "= \[\]|= \{\}|= set\(\)" --type py

# Find old typing syntax
rg "from typing import.*\b(List|Dict|Optional|Tuple)\b" --type py
```

---

## Required Patterns

### Function Signatures

Every function must have complete type annotations:

```python
# Correct
def process_data(items: list[UserData]) -> dict[str, int]:
    result: dict[str, int] = {}
    return result

# Wrong
def process_data(items):
    result = {}
    return result
```

### Empty Collections

Always specify types for empty collections:

```python
# Correct
items: list[str] = []
mapping: dict[str, int] = {}
unique: set[UUID] = set()

# Wrong - type inference fails
items = []
mapping = {}
unique = set()
```

### Pydantic Models Over Dicts

```python
# Correct
def create_user(data: UserCreateRequest) -> UserResponse:
    ...

# Wrong
def create_user(data: dict[str, Any]) -> dict[str, Any]:
    ...
```

### Async Functions

```python
# Correct
async def get_user(user_id: UUID) -> User:
    ...

# Wrong - missing return type
async def get_user(user_id: UUID):
    ...
```

---

## Union Type Best Practices

### Keep Unions Simple

Limit unions to 2-3 logically related types:

```python
# Good unions
Result = Success | Failure  # discriminated union
port: int | str  # both represent same concept
value: str | None  # optional value

# Bad union - too many unrelated types
data: str | int | list | dict | None
```

### Never Mix Strict and Loose Types

```python
# Wrong - defeats type checking
data: RequestData | dict[str, Any]

# Correct - consistent type safety
data: RequestData
```

### Use Type Guards

```python
def process_value(val: str | int) -> str:
    if isinstance(val, str):
        return val.upper()
    else:  # val is int
        return str(val)
```

---

## TypedDict Patterns

Use TypedDict for structured dictionaries with known keys:

```python
from typing import TypedDict, NotRequired

class UserConfig(TypedDict):
    name: str
    email: str
    age: NotRequired[int]  # Optional key

class APIResponse(TypedDict):
    status: int
    data: dict[str, str]
    error: NotRequired[str]

# Usage
def get_config() -> UserConfig:
    return {"name": "Alice", "email": "alice@example.com"}
```

### When to Use TypedDict vs Pydantic

| Use TypedDict | Use Pydantic |
|---------------|--------------|
| Simple structures | Validation needed |
| JSON-like data | Serialization/parsing |
| Performance-critical | Complex transformations |
| No runtime validation | API models |

---

## Literal Types

Use Literal for fixed value sets:

```python
from typing import Literal

Status = Literal["pending", "active", "completed"]
LogLevel = Literal["debug", "info", "warning", "error"]

def set_status(status: Status) -> None:
    ...

# Type error: "unknown" is not a valid Status
set_status("unknown")
```

---

## Callable Types

### Basic Callable

```python
from collections.abc import Callable

# Function taking int, returning str
Handler = Callable[[int], str]

def process(handler: Handler) -> None:
    result = handler(42)
```

### Callable with Multiple Args

```python
# Function taking str and int, returning bool
Validator = Callable[[str, int], bool]

def validate(fn: Validator, name: str, age: int) -> bool:
    return fn(name, age)
```

### Callable with ParamSpec (Advanced)

```python
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def with_logging(fn: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper
```

---

## Common Patterns

### Repository Pattern

```python
class UserRepo:
    async def get_by_id(self, user_id: UUID) -> UserRow | None:
        ...

    async def find_by_email(self, email: str) -> list[UserRow]:
        ...
```

### Service Pattern

```python
class UserService:
    def __init__(self, repo: UserRepo, session: AsyncSession) -> None:
        self.repo = repo
        self.session = session

    async def create_user(self, data: UserCreate) -> UserResponse:
        ...
```

### Dependency Injection

```python
from typing import Annotated
from fastapi import Depends

UserRepoDepends = Annotated[UserRepo, Depends(get_user_repo)]

async def create_user(
    data: UserCreate,
    repo: UserRepoDepends,
) -> UserResponse:
    ...
```

### Test Fixtures

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def user_repo(session: AsyncSession) -> UserRepo:
    return UserRepo(session)
```

---

## Error Resolution

### Type Errors Are Bugs

Treat type checking failures as seriously as runtime errors:
- Don't bypass with `Any`, `cast()`, or `# type: ignore`
- Fix the root cause, not the symptom

### Verify Library Types Before Workarounds

**CRITICAL**: Before assuming a library is untyped:

```python
# tmp/inspect_library.py
from some_library import some_function
import inspect

# Check actual type signature
help(some_function)
print(inspect.signature(some_function))
print(some_function.__annotations__)
```

Run: `uv run python tmp/inspect_library.py`

### Document Exceptions

If workarounds are truly unavoidable after verification:

```python
# type: ignore[import]  # third-party library has no type stubs (verified)
import untyped_library

# Must use Any - external API returns untyped JSON (verified with inspect.signature)
external_data: dict[str, Any] = fetch_external_api()
```

---

## Agent Instructions

When this skill is activated:

1. **Check Pyright Config**: Ensure `pyrightconfig.json` exists with strict mode
2. **Use Modern Syntax**: Always use modern Python type syntax
3. **Type Check Early**: Run pyright on modified files before proceeding
4. **No Shortcuts**: Never use `Any`, `cast()`, or `# type: ignore` without user approval
5. **Fix at Source**: Fix root causes, not symptoms
6. **Check Violations**: Use provided grep patterns to find common violations
7. **Verify Libraries**: Inspect library signatures before adding workarounds

---

<details>
<summary><strong>Deep Dive: Protocol Types</strong></summary>

### Structural Subtyping with Protocol

Use Protocol for duck typing with type safety:

```python
from typing import Protocol

class Readable(Protocol):
    def read(self, n: int = -1) -> str: ...

class Closeable(Protocol):
    def close(self) -> None: ...

class ReadableCloseable(Readable, Closeable, Protocol):
    """Combines multiple protocols"""
    pass

# Any class with these methods works
def process_file(f: Readable) -> str:
    return f.read()

# Works with file objects, StringIO, custom classes
with open("file.txt") as f:
    content = process_file(f)
```

### Runtime Checkable Protocol

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: object) -> None:
    if isinstance(obj, Drawable):  # Runtime check works
        obj.draw()
```

### When to Use Protocol vs ABC

| Use Protocol | Use ABC |
|--------------|---------|
| Duck typing | Explicit inheritance required |
| Third-party compatibility | Internal hierarchy |
| No runtime overhead | Need `isinstance` checks |
| Structural subtyping | Nominal subtyping |

</details>

<details>
<summary><strong>Deep Dive: Generic Types</strong></summary>

### Basic Generic Class

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push("string")  # Type error!
```

### Bounded TypeVar

```python
from typing import TypeVar

# T must be a subclass of Number
Number = int | float
T = TypeVar("T", bound=Number)

def double(x: T) -> T:
    return x * 2  # type: ignore[return-value]

# Constrained TypeVar - must be exactly one of these types
StrOrBytes = TypeVar("StrOrBytes", str, bytes)

def process(data: StrOrBytes) -> StrOrBytes:
    return data
```

### Covariant and Contravariant

```python
from typing import TypeVar, Generic

T_co = TypeVar("T_co", covariant=True)  # Read-only
T_contra = TypeVar("T_contra", contravariant=True)  # Write-only

class Reader(Generic[T_co]):
    def read(self) -> T_co: ...

class Writer(Generic[T_contra]):
    def write(self, value: T_contra) -> None: ...
```

</details>

<details>
<summary><strong>Deep Dive: Overload Decorator</strong></summary>

### Function Overloading

```python
from typing import overload

@overload
def process(data: str) -> str: ...
@overload
def process(data: bytes) -> bytes: ...
@overload
def process(data: None) -> None: ...

def process(data: str | bytes | None) -> str | bytes | None:
    if data is None:
        return None
    if isinstance(data, bytes):
        return data.upper()
    return data.upper()
```

### Overload with Different Return Types

```python
from typing import overload, Literal

@overload
def fetch(url: str, as_json: Literal[True]) -> dict[str, Any]: ...
@overload
def fetch(url: str, as_json: Literal[False]) -> str: ...
@overload
def fetch(url: str) -> str: ...

def fetch(url: str, as_json: bool = False) -> dict[str, Any] | str:
    response = requests.get(url)
    if as_json:
        return response.json()
    return response.text
```

### When to Use Overload

| Use Overload | Don't Use |
|--------------|-----------|
| Return type depends on input | Simple unions work fine |
| Different arg combinations | One implementation handles all |
| API clarity matters | Internal functions |

</details>

<details>
<summary><strong>Deep Dive: Python 3.11+ Features</strong></summary>

### Self Type

```python
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:
        self.name = name
        return self

    def set_value(self, value: int) -> Self:
        self.value = value
        return self

class ExtendedBuilder(Builder):
    def set_extra(self, extra: str) -> Self:
        self.extra = extra
        return self

# Chaining works with correct types
builder = ExtendedBuilder().set_name("test").set_extra("more")
```

### TypeVarTuple (Variadic Generics)

```python
from typing import TypeVarTuple, Unpack

Ts = TypeVarTuple("Ts")

def concat(*args: Unpack[Ts]) -> tuple[Unpack[Ts]]:
    return args

# Preserves exact tuple type
result = concat(1, "hello", 3.14)  # tuple[int, str, float]
```

### Required and NotRequired

```python
from typing import TypedDict, Required, NotRequired

class Config(TypedDict, total=False):
    name: Required[str]  # Always required
    debug: NotRequired[bool]  # Optional
    timeout: int  # Optional (total=False)
```

### TypeGuard

```python
from typing import TypeGuard

def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # items is now list[str]
        for item in items:
            print(item.upper())
```

### ParamSpec for Decorators

```python
from typing import Callable, ParamSpec, TypeVar
import functools

P = ParamSpec("P")
R = TypeVar("R")

def retry(times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for _ in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    pass
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

</details>

<details>
<summary><strong>Deep Dive: Gradual Typing Migration</strong></summary>

### Step 1: Configure Pyright

Start with relaxed settings:

```json
{
  "typeCheckingMode": "basic",
  "reportMissingTypeStubs": false,
  "reportUnknownMemberType": false
}
```

### Step 2: Add Type Stubs

```bash
# Install type stubs for common libraries
uv add types-requests types-pyyaml types-redis

# Check available stubs
uv pip show types-*
```

### Step 3: Type Public APIs First

Priority order:
1. Function signatures in public modules
2. Class `__init__` methods
3. Return types
4. Internal functions

### Step 4: Increase Strictness

Gradually enable stricter checks:

```json
{
  "typeCheckingMode": "standard",
  "reportMissingTypeStubs": true
}
```

### Step 5: Enable Strict Mode

```json
{
  "typeCheckingMode": "strict"
}
```

### CI Integration

```yaml
# .github/workflows/typecheck.yml
- name: Type Check
  run: uv run pyright --verifytypes mypackage
```

</details>

---

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| `Any` without docs | Defeats type checking | Use specific types or document |
| `dict[str, Any]` | No structure | TypedDict or Pydantic |
| `# type: ignore` | Hides real errors | Fix root cause |
| `cast()` everywhere | Runtime errors | Proper type design |
| Huge unions | Unmanageable | Discriminated unions |
| Missing return types | Inference fails | Always annotate |

---

## Verification

Work is only complete when:
- [ ] All pyright checks pass with zero errors
- [ ] No `Any` without documentation
- [ ] No `cast()` without documentation
- [ ] No `# type: ignore` without documentation
- [ ] Modern type syntax throughout
- [ ] All functions have return type annotations

---

## References

- [Type Patterns Catalog](references/type-patterns-catalog.md)
- [Common Error Resolutions](references/error-resolutions.md)
- [Third-Party Stubs Guide](references/third-party-stubs.md)

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| python-code-smell-audit | Complementary code quality checks |
| python-scripts | Script development standards |

---

## Changelog

### v2.0.0
- Added Protocol types section
- Added Generic types with TypeVar
- Added Overload decorator patterns
- Added Python 3.11+ features (Self, TypeVarTuple, ParamSpec, TypeGuard)
- Added TypedDict and Literal patterns
- Added Callable type annotations
- Added Pyright configuration section
- Added gradual typing migration guide
- Restructured with collapsible Deep Dive sections
- Added references directory
- Improved triggers and description

### v1.0.0
- Initial skill with core typing principles
