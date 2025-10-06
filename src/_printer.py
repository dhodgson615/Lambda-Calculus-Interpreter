from functools import lru_cache

from _ansi_helpers import HIGHLIGHT, RESET, rgb, strip_ansi
from _config import COLOR_DIFF, COLOR_PARENS, COMPACT
from _expressions import Expression


@lru_cache(maxsize=None)
def strip_spaces(s: str) -> str:
    """Strip spaces from the string representation of the expression."""
    return s.replace(" ", "") if COMPACT else s


@lru_cache(maxsize=None)
def apply_color(depth: int, max_depth: int, ch: str) -> str:
    """Apply color to a character based on the current depth and max depth."""
    ratio = (depth - 1) / (max_depth - 1) if max_depth > 1 else 0
    r = int(0 * (1 - ratio) + 0 * ratio)
    g = int(128 * (1 - ratio) + 255 * ratio)
    b = int(128 * (1 - ratio) + 255 * ratio)
    return rgb(r, g, b) + ch + RESET


def color_parens(string: str) -> str:
    """Color parentheses by nesting level."""
    if not COLOR_PARENS:
        return string

    # first pass: find max nesting depth
    depth = 0
    max_depth = 0

    for char in string:
        if char == "(":
            depth += 1
            max_depth = max(max_depth, depth)

        elif char == ")":
            depth -= 1

    # second pass: insert ANSI colors
    result = ""
    depth = 0

    for char in string:
        if char == "(":
            depth += 1
            result += apply_color(depth, max_depth, char)

        elif char == ")":
            result += apply_color(depth, max_depth, char)
            depth -= 1

        else:
            result += char

    return result


def highlight_diff(old: str, new: str) -> str:
    """Highlight the difference between two strings."""
    if not COLOR_DIFF:
        return new

    o: str = strip_ansi(old)
    n: str = strip_ansi(new)
    l: int = min(len(o), len(n))

    # find the common prefix length
    i: int = 0
    while i < l and o[i] == n[i]:
        i += 1

    # find common suffix length
    j: int = 0
    while j < (l - i) and o[-1 - j] == n[-1 - j]:
        j += 1

    start = new[:i]
    mid = new[i : len(new) - j]
    end = new[len(new) - j :]

    return f"{start}{HIGHLIGHT}{mid}{RESET}{end}"


def format_expr(expression: Expression) -> str:
    """Format any expression for pretty printing."""
    text = str(expression)
    if COMPACT:
        text = text.replace(" ", "")
    if COLOR_PARENS:
        text = color_parens(text)

    return text
