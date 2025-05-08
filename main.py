from __future__ import annotations

import string
import sys
from copy import deepcopy

from _config import DELTA_ABSTRACT, SHOW_STEP_TYPE
from _expressions import Abs, App, Expr, Var
from _parser import Parser
from _printer import format_expr, highlight_diff

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


for name, src in DEFS_SRC.items():
    DEFS[name] = Parser(src).parse()


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
    """Main function to run the λ calculus interpreter. Can take an
    argument or prompt for input.
    """
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
