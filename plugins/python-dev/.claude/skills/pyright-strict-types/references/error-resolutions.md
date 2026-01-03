# Common Pyright Error Resolutions

Solutions to frequently encountered pyright type errors.

---

## reportMissingImports

**Error:** `Import "module" could not be resolved`

### Solutions

1. **Install the package:**
   ```bash
   uv add module-name
   ```

2. **Install type stubs:**
   ```bash
   uv add types-module-name
   ```

3. **Add to pyrightconfig.json extraPaths:**
   ```json
   {
     "extraPaths": ["./src"]
   }
   ```

4. **For local packages, ensure py.typed exists:**
   ```
   mypackage/
   ├── __init__.py
   └── py.typed  # Empty file marking package as typed
   ```

---

## reportMissingTypeStubs

**Error:** `Stub file not found for "module"`

### Solutions

1. **Check if stubs exist:**
   ```bash
   uv search types-module-name
   ```

2. **Disable for specific libraries (pyrightconfig.json):**
   ```json
   {
     "reportMissingTypeStubs": false
   }
   ```

3. **Create local stubs (stubs/module.pyi):**
   ```python
   # stubs/some_library/__init__.pyi
   def some_function(arg: str) -> int: ...
   ```

4. **Add stubs path:**
   ```json
   {
     "stubPath": "./stubs"
   }
   ```

---

## reportUnknownMemberType

**Error:** `Type of "member" is unknown`

### Solutions

1. **Add explicit type annotation:**
   ```python
   # Before
   self.items = []

   # After
   self.items: list[Item] = []
   ```

2. **Disable for third-party libraries:**
   ```json
   {
     "reportUnknownMemberType": false
   }
   ```

3. **Use type assertion (last resort):**
   ```python
   from typing import cast

   # Document why cast is needed
   result = cast(list[str], unknown_return())
   ```

---

## reportArgumentType

**Error:** `Argument of type "X" cannot be assigned to parameter of type "Y"`

### Solutions

1. **Check for None handling:**
   ```python
   # Before
   def process(user: User): ...
   process(get_user())  # Error if get_user returns User | None

   # After
   user = get_user()
   if user is not None:
       process(user)
   ```

2. **Use proper type narrowing:**
   ```python
   def handle(val: str | int) -> None:
       if isinstance(val, str):
           process_string(val)  # val is str here
       else:
           process_int(val)  # val is int here
   ```

3. **Fix the function signature:**
   ```python
   # If function should accept multiple types
   def process(data: str | bytes) -> None:
       ...
   ```

---

## reportReturnType

**Error:** `Expression of type "X" cannot be assigned to return type "Y"`

### Solutions

1. **Fix the return statement:**
   ```python
   # Before
   def get_name() -> str:
       return None  # Error

   # After
   def get_name() -> str | None:
       return None
   ```

2. **Handle all code paths:**
   ```python
   # Before
   def get_value(flag: bool) -> int:
       if flag:
           return 42
       # Missing return!

   # After
   def get_value(flag: bool) -> int:
       if flag:
           return 42
       return 0
   ```

3. **Use assert for type narrowing:**
   ```python
   def get_first(items: list[str]) -> str:
       result = items[0] if items else None
       assert result is not None
       return result
   ```

---

## reportGeneralTypeIssues

### "Object of type None cannot be used"

```python
# Before
def process(user: User | None) -> str:
    return user.name  # Error: user might be None

# After
def process(user: User | None) -> str:
    if user is None:
        return "Unknown"
    return user.name
```

### "Cannot access member on type"

```python
# Before
items: list[str] | dict[str, str]
items.append("x")  # Error: dict has no append

# After
if isinstance(items, list):
    items.append("x")
```

### "Incompatible types in assignment"

```python
# Before
name: str = None  # Error

# After
name: str | None = None
# Or
name: str = ""
```

---

## reportIncompatibleMethodOverride

**Error:** `Method override is incompatible with base class`

### Solutions

1. **Match parameter types exactly:**
   ```python
   class Base:
       def process(self, data: str) -> None: ...

   class Child(Base):
       # Must match parent signature
       def process(self, data: str) -> None: ...
   ```

2. **Use covariant return types:**
   ```python
   class Base:
       def create(self) -> "Base": ...

   class Child(Base):
       def create(self) -> "Child": ...  # OK: Child is subtype of Base
   ```

3. **Use Self for fluent interfaces:**
   ```python
   from typing import Self

   class Base:
       def chain(self) -> Self: ...

   class Child(Base):
       def chain(self) -> Self: ...  # OK
   ```

---

## reportPrivateUsage

**Error:** `"_member" is private and used outside its owning class`

### Solutions

1. **Use public interface:**
   ```python
   # Instead of accessing _internal
   obj.get_value()  # Use public method
   ```

2. **Make protected if needed by subclasses:**
   ```python
   class Base:
       _protected: str  # Single underscore is convention for protected
   ```

3. **Disable check if intentional:**
   ```json
   {
     "reportPrivateUsage": false
   }
   ```

---

## reportOptionalMemberAccess

**Error:** `"member" is not a known member of "None"`

### Solutions

1. **Guard with if check:**
   ```python
   user: User | None = get_user()
   if user is not None:
       print(user.name)
   ```

2. **Use early return:**
   ```python
   def process(user: User | None) -> str:
       if user is None:
           return "No user"
       return user.name  # user is User here
   ```

3. **Use assert (when you know it's not None):**
   ```python
   user = get_user()
   assert user is not None, "User should exist"
   print(user.name)
   ```

---

## reportUnnecessaryIsInstance

**Error:** `Unnecessary isinstance call; type is always "X"`

### Solutions

1. **Remove redundant check:**
   ```python
   # Before
   name: str = "hello"
   if isinstance(name, str):  # Unnecessary
       print(name.upper())

   # After
   name: str = "hello"
   print(name.upper())
   ```

2. **If check is for runtime safety, use cast:**
   ```python
   # If you need the check for safety despite types
   if isinstance(name, str):  # type: ignore[redundant-condition]
       print(name.upper())
   ```

---

## reportUnusedImport

**Error:** `"module" is imported but unused`

### Solutions

1. **Remove unused import:**
   ```python
   # Delete the line
   ```

2. **If needed for type checking only:**
   ```python
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from mymodule import MyType  # Only imported for type hints
   ```

3. **If needed for side effects:**
   ```python
   import module  # noqa: F401  # Imported for side effects
   ```

---

## reportIncompatibleVariableOverride

**Error:** `"variable" overrides symbol of same name in class "Base"`

### Solutions

1. **Match types exactly:**
   ```python
   class Base:
       value: int

   class Child(Base):
       value: int  # Must match, not int | None
   ```

2. **Use ClassVar for class-level:**
   ```python
   from typing import ClassVar

   class Base:
       default: ClassVar[int] = 0

   class Child(Base):
       default: ClassVar[int] = 10  # OK to override ClassVar
   ```

---

## Quick Fixes Table

| Error | Quick Fix |
|-------|-----------|
| Import not found | `uv add types-xxx` |
| Unknown member | Add type annotation |
| Optional access | Add `if x is not None:` |
| Return type mismatch | Fix return or signature |
| Argument type | Use isinstance check |
| Missing annotation | Add `: type` annotation |
| Incompatible override | Match parent signature |

---

## Diagnostic Codes

Common pyright diagnostic codes and their meanings:

| Code | Meaning |
|------|---------|
| `reportMissingImports` | Module not found |
| `reportMissingTypeStubs` | No type info for module |
| `reportGeneralTypeIssues` | Type incompatibility |
| `reportArgumentType` | Wrong argument type |
| `reportReturnType` | Wrong return type |
| `reportOptionalMemberAccess` | Accessing on None |
| `reportUnknownMemberType` | Can't infer type |
| `reportPrivateUsage` | Using private member |

To suppress a specific error:
```python
# type: ignore[reportGeneralTypeIssues]
```

To suppress all errors on a line:
```python
# type: ignore
```
