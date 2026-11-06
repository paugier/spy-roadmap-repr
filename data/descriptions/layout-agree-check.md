The C backend writes ordinary C structs and lets the C compiler lay them out. The
interpreter uses the layout computed by `calc_layout`. A comment in `cstructwriter.py`
says that assuming both layouts agree is "VERY wrong". Where they differ, the interpreter
and the compiled program read different offsets for the same field, and `sizeof` returns
a different number in the two modes. The two other layout defects
([`sizeof` and `alignof`](node:sizeof-alignof-types), [pointer size](node:ptr-size-platform))
are two ways to get there.

## Proposed fix

Emit one `_Static_assert(offsetof(S, field) == N, ...)` per field and one for the total
size, so that any disagreement is a compile-time error instead of silent memory
corruption.

```c
/* simplified, for Outer {x: i32, p: Pair} */
typedef struct { int32_t x; Pair p; } Outer;

_Static_assert(offsetof(Outer, x) == 0, "layout of Outer.x");
_Static_assert(offsetof(Outer, p) == 4, "layout of Outer.p");
_Static_assert(sizeof(Outer) == 12, "size of Outer");
```

`_Static_assert` is C11, hence the dependency on [C11 and portability macros](node:c-portability).
