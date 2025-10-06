from __future__ import annotations

from functools import lru_cache
from sys import argv, exit

from _config import DELTA_ABSTRACT, SHOW_STEP_TYPE
from _defs import DEFS
from _expressions import (Abstraction, Application, Expression, Variable,
                          abstract, apply, to_var)
from _parser import Parser
from _printer import format_expr, highlight_diff
from _reduce import reduce_once


@lru_cache(maxsize=None)
def is_church_numeral(e: Expression) -> bool:
    """Check if the expression is a Church numeral."""
    if isinstance(e, Abstraction) and isinstance(e.body, Abstraction):
        fpar = e.param
        bpar = e.body.param
        b = e.body.body
        curr = b

        while (
            isinstance(curr, Application)
            and isinstance(curr.fn, Variable)
            and curr.fn.name == fpar
        ):
            curr = curr.arg

        return isinstance(curr, Variable) and curr.name == bpar

    return False


def count_applications(e: Expression) -> int:
    """Count the number of applications in a Church numeral."""
    if not (isinstance(e, Abstraction) and isinstance(e.body, Abstraction)):
        return 0

    n, curr = 0, e.body.body

    while (
        isinstance(curr, Application)
        and isinstance(curr.fn, Variable)
        and curr.fn.name == e.param
    ):
        n, curr = n + 1, curr.arg

    return n


def abstract_numerals(e: Expression) -> Expression:
    """Replace Church numerals with their integer equivalents using an
    iterative approach.
    """
    stack: list[tuple[Expression, str]] = []
    result_map: dict[int, Expression] = {}
    stack.append((e, "visit"))

    while stack:
        expr, action = stack.pop()
        expr_id = id(expr)

        if action == "visit":
            stack.append((expr, "process"))

            if isinstance(expr, Application):
                stack.append((expr.arg, "visit"))
                stack.append((expr.fn, "visit"))

            elif isinstance(expr, Abstraction):
                stack.append((expr.body, "visit"))

        elif action == "process":
            if is_church_numeral(expr):
                result_map[expr_id] = to_var(str(count_applications(expr)))

            elif isinstance(expr, Abstraction):
                body_result = result_map.get(id(expr.body), expr.body)
                result_map[expr_id] = abstract(expr.param, body_result)

            elif isinstance(expr, Application):
                fn_result = result_map.get(id(expr.fn), expr.fn)
                arg_result = result_map.get(id(expr.arg), expr.arg)
                result_map[expr_id] = apply(fn_result, arg_result)

            else:
                result_map[expr_id] = expr

    return result_map.get(id(e), e)


def normalize(e: Expression) -> None:
    """Normalize the expression and print each reduction step."""
    step, prev = 0, format_expr(e)
    print(f"Step {step}: {prev}")

    while True:
        result = reduce_once(e, DEFS)

        if not result:
            break

        e, stype = result
        step += 1
        curr = highlight_diff(prev, format_expr(e))
        label = f" ({stype})" if SHOW_STEP_TYPE else ""
        print(f"Step {step}{label}: {curr}")
        prev = curr

    print("→ normal form reached.")

    if DELTA_ABSTRACT:
        print("\nδ‑abstracted: " + format_expr(abstract_numerals(e)) + "\n")


def main() -> None:
    """Main function to run the λ calculus interpreter. Can take an
    argument or prompt for input.
    """
    user_input = " ".join(argv[1:]) if len(argv) > 1 else input("λ‑expr> ")

    try:
        tree = Parser(user_input).parse()

    except SyntaxError as e:
        print(f"Parse error: {e}")
        exit(1)
        return

    normalize(tree)


if __name__ == "__main__":
    main()
