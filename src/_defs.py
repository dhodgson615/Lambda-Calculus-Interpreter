from __future__ import annotations

from _expressions import Expression
from _parser import Parser

# δ‑definitions for logical connectives and arithmetic operations
DEFS_SRC: dict[str, str] = {
    "⊤": "λx.λy.x",
    "⊥": "λx.λy.y",
    "∧": "λp.λq.p q p",
    "∨": "λp.λq.p p q",
    "↓": "λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)",
    "↑": "λn.λf.λx.f (n f x)",
    "+": "λm.λn.m ↑ n",
    "*": "λm.λn.m (+ n) 0",
    "is0": "λn.n (λx.⊥) ⊤",
    "-": "λm.λn.n ↓ m",
    "≤": "λm.λn.is0 (- m n)",
    "pair": "λx.λy.λf.f x y",
}

DEFS: dict[str | Expression, str | Expression] = {}  # δ‑definitions for Church numerals

for name, src in DEFS_SRC.items():
    DEFS[name] = Parser(src).parse()
