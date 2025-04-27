import re

ESC = "\x1b["
RESET = ESC + "0m"
HIGHLIGHT = ESC + "38;2;255;255;0m"
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def rgb(r: int, g: int, b: int) -> str:
    """Return ANSI SGR sequence for RGB color."""
    return f"{ESC}38;2;{r};{g};{b}m"

def strip_ansi(s: str) -> str:
    """Strip ANSI SGR sequences from a string."""
    return _ANSI_RE.sub("", s)

__all__ = ["ESC", "RESET", "HIGHLIGHT", "_ANSI_RE", "rgb", "strip_ansi"]
