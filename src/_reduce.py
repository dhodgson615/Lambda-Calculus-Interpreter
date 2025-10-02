from __future__ import annotations

from typing import Optional

from _expressions import Abstraction, Application, Expression, Variable
from _vars import substitute


def delta_reduce(
    expression: Expression,
    defs: dict[str, Expression],
) -> Optional[tuple[Expression, str]]:
    """Perform δ-reduction if applicable."""
    if isinstance(expression, Variable) and expression.name in defs:
        return defs[expression.name], "δ"
    return None


def beta_reduce(
    expression: Expression,
) -> Optional[tuple[Expression, str]]:
    """Perform β-reduction if applicable."""
    if isinstance(expression, Application) and isinstance(
        expression.fn, Abstraction
    ):
        return (
            substitute(
                expression.fn.body,
                expression.fn.param,
                expression.arg,
            ),
            "β",
        )
    return None


def reduce_once(
    expression: Expression,
    defs: dict[str, Expression],
) -> Optional[tuple[Expression, str]]:
    """Reduce a single step of the expression."""
    if isinstance(expression, Variable):
        # Only Variables can have delta reduction
        return delta_reduce(expression, defs)

    if isinstance(expression, Application):
        # Try beta reduction first
        beta_result = beta_reduce(expression)
        if beta_result:
            return beta_result

        # Try recursive reduction in the function part
        fn_result = reduce_once(expression.fn, defs)
        if fn_result:
            new_fn, reduction_type = fn_result
            # Create a new Application directly
            return (
                Application(new_fn, expression.arg),
                reduction_type,
            )

        # Try recursive reduction in the argument part
        arg_result = reduce_once(expression.arg, defs)
        if arg_result:
            new_arg, reduction_type = arg_result
            return (
                Application(expression.fn, new_arg),
                reduction_type,
            )

    elif isinstance(
        expression, Abstraction
    ):  # Using elif improves branch prediction
        # Try recursive reduction in the body
        body_result = reduce_once(expression.body, defs)
        if body_result:
            new_body, reduction_type = body_result
            return (
                Abstraction(expression.param, new_body),
                reduction_type,
            )

    # No reduction possible
    return None
