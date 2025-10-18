from functools import lru_cache

from _ansi_helpers import HIGHLIGHT, RESET, rgb, strip_ansi
from _config import COLOR_DIFF, COLOR_PARENS, COMPACT
from _expressions import Expression


@lru_cache(maxsize=None)
def strip_spaces(s: str) -> str:
    """Strip spaces from the string representation of the expression."""
    return s.replace(" ", "") if COMPACT else s


@lru_cache(maxsize=None)
def apply_color(d: int, d_max: int, c: str) -> str:
    """Apply color to a character based on the current depth and max depth."""
    return (
        rgb(
            0,
            int(
                128 * (1 - ((d - 1) / (d_max - 1) if d_max > 1 else 0))
                + 255 * ((d - 1) / (d_max - 1) if d_max > 1 else 0)
            ),
            int(
                128 * (1 - ((d - 1) / (d_max - 1) if d_max > 1 else 0))
                + 255 * ((d - 1) / (d_max - 1) if d_max > 1 else 0)
            ),
        )
        + c
        + RESET
    )


def color_parens(s: str) -> str:
    """Color parentheses by nesting level."""
    if not COLOR_PARENS:
        return s

    depths, depth, max_depth = [], 0, 0

    for c in s:
        depth, max_depth = (
            (depth + 1, max(max_depth, depth + 1))
            if c == "("
            else (depth - 1, max_depth) if c == ")" else (depth, max_depth)
        )

        depths.append(depth)

    return "".join(
        apply_color(depths[idx], max_depth, c) if c in "()" else c
        for idx, c in enumerate(s)
    )


def highlight_diff(o: str, n: str) -> str:
    """Highlight the difference between two strings."""
    if not COLOR_DIFF:
        return n

    o, n = strip_ansi(o), strip_ansi(n)
    l = min(len(o), len(n))
    i = next((k for k in range(l) if o[k] != n[k]), l)
    j = next((k for k in range(l - i) if o[-1 - k] != n[-1 - k]), l - i)
    return f"{n[:i]}{HIGHLIGHT}{n[i:len(n)-j]}{RESET}{n[len(n)-j:]}"


def format_expr(e: Expression) -> str:
    """Return the string representation of the expression, optionally
    coloring parentheses.
    """
    return (
        color_parens(str(e).replace(" ", "") if COMPACT else str(e))
        if COLOR_PARENS
        else (str(e).replace(" ", "") if COMPACT else str(e))
    )
