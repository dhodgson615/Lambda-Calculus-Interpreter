from sys import argv, exit

from lambda_calculus import run_lambda_calculus


def main() -> None:
    """Main function to run the λ calculus interpreter. Can take an
    argument or prompt for input.
    """
    user_input = " ".join(argv[1:]) if len(argv) > 1 else input("λ‑expr> ")

    try:
        tree = Parser(user_input).parse()

    except SyntaxError as e:
        print(f"Parse error: {e}")
        exit(1)
        return

    normalize(tree)


if __name__ == "__main__":
    main()
