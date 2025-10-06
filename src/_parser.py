from functools import lru_cache
from typing import Any

from _expressions import Abstraction, Application, Expression, Variable


@lru_cache(maxsize=None)
def church(n: int) -> Abstraction:
    """Convert a number to its Church numeral representation."""
    body: Expression = Variable("x")

    for _ in range(n):
        body = Application(Variable("f"), body)

    return Abstraction("f", Abstraction("x", body))


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
        var = self.parse_varname()
        self.skip_whitespace()

        if self.consume() != ".":
            raise SyntaxError("Expected '.' after λ parameter")

        body = self.parse_expr()
        return Abstraction(var, body)

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
        arg: Expression

        for arg in args:
            expression = Application(expression, arg)

        return expression

    def parse_atom(self) -> Expression:
        """Parse an atomic expression from the source string."""
        self.skip_whitespace()
        c = self.peek()

        if c == "(":
            self.consume()
            expression: Expression = self.parse_expr()
            self.skip_whitespace()

            if self.consume() != ")":
                raise SyntaxError("Expected ')'")

            return expression

        elif char.isdigit():
            num = self.parse_number()
            return church(num)

        else:
            name = self.parse_varname()
            return Variable(name)

    def parse_number(self) -> int:
        """Parse a number from the source string."""
        return int(
            "".join(
                iter(
                    lambda: self.consume() if self.peek().isdigit() else "", ""
                )
            )
        )

    def parse_varname(self) -> str:
        """Parse a variable name from the source string."""
        c = self.peek()

        if not c or c.isspace() or c in "().λ":
            raise SyntaxError(f"Invalid var start '{c}' at pos {self.i}")

        chars = []

        while True:
            c = self.peek()

            if not c or c.isspace() or c in "().λ":
                break

            chars.append(self.consume())

        return "".join(chars)
