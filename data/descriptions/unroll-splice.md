!!! note "Definition: unrolling, splicing"
    Unrolling a loop means writing its body once per iteration instead of generating a
    loop; it needs a number of iterations known at compile time. Splicing means inserting
    several items into the middle of a list, here the elements of a tuple or the arguments
    of a call.

[Unrolled `for` loops](node:unroll-for) produce statements. This node produces
expressions: a starred generator over `unroll_range` writes one element per index.

```python
def impl(t: T_t) -> new_tuple_type:
    return (*(converters[i](t[i]) for i in unroll_range(N)),)
```

With `N = 2`, the compiler replaces the starred generator by its two elements, and `impl`
becomes `return (converters[0](t[0]), converters[1](t[1]))`. Indexing `t` needs a
compile-time index, which is why a runtime loop cannot do this. The same form is allowed
in a call (`f(*(g(i) for i in unroll_range(N)))`) and in a subscript
(`tuple[*(T(i) for i in unroll_range(N))]`).

In blue code, `unroll_range(n)` behaves like `range(n)` and the result is a plain tuple.
In compiled code, the generator expression is copied for each index. It builds on the
[starred syntax](node:starred-blue) of the parser.
