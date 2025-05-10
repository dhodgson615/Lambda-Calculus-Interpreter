# λ-Calculus Interpreter

Yet another λ-Calculus Interpreter, implemented in Python 3.10+. Designed for
messing around. Not intended for production use, unless your production
involves demolishing call stacks or pretending to be smart for understanding
functional programming.

---

## Project Goals

- **Educational Clarity**

  Walk through λ-calculus parsing and reduction step by step.

- **Practical Demonstration**

  Show parsing, AST manipulation, β- and δ-reduction.

- **Extensibility**

  Modular codebase ready for typed λ-calculus, custom reduction strategies, or
  new primitives.

---

## Installation & Usage

1. **Clone**

   ```bash
   git clone https://github.com/dhodgson615/Lambda-Calculus-Interpreter.git
   cd Lambda-Calculus-Interpreter
   ```

2. **Run**

    - **One-off evaluation**

    ```bash
    python3 main.py "(λx.x) (λy.y)"
    ```

   - **Interactive REPL**

     ```text
     python3 main.py
     λ-expr> * 2 3
     Step 0: (...)
     ```

Note: all of the math needs to be in prefix notation and surrounded by parentheses (except the outermost term) to work like actual math.

---

## Config

All runtime flags are in ` _config.py`. Edit it to customize:

- `COLOR_PARENS` (bool) - color-matched parentheses by nesting level

- `COLOR_DIFF` (bool) - highlight the changed subterm each step

- `SHOW_STEP_TYPE` (bool) - display `(δ)` or `(β)` after each reduction so you
  can tell what changed

- `COMPACT` (bool) - squish the output so it fits in your terminal and is
  unreadable

- `DELTA_ABSTRACT` (bool) - convert Church numerals back to actual numbers
  after normalization

- `RECURSION_LIMIT` (int) - max recursion depth. Set to a positive integer or
  `-1` for system max

---

## Limitations

- **Non-negative only**: negative numbers don't work.

- **No step limit**: non-terminating or very deep reductions may run until
  recursion limit is reached.

- **No CLI flags**: configuration is manual via ` _config.py`.

- **ANSI support**: requires a Unicode-capable terminal for colored output.

---

## Code Overview

### 1. AST (`_expressions.py`)

- `Var`, `Abs`, `App` classes with `__str__` printing.

### 2. Parser (`_parser.py`)

- Recursive-descent parser for variables, abstractions, applications,
  parentheses, and integer literals to Church numerals.

### 3. Reduction Engine (`main.py`)

- `reduce_once(e)` for a single β or δ step.

- `normalize(expr)` to iterate until normal form, logging each step.

### 4. Variable Management

- `free_vars`, `fresh_var` and capture-avoiding `subst` with α-conversion.

### 5. Church Numerals & δ-Definitions

- Built-in definitions (`DEFS_SRC`) for booleans, logic, arithmetic, pairs.

- `church(n)` encodes Python integers as λ-terms.

### 6. Display & Diffing (`_printer.py`, `_ansi_helpers.py`)

- ANSI coloring for parentheses and diff highlighting.

- Optional compact printing to remove spaces.

---

## Contributing

Contributions welcome.

1. Fork the repo

2. Create a feature branch

3. Submit a pull request with tests and documentation

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
