from __future__ import annotations

from functools import lru_cache
from sys import argv, exit

from _config import DELTA_ABSTRACT, SHOW_STEP_TYPE
from _defs import DEFS
from _expressions import Abstraction, Application, Expression, Variable
from _parser import Parser
from _printer import format_expr, highlight_diff
from _reduce import reduce_once


@lru_cache(maxsize=None)
def is_church_numeral(
    e: Expression,
) -> bool:
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

    n = 0
    curr = e.body.body

    while (
        isinstance(curr, Application)
        and isinstance(curr.fn, Variable)
        and curr.fn.name == e.param
    ):
        n += 1
        curr = curr.arg

    return n


def abstract_numerals(e: Expression) -> Expression:
    """Replace Church numerals in the expression with their integer
    equivalents.
    """
    return (
        Variable(str(count_applications(e)))
        if is_church_numeral(e)
        else (
            Abstraction(e.param, abstract_numerals(e.body))
            if isinstance(e, Abstraction)
            else (
                Application(abstract_numerals(e.fn), abstract_numerals(e.arg))
                if isinstance(e, Application)
                else e
            )
        )
    )


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
