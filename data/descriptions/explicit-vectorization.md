!!! note "Definition: SIMD"
    SIMD (single instruction, multiple data) means that one CPU instruction processes
    several numbers at once, held in a wide register. A `SIMD[f32, 8]` is a vector of 8
    single-precision floats, which a 256-bit register holds. Each number is a *lane*.

A SIMD vector is read from memory by indexing a pointer whose element type is the vector,
and obtained from a pointer to scalars with `cast`:

```python
def saxpy(a: f32, x: gc_ptr[SIMD[f32, 8]], y: gc_ptr[SIMD[f32, 8]], n: int) -> None:
    for i in range(n):
        y[i] = a * x[i] + y[i]   # 8 lanes per iteration
```

`a * x[i]` multiplies a scalar by a vector, and `x[i]` loads 8 floats at once. Loads and
stores adapt to the alignment of the pointer, which is part of its type.

The work is split in steps, each a blocker above: the type, the operations, the
reductions, the conversions, the vector width and the target CPU. A final example gathers
the kernels (`saxpy`, `relu`, `dot`, sum of squares, `exp`) in scalar and SIMD versions
and benchmarks them.
