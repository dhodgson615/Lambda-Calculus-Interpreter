from _expressions import Abs, App, Expr, Var


def church(n: int) -> Abs:
    """Convert a number to its Church numeral representation."""
    body: Expr = Var("x")
    for _ in range(n):
        body = App(Var("f"), body)
    return Abs("f", Abs("x", body))


class Parser:
    """Parser for λ calculus expressions."""

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
        c = self.peek()
        self.i += 1
        return c

    def skip_ws(self) -> None:
        """Skip whitespace characters in the source string."""
        while self.peek().isspace():
            self.consume()

    def parse(self) -> Expr:
        """Parse the source string into an expression."""
        e = self.parse_expr()
        self.skip_ws()
        if self.i < self.n:
            raise SyntaxError(f"Unexpected '{self.peek()}' at pos {self.i}")
        return e

    def parse_expr(self) -> Expr:
        """Parse an expression from the source string."""
        self.skip_ws()
        if self.peek() == "λ":
            return self.parse_abs()
        else:
            return self.parse_app()

    def parse_abs(self) -> Abs:
        """Parse an abstraction from the source string."""
        self.consume()  # 'λ'
        var = self.parse_varname()
        self.skip_ws()
        if self.consume() != ".":
            raise SyntaxError("Expected '.' after λ parameter")
        body = self.parse_expr()
        return Abs(var, body)

    def parse_app(self) -> Expr:
        """Parse an application from the source string."""
        self.skip_ws()
        atom = self.parse_atom()
        self.skip_ws()
        args = []
        while True:
            nxt = self.peek()
            if nxt == "" or nxt in ").":
                break
            if nxt == ".":
                break
            args.append(self.parse_atom())
            self.skip_ws()
        e = atom
        for a in args:
            e = App(e, a)
        return e

    def parse_atom(self) -> Expr:
        """Parse an atomic expression from the source string."""
        self.skip_ws()
        ch = self.peek()
        if ch == "(":
            self.consume()
            e = self.parse_expr()
            self.skip_ws()
            if self.consume() != ")":
                raise SyntaxError("Expected ')'")
            return e
        elif ch.isdigit():
            num = self.parse_number()
            return church(num)
        else:
            name = self.parse_varname()
            return Var(name)

    def parse_number(self) -> int:
        """Parse a number from the source string."""
        ds = []
        while self.peek().isdigit():
            ds.append(self.consume())
        return int("".join(ds))

    def parse_varname(self) -> str:
        """Parse a variable name from the source string."""
        if not self.peek() or self.peek().isspace() or self.peek() in "().λ":
            raise SyntaxError(
                f"Invalid var start '{self.peek()}' at pos {self.i}"
            )
        chars = []
        while True:
            ch = self.peek()
            if not ch or ch.isspace() or ch in "().λ":
                break
            chars.append(self.consume())
        return "".join(chars)
