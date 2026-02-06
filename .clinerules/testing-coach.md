# DataBench Testing Coach Skill

## Purpose

Nudge contributors to write tests by providing guided, low-friction test
generation aligned with the project's pytest framework.

## When to Activate

Trigger this skill when:

- User says "add tests", "write tests", "test this", or similar
- User asks "did I add enough tests?" or "test coverage?"
- User modifies a Python file and asks for review
- User mentions wanting to contribute tests

## Core Principles

1. **Default to unit tests** (`@pytest.mark.unit`) - fast feedback loop
2. **Only suggest Django/DB tests when necessary** - and always ask first
3. **Keep tests focused** - one happy path + one edge case minimum
4. **Follow project conventions** - `<app>/tests/test_<module>.py` naming

---

## Workflow Steps

### Step 1: Identify the Target

Determine what code needs tests:

- If user has an active file open → use that file
- If user mentions a specific module → locate it
- If user says "my changes" → run `git diff --name-only` to find changed files

### Step 2: Determine Test Type

Check the target file to decide between unit and Django tests:

**Use `@pytest.mark.unit` (default) when:**

- File contains pure Python logic (parsers, formatters, utilities)
- No Django imports (models, views, settings)
- Examples: `raman_parser.py`, `si_formatter.py`, `fields.py`

**When a module imports Django at top-level but contains pure logic:**

- **Preferred:** Extract pure logic into a separate module (e.g., `core/gun_power.py`).  
  The Django-dependent module then imports from it, and tests import the pure module.  
  This avoids duplicating code and keeps tests fast.
- **Acceptable:** Mark the test as `@pytest.mark.django` and import directly from the Django-coupled module.
- **Not acceptable:** Copying production code into tests to force a `unit` marker.

**Use `@pytest.mark.django` when:**

- File imports Django models or settings
- File is a view (`views.py`) or model (`models.py`)
- Test requires database access
- **Always confirm with user before generating Django tests**

### Step 3: Locate or Create Test File

- Test files go in: `databench/<app>/tests/test_<module>.py`
- Create `__init__.py` in tests directory if missing
- Never use generic `tests.py` - use meaningful names

### Step 4: Generate Test Scaffolding

#### Unit Test Template

```python
"""Tests for <module_name>."""
import pytest

pytestmark = pytest.mark.unit


class Test<ClassName>:
    """Tests for <ClassName>."""

    def test_happy_path(self):
        """Test normal expected behavior."""
        # Arrange
        
        # Act
        
        # Assert
        pass

    def test_edge_case(self):
        """Test boundary or unusual input."""
        # Arrange
        
        # Act
        
        # Assert
        pass
```

#### Django Test Template

```python
"""Django tests for <module_name>."""
import pytest

pytestmark = pytest.mark.django


@pytest.fixture
def sample_fixture(db):
    """Create test data."""
    pass


class Test<ClassName>:
    """Tests for <ClassName>."""

    def test_model_behavior(self, db):
        """Test model creation and basic behavior."""
        pass

    def test_view_response(self, client):
        """Test view returns expected response."""
        pass
```

### Step 5: Run Tests

After generating tests, run the appropriate command:

```bash
# For unit tests (fast, default)
pytest -m unit

# For Django tests (only when explicitly needed)
pytest -m django

# For a specific test file
pytest stub/<app>/tests/test_<module>.py -v
```

### Step 6: Iterate

- If tests fail, help fix either the test or the code
- Suggest additional test cases for edge conditions
- Encourage parametrized tests for multiple inputs

---

## Test Gap Analysis

When user asks "did I add enough tests?", perform this check:

1. **Find changed files:**

   ```bash
   git diff --name-only HEAD~1
   ```

2. **For each changed `.py` file, check:**
   - Does `databench/<app>/tests/test_<module>.py` exist?
   - Was the test file also modified?
   - Are there any `tests.py` files (discouraged)?

3. **Report findings:**
   - List files without corresponding tests
   - Suggest which files would benefit from unit tests
   - Identify any `tests.py` files that should be renamed

---

## Quick Reference

| Scenario | Test Type | Command |
| -------- | --------- | ------- |
| Parser, formatter, utility | `unit` | `pytest -m unit` |
| Model logic | `django` | `pytest -m django` |
| View response | `django` | `pytest -m django` |
| Pure calculation | `unit` | `pytest -m unit` |

## Fixture Data Location

Place test data files in: `stub/<app>/tests/data/`

Example:

```text
stub/core/tests/data/temperature.json
```

---

## Encouraging Test Contributions

When interacting with contributors:

1. Start with the **smallest possible test** - lower barrier to entry
2. Emphasize **unit tests are fast** (~1 second feedback)
3. Show the **exact pytest command** to run their specific test
4. Celebrate when tests pass: "Tests passing - ready for PR!"
