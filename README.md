# λ-Calculus Interpreter

**A toy interpreter for the untyped λ-calculus**, implemented in Python 3.10+,
designed for learning and demonstration. Not intended for production use.

---

## Project Goals

- **Educational Clarity**

  Walk through λ-calculus parsing and reduction step by step, with clear
  visuals.

- **Practical Demonstration**

  Show parsing, AST manipulation, β- and δ-reduction in Python, skills useful
  for compiler design.

- **Extensibility**

  Clean, modular codebase ready for typed λ-calculus, custom reduction
  strategies, or new primitives.

---

## Background

> “Lambda calculus is a formal system in mathematical logic for expressing
> computation by way of variable binding and substitution.”
>
> — Wikipedia: [Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus)

Three constructs:

1. **Variables** (e.g. `x`, `y`)

2. **Abstraction** (function definition) `λx.E`

3. **Application** (function call) `F A`

Reduction rules: **β-reduction** (apply functions) and **α-conversion** (rename
bound variables).

---

## Installation & Usage

1. **Clone the repo**

   ```bash
   git clone https://github.com/dhodgson615/Lambda-Calculus-Interpreter.git
   cd Lambda-Calculus-Interpreter
   ```

2. **Run the interpreter**

    - **One-off evaluation**

    ```bash
    python3 main.py "(λx.x) (λy.y)"
    ```

   - **Interactive REPL**

     ```bash
     python3 main.py
     ```

     ```text
     λ-expr> * 2 3
     Step 0: (…)
     ```

---

## Configuration

All runtime flags live in ` _config.py`. Edit it to customize:

- `COLOR_PARENS` (bool) — color-matched parentheses by nesting level

- `COLOR_DIFF` (bool) — highlight the changed subterm each step

- `SHOW_STEP_TYPE` (bool) — display `(δ)` or `(β)` after each reduction

- `COMPACT` (bool) — drop spaces in printed λ-terms

- `DELTA_ABSTRACT` (bool) — convert Church numerals back to digits after
  normalization

- `RECURSION_LIMIT` (int)  — max recursion depth; set to a positive integer or
  `-1` for system max

**Tip:** After editing, rerun `python3 main.py ...` to apply changes.

---

## Limitations

- **Non-negative only**: numeric literals < 0 parse as variables, not Church
  numerals.

- **No step limit**: non-terminating or very deep reductions may run until
  recursion limit is reached.

- **No CLI flags**: configuration is manual via ` _config.py`.

- **ANSI support**: requires a Unicode-capable terminal for colored output.

All of these (and more!) will be addressed in future updates.

---

## Code Overview

### 1. AST (`_expressions.py`)

- `Var`, `Abs`, `App` classes with concise `__str__` printing.

### 2. Parser (`_parser.py`)

- Recursive-descent parser for variables, abstractions, applications,
  parentheses, and integer literals → Church numerals.

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

## References & Further Reading

- **Alonzo Church**, “An Unsolvable Problem of Elementary Number Theory” (1936)

- **Henk Barendregt**, _The Lambda Calculus: Its Syntax and Semantics_ (1984)

- **Benjamin C. Pierce**, _Types and Programming Languages_ (2002)

- Wikipedia: [Church encoding](https://en.wikipedia.org/wiki/Church_encoding)

---

## Contributing

Contributions welcome!

1. Fork the repo

2. Create a feature branch

3. Submit a pull request with tests and documentation

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.