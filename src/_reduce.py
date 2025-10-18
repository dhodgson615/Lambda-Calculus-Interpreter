from __future__ import annotations

from typing import Optional

from _expressions import Abstraction, Application, Variable, abstract, apply
from _vars import subst
from src._config import DELTA_ABSTRACT, SHOW_STEP_TYPE
from src._defs import DEFS
from src._expressions import Expression
from src._printer import format_expr, highlight_diff
from src._church_utils import abstract_numerals


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

        result = (
            beta_reduce(expr)
            if isinstance(expr, Application)
            else (
                delta_reduce(expr, defs)
                if isinstance(expr, Variable)
                else None
            )
        )

        if result:
            reduced_expr, reduction_type = result
            full_expr = reduced_expr

            for direction, parent in reversed(path):
                full_expr = (
                    apply(full_expr, parent.arg)
                    if direction == "fn" and isinstance(parent, Application)
                    else (
                        apply(parent.fn, full_expr)
                        if direction == "arg"
                        and isinstance(parent, Application)
                        else (
                            abstract(parent.param, full_expr)
                            if direction == "body"
                            and isinstance(parent, Abstraction)
                            else full_expr
                        )
                    )
                )

            return full_expr, reduction_type

        if isinstance(expr, Application):
            stack.append((expr.arg, path + [("arg", expr)]))
            stack.append((expr.fn, path + [("fn", expr)]))

        elif isinstance(expr, Abstraction):
            stack.append((expr.body, path + [("body", expr)]))

    return None


def normalize(e: Expression) -> None:
    """Normalize the expression and print each reduction step."""
    step, prev = 0, format_expr(e)
    print(f"Step {step}: {prev}")

    while True:
        result = reduce_once(e, DEFS)

        if not result:
            break

        e, stype = result
        step += 1
        curr = highlight_diff(prev, format_expr(e))
        label = f" ({stype})" if SHOW_STEP_TYPE else ""
        print(f"Step {step}{label}: {curr}")
        prev = curr

    print("→ normal form reached.")

    if DELTA_ABSTRACT:
        print("\nδ‑abstracted: " + format_expr(abstract_numerals(e)) + "\n")
