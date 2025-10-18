from functools import lru_cache
from typing import Any

from _expressions import Abstraction, Expression, abstract, apply, to_var


@lru_cache(maxsize=None)
def church(n: int) -> Abstraction:
    """Convert a number to its Church numeral representation."""
    body: Expression = to_var("x")

    for _ in range(n):
        body = apply(to_var("f"), body)

    return abstract("f", abstract("x", body))


class Parser:
    """Parser for λ calculus expressions."""

    def __init__(self, src: str) -> None:
        """Initialize the parser with the source string."""
        self.src, self.i, self.n = src, 0, len(src)

    def peek(self) -> str:
        """Return the next character in the source string without
        consuming it.
        """
        return self.src[self.i] if self.i < self.n else ""

    def consume(self) -> str:
        """Consume the next character in the source string and return
        it.
        """
        char = self.peek()
        self.i += 1
        return char

    def skip_whitespace(self) -> None:
        """Skip whitespace characters in the source string."""
        while self.i < self.n and self.src[self.i].isspace():
            self.i += 1

    def parse(self) -> Expression:
        """Parse the source string into an expression."""
        expression = self.parse_expr()
        self.skip_whitespace()

        if self.i < self.n:
            raise SyntaxError(f"Unexpected '{self.peek()}' at pos {self.i}")

        return expression

    def parse_expr(self) -> Expression:
        """Parse an expression from the source string."""
        self.skip_whitespace()
        return self.parse_abs() if self.peek() == "λ" else self.parse_app()

    def parse_abs(self) -> Abstraction:
        """Parse an abstraction from the source string."""
        self.consume()  # 'λ'
        v = self.parse_varname()
        self.skip_whitespace()

        if self.consume() != ".":
            raise SyntaxError("Expected '.' after λ parameter")

        body = self.parse_expr()
        return abstract(v, body)

    def parse_app(self) -> Expression:
        """Parse an application from the source string."""
        self.skip_whitespace()
        atom = self.parse_atom()
        self.skip_whitespace()
        args: list[Any] = []

        while True:
            next_char = self.peek()

            if next_char == "" or next_char in ")." or next_char == ".":
                break

            args.append(self.parse_atom())
            self.skip_whitespace()

        expression = atom

        for arg in args:
            expression = apply(expression, arg)

        return expression

    def parse_atom(self) -> Expression:
        """Parse an atomic expression from the source string."""
        self.skip_whitespace()
        c = self.peek()

        if c == "(":
            self.consume()
            expr = self.parse_expr()
            self.skip_whitespace()

            if self.consume() != ")":
                raise SyntaxError("Expected ')'")

            return expr

        return (
            church(self.parse_number())
            if c.isdigit()
            else to_var(self.parse_varname())
        )

    def parse_number(self) -> int:
        """Parse a number from the source string."""
        start = self.i

        while self.peek().isdigit():
            self.i += 1

        if start == self.i:
            raise SyntaxError(f"Expected digit at pos {self.i}")

        return int(self.src[start : self.i])

    def parse_varname(self) -> str:
        """Parse a variable name from the source string."""
        start, c = self.i, self.peek()

        if not c or c.isspace() or c in "().λ":
            raise SyntaxError(f"Invalid var start '{c}' at pos {self.i}")

        while (
            self.i < self.n
            and not self.src[self.i].isspace()
            and self.src[self.i] not in "().λ"
        ):
            self.i += 1

        return self.src[start : self.i]
