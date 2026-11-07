!!! note "Definition: blue function"
    A blue function is a function that the compiler runs at compile time. Its result is
    fixed before the program runs, so it costs nothing at run time.

Helpers like `vectorize`, `benchmark` (time a function called many times) and `partial`
(fix some arguments of a function) are blue functions that build a new function from the
number and the types of the arguments they receive. They need two tools:

- [unrolled loops](node:unroll-for), to generate the code for each argument in turn;
- [spreading of tuples](node:star-splice), to pass the arguments to the generated code
  whatever their number.

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
the `*args` spread are the missing parts. The spellings are design proposals.
