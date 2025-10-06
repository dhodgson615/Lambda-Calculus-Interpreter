from __future__ import annotations

import string
from functools import lru_cache

from _expressions import Abstraction, Application, Expression, Variable


@lru_cache(maxsize=None)
def free_vars(
    expression: Expression,
) -> frozenset[str]:
    """Return the set of free variables in the expression."""
    return (
        frozenset([expression.name])
        if isinstance(expression, Variable)
        else (
            free_vars(expression.body) - frozenset([expression.param])
            if isinstance(expression, Abstraction)
            else (
                free_vars(expression.fn) | free_vars(expression.arg)
                if isinstance(expression, Application)
                else frozenset()
            )
        )
    )


def fresh_var(used: set[str]) -> str:
    """Generate a fresh variable name not in the used set."""
    return next(
        base if i == 0 else f"{base}{i}"
        for i in count()
        for base in ascii_lowercase
        if (base if i == 0 else f"{base}{i}") not in used
    )


@lru_cache(maxsize=None)
def substitute(e: Expression, var: str, val: Expression) -> Expression:
    """Substitute all free occurrences of variable in expression with
    value.
    """
    if isinstance(e, Variable):
        return val if e.name == var else e

    if isinstance(e, Abstraction):
        if e.param == var:
            return Abstraction(e.param, e.body)

        if expression.param in free_vars(value):
            used = (
                set(free_vars(expression.body))
                | set(free_vars(value))
                | {expression.param, variable}
            )

            new_param = fresh_var(used)

            renamed = substitute(
                expression.body,
                expression.param,
                Variable(new_param),
            )

            return Abstraction(
                new_param,
                substitute(renamed, variable, value),
            )

        else:
            return Abstraction(
                expression.param,
                substitute(
                    expression.body,
                    variable,
                    value,
                ),
            )

    if isinstance(expression, Application):
        return Application(
            substitute(expression.fn, variable, value),
            substitute(expression.arg, variable, value),
        )

    raise TypeError("Unknown Expression in subst")
