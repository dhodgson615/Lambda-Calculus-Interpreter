from __future__ import annotations

from typing import Optional

from _expressions import Abstraction, Application, Expression, Variable
from _vars import substitute


def delta_reduce(
    e: Expression,
    defs: dict[str, Expression],
) -> Optional[tuple[Expression, str]]:
    """Perform δ-reduction if applicable."""
    return (
        (defs[e.name], "δ")
        if isinstance(e, Variable) and e.name in defs
        else None
    )


def beta_reduce(
    e: Expression,
) -> Optional[tuple[Expression, str]]:
    """Perform β-reduction if applicable."""
    return (
        (
            substitute(e.fn.body, e.fn.param, e.arg),
            "β",
        )
        if isinstance(e, Application) and isinstance(e.fn, Abstraction)
        else None
    )


def reduce_once(
    e: Expression,
    defs: dict[str, Expression],
) -> Optional[tuple[Expression, str]]:
    """Reduce a single step of the expression."""
    if isinstance(e, Variable):
        return delta_reduce(e, defs)

    elif isinstance(e, Application):
        result = beta_reduce(e)

        if result:
            return result

        result = reduce_once(e.fn, defs)

        if result:
            return Application(result[0], e.arg), result[1]

        result = reduce_once(e.arg, defs)

        if result:
            return Application(e.fn, result[0]), result[1]

            return (
                Application(e.fn, new_arg),
                reduction_type,
            )

    elif isinstance(e, Abstraction):  # Using elif improves branch prediction
        # Try recursive reduction in the body
        body_result = reduce_once(e.body, defs)

        if body_result:
            new_body, reduction_type = body_result

            return (
                Abstraction(e.param, new_body),
                reduction_type,
            )

    # No reduction possible
    return None
