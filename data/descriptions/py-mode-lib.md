In SPy, the runtime calls `main` and uses its return value as the exit code. In Python
nothing calls `main`, so Python mode needs an explicit entry point. This module is valid
in both modes:

```python
from spy_py_mode import i32, exec_main


def main(argv: list[str]) -> i32:
    print("argv:")
    for arg in argv:
        print(arg)
    print("exit code: 88")
    return 88


if __name__ == "__main__":
    exec_main(main)
```

Under CPython, `exec_main` calls `main` (passing `sys.argv` only if `main` declares a
parameter), then calls `sys.exit` with the returned value. Under SPy, the runtime calls
`main` itself, so the guard at the bottom must be skipped or evaluated as a no-op; how
exactly is still to be defined.

The library could also provide `is_spy`, a constant that is `False` on CPython and `True`
in SPy, to handle a small difference between modes without splitting a module into two
files:

```python
from spy_py_mode import is_spy

if is_spy:
    ...  # SPy version
else:
    ...  # CPython version
```
