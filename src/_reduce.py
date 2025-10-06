from __future__ import annotations

from typing import Optional

from _expressions import (Abstraction, Application, Expression, Variable,
                          abstract, apply)
from _vars import subst


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
            subst(e.fn.body, e.fn.param, e.arg),
            "β",
        )
        if isinstance(e, Application) and isinstance(e.fn, Abstraction)
        else None
    )


def reduce_once(
    e: Expression,
    defs: dict[str, Expression],
) -> Optional[tuple[Expression, str]]:
    """Perform one step of reduction (β or δ) using an iterative approach."""
    stack: list[tuple[Expression, list[tuple[str, Expression]]]] = [(e, [])]

    while stack:
        expr, path = stack.pop()
        result = None

        if isinstance(expr, Application):
            result = beta_reduce(expr)

        if result is None and isinstance(expr, Variable):
            result = delta_reduce(expr, defs)

        if result:
            reduced_expr, reduction_type = result
            full_expr = reduced_expr

            for direction, parent in reversed(path):
                if direction == "fn" and isinstance(parent, Application):
                    full_expr = apply(full_expr, parent.arg)

                elif direction == "arg" and isinstance(parent, Application):
                    full_expr = apply(parent.fn, full_expr)

                elif direction == "body" and isinstance(parent, Abstraction):
                    full_expr = abstract(parent.param, full_expr)

    if isinstance(e, Application):
        return beta_reduce(e) or (
            (lambda r: (apply(r[0], e.arg), r[1]) if r else None)(
                reduce_once(e.fn, defs)
            )
            or (lambda r: (apply(e.fn, r[0]), r[1]) if r else None)(
                reduce_once(e.arg, defs)
            )
        )

    if isinstance(e, Abstraction):
        return (lambda r: (abstract(e.param, r[0]), r[1]) if r else None)(
            reduce_once(e.body, defs)
        )

    return None
