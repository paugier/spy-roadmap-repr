The goal is to declare an external C function in SPy and call it, without the glue code
that [out-of-tree modules](node:out-of-tree-modules) need today. The spelling `@extern` is
**invented**.

!!! note "Definition: FFI and ABI"
    A *foreign function interface* (FFI) lets a language call functions written in another
    one: `ctypes` and `cffi` are the FFIs of Python. The *ABI* (application binary
    interface) is the set of rules saying how a call is made at machine level: where
    arguments are passed, how a struct is laid out in memory, and so on. Two pieces of code
    can only call each other if they agree on the ABI.

## Proposed API

Wrapping BLAS would look like this:

```python
@extern("cblas_ddot", header="cblas.h")
def ddot(n: i32, x: raw_ptr[f64], incx: i32, y: raw_ptr[f64], incy: i32) -> f64: ...


def dot(n: i32, x: raw_ptr[f64], y: raw_ptr[f64]) -> f64:
    return ddot(n, x, 1, y, 1)
```

The `...` body is the Python convention for "no implementation here". The C code generated
for `dot` would be approximately:

```c
#include <cblas.h>

double dot(int32_t n, Ptr_f64 x, Ptr_f64 y) {
    /* checked mode: verify that x and y hold at least n items */
    return cblas_ddot(n, x.p, 1, y.p, 1);   /* C receives plain pointers */
}
```

In checked mode a SPy pointer is a struct, so the call must unwrap it into a plain C
pointer; this is also where the length is available to check the call. A SPy `str` carries
its length and is not guaranteed to end with a NUL byte, so passing one as `const char *`
needs a copy. Zig's `@cImport`, which reads the C header itself, is the reference for the
longer term.

## Implementation

The mechanism must work in the C backend and in the interpreter.

**C backend.** An `@extern` function is a function object without a body, whose C name is
the real one (`cblas_ddot`) instead of the usual `spy_<module>$<function>`. The backend
includes the header, emits no definition, and calls the function directly.

!!! note "Definition: shim"
    A *shim* is a small generated C function that sits between two sides: it converts the
    arguments, calls the real function, and converts the result.

**Interpreter.** The interpreter runs inside one WASM instance together with libspy, so a C
function can only be called through a WASM export. For each `@extern` function, a shim is
generated: it includes the header, unwraps the arguments, calls the C function, and
`WASM_EXPORT` exports it. The shims and the library, compiled to wasm32-wasi, are linked
with libspy by `spy/build/wasm_bundle.py`, the same way as in out-of-tree modules. The
`exp-native-stdlib` prototype already generates such shims for prebuilt stdlib modules
(`spy/build/native_stdlib.py`). A function of wasi-libc needs no build at all, since libc
is already part of the instance.

## Prototype steps

☐ A few libc functions (`strlen`, `abs`, `atoi`): only the mechanism is tested.

☐ `spyvm_qrcodegen` rewritten without C glue or Python binding: the `@extern`
declarations and `build_info` are all that remains.

☐ sqlite: opaque pointers, out-parameters (`sqlite3 **`) and the `sqlite3_exec` callback.

## Prerequisites

- Passing a function to C (for example the comparison function given to `qsort`) requires
  function values; see [function types](node:function-types). A plain `@extern` call does
  not.
- Passing a struct by value to C, or receiving one, requires the layout computed by SPy to
  be identical to the one the C compiler uses for the same struct. The interpreter uses the
  SPy layout, the C backend uses the C compiler's: see
  [the layout check](node:layout-agree-check).

## Later use: exchanging arrays

!!! note "Definition: DLPack"
    DLPack is a tiny C struct describing an array: pointer to the data, shape, strides, item
    type and device. NumPy, PyTorch and JAX use it to hand arrays to each other without
    copying, and the Python array API standard exposes it as `from_dlpack` and
    `__dlpack__`.

NumSPy needs both directions. `ndarray.from_buffer` already wraps an existing pointer;
conversions from and to `memoryview` and NumPy arrays are still a TODO (see
[array conversion](node:array-memoryview)). DLPack needs `@extern` and a correct struct
layout, since the struct is defined in C.
