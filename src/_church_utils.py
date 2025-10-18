from __future__ import annotations

from functools import lru_cache

from _expressions import (Abstraction, Application, Expression, Variable,
                          abstract, apply, to_var)


@lru_cache(maxsize=None)
def is_church_numeral(e: Expression) -> bool:
    """Check if the expression is a Church numeral."""
    return (
        isinstance(e, Abstraction)
        and isinstance(e.body, Abstraction)
        and (
            lambda fpar, bpar, body: (
                lambda check_apps: check_apps(check_apps, body)
            )(
                lambda f, curr: (
                    isinstance(curr, Variable) and curr.name == bpar
                    if not (
                        isinstance(curr, Application)
                        and isinstance(curr.fn, Variable)
                        and curr.fn.name == fpar
                    )
                    else f(f, curr.arg)
                )
            )
        )(e.param, e.body.param, e.body.body)
    )


def count_applications(e: Expression) -> int:
    """Count the number of applications in a Church numeral."""
    return (
        0
        if not (isinstance(e, Abstraction) and isinstance(e.body, Abstraction))
        else (
            lambda abs_e: (
                lambda count: count(count, 0, abs_e.body.body, abs_e.param)
            )(
                lambda f, n, curr, fpar: (
                    n
                    if not (
                        isinstance(curr, Application)
                        and isinstance(curr.fn, Variable)
                        and curr.fn.name == fpar
                    )
                    else f(f, n + 1, curr.arg, fpar)
                )
            )
        )(e)
    )


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
            stack.extend(
                [(expr, "process")]
                + (
                    [(expr.arg, "visit"), (expr.fn, "visit")]
                    if isinstance(expr, Application)
                    else []
                )
                + (
                    [(expr.body, "visit")]
                    if isinstance(expr, Abstraction)
                    else []
                )
            )

        elif action == "process":
            result_map[expr_id] = (
                to_var(str(count_applications(expr)))
                if is_church_numeral(expr)
                else (
                    abstract(
                        expr.param, result_map.get(id(expr.body), expr.body)
                    )
                    if isinstance(expr, Abstraction)
                    else (
                        apply(
                            result_map.get(id(expr.fn), expr.fn),
                            result_map.get(id(expr.arg), expr.arg),
                        )
                        if isinstance(expr, Application)
                        else expr
                    )
                )
            )

    return result_map.get(id(e), e)
