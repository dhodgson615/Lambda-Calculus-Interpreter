from __future__ import annotations

from functools import cache
from itertools import count
from string import ascii_lowercase

from _expressions import (Abstraction, Application, Expression, Variable,
                          abstract, apply, to_var)


@cache
def free_vars(e: Expression) -> frozenset[str]:
    """Return the set of free variables in the expression."""
    stack: list[tuple[Expression, frozenset[str]]] = [(e, frozenset())]
    result: frozenset[str] = frozenset()

    while stack:
        expr, bound = stack.pop()

        result |= (
            frozenset([expr.name])
            if isinstance(expr, Variable) and expr.name not in bound
            else frozenset()
        )

        stack.extend(
            [(expr.body, bound | frozenset([expr.param]))]
            if isinstance(expr, Abstraction)
            else (
                [(expr.fn, bound), (expr.arg, bound)]
                if isinstance(expr, Application)
                else []
            )
        )

    return result


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
    """Substitute all free occurrences of variable in expression with value."""
    stack = [(e, v, val)]
    results = {}

    while stack:
        expr, var, value = stack.pop()
        key = (id(expr), var, id(value))

        if key in results:
            continue

        if isinstance(expr, Variable):
            results[key] = value if expr.name == var else expr

        elif isinstance(expr, Abstraction):
            if expr.param == var:
                results[key] = abstract(expr.param, expr.body)

            elif expr.param in free_vars(value):
                used = (
                    free_vars(expr.body) | free_vars(value) | {expr.param, var}
                )

                new_param = fresh_var(set(used))
                renamed = subst(expr.body, expr.param, to_var(new_param))
                results[key] = abstract(new_param, subst(renamed, var, value))

            else:
                body_key = (id(expr.body), var, id(value))

                if body_key not in results:
                    stack.append((expr, var, value))
                    stack.append((expr.body, var, value))
                    continue

                results[key] = abstract(expr.param, results[body_key])

        elif isinstance(expr, Application):
            fn_key = (id(expr.fn), var, id(value))
            arg_key = (id(expr.arg), var, id(value))

            if fn_key not in results or arg_key not in results:
                stack.extend(
                    [(expr, var, value)]
                    + (
                        [(expr.fn, var, value)]
                        if fn_key not in results
                        else []
                    )
                    + (
                        [(expr.arg, var, value)]
                        if arg_key not in results
                        else []
                    )
                )

                continue

            results[key] = apply(results[fn_key], results[arg_key])

    return results[(id(e), v, id(val))]
