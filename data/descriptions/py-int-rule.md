```python
def factorial(n: i32) -> i32:
    res = 1
    for i in range(n):
        res *= i + 1
    return res
```

`factorial(13)` is 6227020800 in plain CPython, but 1932053504 with 32-bit wrapping, the
result in SPy. Three options are open:

- **In-range arithmetic only**: a conforming program never overflows. Then `i32` can be
  a plain `int` on CPython (fast), and a debug switch replaces it by a checked type that
  raises on overflow, so that tests in the three execution modes catch violations.
- **Arbitrary-precision `int` in SPy**, with fixed-width types only when explicitly
  requested.
- **Explicit types everywhere** in Python mode, with a checker rejecting ambiguous
  literals.

Code where exact 32-bit wrapping matters can also live in a `.spy` file, which limits how
much depends on this choice.
