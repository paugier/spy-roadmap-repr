!!! note "Definition: alignment, padding and layout"
    A CPU reads an `i32` efficiently only at an address multiple of 4: that is its
    *alignment*. To keep every field aligned, a compiler inserts unused bytes called
    *padding* between fields. The *layout* of a struct is the set of its field offsets
    and its total size.

A struct `{a: i8, b: i32}` has size 8: `a` at offset 0, 3 bytes of padding, `b` at offset
4. Some programs need to choose the layout themselves: binary file formats and network
headers have no padding, and arrays of structs shared between threads or with hardware
must start on a cache line.

## Proposal

Three tools:

```python
@struct(packed=True)
class Header:
    magic: u32
    version: u8
    length: u32

@struct(align=64)
class Counter:
    value: i64

assert sizeof(Header) == 9
assert offsetof(Header, "length") == 5
assert alignof(Counter) == 64
```

- `packed=True` removes all padding;
- `align=N` aligns every instance of the struct on `N` bytes (this differs from the
  existing `gc_ptr[T, align(N)]`, which describes only a pointer);
- `offsetof(T, "field")` is a blue function returning the byte offset of a field.

In `calc_layout` (see [calc_layout follows the C layout rules](node:calc-layout-c-rules)),
a packed struct uses alignment 1 for all its fields, and `align=N` raises the alignment
of the struct to `N` before its size is rounded up.

## Lowered C

```c
struct __attribute__((packed)) Header {
    uint32_t magic;
    uint8_t version;
    uint32_t length;
};

struct __attribute__((aligned(64))) Counter {
    int64_t value;
};
```

Reading `Header.length` is a misaligned access (offset 5). The `packed` attribute makes
the C compiler generate the safe form, which is slower on some CPUs and illegal to do by
hand with a pointer cast on others. `__attribute__` is a GCC and Clang extension, hence
the dependency on [C11 and portability macros](node:c-portability).
