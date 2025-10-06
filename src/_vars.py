from __future__ import annotations

from functools import lru_cache
from itertools import count
from string import ascii_lowercase

from _expressions import (Abstraction, Application, Expression, Variable,
                          abstract, apply, var)


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
def subst(e: Expression, v: str, val: Expression) -> Expression:
    """Substitute all free occurrences of variable in expression with
    value.
    """
    if isinstance(e, Variable):
        return val if e.name == v else e

    if isinstance(e, Abstraction):
        if e.param == v:
            return abstract(e.param, e.body)

        if e.param in free_vars(val):
            used = set(free_vars(e.body)) | set(free_vars(val)) | {e.param, v}
            new_param = fresh_var(used)
            renamed = substitute(e.body, e.param, var(new_param))
            return abstract(new_param, substitute(renamed, v, val))

        return abstract(e.param, substitute(e.body, v, val))

    if isinstance(e, Application):
        return apply(substitute(e.fn, v, val), substitute(e.arg, v, val))

    raise TypeError("Unknown Expression in subst")
