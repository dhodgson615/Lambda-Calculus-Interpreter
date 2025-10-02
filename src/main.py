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
    expression: Expression,
) -> bool:
    """Check if the expression is a Church numeral."""
    if isinstance(expression, Abstraction) and isinstance(
        expression.body, Abstraction
    ):
        fn_param = expression.param
        body_param = expression.body.param
        body = expression.body.body
        current = body

        while (
            isinstance(current, Application)
            and isinstance(current.fn, Variable)
            and current.fn.name == fn_param
        ):
            current = current.arg

        return isinstance(current, Variable) and current.name == body_param
    return False


def count_applications(
    expression: Expression,
) -> int:
    """Count the number of applications in a Church numeral."""
    count = 0

    if not (
        isinstance(expression, Abstraction)
        and isinstance(expression.body, Abstraction)
    ):
        return count

    current = expression.body.body

    while (
        isinstance(current, Application)
        and isinstance(current.fn, Variable)
        and current.fn.name == expression.param
    ):
        count += 1
        current = current.arg

    return count


def abstract_numerals(
    expression: Expression,
) -> Expression:
    """Abstract Church numerals to digits."""
    if is_church_numeral(expression):
        count = count_applications(expression)
        return Variable(str(count))

    if isinstance(expression, Abstraction):
        return Abstraction(
            expression.param,
            abstract_numerals(expression.body),
        )

    if isinstance(expression, Application):
        return Application(
            abstract_numerals(expression.fn),
            abstract_numerals(expression.arg),
        )

    return expression


def normalize(expression: Expression) -> None:
    """Normalize the expression to its normal form."""
    step = 0
    previous_render: str = format_expr(expression)
    print(f"Step {step}: {previous_render}")

    while True:
        result: tuple[Expression, str] | None = reduce_once(expression, DEFS)
        if not result:
            print("→ normal form reached.")
            break

        expression = result[0]
        stype: str = result[1]
        step += 1
        rend: str = format_expr(expression)
        rend = highlight_diff(previous_render, rend)
        if SHOW_STEP_TYPE:
            label: str = f" ({stype})"
        else:
            label = ""

        print(f"Step {step}{label}: {rend}")
        previous_render = rend

    if DELTA_ABSTRACT:
        abstracted: Expression = abstract_numerals(expression)
        print("\nδ‑abstracted: " + format_expr(abstracted) + "\n")


def main() -> None:
    """Main function to run the λ calculus interpreter. Can take an
    argument or prompt for input.
    """
    user_input: str = (
        " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("λ‑expr> ")
    )

    try:
        tree: Expression = Parser(user_input).parse()
    except SyntaxError as e:
        sys.exit(f"Parse error: {e}")

    normalize(tree)


if __name__ == "__main__":
    main()
