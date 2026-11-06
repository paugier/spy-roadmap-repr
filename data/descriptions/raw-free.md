Raw memory must be released explicitly, but `raw_free` is documented and not implemented
yet. Memory from `gc_alloc` is collected in native builds (Boehm GC), but never freed in
builds without a GC (`SPY_GC_NONE`), including the interpreter. Once `raw_free` exists,
the missing piece is a way to call it at scope exit: the planned
[`with` statement](node:with-ctx).

!!! note "Definition: context manager"
    A *context manager* is an object with `__enter__` and `__exit__` methods. The
    statement `with obj as x:` calls `__enter__` (its result is bound to `x`), runs the
    block, and calls `__exit__` however the block is left. In C++ and Rust the same
    guarantee is called RAII.

```python
@struct
class Buffer:
    ptr: raw_ptr[f64]

    def __enter__(self) -> raw_ptr[f64]:
        return self.ptr

    def __exit__(self) -> None:
        raw_free(self.ptr)

def sum_of_constants(n: i32) -> f64:
    with Buffer(raw_alloc[f64](n)) as xs:
        s = 0.0
        for i in range(n):
            xs[i] = 1.5
            s = s + xs[i]
        return s
```

```c
double sum_of_constants(int32_t n) {
    Buffer b = { raw_alloc_f64(n) };
    Ptr_f64 xs = Buffer_enter(b);
    double s = 0.0;
    for (int32_t i = 0; i < n; i++) {
        xs.p[i] = 1.5;
        s = s + xs.p[i];
    }
    double result = s;      /* the returned value is computed first... */
    Buffer_exit(b);         /* ...then the cleanup runs, then we return */
    return result;
}
```

Today every `raise` is a panic that aborts the program, so no exception ever leaves the
block: `__exit__` only has to run on normal exit and on `return`.

## Relation with reference counting

The roadmap also plans basic [reference counting](node:refcounting), without cycle
detection. It does not overlap with `raw_free`: refcounting manages objects allocated
with `gc_alloc`, while a `raw_ptr` is never counted and is released by `raw_free`, called
by hand or by `with`. An object that owns raw memory can release it in `__del__`, which
refcounting calls when the count reaches zero. This is deterministic only under
refcounting; with a tracing GC, `__del__` would run at an unpredictable time, or never.
`with` is deterministic in every memory model, so it stays the way to release raw memory
at scope exit. `__del__` must not be defined on a `@struct`: a struct is copied by value,
and every copy would free the same memory.
