from sys import setrecursionlimit

COLOR_PARENS: bool = True  # color‑matched parentheses by nesting level
COLOR_DIFF: bool = False  # highlight the subterm(s) that changed
SHOW_STEP_TYPE: bool = True  # print “(δ)” or “(β)” after each step
COMPACT: bool = True  # drop all spaces in printed terms
DELTA_ABSTRACT: bool = True  # abstract Church numerals to digits
RECURSION_LIMIT: int = -1  # recursion limit for deep reductions
setrecursionlimit(RECURSION_LIMIT if RECURSION_LIMIT > 0 else 2**31 - 1)
