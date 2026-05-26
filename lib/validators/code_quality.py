#!/usr/bin/env python3
"""
Code Quality Validator - Detects common code quality violations.

This module provides a unified code quality check interface for all validator
domains. It detects:
- Debug statements (print, console.log, debugger, etc.)
- Hardcoded secrets (password, api_key, etc.)
- Wildcard imports (from X import *)
- Skipped tests (.skip, @pytest.mark.skip, xit, etc.)
- File size exceeding 300 lines
"""

import re
from pathlib import Path

# Debug statement patterns by file extension
DEBUG_PATTERNS = {
    '.py': [
        r'^\s*print\s*\(',
        r'^\s*pprint\s*\(',
    ],
    '.js': [
        r'^\s*console\.(log|debug|info|warn|error)\s*\(',
        r'^\s*debugger\s*;?',
    ],
    '.ts': [
        r'^\s*console\.(log|debug|info|warn|error)\s*\(',
        r'^\s*debugger\s*;?',
    ],
    '.tsx': [
        r'^\s*console\.(log|debug|info|warn|error)\s*\(',
        r'^\s*debugger\s*;?',
    ],
    '.jsx': [
        r'^\s*console\.(log|debug|info|warn|error)\s*\(',
        r'^\s*debugger\s*;?',
    ],
    '.go': [
        r'^\s*fmt\.Print(ln|f)?\s*\(',
        r'^\s*log\.Print(ln|f)?\s*\(',
    ],
    '.rs': [
        r'^\s*println!\s*\(',
        r'^\s*dbg!\s*\(',
    ],
    '.java': [
        r'^\s*System\.out\.print(ln)?\s*\(',
    ],
}

# Secret patterns (all languages)
SECRET_PATTERNS = [
    r'password\s*=\s*["\'][^"\']+["\']',
    r'secret\s*=\s*["\'][^"\']+["\']',
    r'api_key\s*=\s*["\'][^"\']+["\']',
    r'apikey\s*=\s*["\'][^"\']+["\']',
    r'token\s*=\s*["\'][^"\']+["\']',
    r'AWS_SECRET',
    r'PRIVATE_KEY\s*=',
]

# Wildcard import patterns
WILDCARD_PATTERNS = {
    '.py': [r'from\s+\S+\s+import\s+\*'],
    '.js': [r'import\s+\*\s+from'],
    '.ts': [r'import\s+\*\s+from'],
}

# Skipped test patterns
SKIP_TEST_PATTERNS = [
    r'\.skip\s*\(',
    r'@pytest\.mark\.skip',
    r'\bxit\s*\(',
    r'\bxdescribe\s*\(',
    r'@Ignore',
    r'#\s*\[ignore\]',
]

# Maximum allowed file lines
MAX_FILE_LINES = 300


def get_extension(file_path: str) -> str:
    """Get file extension from path."""
    return Path(file_path).suffix.lower()


def check_debug_statements(content: str, ext: str) -> list:
    """Check for debug statements based on file extension."""
    violations = []
    patterns = DEBUG_PATTERNS.get(ext, [])

    for i, line in enumerate(content.split('\n'), 1):
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(f"Debug statement detected at line {i}")
                break

    return violations


def check_secrets(content: str) -> list:
    """Check for hardcoded secrets (language-agnostic)."""
    violations = []

    for i, line in enumerate(content.split('\n'), 1):
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(f"Hardcoded secret detected at line {i}")
                break

    return violations


def check_wildcard_imports(content: str, ext: str) -> list:
    """Check for wildcard imports (language-specific)."""
    violations = []
    patterns = WILDCARD_PATTERNS.get(ext, [])

    for i, line in enumerate(content.split('\n'), 1):
        for pattern in patterns:
            if re.search(pattern, line):
                violations.append(f"Wildcard import at line {i}")
                break

    return violations


def check_skipped_tests(content: str, file_path: str) -> list:
    """Check for skipped tests (only in test files)."""
    # Only check test files
    if not any(p in file_path.lower() for p in ['test', 'spec']):
        return []

    violations = []

    for i, line in enumerate(content.split('\n'), 1):
        for pattern in SKIP_TEST_PATTERNS:
            if re.search(pattern, line):
                violations.append(f"Skipped test at line {i}")
                break

    return violations


def check_file_size(content: str) -> list:
    """Check that file doesn't exceed maximum line count."""
    lines = content.count('\n') + 1
    if lines > MAX_FILE_LINES:
        return [f"File exceeds {MAX_FILE_LINES} lines ({lines} lines) — consider breaking into modules"]
    return []


def check(file_path: str, content: str) -> list:
    """
    Check code for quality violations.

    Args:
        file_path: Path to the file being checked
        content: File content as string

    Returns:
        List of violation strings (empty list = no violations)

    Examples:
        >>> check("test.py", "import os")
        []

        >>> check("test.py", "x = 1")
        []

        >>> len(check("test.py", "print('')")) > 0
        True
    """
    violations = []
    ext = get_extension(file_path)

    # Run all checks
    violations.extend(check_debug_statements(content, ext))
    violations.extend(check_secrets(content))
    violations.extend(check_wildcard_imports(content, ext))
    violations.extend(check_skipped_tests(content, file_path))
    violations.extend(check_file_size(content))

    return violations
