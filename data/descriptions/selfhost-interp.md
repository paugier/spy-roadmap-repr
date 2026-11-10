The four levels of self-hosting are: this node (interpreter and compiler), then
[the spy command as a native launcher](node:selfhost-cli), then
[parsing in SPy](node:selfhost-pyast), then [full self-hosting](node:selfhost-full).

Counted in the 104 files of this level (parser, AST, `analyze`, `vm`, `backend`), the
Python the code uses is:

| Feature                                 | Occurrences | Roadmap node |
| --------------------------------------- | ----------- | ------------ |
| calls with keyword arguments            | 832         | none yet |
| classes with base classes               | 185         | [metaclasses](node:metaclasses) |
| decorated classes (mostly `@dataclass`) | 180         | [heap classes](node:heap-classes), [metaclasses](node:metaclasses) |
| comprehensions                          | 147         | none yet |
| walrus operator `:=`                    | 79          | none yet |
| `*args` / `**kwargs` definitions        | 56          | partly: [blue-time *args](node:blue-args), [blue-time **kwargs](node:blue-kwargs) |
| `lambda`                                | 48          | [function types](node:function-types) |
| `with`                                  | 31          | [with](node:with-ctx) |
| `try`                                   | 29          | [try/except](node:try-catch) |
| generators (`yield`)                    | 21          | none yet |
| `match`                                 | 2           | none yet |

Beyond syntax, the code relies on `ctypes` (the `unsafe` memory model), `pickle` (the
cache of compiled modules), `dataclasses`, heavy use of `typing`, and the
[inspection of annotations](node:blue-annotations). A module that depends on CPython
internals can be split: the `.py` file keeps the CPython implementation, and a `.spy`
file provides the SPy one (see [dual packages](node:dual-packages)).

Packages: `fixedint` is replaced by native fixed-width types, `py.path.local` by
[pathlib](node:mod-pathlib), and `pytest`, `pyperclip`, `pexpect`, `js` and `ziglang`
stay out of the core. The standard library modules to provide in a SPy-compatible form
are, by number of imports: `typing`, `dataclasses`, `re`, `sys`, `ctypes`, `types`,
`math`, `pathlib`, `textwrap`, `linecache`, `inspect`, `itertools`, `os` and
`collections`. Only `re`, `math`, `pathlib` and `collections` have a roadmap node.
