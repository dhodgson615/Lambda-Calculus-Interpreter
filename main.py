from __future__ import annotations

import string
import sys
from copy import deepcopy
from functools import lru_cache

from config import DELTA_ABSTRACT, SHOW_STEP_TYPE
from printer import format_expr, highlight_diff


def church(n: int) -> Abs:
    """Return the Church numeral for n."""
    body: Expr = Var("x")
    for _ in range(n):
        body = App(Var("f"), body)
    return Abs("f", Abs("x", body))


# δ‑definitions for logical connectives and arithmetic operations
DEFS_SRC = {
    "⊤": "λx.λy.x",
    "⊥": "λx.λy.y",
    "∧": "λp.λq.p q p",
    "∨": "λp.λq.p p q",
    "↓": "λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)",
    "↑": "λn.λf.λx.f (n f x)",
    "+": "λm.λn.m ↑ n",
    "*": "λm.λn.m (+ n) 0",
    "is0": "λn.n (λx.⊥) ⊤",
    "-": "λm.λn.n ↓ m",
    "≤": "λm.λn.is0 (- m n)",
    "pair": "λx.λy.λf.f x y",
}

DEFS = {}  # δ‑definitions for Church numerals


class Expr:
    """Base class for all expressions."""

    def __repr__(self) -> str:
        """Return the string representation of the expression."""
        return self.__str__()

    def __str__(self) -> str:
        """Return the string representation of the expression."""
        return ""


class Var(Expr):
    """Variable class for λ calculus."""

    __slots__ = ("name",)

    def __repr__(self) -> str:
        """Return the string representation of the variable."""
        return self.__str__()

    def __hash__(self) -> int:
        """Return the hash of the variable."""
        return hash(self.name)

    def __init__(self, name: str) -> None:
        """Initialize a variable with a name."""
        self.name: str = name

    def __str__(self) -> str:
        """Return the string representation of the variable."""
        return self.name


class Abs(Expr):
    """Abstraction class for λ calculus."""

    __slots__ = ("param", "body")

    def __repr__(self) -> str:
        """Return the string representation of the abstraction."""
        return self.__str__()

    def __hash__(self) -> int:
        """Return the hash of the abstraction."""
        return hash((self.param, self.body))

    def __init__(self, param: str, body: Expr) -> None:
        """Initialize an abstraction with a parameter and body."""
        self.param = param
        self.body = body

    def __str__(self) -> str:
        """Return the string representation of the abstraction."""
        b = str(self.body)
        if isinstance(self.body, Abs):
            b = f"({b})"
        return f"λ{self.param}.{b}"


class App(Expr):
    """Application class for λ calculus."""

    __slots__ = ("fn", "arg")

    def __repr__(self) -> str:
        """Return the string representation of the application."""
        return self.__str__()

    def __hash__(self) -> int:
        """Return the hash of the application."""
        return hash((self.fn, self.arg))

    def __init__(self, fn: Expr, arg: Expr) -> None:
        """Initialize an application with a function and argument."""
        self.fn = fn
        self.arg = arg

    def __str__(self) -> str:
        """Return the string representation of the application."""
        if isinstance(self.fn, Abs):
            fn_s = f"({self.fn})"
        else:
            fn_s = str(self.fn)
        if isinstance(self.arg, (Abs, App)):
            arg_s = f"({self.arg})"
        else:
            arg_s = str(self.arg)
        return f"{fn_s} {arg_s}"


class Parser:
    """Parser for λ calculus expressions."""

    def __init__(self, src: str) -> None:
        """Initialize the parser with the source string."""
        self.src = src
        self.i = 0
        self.n = len(src)

    def peek(self) -> str:
        """Return the next character in the source string without
           consuming it.
        """
        if self.i < self.n:
            return self.src[self.i]
        else:
            return ""

    def consume(self) -> str:
        """Consume the next character in the source string and return
           it.
        """
        c = self.peek()
        self.i += 1
        return c

    def skip_ws(self) -> None:
        """Skip whitespace characters in the source string."""
        while self.peek().isspace():
            self.consume()

    def parse(self) -> Expr:
        """Parse the source string into an expression."""
        e = self.parse_expr()
        self.skip_ws()
        if self.i < self.n:
            raise SyntaxError(f"Unexpected '{self.peek()}' at pos {self.i}")
        return e

    def parse_expr(self) -> Expr:
        """Parse an expression from the source string."""
        self.skip_ws()
        if self.peek() == "λ":
            return self.parse_abs()
        else:
            return self.parse_app()

    def parse_abs(self) -> Abs:
        """Parse an abstraction from the source string."""
        self.consume()  # 'λ'
        var = self.parse_varname()
        self.skip_ws()
        if self.consume() != ".":
            raise SyntaxError("Expected '.' after λ parameter")
        body = self.parse_expr()
        return Abs(var, body)

    def parse_app(self) -> Expr:
        """Parse an application from the source string."""
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
        """Parse an atomic expression from the source string."""
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
        """Parse a number from the source string."""
        ds = []
        while self.peek().isdigit():
            ds.append(self.consume())
        return int("".join(ds))

    def parse_varname(self) -> str:
        """Parse a variable name from the source string."""
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


@lru_cache(maxsize=None)
def free_vars(e: Expr) -> set[str]:
    """Return the set of free variables in the expression."""
    if isinstance(e, Var):
        return {e.name}
    if isinstance(e, Abs):
        return free_vars(e.body) - {e.param}
    if isinstance(e, App):
        return free_vars(e.fn) | free_vars(e.arg)
    return set()


def fresh_var(used: set[str]) -> str:
    """Generate a fresh variable name that is not in the used set."""
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


def subst(e: Expr, var: str, val: Expr) -> Expr:
    """Substitute all free occurrences of var in e with val."""
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


def reduce_once(e: Expr) -> tuple[Expr, str] | None:
    """Reduce a single step of the expression."""
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


def abstract_numerals(e: Expr) -> Expr:
    """Abstract Church numerals to digits."""
    if isinstance(e, Abs) and isinstance(e.body, Abs):
        fparam = e.param
        xparam = e.body.param
        body = e.body.body
        count = 0
        cur = body
        while (
            isinstance(cur, App)
            and isinstance(cur.fn, Var)
            and cur.fn.name == fparam
        ):
            count += 1
            cur = cur.arg
        if isinstance(cur, Var) and cur.name == xparam:
            return Var(str(count))
    if isinstance(e, Abs):
        return Abs(e.param, abstract_numerals(e.body))
    if isinstance(e, App):
        return App(abstract_numerals(e.fn), abstract_numerals(e.arg))
    return e


def normalize(expr: Expr) -> None:
    """Normalize the expression to its normal form."""
    step = 0
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


def main() -> None:
    """Main function to run the λ calculus interpreter."""
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
