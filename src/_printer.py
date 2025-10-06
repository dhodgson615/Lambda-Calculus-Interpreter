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

    depth = max_depth = 0

    for c in string:
        if c == "(":
            depth += 1
            max_depth = max(max_depth, depth)

        elif c == ")":
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

    o, n, l = strip_ansi(old), strip_ansi(new), min(len(old), len(new))
    i = next((k for k in range(l) if o[k] != n[k]), l)
    j = next((k for k in range(l - i) if o[-1 - k] != n[-1 - k]), l - i)
    return f"{new[:i]}{HIGHLIGHT}{new[i:len(new)-j]}{RESET}{new[len(new)-j:]}"


def format_expr(e: Expression) -> str:
    """Return the string representation of the expression, optionally
    coloring parentheses.
    """
    return (
        color_parens(str(e).replace(" ", "") if COMPACT else str(e))
        if COLOR_PARENS
        else (str(e).replace(" ", "") if COMPACT else str(e))
    )
