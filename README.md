# λ-Calculus Interpreter

**A toy interpreter for the untyped λ-calculus**, implemented in Python 3.10+,
designed both as an educational tool and a demonstration of core functional
concepts. Not for production use.

---

## 🎯 Project Goals

- **Educational Clarity**: Present λ-calculus concepts in a step-by-step,
  interactive manner, suitable for classroom demonstrations or self-study.
  
- **Practical Demonstration**: Showcase parsing, AST manipulation, and
  reduction mechanics in Python, skills valued by employers in compiler design
  and language tooling.
  
- **Extensibility**: Provide a clean, modular codebase for adding features like
  typed λ-calculus, optimization strategies, or alternative reduction orders.

---

## 📚 Background: What Is Lambda Calculus?

> "Lambda calculus is a formal system in mathematical logic for expressing
> computation by way of variable binding and substitution."
>
> — Wikipedia: [Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus)

Originally introduced by **Alonzo Church** in 1932 (*An Unsolvable Problem of
Elementary Number Theory*, 1936), the λ-calculus underpins functional
programming and the theory of computation. It uses just three constructs:

1. **Variables** (e.g. `x`, `y`)

2. **Abstraction** (function definition): `λx.E`

3. **Application** (function call): `F A`

Through **β‑reduction** (applying functions) and **α‑conversion** (renaming
bound variables), any computable function can be represented.

---

## 🚀 Features in This Interpreter

- **Normal‐order β‑reduction** (outermost-first)

- **δ‑reduction**: support for user‑defined primitives via a global definitions
  map (e.g. booleans, arithmetic)

- **Church numerals**: automatic translation of numeric literals into
  λ‑expressions
  ([Church encoding](https://en.wikipedia.org/wiki/Church_encoding))

- **ANSI‑colored output**: visual parentheses nesting, diff highlighting
  between steps

- **Compact mode**: optional removal of spaces for concise printing

- **Delta‑abstraction**: re‑present numerals back into digits after
  normalization

- **Interactive CLI**: REPL prompt or one‑off evaluation via command‑line
  argument

---

## 🛠️ Installation & Usage

1. **Clone the repo**

   ```bash
   git clone https://github.com/dhodgson615/Lambda-Calculus-Interpreter.git
   cd lambda-calculus-interpreter
   ```

2. **Run**
   - One‑time expression:

     ```bash
     python3 lc.py "(λx.x) (λy.y)"
     ```
     
   - Interactive REPL:

     ```bash
     python3 lc.py
     λ‑expr> (* 2 3)
     ```

3. **Adjust flags** in `main.py` for coloring, compact mode, or step‑type
labels as desired.

---

## 🔍 Code Walkthrough

### 1. Abstract Syntax Tree (AST)
- `Var`, `Abs`, `App` classes represent variables, abstractions, and
  applications.

- Each class implements `__str__` for unambiguous pretty‑printing.

### 2. Parser
- A **recursive‑descent parser** in `Parser`, handling:
  - Whitespace skipping
  - Abstraction (`λx.E`)
  - Application (left‑associative)
  - Parenthesized subexpressions
  - Numeric literals → `church(n)`

### 3. Reduction Engine
- **`reduce_once(e)`** performs a single δ or β step.

- Recurses into subterms to find the next reducible expression.

- **Normalization** via repeated `reduce_once` until no more reductions.

### 4. Variable Management
- **Free‑variable analysis** (`free_vars`) prevents unintended captures.

- **α‑conversion** (`fresh_var`, `subst`) renames bound variables when
  necessary.

### 5. Church Numerals & δ‑Definitions
- Built‑in definitions (`DEFS_SRC`) include booleans (`⊤`, `⊥`), logical
  connectives, arithmetic (`+`, `*`, `is0`, `−`, `≤`), and pairs.

- **Church encoding** transforms Python integers → λ‑terms.

### 6. Display & Diffing
- **ANSI SGR coloring** for nested parentheses (`color_parens`).

- **Highlight diffs** between reduction steps (`highlight_diff`).

- **Compact printing** strips spaces for terse output.

---

## 📖 References & Further Reading

- **Alonzo Church**, "An Unsolvable Problem of Elementary Number Theory" (1936)

- **Henk Barendregt**, _The Lambda Calculus: Its Syntax and Semantics_ (1984)

- **Wikipedia**,
  [Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus),
  [Church encoding](https://en.wikipedia.org/wiki/Church_encoding)

- **Benjamin C. Pierce**, _Types and Programming Languages_ (2002) – for
  advanced type systems

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork the project and open a pull request.

---

## 📜 License

This project is released under the [MIT License](LICENSE).
