```python
def stencil(x: ptr[f64], weights: tuple[f64, f64, f64]) -> f64:
    acc: f64 = 0.0
    for i in unroll_range(3):
        acc = acc + x[i] * weights[i]
    return acc
```

Because `3` is known at compile time, the loop is replaced by three copies of its body
with `i` equal to `0`, `1` and `2`. Indexing a tuple needs a compile-time index, so
`weights[i]` is only possible in an unrolled loop. In the interpreter, `unroll_range(n)`
behaves like `range(n)`.
