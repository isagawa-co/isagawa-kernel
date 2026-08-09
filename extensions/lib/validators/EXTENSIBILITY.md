# Extensibility Guide — Adding New Validators

## Introduction

### What is a validator?

A validator is a single-purpose Python module that checks one concern (code quality, bash safety, state consistency, etc.) and returns a list of violations. Each validator lives in its own file under `lib/validators/`.

### Why modular validators?

- **Single Responsibility (SOLID):** Each validator checks exactly one thing. Adding git safety doesn't touch code quality checks.
- **Testable in isolation:** Each validator has its own `check()` function you can call directly.
- **Composable:** Workspace hooks import only the validators they need.
- **No core modifications:** Adding a new validator never requires changing existing validators or the common utilities.

### When to add a new validator

Add a new validator when you identify a repeatable check that:
1. Applies across multiple workspaces (not one-off logic)
2. Can be expressed as input → violations (pure function)
3. Doesn't duplicate an existing validator's concern

---

## Validator Signature

Every validator MUST export a `check()` function with this signature:

```python
def check(input_data, config=None) -> list[str]:
    """
    Validate input and return violations.

    Args:
        input_data: Tool input dict or string (depends on validator)
        config: Optional per-domain configuration dict

    Returns:
        List of violation strings. Empty list = pass.
    """
```

**Rules:**
- Return `[]` when input is valid (never `None`, never `True/False`)
- Each violation string should describe what went wrong and why
- `config` is optional — validators work without it but can use it for per-workspace tuning
- Validators must be pure functions — no side effects, no file writes, no state mutations

---

## Validator Template

Create a new file `lib/validators/my_new_check.py`:

```python
"""
Validator: my_new_check

Checks for [describe what this validates].
"""


def check(input_data, config=None) -> list[str]:
    """
    Check for [specific concern].

    Args:
        input_data: [describe expected input format]
        config: Optional per-domain config

    Returns:
        List of violation strings (empty = pass)

    Examples:
        >>> check("safe_input")
        []

        >>> check("dangerous_input")
        ["Violation: dangerous_input does X (expected Y)"]
    """
    violations = []

    # Your validation logic here
    if bad_condition(input_data):
        violations.append("Violation description with context")

    return violations
```

---

## Example 1: Git Safety Validator

**File:** `lib/validators/git_validation.py`

```python
"""
Validator: git_validation

Checks git commands for dangerous operations (force push, force add, etc.).
"""


def check(tool_input, config=None) -> list[str]:
    """
    Check git command safety.

    Args:
        tool_input: Dict with 'command' key containing the bash command string

    Returns:
        List of violation strings

    Examples:
        >>> check({"command": "git push origin main"})
        []

        >>> check({"command": "git push --force origin main"})
        ["Git command uses '--force' (dangerous in shared repos)"]
    """
    violations = []
    command = tool_input.get("command", "")

    if "--force" in command or "push -f " in command:
        violations.append("Git command uses '--force' (dangerous in shared repos)")

    if "git add --force" in command:
        violations.append("Git command uses '--force' with add (bypasses .gitignore)")

    if "reset --hard" in command:
        violations.append("Git reset --hard discards uncommitted changes")

    return violations
```

**Usage in a workspace hook:**

```python
from lib.validators import git_validation
from lib.validators.common import smart_block

# In your hook's main():
if tool_name == "Bash":
    command = tool_input.get("command", "")
    violations = git_validation.check({"command": command})
    if violations:
        smart_block(violations, "Git safety")
```

---

## Example 2: Test Isolation Validator

**File:** `lib/validators/test_isolation.py`

```python
"""
Validator: test_isolation

Checks test files for state leakage patterns (global state modifications,
shared mutable fixtures, etc.).
"""


def check(file_path, content=None, config=None) -> list[str]:
    """
    Check test isolation.

    Args:
        file_path: Path to the file being written/edited
        content: File content string (optional, for Write tool)

    Returns:
        List of violation strings

    Examples:
        >>> check("test_auth.py", "os.environ['DB'] = 'prod'")
        ["Modifying os.environ outside setUp/fixture (test isolation risk)"]

        >>> check("test_auth.py", "result = add(1, 2)")
        []
    """
    violations = []

    if content is None:
        return violations

    # Check for module-level env modifications
    if "os.environ[" in content:
        # Allow inside test functions and fixtures
        lines = content.split("\n")
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if "os.environ[" in stripped and not stripped.startswith("#"):
                # Check indentation — module-level has 0 indent
                if len(line) - len(stripped) == 0:
                    violations.append(
                        f"Line {i+1}: Modifying os.environ at module level "
                        "(test isolation risk)"
                    )

    # Check for global mutable state
    if "global " in content and "test_" in file_path:
        violations.append(
            "Using 'global' keyword in test file (shared mutable state)"
        )

    return violations
```

---

## Integration Checklist

When adding a new validator:

1. Create new file: `lib/validators/my_validator.py`
2. Implement `check()` function matching the signature above
3. Add module docstring and function docstring with examples
4. Test L1: `from lib.validators import my_validator` succeeds
5. Test L2: `my_validator.check(valid_input)` returns `[]`
6. Test L3: `my_validator.check(known_bad_input)` returns expected violations
7. Import in workspace hook and wire to appropriate tool event
8. Add entry to this document under "Existing Validators"

---

## Existing Validators

| Module | Concern | Input Type |
|--------|---------|------------|
| `code_quality.py` | File naming, print statements, line length | `(file_path, content)` |
| `state_validation.py` | State file consistency, required fields | `(state_data)` |
| `bash_validation.py` | Dangerous bash commands, cd usage | `(command_string)` |
| `common.py` | Shared utilities (not a validator) | N/A |

---

## Common Utilities (`common.py`)

These helpers are available for all validators and hooks:

| Function | Purpose |
|----------|---------|
| `should_skip(file_path, skip_patterns)` | Check if a file should be excluded from validation |
| `get_extension(file_path)` | Extract file extension safely |
| `smart_block(violations, category)` | Format and emit a hook block message |
| `state_block(message, fix_command)` | Emit a state-related block with fix instructions |
| `bash_block(message, safe_alternative)` | Emit a bash-related block with safe alternative |

---

## Future Validator Ideas

Good candidates for new validators:

1. **git_validation.py** — Force push, force add, reset --hard detection
2. **test_isolation.py** — Global state, module-level env vars, shared mutables
3. **performance_validation.py** — Expensive imports at module level, sleep in loops
4. **security_validation.py** — SQL injection patterns, hardcoded credentials, XSS
5. **architecture_validation.py** — Circular imports, layer boundary violations

---

## Design Principles

This system follows the [SOLID principles](https://en.wikipedia.org/wiki/SOLID):

- **S — Single Responsibility:** Each validator checks one concern
- **O — Open/Closed:** Add new validators without modifying existing ones
- **L — Liskov Substitution:** All validators share the same `check()` signature
- **I — Interface Segregation:** Hooks import only the validators they need
- **D — Dependency Inversion:** Hooks depend on the `check()` interface, not implementation details
