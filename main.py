""" λ Calculus Interpreter featuring:

    * Normal‑order β‑reduction

    * δ‑reduction from a global definitions map

    * Numeric literals → Church numerals

    * Colorful parentheses, diff highlighting, step‑type
      labels, delta‑abstraction of numerals, compact mode

    * ANSI SGR support

    * Python 3.10+ required

Usage:

    $ python3 lc.py "(λx.x) (λy.y)"

Or when run without arguments:

    $ python3 lc.py
    λ‑expr> (λx.x) (λy.y)


    This interpreter is a toy project and not intended for production use.
    It is meant for educational purposes and to demonstrate the concepts of
    λ calculus.  It is not optimized for performance or security.  Use at
    your own risk.  This code is a work in progress and may contain bugs or
    incomplete features.  Please report any issues or suggestions to the
    author.

Copyright (C) 2025 by Dylan Hodgson """

# =========================================================================== #
# ---------------- Imports -------------------------------------------------- #
# =========================================================================== #

import re                 # regex
import string             # for generating fresh variable names
import sys                # for recursion limit
from copy import deepcopy # for deep copy of expressions

# =========================================================================== #
# ---------------- Configuration Flags -------------------------------------- #
# =========================================================================== #

COLOR_PARENS   = True   # color‑matched parentheses by nesting level
COLOR_DIFF     = False  # highlight the subterm(s) that changed
SHOW_STEP_TYPE = True   # print “(δ)” or “(β)” after each step
COMPACT        = True   # drop all spaces in printed terms
DELTA_ABSTRACT = True   # after normal form, abstract Church numerals to digits

# =========================================================================== #
# ---------------- Constants & Globals -------------------------------------- #
# =========================================================================== #

# ANSI helpers
ESC = "\x1b["
RESET = ESC + "0m"
HIGHLIGHT = ESC + "38;2;255;255;0m"

# regex to strip ANSI SGR sequences
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def rgb(r, g, b) -> str:
    return f"{ESC}38;2;{r};{g};{b}m"


def strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


# Increase recursion limit for deep reductions
sys.setrecursionlimit(2**31 - 1)

# =========================================================================== #
# -------- Church Numeral Helper & Definitions ------------------------------ #
# =========================================================================== #


# Church numerals are defined as:
#   0 = λf.λx.x
#   1 = λf.λx.f x
#   2 = λf.λx.f (f x)
#   3 = λf.λx.f (f (f x))
#   n = λf.λx.f (f (...(f x)))  (n times)


def church(n: int):
    body = Var("x")
    for _ in range(n):
        body = App(Var("f"), body)

    return Abs("f", Abs("x", body))


DEFS_SRC = {"⊤"    : "λx.λy.x",
            "⊥"    : "λx.λy.y",
            "∧"    : "λp.λq.p q p",
            "∨"    : "λp.λq.p p q",
            "↓"    : "λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)",
            "↑"    : "λn.λf.λx.f (n f x)",
            "+"    : "λm.λn.m ↑ n",
            "*"    : "λm.λn.m (+ n) 0",
            "is0"  : "λn.n (λx.⊥) ⊤",
            "-"    : "λm.λn.n ↓ m",
            "≤"    : "λm.λn.is0 (- m n)",
            "pair" : "λx.λy.λf.f x y"}

DEFS = {}


# =========================================================================== #
# -------- AST Definitions & Pretty‑Printing -------------------------------- #
# =========================================================================== #


# Forward‐declare Parser so DEFS_SRC can be parsed immediately
class Parser:
    pass


# Abstract syntax tree (AST) for λ calculus
class Expr:
    pass


# Base class for all expressions
class Var(Expr):
    __slots__ = ("name")

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


# Variable class for Church numerals
class Abs(Expr):
    __slots__ = ("param", "body")

    def __init__(self, param, body):
        self.param = param
        self.body  = body

    def __str__(self):
        b = str(self.body)

        if isinstance(self.body, Abs):
            b = f"({b})"

        return f"λ{self.param}.{b}"


# Application class for function application
class App(Expr):
    __slots__ = ("fn", "arg")

    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def __str__(self):
        if isinstance(self.fn, Abs):
            fn_s = f"({self.fn})"
        else:
            fn_s = str(self.fn)

        if isinstance(self.arg, (Abs, App)):
            arg_s = f"({self.arg})"
        else:
            arg_s = str(self.arg)

        return f"{fn_s} {arg_s}"


# =========================================================================== #
# -------- Parser ----------------------------------------------------------- #
# =========================================================================== #


# Parser for λ calculus expressions
class Parser:
    def __init__(self, src: str):
        self.src = src
        self.i   = 0
        self.n   = len(src)

    def peek(self):
        if self.i < self.n:
            return self.src[self.i]
        else:
            return ""

    def consume(self):
        c = self.peek()
        self.i += 1

        return c

    def skip_ws(self):
        while self.peek().isspace():
            self.consume()

    def parse(self) -> Expr:
        e = self.parse_expr()
        self.skip_ws()

        if self.i < self.n:
            raise SyntaxError(f"Unexpected '{self.peek()}' at pos {self.i}")

        return e

    def parse_expr(self) -> Expr:
        self.skip_ws()

        if self.peek() == "λ":
            return self.parse_abs()
        else:
            return self.parse_app()

    def parse_abs(self) -> Abs:
        self.consume()  # 'λ'
        var = self.parse_varname()
        self.skip_ws()

        if self.consume() != ".":
            raise SyntaxError("Expected '.' after λ parameter")

        body = self.parse_expr()

        return Abs(var, body)

    def parse_app(self) -> Expr:
        self.skip_ws()
        atom = self.parse_atom()
        self.skip_ws()
        args = []

        while True:
            nxt = self.peek()

            if nxt == "" or nxt in ").":
                break

            if nxt == ".":
                break

            args.append(self.parse_atom())
            self.skip_ws()

        e = atom

        for a in args:
            e = App(e, a)

        return e

    def parse_atom(self) -> Expr:
        self.skip_ws()
        ch = self.peek()

        if ch == "(":
            self.consume()
            e = self.parse_expr()
            self.skip_ws()
            if self.consume() != ")":
                raise SyntaxError("Expected ')'")

            return e

        elif ch.isdigit():
            num = self.parse_number()
            return church(num)
        else:
            name = self.parse_varname()
            return Var(name)

    def parse_number(self) -> int:
        ds = []

        while self.peek().isdigit():
            ds.append(self.consume())

        return int("".join(ds))

    def parse_varname(self) -> str:
        if not self.peek() or self.peek().isspace() or self.peek() in "().λ":
            raise SyntaxError(
                f"Invalid var start '{self.peek()}' at pos {self.i}"
            )

        chars = []

        while True:
            ch = self.peek()
            if not ch or ch.isspace() or ch in "().λ":
                break

            chars.append(self.consume())

        return "".join(chars)


# parse δ‑definitions
for nm, src in DEFS_SRC.items():
    DEFS[nm] = Parser(src).parse()


# =========================================================================== #
# -------- Substitution & α‑Conversion -------------------------------------- #
# =========================================================================== #


# α‑conversion: rename bound variables to avoid name capture
def free_vars(e: Expr) -> set[str]:
    if isinstance(e, Var):
        return {e.name}

    if isinstance(e, Abs):
        return free_vars(e.body) - {e.param}

    if isinstance(e, App):
        return free_vars(e.fn) | free_vars(e.arg)

    return set()


# Generate a fresh variable name that is not in the used set
def fresh_var(used: set[str]) -> str:
    for base in string.ascii_lowercase:
        if base not in used:
            return base

    i = 1

    while True:
        for base in string.ascii_lowercase:
            cand = f"{base}{i}"

            if cand not in used:
                return cand

        i += 1


# Substitution: replace all free occurrences of var in e with val
def subst(e: Expr, var: str, val: Expr) -> Expr:
    if isinstance(e, Var):
        if e.name == var:
            return deepcopy(val)
        else:
            return Var(e.name)

    if isinstance(e, Abs):
        if e.param == var:
            return Abs(e.param, e.body)

        if e.param in free_vars(val):
            used = free_vars(e.body) | free_vars(val) | {e.param, var}
            np = fresh_var(used)
            renamed = subst(e.body, e.param, Var(np))
            return Abs(np, subst(renamed, var, val))
        else:
            return Abs(e.param, subst(e.body, var, val))

    if isinstance(e, App):
        return App(subst(e.fn, var, val), subst(e.arg, var, val))

    raise TypeError("Unknown Expr in subst")


# =========================================================================== #
# -------- Reduction Engine (β + δ) ----------------------------------------- #
# =========================================================================== #


# Reduce a single step of the expression
def reduce_once(e: Expr):
    # δ‑step
    if isinstance(e, Var) and e.name in DEFS:
        return deepcopy(DEFS[e.name]), "δ"

    # β‑step
    if isinstance(e, App) and isinstance(e.fn, Abs):
        return subst(e.fn.body, e.fn.param, e.arg), "β"

    # recurse fn
    if isinstance(e, App):
        res = reduce_once(e.fn)

        if res:
            ne, typ = res
            return App(ne, e.arg), typ

        res = reduce_once(e.arg)

        if res:
            ne, typ = res
            return App(e.fn, ne), typ

        return None

    # recurse body of Abs
    if isinstance(e, Abs):
        res = reduce_once(e.body)
        if res:
            nb, typ = res
            return Abs(e.param, nb), typ

        return None

    return None


# =========================================================================== #
# -------- Helpers for formatting, coloring, diffing, abstraction ----------- #
# =========================================================================== #


# Strip spaces from the string representation of the expression
def strip_spaces(s: str) -> str:
    if COMPACT:
        s = s.replace(" ", "")

    return s


# Color parentheses by nesting level
def color_parens(s: str) -> str:
    if not COLOR_PARENS:
        return s

    depth = 0
    maxd  = 0

    for c in s:
        if c == "(":
            depth += 1
            maxd = max(maxd, depth)
        elif c == ")":
            depth -= 1

    out   = ""
    depth = 0

    for c in s:
        if c == "(":
            depth += 1

            if maxd > 1:
                ratio = (depth - 1) / (maxd - 1)
            else:
                ratio = 0

            r = int(  0 * (1 - ratio) +   0 * ratio)
            g = int(128 * (1 - ratio) + 255 * ratio)
            b = int(128 * (1 - ratio) + 255 * ratio)
            out += rgb(r, g, b) + c + RESET

        elif c == ")":
            if maxd > 1:
                ratio = (depth - 1) / (maxd - 1)
            else:
                ratio = 0

            r = int(  0 * (1 - ratio) +   0 * ratio)
            g = int(128 * (1 - ratio) + 255 * ratio)
            b = int(128 * (1 - ratio) + 255 * ratio)

            out += rgb(r, g, b) + c + RESET
            depth -= 1

        else:
            out += c

    return out


# Highlight the difference between two strings
def highlight_diff(old: str, new: str) -> str:
    if not COLOR_DIFF:
        return new

    o = strip_ansi(old)
    n = strip_ansi(new)
    i = 0
    L = min(len(o), len(n))

    while i < L and o[i] == n[i]:
        i += 1

    j = 0

    while j < L - i and o[-1 - j] == n[-1 - j]:
        j += 1

    start = new[:i]
    mid   = new[i:len(new) - j]
    end   = new[len(new) - j:]

    return start + HIGHLIGHT + mid + RESET + end


# δ‑abstraction: replace λf.λx.f(f(...x)) with a numeral
def abstract_numerals(e: Expr) -> Expr:
    # detect λf.λx.f(f(...x))
    if isinstance(e, Abs) and isinstance(e.body, Abs):
        fparam = e.param
        xparam = e.body.param
        body   = e.body.body
        count  = 0
        cur    = body

        while (isinstance(cur, App) and isinstance(cur.fn, Var)
               and cur.fn.name == fparam):
            count += 1
            cur = cur.arg

        if isinstance(cur, Var) and cur.name == xparam:
            return Var(str(count))

    if isinstance(e, Abs):
        return Abs(e.param, abstract_numerals(e.body))

    if isinstance(e, App):
        return App(abstract_numerals(e.fn), abstract_numerals(e.arg))

    return e


# Colorize the expression for pretty printing
def format_expr(e: Expr) -> str:
    s = str(e)
    s = strip_spaces(s)

    return color_parens(s)


# =========================================================================== #
# -------- Normalization Loop ----------------------------------------------- #
# =========================================================================== #


# Normalize the expression to its normal form
def normalize(expr: Expr):
    step        = 0
    prev_render = format_expr(expr)

    print(f"Step {step}: {prev_render}")

    while True:
        res = reduce_once(expr)

        if not res:
            print("→ normal form reached.")
            break

        expr, stype = res
        step += 1
        rend = format_expr(expr)
        rend = highlight_diff(prev_render, rend)

        if SHOW_STEP_TYPE:
            label = f" ({stype})"
        else:
            label = ""

        print(f"Step {step}{label}: {rend}")
        prev_render = rend

    if DELTA_ABSTRACT:
        abstracted = abstract_numerals(expr)
        print("\nδ‑abstracted: " + format_expr(abstracted) + "\n")


# =========================================================================== #
# -------------------------------- Main CLI --------------------------------- #
# =========================================================================== #


def main():
    # Check if the script is run with a filename argument
    if len(sys.argv) > 1:
        src = " ".join(sys.argv[1:])
    else:
        src = input("λ‑expr> ")


    try:
        tree = Parser(src).parse()
    except SyntaxError as e:
        sys.exit(f"Parse error: {e}")

    normalize(tree)


if __name__ == "__main__":
    main()
