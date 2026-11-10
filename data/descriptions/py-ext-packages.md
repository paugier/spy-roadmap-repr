!!! note "Definition: extension module"
    A module written in a compiled language (C, or SPy compiled to C) that CPython
    imports like a Python module.

```text
mypkg/
    __init__.py
    io.py            # ordinary Python
    kernels.spy      # compiled to an extension module
```

Python code uses the compiled module with a normal import:

```python
from mypkg.kernels import integrate
```

Such a package cannot be imported by SPy (unlike a [dual package](node:dual-packages)).
Importing a Python package from SPy is a different subject: see
[Call Python from SPy](node:call-python-from-spy).
