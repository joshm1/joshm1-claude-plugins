# Type Patterns Catalog

Quick reference for common typing patterns in Python.

---

## Basic Patterns

### Collections

```python
# Lists
names: list[str] = []
users: list[User] = []

# Dicts
config: dict[str, str] = {}
cache: dict[int, User] = {}

# Sets
ids: set[int] = set()
unique: frozenset[str] = frozenset()

# Tuples
point: tuple[int, int] = (0, 0)
mixed: tuple[str, int, float] = ("a", 1, 1.0)
unbounded: tuple[int, ...] = (1, 2, 3, 4)
```

### Optional Values

```python
# Modern syntax (Python 3.10+)
name: str | None = None
user: User | None = None

# Multiple optionals
result: str | int | None = None
```

### Type Aliases

```python
# Simple alias
UserId = int
UserIds = list[int]

# Complex alias
UserMap = dict[str, list[User]]
Callback = Callable[[int, str], bool]

# NewType for distinct types
from typing import NewType
UserId = NewType("UserId", int)
PostId = NewType("PostId", int)

# Now these are distinct types
def get_user(id: UserId) -> User: ...
def get_post(id: PostId) -> Post: ...
```

---

## Function Patterns

### Basic Functions

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

def process(items: list[int]) -> None:
    for item in items:
        print(item)
```

### Optional Parameters

```python
def fetch(url: str, timeout: int | None = None) -> str:
    ...

def search(query: str, limit: int = 10) -> list[Result]:
    ...
```

### *args and **kwargs

```python
def log(*args: str) -> None:
    print(" ".join(args))

def configure(**kwargs: int) -> dict[str, int]:
    return kwargs

# More specific with TypedDict
class Options(TypedDict, total=False):
    timeout: int
    retries: int

def request(url: str, **options: Unpack[Options]) -> Response:
    ...
```

### Generators

```python
from collections.abc import Generator, Iterator

def count_up(n: int) -> Generator[int, None, None]:
    for i in range(n):
        yield i

def iter_users() -> Iterator[User]:
    for user in users:
        yield user
```

### Async Functions

```python
async def fetch_user(id: int) -> User:
    ...

async def get_users() -> list[User]:
    ...

# Async generators
from collections.abc import AsyncGenerator

async def stream_events() -> AsyncGenerator[Event, None]:
    async for event in source:
        yield event
```

---

## Class Patterns

### Basic Class

```python
class User:
    name: str
    age: int

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hello, {self.name}"
```

### Class Variables

```python
from typing import ClassVar

class Config:
    DEBUG: ClassVar[bool] = False
    VERSION: ClassVar[str] = "1.0.0"

    def __init__(self, name: str) -> None:
        self.name = name  # Instance variable
```

### Final

```python
from typing import Final, final

# Final variable (cannot be reassigned)
MAX_SIZE: Final = 100
API_URL: Final[str] = "https://api.example.com"

# Final class (cannot be subclassed)
@final
class Singleton:
    ...

# Final method (cannot be overridden)
class Base:
    @final
    def critical_method(self) -> None:
        ...
```

### Self Type

```python
from typing import Self

class Builder:
    def with_name(self, name: str) -> Self:
        self.name = name
        return self

    def with_value(self, value: int) -> Self:
        self.value = value
        return self

# Works correctly with inheritance
class ExtendedBuilder(Builder):
    def with_extra(self, extra: str) -> Self:
        self.extra = extra
        return self

builder = ExtendedBuilder().with_name("test").with_extra("more")
# builder is ExtendedBuilder, not Builder
```

---

## Protocol Patterns

### Basic Protocol

```python
from typing import Protocol

class Readable(Protocol):
    def read(self, n: int = -1) -> str: ...

class Writable(Protocol):
    def write(self, data: str) -> int: ...

# Any class with these methods works
def process(f: Readable) -> str:
    return f.read()
```

### Protocol with Properties

```python
class Named(Protocol):
    @property
    def name(self) -> str: ...

class Aged(Protocol):
    @property
    def age(self) -> int: ...

class Person(Named, Aged, Protocol):
    pass
```

### Runtime Checkable

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

# Can use isinstance
def render(obj: object) -> None:
    if isinstance(obj, Drawable):
        obj.draw()
```

---

## Generic Patterns

### Generic Class

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

box: Box[int] = Box(42)
value: int = box.get()
```

### Bounded TypeVar

```python
from typing import TypeVar

class Animal:
    name: str

T = TypeVar("T", bound=Animal)

def get_name(animal: T) -> str:
    return animal.name
```

### Constrained TypeVar

```python
from typing import TypeVar

StrOrBytes = TypeVar("StrOrBytes", str, bytes)

def decode(data: StrOrBytes) -> StrOrBytes:
    return data
```

### Multiple TypeVars

```python
from typing import TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")

class Mapping(Generic[K, V]):
    def get(self, key: K) -> V | None: ...
    def set(self, key: K, value: V) -> None: ...
```

---

## TypedDict Patterns

### Basic TypedDict

```python
from typing import TypedDict

class User(TypedDict):
    name: str
    email: str
    age: int
```

### Optional Keys

```python
from typing import TypedDict, NotRequired, Required

# All optional by default
class Config(TypedDict, total=False):
    debug: bool
    timeout: int
    name: Required[str]  # This one is required

# All required by default
class User(TypedDict):
    name: str
    email: str
    phone: NotRequired[str]  # This one is optional
```

### Nested TypedDict

```python
class Address(TypedDict):
    street: str
    city: str
    country: str

class User(TypedDict):
    name: str
    address: Address
```

---

## Callable Patterns

### Basic Callable

```python
from collections.abc import Callable

# No args, returns None
Action = Callable[[], None]

# Takes int, returns str
Handler = Callable[[int], str]

# Multiple args
Processor = Callable[[str, int, bool], list[str]]
```

### Callable with ParamSpec

```python
from typing import ParamSpec, TypeVar, Callable

P = ParamSpec("P")
R = TypeVar("R")

def decorator(fn: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn(*args, **kwargs)
    return wrapper
```

### Callable Protocol (Alternative)

```python
from typing import Protocol

class Handler(Protocol):
    def __call__(self, event: Event) -> None: ...

def register(handler: Handler) -> None:
    ...
```

---

## Overload Patterns

### Basic Overload

```python
from typing import overload

@overload
def process(x: str) -> str: ...
@overload
def process(x: int) -> int: ...

def process(x: str | int) -> str | int:
    return x
```

### Overload with Literal

```python
from typing import overload, Literal

@overload
def fetch(url: str, format: Literal["json"]) -> dict: ...
@overload
def fetch(url: str, format: Literal["text"]) -> str: ...
@overload
def fetch(url: str, format: Literal["bytes"]) -> bytes: ...

def fetch(url: str, format: str) -> dict | str | bytes:
    ...
```

---

## Type Guard Patterns

### Basic TypeGuard

```python
from typing import TypeGuard

def is_string(val: object) -> TypeGuard[str]:
    return isinstance(val, str)

def process(val: object) -> None:
    if is_string(val):
        print(val.upper())  # val is str here
```

### List TypeGuard

```python
def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)
```

### TypeIs (Python 3.13+)

```python
from typing import TypeIs

def is_int(val: int | str) -> TypeIs[int]:
    return isinstance(val, int)

# TypeIs narrows in both branches
def process(val: int | str) -> None:
    if is_int(val):
        print(val + 1)  # val is int
    else:
        print(val.upper())  # val is str
```

---

## Advanced Patterns

### Concatenate for Decorators

```python
from typing import Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def with_context(
    fn: Callable[Concatenate[Context, P], R]
) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        ctx = get_context()
        return fn(ctx, *args, **kwargs)
    return wrapper

@with_context
def process(ctx: Context, data: str) -> int:
    ...

# Called without context - it's injected
result = process("data")
```

### TypeVarTuple

```python
from typing import TypeVarTuple, Unpack

Ts = TypeVarTuple("Ts")

def concat(*args: Unpack[Ts]) -> tuple[Unpack[Ts]]:
    return args

result = concat(1, "hello", 3.14)
# result: tuple[int, str, float]
```

### Annotated

```python
from typing import Annotated
from dataclasses import dataclass

# With runtime validators (Pydantic, etc.)
Name = Annotated[str, "Must be non-empty"]
Age = Annotated[int, "Must be positive"]

# With FastAPI
from fastapi import Query

def search(
    q: Annotated[str, Query(min_length=1)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[Result]:
    ...
```
