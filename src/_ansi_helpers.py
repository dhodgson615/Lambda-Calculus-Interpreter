import re
from functools import lru_cache
from re import Pattern

ESC: str = "\x1b["
RESET: str = ESC + "0m"
HIGHLIGHT: str = ESC + "38;2;255;255;0m"
_ANSI_RE: Pattern[str] = re.compile(r"\x1b\[[0-9;]*m")


@lru_cache(maxsize=None)
def rgb(r: int, g: int, b: int) -> str:
    """Return ANSI SGR sequence for RGB color."""
    return f"{ESC}38;2;{r};{g};{b}m"


@lru_cache(maxsize=None)
def strip_ansi(s: str) -> str:
    """Strip ANSI SGR sequences from a string."""
    return _ANSI_RE.sub("", s)
