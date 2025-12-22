---
name: pyright-strict-types
description: Enforce strict Python typing standards with pyright type checking. Use when user mentions pyright, type checking, strict types, type safety, type hints, type annotations, type errors, typing issues, Any, cast(), or type ignore.
---

# Pyright Strict Types

Enforce strict Python typing standards with pyright type checking.

## When to Activate

This skill activates when the user mentions:
- **pyright** or type checking
- **strict types** or type safety
- **type hints** or type annotations
- **type errors** or typing issues
- **Any**, **cast()**, or **type: ignore**

## Core Principles

**Type Safety is Non-Negotiable**
- All code must pass strict pyright type checking before being considered complete
- Type errors are bugs and must be fixed, not bypassed
- No compromises on type safety

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
- Never rely on type inference for collections

## Required Patterns

### Function Signatures
Every function must have complete type annotations:

```python
# ✅ Correct
def process_data(items: list[UserData]) -> dict[str, int]:
    result: dict[str, int] = {}
    return result

# ❌ Wrong
def process_data(items):
    result = {}
    return result
```

### Empty Collections
Always specify types for empty collections to prevent inference errors:

```python
# ✅ Correct
items: list[str] = []
mapping: dict[str, int] = {}
unique: set[UUID] = set()

# ❌ Wrong
items = []
mapping = {}
unique = set()
```

### Pydantic Models Over Dicts
Prefer Pydantic models with strict type fields instead of untyped dictionaries:

```python
# ✅ Correct
def create_user(data: UserCreateRequest) -> UserResponse:
    ...

# ❌ Wrong
def create_user(data: dict[str, Any]) -> dict[str, Any]:
    ...
```

### Async Functions
Async functions must return concrete types, not wrapped in Coroutine:

```python
# ✅ Correct
async def get_user(user_id: UUID) -> User:
    ...

# ❌ Wrong
async def get_user(user_id: UUID):
    ...
```

## Union Type Best Practices

### Keep Unions Simple
Limit unions to 2-3 types that are logically related:

```python
# ✅ Good unions
Result = Success | Failure  # discriminated union
port: int | str  # both represent the same concept
value: str | None  # optional value

# ❌ Bad unions
data: str | int | list | dict | None  # too many unrelated types
```

### Never Mix Strict and Loose Types
Avoid unions that combine typed and untyped data:

```python
# ❌ Wrong - defeats type checking
data: RequestData | dict[str, Any]
config: ConfigModel | dict[str, Any] | None

# ✅ Correct - consistent type safety
data: RequestData
config: ConfigModel | None
```

**Why this matters**: Mixed unions force every function to handle both typed and untyped cases, leading to:
- Complex type guards and conditional logic
- Loss of type safety benefits
- Confusion about which type to use
- Gradual degradation of type safety

### Use Type Guards
When using unions, implement type guards for safe narrowing:

```python
def process_value(val: str | int) -> str:
    if isinstance(val, str):
        return val.upper()
    else:  # val is int
        return str(val)
```

### Document Union Rationale
When unions are necessary, document why:

```python
# Union because API accepts both formats for backward compatibility
def set_timeout(duration: int | timedelta) -> None:
    ...
```

## Validation Workflow

### After Each Modification
1. Run pyright on every modified file: `make pyright -- path/to/file.py`
2. Fix all type errors before proceeding
3. Never bypass type errors with casts or ignores

### Test Files
Test files require the same strict typing standards as production code:
- All fixtures must have type hints
- All test functions must have type hints
- Test data must use proper types

### Completion Criteria
Work is only complete when:
- All pyright checks pass with zero errors
- All tests pass
- No type workarounds without documentation

## Quick Violation Checks

Use these commands to find common violations:

```bash
# Find Any, cast, or type: ignore
rg "\bAny\b|cast\(|# type: ignore" --type py

# Find untyped functions
rg "def \w+\([^)]*\):" --type py | rg -v "->"

# Find loose dicts
rg "dict\[str,\s*Any\]" --type py

# Find empty collections without types
rg "= \[\]|= \{\}|= set\(\)" --type py
```

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

## Error Resolution

### Type Errors Are Bugs
Treat type checking failures as seriously as runtime errors:
- Don't bypass with `Any`, `cast()`, or `# type: ignore`
- Fix the root cause, not the symptom
- Seek type-safe solutions first

### Verify Assumptions Before Adding Workarounds
Before assuming a library is untyped and adding `Any` or `# type: ignore`:

**CRITICAL**: Verify the library's actual type signatures before concluding it's untyped. A pyright error may be caused by:
- A bug in your code (incorrect usage, wrong types)
- Missing type annotations in your code
- Incorrect import paths
- Your code not matching the library's actual type signature

**Best practice**: Create a temporary Python script to inspect the library at runtime:

```python
# tmp/inspect_library.py
from some_library import some_function
import inspect

# Method 1: Use help() to see the full signature and docstring
help(some_function)

# Method 2: Use inspect.signature() for just the signature
print(inspect.signature(some_function))

# Method 3: Check for type annotations directly
print(some_function.__annotations__)

# Method 4: For classes, inspect methods
from some_library import SomeClass
help(SomeClass.method_name)
print(inspect.signature(SomeClass.method_name))
```

Then run: `uv run python tmp/inspect_library.py`

This will show you the actual type hints as Python sees them at runtime, which is what pyright uses for type checking.

**Only after verification**:
- If the library IS typed, fix your code to match its types
- If the library truly lacks type stubs, then document the workaround

### Document Exceptions
If `Any` or `# type: ignore` is truly unavoidable after verification, document why:

```python
# type: ignore[import]  # third-party library has no type stubs (verified with help())
import untyped_library

# Must use Any - external API returns untyped JSON (verified with inspect.signature)
external_data: dict[str, Any] = fetch_external_api()
```

### Progressive Enhancement
When working with existing code:
- Improve type annotations wherever possible
- Don't make code worse by adding loose types
- Refactor towards stricter typing over time

## Agent Instructions

When this skill is activated, you must:

1. **Read Project Documentation**: Check for project-specific typing guides in `docs/code-style/` or similar locations

2. **Enforce Standards**: Apply all rules from this guide to any code you write or modify

3. **Type Check Early**: Run pyright on modified files before proceeding with other tasks

4. **Use Modern Syntax**: Always use modern Python type syntax (builtin generics, union operator)

5. **No Shortcuts**: Never use `Any`, `cast()`, or `# type: ignore` without explicit user approval and documentation

6. **Fix at Source**: When encountering type errors, fix the root cause rather than adding type workarounds

7. **Check Violations**: Use the provided grep patterns to find and fix common violations

8. **Document Exceptions**: When type workarounds are truly necessary, add clear comments explaining why

Remember: Type safety is a core quality metric. Strict typing prevents bugs, improves code clarity, and enables better tooling support.
