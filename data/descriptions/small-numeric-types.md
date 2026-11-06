SPy has `i8`, `u8`, `i32`, `u32`, `i64`, `u64`, `f32`, `f64` and `complex128`. Missing:
`i16` and `u16` (audio and image formats), `f16` and `bf16`.

!!! note "Definition: f16 and bf16"
    `f16` is the IEEE 754 *half precision* float: 16 bits with 5 bits of exponent and 10
    of mantissa. `bf16` ("brain float") keeps the 8-bit exponent of `f32` and only 7 bits
    of mantissa: less precise, but with the same range as `f32`. Both exist to store large
    arrays (machine learning, reduced-precision simulation) in a quarter of the memory of
    `f64`.

They are storage types: values are widened to `f32` before any arithmetic.

```python
def sum_half(x: raw_ptr[f16], n: i32) -> f32:
    s: f32 = 0.0
    for i in range(n):
        s = s + f32(x[i])
    return s
```

```c
float sum_half(Ptr_f16 x, int32_t n) {
    float s = 0.0f;
    for (int32_t i = 0; i < n; i++) {
        s = s + spy_f16_to_f32(x.p[i]);   /* x.p has type uint16_t * */
    }
    return s;
}
```

`_Float16` needs GCC ≥ 12 or Clang ≥ 15 on x86-64 and does not exist in MSVC, so SPy
stores an `f16` as a `uint16_t` and converts it with the libspy function `spy_f16_to_f32`
(a few bit operations); where `__FLT16_MAX__` is defined, this function can be a plain
`_Float16` cast. A `bf16` is simpler: its conversion to `f32` is a 16-bit shift.
