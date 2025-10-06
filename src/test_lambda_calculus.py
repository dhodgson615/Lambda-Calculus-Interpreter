from sys import getrecursionlimit
from unittest.mock import MagicMock, patch

from pytest import mark, raises

from _ansi_helpers import _ANSI_RE, ESC, HIGHLIGHT, RESET, rgb, strip_ansi
from _config import RECURSION_LIMIT
from _defs import DEFS
from _expressions import Abstraction, Application, Variable
from _parser import Parser, church
from _printer import apply_color, color_parens, highlight_diff, strip_spaces
from _reduce import reduce_once
from _vars import free_vars, fresh_var, substitute
from main import (abstract_numerals, count_applications, is_church_numeral,
                  main, normalize)


class TestAnsiHelpers:
    """Test ANSI helpers for color and string manipulation."""

    def test_rgb(self) -> None:
        """Test RGB color1 generation."""
        color1 = rgb(255, 0, 0)
        color2 = rgb(255, 0, 0)
        assert color1 == f"{ESC}38;2;255;0;0m"
        assert color2 is color1  # Same object due to lru_cache

    def test_strip_ansi(self) -> None:
        """Test stripping ANSI codes from strings."""
        assert strip_ansi(f"{ESC}38;2;255;0;0mHello{RESET}") == "Hello"
        assert strip_ansi(f"{ESC}1m{ESC}31mBold Red{ESC}0m") == "Bold Red"
        assert strip_ansi("Plain text") == "Plain text"

    def test_ansi_regex(self) -> None:
        """Test that the ANSI regex matches escape sequences."""
        assert _ANSI_RE.match(f"{ESC}38;2;255;0;0m") is not None
        assert _ANSI_RE.match("regular text") is None


class TestConfig:
    """Test configuration settings."""

    def test_recursion_limit(self) -> None:
        """Test that the recursion limit is set correctly."""
        if RECURSION_LIMIT > 0:
            assert getrecursionlimit() == RECURSION_LIMIT

        else:
            assert getrecursionlimit() == 2**31 - 1


class TestExpressions:
    """Test expression creation and string representation."""

    def test_variable_creation(self) -> None:
        """Test variable creation and string representation."""
        assert Variable("x").name == "x"
        assert str(Variable("x")) == "x"
        assert hash(Variable("x")) == hash("x")

    def test_abstraction_creation(self) -> None:
        """Test abstraction creation and string representation."""
        assert Abstraction("x", Variable("x")).param == "x"
        assert Abstraction("x", Variable("x")).body == Variable("x")
        assert str(Abstraction("x", Variable("x"))) == "λx.x"

        assert hash(Abstraction("x", Variable("x"))) == hash(
            ("x", Variable("x"))
        )

    def test_application_creation(self) -> None:
        """Test application creation and string representation."""
        assert Application(Variable("x"), Variable("y")).fn == Variable("x")
        assert Application(Variable("x"), Variable("y")).arg == Variable("y")
        assert str(Application(Variable("x"), Variable("y"))) == "x y"
        assert hash(Application(Variable("x"), Variable("y"))) == hash(
            (Variable("x"), Variable("y"))
        )

    def test_nested_expression_str(self) -> None:
        """Test string representation of nested expressions."""
        assert (
            str(Abstraction("z", Abstraction("y", Variable("x"))))
            == "λz.(λy.x)"
        )
        assert (
            str(
                Application(
                    Abstraction("y", Variable("x")),
                    Application(Variable("x"), Variable("x")),
                )
            )
            == "(λy.x) (x x)"
        )


class TestParser:
    """Test the parser for λ calculus expressions."""

    def test_church_function(self) -> None:
        """Test that church numerals are parsed correctly."""
        for i in range(5):
            numeral = church(i)
            assert isinstance(numeral, Abstraction)
            assert numeral.param == "f"
            assert isinstance(numeral.body, Abstraction)
            assert numeral.body.param == "x"
            count = 0
            current = numeral.body.body
            while isinstance(current, Application):
                count += 1
                current = current.arg
            assert count == i

    def test_peek_and_consume(self) -> None:
        """Test peek and consume methods."""
        parser = Parser("λx.x y")
        assert parser.peek() == "λ"
        assert parser.consume() == "λ"
        assert parser.peek() == "x"

    def test_skip_whitespace(self) -> None:
        """Test skip_whitespace method."""
        parser = Parser("  λx.x  ")
        parser.skip_whitespace()
        assert parser.i == 2
        assert parser.peek() == "λ"

    def test_parse_varname(self) -> None:
        """Test parse_varname method."""
        parser = Parser("xyz")
        name = parser.parse_varname()
        assert name == "xyz"
        assert parser.i == 3

    def test_parse_number(self) -> None:
        """Test parse_number method."""
        parser = Parser("123")
        number = parser.parse_number()
        assert number == 123
        assert parser.i == 3

    def test_error_handling(self) -> None:
        """Test error handling in the parser."""
        with raises(SyntaxError):
            Parser("λ").parse()

        with raises(SyntaxError):
            Parser("λx").parse()

        with raises(SyntaxError):
            Parser("λx x").parse()

        with raises(SyntaxError):
            Parser("(λx.x").parse()

        with raises(SyntaxError):
            Parser("").parse_varname()


class TestPrinter:
    """Test the printer for λ calculus expressions."""

    def test_strip_spaces_with_config(self) -> None:
        """Test strip_spaces with different COMPACT settings."""
        strip_spaces.cache_clear()
        with patch("_printer.COMPACT", True):
            assert strip_spaces("a b c") == "abc"

        strip_spaces.cache_clear()
        with patch("_printer.COMPACT", False):
            assert strip_spaces("a b c") == "a b c"

    def test_apply_color(self) -> None:
        """Test the apply_color function for coloring characters."""
        color1 = apply_color(1, 10, "(")
        color2 = apply_color(5, 10, "(")
        color3 = apply_color(10, 10, "(")

        assert color1 != color2
        assert color2 != color3

        # Test with a single depth
        single_depth = apply_color(1, 1, "(")
        assert single_depth.startswith(rgb(0, 128, 128))

    def test_color_parens_with_config(self) -> None:
        """Test the color_parens function with different COLOR_PARENS
        settings.
        """
        with patch("_printer.COLOR_PARENS", True):
            result = color_parens("(a(b)c)")
            assert ESC in result  # Should contain ANSI codes

        with patch("_printer.COLOR_PARENS", False):
            result = color_parens("(a(b)c)")
            assert result == "(a(b)c)"  # No ANSI codes

    def test_highlight_diff_with_config(self) -> None:
        """Test the highlight_diff function with different COLOR_DIFF
        settings.
        """
        with patch("_printer.COLOR_DIFF", True):
            result = highlight_diff("abc", "abd")
            assert HIGHLIGHT in result

        with patch("_printer.COLOR_DIFF", False):
            result = highlight_diff("abc", "abd")
            assert result == "abd"

        colored_old = f"a{ESC}31mb{RESET}c"
        colored_new = f"a{ESC}31mb{RESET}d"
        result = highlight_diff(colored_old, colored_new)
        assert strip_ansi(result) == "abd"


class TestReduction:
    """Test reduction functions for λ calculus expressions."""

    def test_nested_beta_reduction(self) -> None:
        """Test beta reduction with nested expressions."""
        expr = Parser("(λx.λy.x y) a b").parse()
        result1 = reduce_once(expr, {})
        assert result1 is not None
        expr1, type1 = result1
        assert type1 == "β"
        assert isinstance(expr1, Application)
        result2 = reduce_once(expr1, {})
        assert result2 is not None
        expr2, type2 = result2
        assert type2 == "β"
        assert str(expr2) == "a b"

    def test_delta_reduction_with_nested(self) -> None:
        """Test delta reduction with nested expressions"""
        expr = Parser("(λx.⊤) y").parse()
        result1 = reduce_once(expr, DEFS)
        assert result1 is not None
        expr1, type1 = result1
        assert type1 == "β"
        result2 = reduce_once(expr1, DEFS)
        assert result2 is not None
        expr2, type2 = result2
        assert type2 == "δ"
        assert str(expr2) == "λx.(λy.x)"

    def test_reduce_once_inside_abstraction(self) -> None:
        """Test reduce_once inside an abstraction."""
        expr = Parser("λx.(λy.y) x").parse()
        result = reduce_once(expr, {})
        assert result is not None
        expr1, type_red = result
        assert type_red == "β"
        assert str(expr1) == "λx.x"


class TestVariables:
    """Test variable handling functions."""

    def test_free_vars_complex(self) -> None:
        """Test free_vars with complex expressions"""
        expr = Parser("λx.λy.x y z").parse()
        assert free_vars(expr) == frozenset(["z"])
        expr2 = Parser("λx.(λy.x y) z").parse()
        assert free_vars(expr2) == frozenset(["z"])

    def test_substitute_with_name_clash(self) -> None:
        """Test substitution with name clashes"""
        expr = Parser("λy.x y").parse()
        result = substitute(expr, "x", Variable("y"))

        # Should rename the bound 'y' to avoid capture
        assert str(result) != "λy.y y"
        assert isinstance(result, Abstraction)
        assert result.param != "y"  # Should be renamed

    def test_fresh_var_extended(self) -> None:
        """Test fresh_var with extended scenarios"""
        used = {"a", "b", "c"}
        assert fresh_var(used) == "d"

        # Test with all lowercase letters used
        all_letters = set(chr(ord("a") + i) for i in range(26))
        fresh = fresh_var(all_letters)
        assert fresh[0] in "abcdefghijklmnopqrstuvwxyz"
        assert len(fresh) > 1
        assert fresh[1:].isdigit()


class TestMainModule:
    """Test the main module functions."""

    def test_is_church_numeral_edge_cases(self) -> None:
        """Test is_church_numeral with edge cases"""
        not_church1 = Parser("λf.λx.y").parse()  # Free variable
        assert not is_church_numeral(not_church1)

        not_church2 = Parser("λf.λx.f y").parse()  # Free variable
        assert not is_church_numeral(not_church2)

        not_church3 = Parser("λf.λx.g x").parse()  # Wrong function
        assert not is_church_numeral(not_church3)

    def test_count_applications_edge_cases(self) -> None:
        """Test count_applications with edge cases"""
        church3_alt = Parser("λf.λx.f (f (f x))").parse()
        assert count_applications(church3_alt) == 3
        malformed = Parser("λf.λx.f (g x)").parse()
        assert count_applications(malformed) == 1

    def test_abstract_numerals_complex(self) -> None:
        """Test abstract_numerals with complex expressions"""
        expr = Parser("(λf.λx.f (f x)) (λf.λx.f x)").parse()
        result = abstract_numerals(expr)
        assert str(result) == "2 1"

        # Test with non-church numerals mixed in
        expr2 = Parser("λz.z (λf.λx.f (f x))").parse()
        result2 = abstract_numerals(expr2)
        assert str(result2) == "λz.z 2"

    @patch("builtins.print")
    def test_normalize(self, mock_print: MagicMock) -> None:
        """Test normalization process"""
        expr = Parser("(λx.x) (λy.y)").parse()
        normalize(expr)

        assert mock_print.call_count >= 2

        with patch("main.DELTA_ABSTRACT", True):
            expr2 = Parser("(λf.λx.f (f x))").parse()
            normalize(expr2)

            assert any("2" in call[0][0] for call in mock_print.call_args_list)

    @patch("builtins.input", return_value="λx.x")
    @patch("builtins.print")
    def test_main(self, mock_print: MagicMock, mock_input: MagicMock) -> None:
        """Test the main function with input and command line
        arguments.
        """
        with patch("sys.argv", ["main.py"]):
            from main import main

            main()

        assert mock_print.call_count > 0
        with patch("sys.argv", ["main.py", "λx.x", "y"]):
            mock_print.reset_mock()
            from main import main

            main()
            assert mock_print.call_count > 0


class TestNumericAbstraction:
    """Test numeric abstraction functions."""

    def test_simple_abstraction(self) -> None:
        """Test simple abstraction of Church numerals"""
        for i in range(5):
            expr = church(i)
            result = abstract_numerals(expr)
            assert str(result) == str(i)

    def test_addition(self) -> None:
        """Test simple addition operations"""
        test_cases = [
            ("+ 0 0", "0"),
            ("+ 1 1", "2"),
            ("+ 2 3", "5"),
            ("+ 3 4", "7"),
            ("+ 5 7", "12"),
            ("+ 500 500", "1000"),
        ]

        for expr_str, expected in test_cases:
            expr = Parser(expr_str).parse()

            normal_expr = expr
            while True:
                result = reduce_once(normal_expr, DEFS)
                if not result:
                    break
                normal_expr = result[0]

            abstracted = abstract_numerals(normal_expr)
            assert str(abstracted) == expected

    def test_multiplication(self) -> None:
        """Test simple multiplication operations"""
        test_cases = [
            ("* 0 5", "0"),
            ("* 1 7", "7"),
            ("* 2 3", "6"),
            ("* 3 4", "12"),
            ("* 5 5", "25"),
            ("* 8 8", "64"),
            ("* 10 10", "100"),
        ]

        for expr_str, expected in test_cases:
            expr = Parser(expr_str).parse()

            normal_expr = expr
            while True:
                result = reduce_once(normal_expr, DEFS)
                if not result:
                    break
                normal_expr = result[0]

            abstracted = abstract_numerals(normal_expr)
            assert str(abstracted) == expected

    def test_complex_expressions(self) -> None:
        """Test more complex arithmetic expressions"""
        test_cases = [
            ("+ (* 2 3) 4", "10"),
            ("* (+ 1 2) 3", "9"),
            ("+ (* 2 2) (* 3 3)", "13"),
            ("* (+ 2 2) (+ 3 3)", "24"),
            ("+ (* 2 3) (* 4 5)", "26"),
            ("* (+ 1 1) (+ 2 2)", "8"),
            ("+ (* 2 3) (+ 4 5)", "15"),
            ("* (+ 1 2) (+ 3 4)", "21"),
            ("* (+ 1 1) (+ 2 2)", "8"),
            ("* 50 (* 2 3)", "300"),
        ]

        for expr_str, expected in test_cases:
            expr = Parser(expr_str).parse()

            normal_expr = expr
            while True:
                result = reduce_once(normal_expr, DEFS)
                if not result:
                    break
                normal_expr = result[0]

            abstracted = abstract_numerals(normal_expr)
            assert str(abstracted) == expected

    @mark.parametrize(
        "a,b,expected",
        [
            (2, 2, "4"),
            (3, 5, "8"),
            (10, 10, "20"),
            (0, 0, "0"),
            (1, 1, "2"),
            (5, 5, "10"),
            (7, 3, "10"),
            (4, 6, "10"),
            (8, 2, "10"),
            (9, 1, "10"),
        ],
    )
    def test_parametrized_addition(
        self, a: int, b: int, expected: str
    ) -> None:
        """Test addition with parametrized values"""
        expr = Parser(f"+ {a} {b}").parse()
        normal_expr = expr
        while True:
            result = reduce_once(normal_expr, DEFS)
            if not result:
                break
            normal_expr = result[0]

        abstracted = abstract_numerals(normal_expr)
        assert str(abstracted) == expected

    # def test_recursion_error_for_large_input(self):
    #    with pytest.raises(RecursionError):
    #        expr = Parser("* 1000 1000").parse()
    #        while True:
    #            step = reduce_once(expr, DEFS)
    #            if not step:
    #                break
    #
    #            expr = step[0]


class TestBooleanOperations:
    """Test boolean operations and comparisons."""

    def test_boolean_values(self) -> None:
        """Test true and false values from definitions"""
        true_expr = DEFS["⊤"]
        false_expr = DEFS["⊥"]

        assert str(true_expr) == "λx.(λy.x)"
        assert str(false_expr) == "λx.(λy.y)"

    @mark.parametrize(
        "a,b,expected",
        [
            (2, 5, True),
            (5, 2, False),
            (3, 3, True),
            (0, 1, True),
            (10, 0, False),
            (2, 2, True),
            (5, 5, True),
            (3, 4, True),
            (4, 3, False),
            (1, 0, False),
            (0, 0, True),
            (7, 8, True),
            (8, 7, False),
            (9, 10, True),
            (10, 9, False),
        ],
    )
    def test_all_comparisons(self, a: int, b: int, expected: bool) -> None:
        normal_expr = Parser(f"≤ {a} {b}").parse()
        while True:
            result = reduce_once(normal_expr, DEFS)
            if not result:
                break
            normal_expr = result[0]

        true_repr = str(DEFS["⊤"])
        false_repr = str(DEFS["⊥"])

        if expected:
            assert str(normal_expr) == true_repr
        else:
            assert str(normal_expr) == false_repr
