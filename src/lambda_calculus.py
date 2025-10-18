from _parser import Parser
from _reduce import normalize


def run_lambda_calculus(expr: str) -> None:
    tree = Parser(expr).parse()
    normalize(tree)
