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
        fparam = e.param
        bparam = e.body.param
        b = e.body.body
        curr = b

        while (
            isinstance(curr, Application)
            and isinstance(curr.fn, Variable)
            and curr.fn.name == fparam
        ):
            curr = curr.arg

        return isinstance(curr, Variable) and curr.name == bparam

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


def abstract_numerals(
    e: Expression,
) -> Expression:
    """Abstract Church numerals to digits."""
    if is_church_numeral(e):
        c = count_applications(e)
        return Variable(str(c))

    if isinstance(e, Abstraction):
        return Abstraction(
            e.param,
            abstract_numerals(e.body),
        )

    if isinstance(e, Application):
        return Application(
            abstract_numerals(e.fn),
            abstract_numerals(e.arg),
        )

    return e


def normalize(e: Expression) -> None:
    """Normalize the expression to its normal form."""
    step = 0
    prev = format_expr(e)
    print(f"Step {step}: {prev}")

    while True:
        result = reduce_once(e, DEFS)

        if not result:
            print("→ normal form reached.")
            break

        e, stype = result
        step += 1
        curr = highlight_diff(prev, format_expr(e))
        label = f" ({stype})" if SHOW_STEP_TYPE else ""
        print(f"Step {step}{label}: {curr}")
        prev = curr

    if DELTA_ABSTRACT:
        print(
            "\nδ‑abstracted: "
            + format_expr(abstract_numerals(expression))
            + "\n"
        )


def main() -> None:
    """Main function to run the λ calculus interpreter. Can take an
    argument or prompt for input.
    """
    user_input = " ".join(argv[1:]) if len(argv) > 1 else input("λ‑expr> ")

    try:
        tree = Parser(user_input).parse()

    except SyntaxError as e:
        exit(f"Parse error: {e}")
        tree = None

    normalize(tree)


if __name__ == "__main__":
    main()
