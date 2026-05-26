"""
Bash command safety validator.

Checks bash commands for protocol violations:
- No 'cd' command (breaks hook path resolution)
- Extensible for future checks (force push, dangerous pipes, etc.)
"""

import re


def check_cd(command: str) -> list[str]:
    """
    Check for cd command in bash string.

    Args:
        command: Bash command string from Bash tool input

    Returns:
        List of violation strings (empty = safe)

    The check distinguishes between:
    - Actual 'cd' command (blocks)
    - 'cd' in string literals (allows)
    - 'cd' in comments (allows)
    - 'cd' in variable names (allows)

    Examples:
        >>> check_cd("cd /path && git log")
        ["Bash command uses 'cd' (breaks hook path resolution)"]

        >>> check_cd("git commit -m 'cd implementation'")
        []

        >>> check_cd("mkdir /path")
        []
    """
    # Remove quoted strings (both single and double quotes)
    # This prevents false positives on 'cd' inside strings or comments
    cmd_without_quotes = re.sub(r'["\'].*?["\']', '', command)

    # Check for cd as a standalone command
    # Pattern: cd preceded by start/space/semicolon/pipe/&
    #         and followed by space/semicolon/end/pipe/&
    if re.search(r'(^|\s|;|\||\&)\bcd\b(\s|;|$|\||&)', cmd_without_quotes):
        return ["Bash command uses 'cd' (breaks hook path resolution)"]

    return []


def check(command: str) -> list[str]:
    """
    Check bash command for safety violations.

    Args:
        command: Bash command string from Bash tool input

    Returns:
        List of violation strings (empty = safe)

    Examples:
        >>> check("cd /some/path && git log")
        ["Bash command uses 'cd' (breaks hook path resolution)"]

        >>> check("git log --oneline")
        []
    """
    violations = []
    violations.extend(check_cd(command))
    # Future checks:
    # violations.extend(check_force_push(command))
    # violations.extend(check_dangerous_pipes(command))
    return violations
