# λ-Calculus Interpreter

Yet another [λ-calculus](https://en.m.wikipedia.org/wiki/Lambda_calculus)
Interpreter, implemented in Python 3.10+. Designed for messing around. Not
intended for production use, unless your production involves demolishing call
stacks or pretending you understanding functional programming. [Now imagine if
it wasn't so
slow.](https://github.com/dhodgson615/Lambda-Calculus-Interpreter-C/tree/master)

---

## Project Goals

- **Educational Clarity**

  Walk through λ-calculus parsing and reduction step by step in its full
  inefficient glory.

- **Practical Demonstration**

  Show parsing, AST manipulation, β- and δ-reduction to practice interpreter
  design for when I make big boy compilers later.

- **Extensibility**

  Modular codebase ready for typed λ-calculus, custom reduction strategies, or
  new primitives, assuming I have time to get around to those.

- **Prototyping**

  Developing this in Python was arguably way easier than in C, which I eventually
  rewrote it in.

---

## Installation & Usage

1. **Clone**

   ```bash
   git clone https://github.com/dhodgson615/Lambda-Calculus-Interpreter.git
   cd Lambda-Calculus-Interpreter
   ```

2. **Run**

  **One-off evaluation**

  ```bash
  python3 main.py "(λx.x) (λy.y)"
  ```

  **Interactive REPL**

  ```bash
  python3 main.py
  ```
  ```text
  λ-expr> * 2 3
  Step 0: (...)
  ```

Note: all of the math needs to be in prefix notation and surrounded by
parentheses (except the outermost term) to work like actual math. I wish I had
made it so that you could write it without parentheses the way that it works in
real life, but unfortunately it do not be like that. Also, you can theoretically
pull off shenanigans like `"* + *"`, but it won't be mathematically useful.

Some of the following are my personal favorites:

```bash
python3 main.py "* 50 49"  # one of the largest multiplications without getting a RecursionError
python3 main.py "* 49 50"  # note that it's the same as above but runs with a different number of steps
python3 main.py "* 2 (* 2 (* 2 (* 2 (* 2 (* 2 (* 2 (* 2 (* 2 2))))))))"  # 2^10
```

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

### 1. AST

- `Var`, `Abs`, `App` classes with `__str__` printing.

### 2. Parser

- Recursive-descent parser for variables, abstractions, applications,
  parentheses, and integer literals to Church numerals.

### 3. Reduction Engine

- `reduce_once(expression)` for a single β or δ step.

- `normalize(expression)` to iterate until normal form, logging each step.

### 4. Variable Management

- `free_vars`, `fresh_var` and capture-avoiding `subst` with α-conversion.

### 5. Church Numerals & δ-Definitions

- Built-in definitions (`DEFS_SRC`) for booleans, logic, arithmetic, pairs.

- `church(n)` encodes Python integers as λ-terms.

### 6. Display & Diffing

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

