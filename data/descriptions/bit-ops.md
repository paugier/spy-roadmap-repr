## Reinterpreting bits

!!! note "Definition: bit reinterpretation"
    Reinterpreting a value means keeping its bits and changing its type, for example
    reading the 64 bits of an `f64` as a `u64` to inspect its exponent. This differs from
    a conversion, which changes the bits to preserve the numeric value. In C the usual
    pointer-cast trick is UB (it breaks the *strict aliasing* rule, which says that memory
    holding a `double` may not be read through a `uint64_t`); the legal way is `memcpy`.

The proposal is not a generic `bitcast[T](x)`, which is an easy way to write undefined
behavior, but dedicated functions with fixed types: `f32_to_bits`, `f32_from_bits`,
`f64_to_bits` and `f64_from_bits`. The same restraint applies to the `cast[T](ptr)` of
SPy PR #738, which only converts a pointer to `T` into a pointer to `SIMD[T, N]` and back.

```python
def sign_bit(x: f64) -> u64:
    return f64_to_bits(x) >> 63
```

```c
uint64_t sign_bit(double x) {
    uint64_t r;
    memcpy(&r, &x, sizeof r);   /* compiled to a single register move */
    return r >> 63;
}
```

## Bit intrinsics

The usual bit intrinsics map to single CPU instructions:

| Function | Meaning |
| --- | --- |
| `popcount(x)` | number of bits set to 1 |
| `clz(x)`, `ctz(x)` | number of leading and trailing zero bits |
| `rotl(x, k)`, `rotr(x, k)` | rotation |

The C spelling depends on the compiler: `__builtin_popcountll`, `__builtin_clzll`,
`__builtin_ctzll` on GCC and Clang; `__popcnt64`, `_BitScanReverse64`,
`_BitScanForward64` on MSVC; the `<stdbit.h>` functions of C23. The macros of the libspy
header (see [C11 and portability macros](node:c-portability)) choose among them.
Rotations are written with shifts, which compilers recognize.
