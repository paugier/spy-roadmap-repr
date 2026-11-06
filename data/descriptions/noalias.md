!!! note "Definition: aliasing"
    Two pointers *alias* if the memory regions they give access to may overlap. The
    compiler usually cannot prove that they don't, so it has to assume the worst.

```python
def axpy(n: i32, a: f64, x: raw_ptr[f64], y: raw_ptr[f64]) -> None:
    for i in range(n):
        y[i] = y[i] + a * x[i]
```

If `y` is `x + 1`, then writing `y[i]` changes `x[i + 1]`, which the next iteration
reads. To stay correct, the compiler must reload `x[i]` from memory at every iteration
and cannot reorder or vectorize the loop. In practice such loops are several times slower
than the version where the compiler knows that `x` and `y` don't overlap.

## Proposal

A decorator lists the pointer parameters that do not alias:

```python
@noalias("x", "y")
def axpy(n: i32, a: f64, x: raw_ptr[f64], y: raw_ptr[f64]) -> None:
    for i in range(n):
        y[i] = y[i] + a * x[i]
```

`@noalias` is a promise made by the programmer: during the call, memory accessed through
one listed pointer is not accessed through another pointer, listed or not. It is a
property of the function, not of the pointer type: the parameters keep the type
`raw_ptr[f64]`, so callers need no conversion, and any number of parameters can be
listed.

## Lowered C

`@noalias` maps to the C keyword `restrict`. A pointer is a struct in SPy's C code
(`Ptr_T` in `unsafe.h`), and compilers mostly ignore `restrict` on a struct member, so
the lowered function first copies the address into local `restrict` variables:

```c
void axpy(int32_t n, double a, Ptr_f64 x_, Ptr_f64 y_) {
    #ifdef SPY_PTR_CHECKED
    /* for each pair of listed pointers, panic if the ranges
       [x_.p, x_.p + x_.length) and [y_.p, y_.p + y_.length) overlap */
    #endif
    double *restrict x = x_.p;
    double *restrict y = y_.p;
    for (int32_t i = 0; i < n; i++) {
        y[i] = y[i] + a * x[i];
    }
}
```

!!! note "Definition: undefined behavior"
    In C, *undefined behavior* (UB) is an operation for which the language defines no
    result. The compiler is allowed to assume that it never happens, so if it does,
    anything can happen: wrong results, crashes, or code silently removed.

Breaking a `restrict` promise is UB. In checked mode pointers also store the length of
their region, which allows the overlap check shown in the `#ifdef`: the UB becomes a
clear panic. The check is stricter than C: two listed pointers that are only read may
overlap legally, but are rejected.
