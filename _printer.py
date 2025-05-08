from _ansi_helpers import HIGHLIGHT, RESET, rgb, strip_ansi
from _config import COLOR_DIFF, COLOR_PARENS, COMPACT
from _expressions import Expr


def strip_spaces(s: str) -> str:
    """Strip spaces from the string representation of the expression."""
    if COMPACT:
        return s.replace(" ", "")
    return s


def color_parens(s: str) -> str:
    """Color parentheses by nesting level."""
    if not COLOR_PARENS:
        return s

    # first pass: find max nesting depth
    depth = 0
    max_depth = 0
    for ch in s:
        if ch == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == ")":
            depth -= 1

    # second pass: insert ANSI colors
    result = ""
    depth = 0
    for ch in s:
        if ch == "(":
            depth += 1
            ratio = (depth - 1) / (max_depth - 1) if max_depth > 1 else 0
            r = int(0 * (1 - ratio) + 0 * ratio)
            g = int(128 * (1 - ratio) + 255 * ratio)
            b = int(128 * (1 - ratio) + 255 * ratio)
            result += rgb(r, g, b) + ch + RESET
        elif ch == ")":
            ratio = (depth - 1) / (max_depth - 1) if max_depth > 1 else 0
            r = int(0 * (1 - ratio) + 0 * ratio)
            g = int(128 * (1 - ratio) + 255 * ratio)
            b = int(128 * (1 - ratio) + 255 * ratio)
            result += rgb(r, g, b) + ch + RESET
            depth -= 1
        else:
            result += ch

    return result


def highlight_diff(old: str, new: str) -> str:
    """Highlight the difference between two strings."""
    if not COLOR_DIFF:
        return new

    o = strip_ansi(old)
    n = strip_ansi(new)
    L = min(len(o), len(n))

    # find common prefix length
    i = 0
    while i < L and o[i] == n[i]:
        i += 1

    # find common suffix length
    j = 0
    while j < (L - i) and o[-1 - j] == n[-1 - j]:
        j += 1

    start = new[:i]
    mid = new[i : len(new) - j]
    end = new[len(new) - j :]
    return f"{start}{HIGHLIGHT}{mid}{RESET}{end}"


def format_expr(e: Expr) -> str:
    """Format any expression for pretty printing."""
    text = str(e)
    text = strip_spaces(text)
    return color_parens(text)
