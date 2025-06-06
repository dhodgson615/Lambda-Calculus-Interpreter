from __future__ import annotations

import string
from functools import lru_cache

from _expressions import Abstraction, Application, Expression, Variable


@lru_cache(maxsize=None)
def free_vars(
    expression: Expression,
) -> frozenset[str]:
    """Return the set of free variables in the expression."""
    if isinstance(expression, Variable):
        return frozenset([expression.name])

    if isinstance(expression, Abstraction):
        return free_vars(expression.body) - frozenset([expression.param])

    if isinstance(expression, Application):
        return free_vars(expression.fn) | free_vars(expression.arg)

    return frozenset()


def fresh_var(used: set[str]) -> str:
    """Generate a fresh variable name not in the used set."""
    for base in string.ascii_lowercase:
        if base not in used:
            return base

    i: int = 1
    while True:
        for base in string.ascii_lowercase:
            candidate = f"{base}{i}"
            if candidate not in used:
                return candidate

        i += 1


@lru_cache(maxsize=None)
def substitute(
    expression: Expression,
    variable: str,
    value: Expression,
) -> Expression:
    """Substitute all free occurrences of the variable in the
    expression with value.
    """
    if isinstance(expression, Variable):
        if expression.name == variable:
            return value
        else:
            return expression

    if isinstance(expression, Abstraction):
        if expression.param == variable:
            return Abstraction(expression.param, expression.body)

        if expression.param in free_vars(value):
            used: set[str] = (
                free_vars(expression.body)
                | free_vars(value)
                | {expression.param, variable}
            )

            new_param: str = fresh_var(used)
            renamed: Expression = substitute(
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
