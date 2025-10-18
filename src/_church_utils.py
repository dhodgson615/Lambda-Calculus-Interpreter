from __future__ import annotations

from functools import lru_cache

from src._expressions import (Abstraction, Application, Expression, Variable,
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
