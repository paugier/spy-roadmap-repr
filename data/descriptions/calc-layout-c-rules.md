`calc_layout` (`spy/vm/struct.py`) computes the offset of each struct field and the size
of the struct. SPy PR #749 makes it follow the C rules: each field offset is rounded up
to the *alignment* of the field, not to its size, and the total size is rounded up to the
alignment of the struct.

For `Outer {x: i32, p: Pair}` with `Pair {a: i32, b: i32}`, the field `p` is at offset 4
and `sizeof(Outer)` is 12, as in C.

Three defects remain after this change: [the layouts are never compared](node:layout-agree-check),
[`sizeof` and `alignof` know only some types](node:sizeof-alignof-types) and
[the size of a pointer is hard-coded](node:ptr-size-platform).
