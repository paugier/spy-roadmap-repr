!!! note "Definition: blue function"
    A blue function is a function that the compiler runs at compile time. Its result is
    fixed before the program runs, so it costs nothing at run time.

Helpers like `vectorize`, `benchmark` (time a function called many times) and `partial`
(fix some arguments of a function) are blue functions that build a new function from the
number and the types of the arguments they receive. Besides [unroll for
splicing](node:unroll-splice), they need three pieces:

- `args_m.types`: the tuple of the types of the arguments of a metafunction;
- `*args: *types`: a compiled function that takes any number of arguments, whose types
  are given by a compile-time tuple;
- `f(*args)` in compiled code, where `args` is a tuple of known length.

```python
@blue.generic
def benchmark(fct, repeat):
    @blue.metafunc
    def meta(*args_m):
        def impl(*args: *args_m.types):
            for _ in unroll_range(repeat):
                fct(*args)
        return OpSpec(impl)
    return meta
```

`benchmark[kernel, 100]` is a function whose body contains 100 copies of the call
`kernel(*args)`. The `unroll_range` loop already works; the `*args_m.types` annotation and
the `*args` spread in compiled code are the missing parts. The spellings are design
proposals.
