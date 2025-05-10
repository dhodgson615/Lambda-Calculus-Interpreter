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

    n: int
    i: int
    src: str

    def __init__(self, src: str) -> None:
        """Initialize the parser with the source string."""
        self.src = src
        self.i = 0
        self.n = len(src)

    def peek(self) -> str:
        """Return the next character in the source string without
        consuming it.
        """
        if self.i < self.n:
            return self.src[self.i]
        else:
            return ""

    def consume(self) -> str:
        """Consume the next character in the source string and return
        it.
        """
        char: str = self.peek()
        self.i += 1
        return char

    def skip_whitespace(self) -> None:
        """Skip whitespace characters in the source string."""
        i = self.i
        n = self.n
        src = self.src
        while i < n and src[i].isspace():
            i += 1
        self.i = i

    def parse(self) -> Expression:
        """Parse the source string into an expression."""
        expression: Expression = self.parse_expr()
        self.skip_whitespace()
        if self.i < self.n:
            raise SyntaxError(f"Unexpected '{self.peek()}' at pos {self.i}")
        return expression

    def parse_expr(self) -> Expression:
        """Parse an expression from the source string."""
        self.skip_whitespace()
        if self.peek() == "λ":
            return self.parse_abs()
        else:
            return self.parse_app()

    def parse_abs(self) -> Abstraction:
        """Parse an abstraction from the source string."""
        self.consume()  # 'λ'
        var: str = self.parse_varname()
        self.skip_whitespace()
        if self.consume() != ".":
            raise SyntaxError("Expected '.' after λ parameter")
        body: Expression = self.parse_expr()
        return Abstraction(var, body)

    def parse_app(self) -> Expression:
        """Parse an application from the source string."""
        self.skip_whitespace()
        atom: Expression = self.parse_atom()
        self.skip_whitespace()
        args: list[Any] = []
        while True:
            next_char = self.peek()
            if next_char == "" or next_char in ").":
                break
            if next_char == ".":
                break
            args.append(self.parse_atom())
            self.skip_whitespace()
        expression: Expression = atom
        arg: object
        for arg in args:
            expression = Application(expression, arg)
        return expression

    def parse_atom(self) -> Expression:
        """Parse an atomic expression from the source string."""
        self.skip_whitespace()
        char: str = self.peek()
        if char == "(":
            self.consume()
            expression: Expression = self.parse_expr()
            self.skip_whitespace()
            if self.consume() != ")":
                raise SyntaxError("Expected ')'")
            return expression
        elif char.isdigit():
            num: int = self.parse_number()
            return church(num)
        else:
            name: str = self.parse_varname()
            return Variable(name)

    def parse_number(self) -> int:
        """Parse a number from the source string."""
        digits: list[Any] = []
        while self.peek().isdigit():
            digits.append(self.consume())
        return int("".join(digits))

    def parse_varname(self) -> str:
        """Parse a variable name from the source string."""
        if not self.peek() or self.peek().isspace() or self.peek() in "().λ":
            raise SyntaxError(
                f"Invalid var start '{self.peek()}' at pos {self.i}"
            )
        chars: list[Any] = []
        while True:
            char: str = self.peek()
            if not char or char.isspace() or char in "().λ":
                break
            chars.append(self.consume())
        return "".join(chars)
