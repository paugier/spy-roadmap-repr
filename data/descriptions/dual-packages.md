!!! note "Definition: dual package"
    A package that can be imported and run with CPython alone, or with SPy alone. When
    SPy imports it, no Python interpreter is needed, so a SPy program using it can be
    compiled to a native binary.

!!! note "Definition: Python mode"
    A way of writing a module so that it is at the same time valid Python and valid
    high-level SPy. CPython runs it with the help of a small library
    ([spy_py_mode](node:py-mode-lib)); SPy runs or compiles it directly.

A dual package mixes three kinds of files:

| Kind                      | Read by CPython | Read by SPy |
| ------------------------- | --------------- | ----------- |
| Shared file (Python mode) | yes             | yes         |
| Python-only file (`.py`)  | yes             | no          |
| SPy-only file (`.spy`)    | no              | yes         |

```text
mypkg/
    __init__.py      # shared
    core.py          # shared
    paths.py         # read by CPython
    paths.spy        # read by SPy instead of paths.py
    plotting.py      # Python-only: uses matplotlib, SPy never imports it
```

When SPy resolves an import, a `.spy` file wins over a `.py` file with the same name,
and CPython ignores `.spy` files. So `paths.py` and `paths.spy` are two implementations
of the same module, each used by one implementation of the language. `plotting.py` has
no `.spy` counterpart and no SPy module imports it, so SPy never reads it and it may use
any Python. A `.py` file that SPy does import without a `.spy` counterpart must be in
Python mode.

The rule is that all modules of a dual package give the same results in the three
execution modes. For a shared file this comes from the single source; for a module split
into a `.py` and a `.spy` file, only [tests](node:py-test-plugin) can guarantee it.
