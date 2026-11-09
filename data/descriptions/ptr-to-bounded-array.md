In checked mode, a pointer carries the length of its region; in release mode it is a bare
address. Code that takes "a range of an array" as argument therefore cannot rely on the
length. The missing pointer type is the pointer to a bounded array, spelled `span[T]` here (a
proposal): an address plus a length, in every mode, like a Rust slice. Pointers to an
unbounded array already exist, and [pointers to an object](node:ptr-to-object) are the
other missing kind.

```python
def total(xs: span[f64]) -> f64:
    t = 0.0
    for i in range(len(xs)):
        t = t + xs[i]
    return t

def total_middle(buf: raw_ptr[f64]) -> f64:  # buf holds 100 items
    xs = span(buf, 100)
    return total(xs[10:20])
```

```c
typedef struct { double *p; int32_t length; } span_f64;

double total_middle(Ptr_f64 buf) {
    /* checked mode: verify 100 <= buf.length */
    span_f64 xs = { buf.p, 100 };
    /* always: verify 0 <= 10 <= 20 <= xs.length */
    span_f64 tmp = { xs.p + 10, 10 };   /* no copy: same memory, new start and length */
    return total(tmp);
}
```
