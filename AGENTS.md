# Agent Guidelines

This file contains project-wide style and coding preferences for AI coding assistants.

## Python Imports

**CRITICAL: Imports must ONLY appear at the top of a file, NEVER inline within functions or methods.**

This rule has NO exceptions. Inline imports cause maintenance issues and violate project standards. Before writing any import statement, verify it is at the top of the file with other imports.

Imports should be grouped into three blocks, separated by a blank line:

1. **Standard library** - imports from Python's standard library
2. **Third-party packages** - imports from external dependencies
3. **Local imports** - imports from within this codebase

Within each block, imports should be ordered alphabetically.

When adding a new import, follow these rules. To reduce diff noise, do not reorder existing imports that don't follow these rules - instead gently push towards this goal over time.

Example:

```python
import json
import logging
from typing import Optional

from django.conf import settings
from django.http import HttpRequest
import requests

```

## Code Formatting and Linting

Before committing Python code, run the following tools and ensure they pass:

1. **black** - Code formatter (line length 88)

   ```bash
   black --line-length=88 <files>
   ```

   Accept all reformatting changes from black.

2. **ruff** - Linter

   ```bash
   ruff check --target-version py312 <files>
   ```

   Ensure no lint errors before committing.

3. **pyright** - Type checker

   ```bash
   pyright
   ```

   Prefer correct type annotations (`Optional`, union types, `cast()`, type guards) over suppression comments. Only use `# type: ignore[error-code]` when proper typing is impossible or disproportionately expensive — e.g., Django dynamic attributes, incomplete third-party stubs. Always include the specific error code and a brief reason.