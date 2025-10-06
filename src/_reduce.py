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
    """Perform a single reduction step (either β or δ)."""
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

        return None

    elif isinstance(e, Abstraction):
        result = reduce_once(e.body, defs)
        return (Abstraction(e.param, result[0]), result[1]) if result else None

    return None
