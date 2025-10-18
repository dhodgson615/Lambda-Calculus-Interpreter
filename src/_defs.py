from _expressions import Expression
from _parser import Parser

DEFS: dict[str, Expression] = {
    name: Parser(src).parse()
    for name, src in {
        "⊤": "λx.λy.x",
        "⊥": "λx.λy.y",
        "∧": "λp.λq.p q p",
        "∨": "λp.λq.p p q",
        "↓": "λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)",
        "↑": "λn.λf.λx.f (n f x)",
        "+": "λm.λn.m ↑ n",
        "*": "λm.λn.m (+ n) 0",
        "is_zero": "λn.n (λx.⊥) ⊤",
        "-": "λm.λn.n ↓ m",
        "≤": "λm.λn.is_zero (- m n)",
        "pair": "λx.λy.λf.f x y",
    }.items()
}
