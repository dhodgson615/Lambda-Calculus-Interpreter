from dataclasses import dataclass


@dataclass(frozen=True, eq=True, repr=False, slots=True)
class Expression:
    """Base class for all expressions."""


@dataclass(frozen=True, eq=True, repr=False, slots=True)
class Variable(Expression):
    """Variable class for λ calculus."""

    name: str

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass(frozen=True, eq=True, repr=False, slots=True)
class Abstraction(Expression):
    """Abstraction class for λ calculus."""

    param: str
    body: Expression

    def __hash__(self) -> int:
        return hash((self.param, self.body))

    def __str__(self) -> str:
        b = (
            f"({self.body})"
            if isinstance(self.body, Abstraction)
            else str(self.body)
        )

        return f"λ{self.param}.{b}"


@dataclass(frozen=True, eq=True, repr=False, slots=True)
class Application(Expression):
    """Application class for λ calculus."""

    fn: Expression
    arg: Expression

    def __hash__(self) -> int:
        return hash((self.fn, self.arg))

    def __str__(self) -> str:
        fn_s = (
            f"({self.fn})"
            if isinstance(self.fn, Abstraction)
            else str(self.fn)
        )

        arg_s = (
            f"({self.arg})"
            if isinstance(self.arg, (Abstraction, Application))
            else str(self.arg)
        )

        return f"{fn_s} {arg_s}"


def to_var(name: str) -> Variable:
    """Create a variable expression."""
    return Variable(name)


def abstract(param: str, body: Expression) -> Abstraction:
    """Create an abstraction expression."""
    return Abstraction(param, body)


def apply(fn: Expression, arg: Expression) -> Application:
    """Create an application expression."""
    return Application(fn, arg)
