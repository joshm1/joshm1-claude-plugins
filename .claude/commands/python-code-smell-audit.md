---
description: Audit Python code for common AI coding agent mistakes
---

Scan the specified Python files or directory for code smells commonly introduced by AI coding agents:

## 1. Inline Imports
Check for imports inside functions/methods that should be at module level.

**Bad:**
```python
def process_data():
    import json  # Should be at top of file
    return json.dumps(data)
```

**Acceptable:** Only for expensive lazy-loading (e.g., `import pandas`, `import torch`).

---

## 2. Deep Relative Imports
Check for relative imports with multiple dots (grandparent+ imports).

**Bad:**
```python
from ...models import User  # Hard to read, fragile to restructuring
from ....services import DataService
```

**Good:**
```python
from myproject.models import User  # Absolute import from package root
from myproject.services import DataService
```

**Why:** Absolute imports are clearer, more maintainable, and don't break when files move.

---

Search the target files and report violations with file paths and line numbers. Group findings by smell type.
