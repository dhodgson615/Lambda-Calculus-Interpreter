class Expr:
    """Base class for all expressions."""

    def __repr__(self) -> str:
        """Return the string representation of the expression."""
        return self.__str__()

    def __str__(self) -> str:
        """Return the string representation of the expression."""
        return ""


class Var(Expr):
    """Variable class for λ calculus."""

    __slots__ = ("name",)

    def __repr__(self) -> str:
        """Return the string representation of the variable."""
        return self.__str__()

    def __hash__(self) -> int:
        """Return the hash of the variable."""
        return hash(self.name)

    def __init__(self, name: str) -> None:
        """Initialize a variable with a name."""
        self.name: str = name

    def __str__(self) -> str:
        """Return the string representation of the variable."""
        return self.name


class Abs(Expr):
    """Abstraction class for λ calculus."""

    __slots__ = ("param", "body")

    def __repr__(self) -> str:
        """Return the string representation of the abstraction."""
        return self.__str__()

    def __hash__(self) -> int:
        """Return the hash of the abstraction."""
        return hash((self.param, self.body))

    def __init__(self, param: str, body: Expr) -> None:
        """Initialize an abstraction with a parameter and body."""
        self.param = param
        self.body = body

    def __str__(self) -> str:
        """Return the string representation of the abstraction."""
        b = str(self.body)
        if isinstance(self.body, Abs):
            b = f"({b})"
        return f"λ{self.param}.{b}"


class App(Expr):
    """Application class for λ calculus."""

    __slots__ = ("fn", "arg")

    def __repr__(self) -> str:
        """Return the string representation of the application."""
        return self.__str__()

    def __hash__(self) -> int:
        """Return the hash of the application."""
        return hash((self.fn, self.arg))

    def __init__(self, fn: Expr, arg: Expr) -> None:
        """Initialize an application with a function and argument."""
        self.fn = fn
        self.arg = arg

    def __str__(self) -> str:
        """Return the string representation of the application."""
        if isinstance(self.fn, Abs):
            fn_s = f"({self.fn})"
        else:
            fn_s = str(self.fn)
        if isinstance(self.arg, (Abs, App)):
            arg_s = f"({self.arg})"
        else:
            arg_s = str(self.arg)
        return f"{fn_s} {arg_s}"
