#!/usr/bin/env python3
"""
Common utilities for validation hooks.

Shared helper functions used by all validators and workspace hooks.
"""
import sys
from pathlib import Path


# Files to skip (infrastructure, tests, generated files)
SKIP_PATTERNS = [
    '.claude/',
    '.git/',
    '__pycache__/',
    '.venv/',
    'venv/',
    'env/',
    'node_modules/',
    '.egg-info/',
    'vendor/',
    'dist/',
    'build/',
    'test_',
    '_test.py',
    'tests.py',
    '.pyc',
    '.pyo',
    '.so',
    'package-lock.json',
    'poetry.lock',
    'Pipfile.lock',
]


def should_skip(file_path: str) -> bool:
    """
    Check if file should be skipped from validation.

    Skips infrastructure, tests, generated files, and vendor directories.

    Args:
        file_path: Path to the file

    Returns:
        True if file should be skipped, False otherwise

    Examples:
        >>> should_skip(".claude/hooks/test.py")
        True

        >>> should_skip("tests/unit_test.py")
        True

        >>> should_skip("src/main.py")
        False
    """
    normalized = file_path.replace('\\', '/')

    for pattern in SKIP_PATTERNS:
        if pattern in normalized:
            return True

    return False


def get_extension(file_path: str) -> str:
    """
    Get file extension.

    Returns the file extension with dot (e.g., ".py").
    For files with no extension like ".gitignore", returns the full filename.

    Args:
        file_path: Path to the file

    Returns:
        Extension (with dot) or full filename for extensionless files

    Examples:
        >>> get_extension("script.py")
        ".py"

        >>> get_extension(".gitignore")
        ".gitignore"

        >>> get_extension("path/to/file.txt")
        ".txt"
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    # If no suffix and filename starts with dot, return full filename
    if not suffix and path.name.startswith('.'):
        return path.name.lower()

    return suffix


def smart_block(violations: list, category: str) -> None:
    """
    Format and block on code quality violations.

    Prints helpful error message and exits with code 2.

    Args:
        violations: List of violation strings
        category: Category name (e.g., "Code quality", "Syntax")

    Returns:
        None (exits with code 2)

    Examples:
        >>> smart_block(["Debug statement: print() at line 5"], "Code quality")
        # Outputs error message and exits with code 2
    """
    lines = ["BLOCKED: " + category, ""]
    lines.extend("  • " + v for v in violations)
    lines.append("")
    lines.append("Fix violations and retry.")

    msg = "\n".join(lines)
    print(msg, file=sys.stderr)
    sys.exit(2)


def state_block(violations: list) -> None:
    """
    Format and block on state validation violations.

    Used for anchor ceremony and state validation failures.

    Args:
        violations: List of violation strings

    Returns:
        None (exits with code 2)

    Examples:
        >>> state_block(["Anchor ceremony incomplete: missing protocol_read_timestamp"])
        # Outputs error message and exits with code 2
    """
    lines = ["BLOCKED: Anchor ceremony violation", ""]
    lines.extend("  • " + v for v in violations)
    lines.append("")
    lines.append("Invoke /kernel/anchor to reset ceremony.")

    msg = "\n".join(lines)
    print(msg, file=sys.stderr)
    sys.exit(2)


def bash_block(violations: list) -> None:
    """
    Format and block on bash validation violations.

    Used for bash safety and command validation failures.

    Args:
        violations: List of violation strings

    Returns:
        None (exits with code 2)

    Examples:
        >>> bash_block(["Bash command uses 'cd' (breaks hook path resolution)"])
        # Outputs error message and exits with code 2
    """
    lines = ["BLOCKED: Bash safety violation", ""]
    lines.extend("  • " + v for v in violations)
    lines.append("")
    lines.append("Use absolute paths, avoid cd.")

    msg = "\n".join(lines)
    print(msg, file=sys.stderr)
    sys.exit(2)
