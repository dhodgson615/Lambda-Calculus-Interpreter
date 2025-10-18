from functools import cache
from re import compile

ESC = "\x1b["
RESET = ESC + "0m"
HIGHLIGHT = ESC + "38;2;255;255;0m"
_ANSI_RE = compile(r"\x1b\[[0-9;]*m")


@cache
def rgb(r: int, g: int, b: int) -> str:
    """Return ANSI SGR sequence for RGB color."""
    return f"{ESC}38;2;{r};{g};{b}m"


@lru_cache(maxsize=None)
def strip_ansi(s: str) -> str:
    """Strip ANSI SGR sequences from a string."""
    return _ANSI_RE.sub("", s)
