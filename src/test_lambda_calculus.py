import sys
from unittest.mock import patch

import pytest

from _ansi_helpers import _ANSI_RE, ESC, HIGHLIGHT, RESET, rgb, strip_ansi
from _config import RECURSION_LIMIT
from _defs import DEFS, DEFS_SRC
from _expressions import Abstraction, Application, Expression, Variable
from _parser import Parser, church
from _printer import apply_color, color_parens, highlight_diff, strip_spaces
from _reduce import reduce_once
from _vars import free_vars, fresh_var, substitute
from main import (abstract_numerals, count_applications, is_church_numeral,
                  normalize)

# ====== ANSI Helpers Tests ======


class TestAnsiHelpers:
    """Test ANSI helpers for color and string manipulation."""

    def test_rgb(self):
        """Test RGB color generation."""
        color = rgb(255, 0, 0)
        assert color == f"{ESC}38;2;255;0;0m"

        # Test caching
        color2 = rgb(255, 0, 0)
        assert color2 is color  # Same object due to lru_cache

    def test_strip_ansi(self):
        """Test stripping ANSI codes from strings."""
        text = f"{ESC}38;2;255;0;0mHello{RESET}"
        assert strip_ansi(text) == "Hello"

        # Test with multiple ANSI codes
        complex_text = f"{ESC}1m{ESC}31mBold Red{ESC}0m"
        assert strip_ansi(complex_text) == "Bold Red"

        # Test with no ANSI codes
        plain_text = "Plain text"
        assert strip_ansi(plain_text) == plain_text

    def test_ansi_regex(self):
        """Test that the ANSI regex matches escape sequences."""
        # Test that the regex matches ANSI escape sequences
        assert _ANSI_RE.match(f"{ESC}38;2;255;0;0m") is not None
        assert _ANSI_RE.match("regular text") is None


# ====== Config Tests ======


class TestConfig:
    """Test configuration settings."""

    def test_recursion_limit(self):
        """Test that the recursion limit is set correctly."""
        if RECURSION_LIMIT > 0:
            assert sys.getrecursionlimit() == RECURSION_LIMIT
        else:
            assert sys.getrecursionlimit() == 2**31 - 1


# ====== Definitions Tests ======


class TestDefinitions:
    """Test definitions and their parsing."""

    def test_defs_src_contents(self):
        """Test that DEFS_SRC contains expected definitions."""
        assert "⊤" in DEFS_SRC
        assert "⊥" in DEFS_SRC
        assert "+" in DEFS_SRC
        assert "*" in DEFS_SRC

    def test_defs_parsing(self):
        """Test that DEFS are parsed correctly."""
        for name in DEFS_SRC:
            assert name in DEFS
            assert isinstance(DEFS[name], Expression)


# ====== Expressions Tests ======


class TestExpressions:
    """Test expression creation and string representation."""

    def test_variable_creation(self):
        """Test variable creation and string representation."""
        var = Variable("x")
        assert var.name == "x"
        assert str(var) == "x"
        assert hash(var) == hash("x")

    def test_abstraction_creation(self):
        """Test abstraction creation and string representation."""
        var = Variable("x")
        abs_expr = Abstraction("x", var)
        assert abs_expr.param == "x"
        assert abs_expr.body == var
        assert str(abs_expr) == "λx.x"
        assert hash(abs_expr) == hash(("x", var))

    def test_application_creation(self):
        """Test application creation and string representation."""
        var1 = Variable("x")
        var2 = Variable("y")
        app = Application(var1, var2)
        assert app.fn == var1
        assert app.arg == var2
        assert str(app) == "x y"
        assert hash(app) == hash((var1, var2))

    def test_nested_expression_str(self):
        """Test string representation of nested expressions."""
        var = Variable("x")
        abs1 = Abstraction("y", var)
        abs2 = Abstraction("z", abs1)
        assert str(abs2) == "λz.(λy.x)"
        app1 = Application(var, var)
        app2 = Application(abs1, app1)
        assert str(app2) == "(λy.x) (x x)"


# ====== Parser Tests (Enhanced) ======


class TestParserEnhanced:
    """Test the parser for λ calculus expressions."""

    def test_church_function(self):
        """Test that church numerals are parsed correctly."""
        for i in range(5):
            numeral = church(i)
            assert isinstance(numeral, Abstraction)
            assert numeral.param == "f"
            assert isinstance(numeral.body, Abstraction)
            assert numeral.body.param == "x"

            # Count applications to verify the number
            count = 0
            current = numeral.body.body
            while isinstance(current, Application):
                count += 1
                current = current.arg
            assert count == i

    def test_parser_methods(self):
        """Test various parser methods."""
        parser = Parser("λx.x y")

        # Test peek and consume
        assert parser.peek() == "λ"
        assert parser.consume() == "λ"
        assert parser.peek() == "x"

        # Test skip_whitespace
        parser = Parser("  x  ")
        parser.skip_whitespace()
        assert parser.i == 2
        assert parser.peek() == "x"

        # Test parse_varname
        parser = Parser("xyz")
        name = parser.parse_varname()
        assert name == "xyz"

        # Test parse_number
        parser = Parser("123")
        num = parser.parse_number()
        assert num == 123

    def test_error_handling(self):
        """Test error handling in the parser."""
        with pytest.raises(SyntaxError):
            Parser("λ").parse()

        with pytest.raises(SyntaxError):
            Parser("λx").parse()

        with pytest.raises(SyntaxError):
            Parser("λx x").parse()

        with pytest.raises(SyntaxError):
            Parser("(λx.x").parse()

        with pytest.raises(SyntaxError):
            Parser("").parse_varname()


# ====== Printer Tests (Enhanced) ======


class TestPrinterEnhanced:
    """Test the printer for λ calculus expressions."""

    def test_strip_spaces_with_config(self):
        """Test strip_spaces with different COMPACT settings."""
        strip_spaces.cache_clear()  # Clear cache before first test
        with patch("_printer.COMPACT", True):
            assert strip_spaces("a b c") == "abc"

        strip_spaces.cache_clear()  # Clear cache before second test
        with patch("_printer.COMPACT", False):
            assert strip_spaces("a b c") == "a b c"

    def test_apply_color(self):
        """Test the apply_color function for coloring characters."""
        color1 = apply_color(1, 10, "(")
        color2 = apply_color(5, 10, "(")
        color3 = apply_color(10, 10, "(")

        # Colors should be different based on depth
        assert color1 != color2
        assert color2 != color3

        # Test with a single depth
        single_depth = apply_color(1, 1, "(")
        assert single_depth.startswith(rgb(0, 128, 128))

    def test_color_parens_with_config(self):
        """Test the color_parens function with different COLOR_PARENS
        settings.
        """
        with patch("_printer.COLOR_PARENS", True):
            result = color_parens("(a(b)c)")
            assert ESC in result  # Should contain ANSI codes

        with patch("_printer.COLOR_PARENS", False):
            result = color_parens("(a(b)c)")
            assert result == "(a(b)c)"  # No ANSI codes

    def test_highlight_diff_with_config(self):
        """Test the highlight_diff function with different COLOR_DIFF
        settings.
        """
        with patch("_printer.COLOR_DIFF", True):
            result = highlight_diff("abc", "abd")
            assert HIGHLIGHT in result

        with patch("_printer.COLOR_DIFF", False):
            result = highlight_diff("abc", "abd")
            assert result == "abd"

        # Test with ANSI codes in input
        colored_old = f"a{ESC}31mb{RESET}c"
        colored_new = f"a{ESC}31mb{RESET}d"
        result = highlight_diff(colored_old, colored_new)
        assert strip_ansi(result) == "abd"


# ====== Reduction Tests (Enhanced) ======


class TestReductionEnhanced:
    """Test reduction functions for λ calculus expressions."""

    def test_nested_beta_reduction(self):
        """Test beta reduction with nested expressions."""
        # Test beta reduction with nested expressions
        expr = Parser("(λx.λy.x y) a b").parse()

        # The first reduction should apply λx to 'a'
        result1, type1 = reduce_once(expr, {})
        assert type1 == "β"
        assert isinstance(result1, Application)

        # The second reduction should apply λy to 'b'
        result2, type2 = reduce_once(result1, {})
        assert type2 == "β"

        # The final result should be 'a b'
        assert str(result2) == "a b"

    def test_delta_reduction_with_nested(self):
        """Test delta reduction with nested expressions"""
        expr = Parser("(λx.⊤) y").parse()

        result1, type1 = reduce_once(expr, DEFS)
        assert type1 == "β"

        result2, type2 = reduce_once(result1, DEFS)
        assert type2 == "δ"
        assert str(result2) == "λx.(λy.x)"

    def test_reduce_once_inside_abstraction(self):
        """Test reduce_once inside an abstraction."""
        expr = Parser("λx.(λy.y) x").parse()

        result, type_red = reduce_once(expr, {})
        assert type_red == "β"
        assert str(result) == "λx.x"


# ====== Variables Tests (Enhanced) ======


class TestVariablesEnhanced:
    """Test variable handling functions."""

    def test_free_vars_complex(self):
        """Test free_vars with complex expressions"""
        expr = Parser("λx.λy.x y z").parse()
        assert free_vars(expr) == frozenset(["z"])

        expr2 = Parser("λx.(λy.x y) z").parse()
        assert free_vars(expr2) == frozenset(["z"])

    def test_substitute_with_name_clash(self):
        """Test substitution with name clashes"""
        expr = Parser("λy.x y").parse()
        result = substitute(expr, "x", Variable("y"))

        # Should rename the bound 'y' to avoid capture
        assert str(result) != "λy.y y"
        assert isinstance(result, Abstraction)
        assert result.param != "y"  # Should be renamed

    def test_fresh_var_extended(self):
        """Test fresh_var with extended scenarios"""
        used = set(["a", "b", "c"])
        assert fresh_var(used) == "d"

        # Test with all lowercase letters used
        all_letters = set(chr(ord("a") + i) for i in range(26))
        fresh = fresh_var(all_letters)
        assert fresh[0] in "abcdefghijklmnopqrstuvwxyz"
        assert len(fresh) > 1
        assert fresh[1:].isdigit()


# ====== Main Module Tests ======


class TestMainModule:
    """Test the main module functions."""

    def test_is_church_numeral_edge_cases(self):
        """Test is_church_numeral with edge cases"""
        not_church1 = Parser("λf.λx.y").parse()  # Free variable
        assert not is_church_numeral(not_church1)

        not_church2 = Parser("λf.λx.f y").parse()  # Free variable
        assert not is_church_numeral(not_church2)

        not_church3 = Parser("λf.λx.g x").parse()  # Wrong function
        assert not is_church_numeral(not_church3)

    def test_count_applications_edge_cases(self):
        """Test count_applications with edge cases"""
        church3_alt = Parser("λf.λx.f (f (f x))").parse()
        assert count_applications(church3_alt) == 3
        malformed = Parser("λf.λx.f (g x)").parse()
        assert count_applications(malformed) == 1

    def test_abstract_numerals_complex(self):
        """Test abstract_numerals with complex expressions"""
        expr = Parser("(λf.λx.f (f x)) (λf.λx.f x)").parse()
        result = abstract_numerals(expr)
        assert str(result) == "2 1"

        # Test with non-church numerals mixed in
        expr2 = Parser("λz.z (λf.λx.f (f x))").parse()
        result2 = abstract_numerals(expr2)
        assert str(result2) == "λz.z 2"

    @patch("builtins.print")
    def test_normalize(self, mock_print):
        """Test normalization process"""
        expr = Parser("(λx.x) (λy.y)").parse()
        normalize(expr)

        # Check if print was called with the right arguments
        assert mock_print.call_count >= 2

        # Test with delta abstraction
        with patch("main.DELTA_ABSTRACT", True):
            expr2 = Parser("(λf.λx.f (f x))").parse()
            normalize(expr2)
            # Should print the abstracted form
            assert any("2" in call[0][0] for call in mock_print.call_args_list)

    @patch("builtins.input", return_value="λx.x")
    @patch("builtins.print")
    def test_main(self, mock_print, mock_input):
        """Test the main function with input and command line
        arguments.
        """
        with patch("sys.argv", ["main.py"]):
            from main import main

            main()

        # Should call normalize which prints results
        assert mock_print.call_count > 0

        # Test main with command line arguments
        with patch("sys.argv", ["main.py", "λx.x", "y"]):
            mock_print.reset_mock()
            from main import main

            main()
            assert mock_print.call_count > 0


# ====== Numeric Abstraction Tests ======


class TestNumericAbstraction:
    """Test numeric abstraction functions."""

    def test_simple_abstraction(self):
        """Test simple abstraction of Church numerals"""
        for i in range(5):
            expr = church(i)
            result = abstract_numerals(expr)
            assert str(result) == str(i)

    def test_addition(self):
        """Test addition operations"""
        test_cases = [
            ("+ 0 0", "0"),
            ("+ 1 1", "2"),
            ("+ 2 3", "5"),
            ("+ 3 4", "7"),
            ("+ 5 7", "12"),
        ]

        for expr_str, expected in test_cases:
            expr = Parser(expr_str).parse()
            # Normalize first to perform the calculation
            normal_expr = expr
            while True:
                result = reduce_once(normal_expr, DEFS)
                if not result:
                    break
                normal_expr = result[0]
            # Then abstract the result
            abstracted = abstract_numerals(normal_expr)
            assert str(abstracted) == expected

    def test_multiplication(self):
        """Test multiplication operations"""
        test_cases = [
            ("* 0 5", "0"),
            ("* 1 7", "7"),
            ("* 2 3", "6"),
            ("* 3 4", "12"),
            ("* 5 5", "25"),
            ("* 8 8", "64"),
        ]

        for expr_str, expected in test_cases:
            expr = Parser(expr_str).parse()
            # Normalize first
            normal_expr = expr
            while True:
                result = reduce_once(normal_expr, DEFS)
                if not result:
                    break
                normal_expr = result[0]
            # Then abstract
            abstracted = abstract_numerals(normal_expr)
            assert str(abstracted) == expected

    def test_complex_expressions(self):
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
            ("* 20 20", "400"),
            ("* (+ 1 1) (+ 2 2)", "8"),
            ("* 50 (* 2 3)", "300"),
        ]

        for expr_str, expected in test_cases:
            expr = Parser(expr_str).parse()
            # Normalize completely
            normal_expr = expr
            while True:
                result = reduce_once(normal_expr, DEFS)
                if not result:
                    break
                normal_expr = result[0]
            # Then abstract
            abstracted = abstract_numerals(normal_expr)
            assert str(abstracted) == expected

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (2, 2, "4"),
            (3, 5, "8"),
            (10, 10, "20"),
        ],
    )
    def test_parametrized_addition(self, a, b, expected):
        """Test addition with parametrized values"""
        expr_str = f"+ {a} {b}"
        expr = Parser(expr_str).parse()
        # Normalize
        normal_expr = expr
        while True:
            result = reduce_once(normal_expr, DEFS)
            if not result:
                break
            normal_expr = result[0]
        # Abstract
        abstracted = abstract_numerals(normal_expr)
        assert str(abstracted) == expected


# ====== Boolean Operations Tests ======


class TestBooleanOperations:
    """Test boolean operations and comparisons."""

    def test_boolean_values(self):
        """Test true and false values from definitions"""
        true_expr = DEFS["⊤"]
        false_expr = DEFS["⊥"]

        assert str(true_expr) == "λx.(λy.x)"
        assert str(false_expr) == "λx.(λy.y)"

    def test_comparisons(self):
        """Test comparison operations"""
        test_cases = [
            ("≤ 2 5", True),  # 2 ≤ 5 should be true
            ("≤ 5 2", False),  # 5 ≤ 2 should be false
            ("≤ 3 3", True),  # 3 ≤ 3 should be true
        ]

        for expr_str, expected in test_cases:
            expr = Parser(expr_str).parse()
            # Normalize expression to get a boolean result
            normal_expr = expr
            while True:
                result = reduce_once(normal_expr, DEFS)
                if not result:
                    break
                normal_expr = result[0]

            # Check if the result matches true or false
            true_repr = str(DEFS["⊤"])
            false_repr = str(DEFS["⊥"])

            if expected:
                assert str(normal_expr) == true_repr
            else:
                assert str(normal_expr) == false_repr

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (2, 5, True),
            (5, 2, False),
            (3, 3, True),
            (0, 1, True),
            (10, 0, False),
        ],
    )
    def test_parametrized_comparisons(self, a, b, expected):
        """Test comparisons with parametrized values"""
        expr_str = f"≤ {a} {b}"
        expr = Parser(expr_str).parse()

        # Normalize to get a result
        normal_expr = expr
        while True:
            result = reduce_once(normal_expr, DEFS)
            if not result:
                break
            normal_expr = result[0]

        # Check against expected boolean value
        true_repr = str(DEFS["⊤"])
        false_repr = str(DEFS["⊥"])

        if expected:
            assert str(normal_expr) == true_repr
        else:
            assert str(normal_expr) == false_repr
