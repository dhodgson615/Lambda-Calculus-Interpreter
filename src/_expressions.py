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
        b = str(self.body)
        if isinstance(self.body, Abstraction):
            b = f"({b})"

        return f"λ{self.param}.{b}"


@dataclass(frozen=True, eq=True, repr=False, slots=True)
class Application(Expression):
    """Application class for λ calculus."""

    fn: Expression
    arg: Expression

    def __hash__(self) -> int:
        return hash((self.fn, self.arg))

    def __str__(self) -> str:
        if isinstance(self.fn, Abstraction):
            fn_s = f"({self.fn})"
        else:
            fn_s = str(self.fn)

        if isinstance(self.arg, (Abstraction, Application)):
            arg_s = f"({self.arg})"
        else:
            arg_s = str(self.arg)
        return f"{fn_s} {arg_s}"
