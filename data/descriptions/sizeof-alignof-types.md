`sizeof` and `alignof` (`spy/vm/modules/unsafe/misc.py`) raise `WIP` for any type outside
an explicit list: `bool`, the 8, 32 and 64-bit integers, `f32`, `f64`, structs, pointers,
`str`, SIMD vectors, `_FILE` and `JsRef`.

`complex128` is not in the list, although the C backend maps it to `spy_Complex128`; a
struct with a `complex128` field is therefore likely to fail (to be confirmed by a test).

A comment in `alignof` states that "for every scalar type SPy has today, natural
alignment == size". This is false for `complex128` (size 16, alignment 8), so
`complex128` needs its own entry in both functions.

These observations come from reading the code, not from running it.
