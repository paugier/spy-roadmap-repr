!!! note "Definition: metaclass"
    A class is an object, and its metaclass is its type, as `int` is the type of `3`. In
    `class Point(metaclass=Record)`, `Record` is the metaclass of `Point`: it decides what
    the class statement means (how the fields are laid out in memory, which methods are
    added). A metaclass runs at compile time, so it has no run-time cost.

Today only plain structs exist, and the compiler hard-codes how a class is defined. The
plan is that the compiler knows only structs, and that every other kind of class is a
metaclass written in SPy, in the standard library, which a user can read or replace.

```python
class Point(metaclass=Record):
    x: i32
    y: i32
```

`Record` is a heap-allocated class: a `Point` is a pointer to its data, so copying a
`Point` copies the pointer, as in Python. Its method `define_from_classbody` receives the
fields and methods of the class statement and builds an ordinary struct holding a
pointer, with generated `__init__`, `__eq__` and `__repr__`. Writing it needs unrolled
loops over the fields and functions with any number of arguments, hence [advanced
metaprogramming](node:advanced-metaprog).

The planned metaclasses are `Record`, `ClassMetaClass` (single inheritance with a
vtable), `DataClass`, `Protocol` (see [Protocols](node:protocols)) and `Variant` (see
[Variants](node:variants)). The names, and the `ClassBody` API they use, are proposals.
