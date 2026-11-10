!!! note "Definition: execution mode"
    One of the three ways to execute the same code: `py` (CPython with the `spy_py_mode`
    library), `interp` (the SPy interpreter) and `compiled` (the SPy compiler, producing
    a native or WASM binary).

```python
from mypkg.maths import factorial


def test_factorial():
    assert factorial(5) == 120
```

The plugin turns this one function into three tests: `test_factorial[py]`,
`test_factorial[interp]` and `test_factorial[compiled]`, like the SPy tests that already
run on several backends. The test file must itself be in Python mode, so that SPy can run
and compile it.
