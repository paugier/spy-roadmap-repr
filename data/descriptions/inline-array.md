## Motivation

Small vectors and matrices (a 3D position, a 3×3 tensor, the 5 conserved variables of a
fluid cell) are everywhere in scientific code. Today there are three ways to write them,
and all are poor: a struct with fields `x`, `y`, `z` (no indexing, so no loops), a tuple
such as `tuple[f64, f64, f64]` (its items may have different types, which rules out a
run-time index in general), or a `gc_alloc`'ed buffer (a heap allocation and a pointer
indirection for 3 numbers).

!!! note "Definition: inline storage"
    A value has *inline storage* when its bytes live directly inside the enclosing object or
    stack frame, with no separate allocation and no pointer to follow. SPy structs already
    work this way.

## The `InlineArray` type

The proposed type is `InlineArray[T, N]`. `N` is the length, a blue value (known when the
program is redshifted). `T` is the item type: any type with a fixed size, so a primitive,
a struct, a SIMD vector or another `InlineArray`. An `InlineArray` has inline storage and
is a value type.

!!! note "Definition: value type"
    A *value type* is a type whose objects are copied when they are assigned or passed to a
    function. Structs, SIMD vectors and inline arrays are value types.

It is a basic type of the compiler, kept minimal: indexing, `with_item`, `len` and `==`.
Operators such as `+` and `*` are left to library types built on top of it (see
"Building other types on top" below). `InlineArray` must not be confused with
`array(DTYPE, NDIM)` of `array.spy`, which is a heap-allocated, multi-dimensional array
whose shape is only known at run time.

## Reading and replacing items

```python
def dot(a: InlineArray[f64, 3], b: InlineArray[f64, 3]) -> f64:
    s = 0.0
    for i in range(3):
        s = s + a[i] * b[i]
    return s

def scale(a: InlineArray[f64, 3], k: f64) -> InlineArray[f64, 3]:
    for i in range(3):
        a = a.with_item(i, a[i] * k)
    return a
```

`a.with_item(i, v)` returns a new array equal to `a` except at index `i`. `scale`
therefore only changes its own copy of `a`, and the caller's array is untouched.

The lowered code (simplified) wraps the C array in a struct, because a bare C array
cannot be passed or returned by value: it silently turns into a pointer to its first
item.

```c
typedef struct { double items[3]; } InlineArray_f64_3;

double dot(InlineArray_f64_3 a, InlineArray_f64_3 b) {
    double s = 0.0;
    for (int32_t i = 0; i < 3; i++) {
        /* checked mode: verify 0 <= i < 3 */
        s = s + a.items[i] * b.items[i];
    }
    return s;
}

InlineArray_f64_3 scale(InlineArray_f64_3 a, double k) {
    for (int32_t i = 0; i < 3; i++) {
        a.items[i] = a.items[i] * k;   /* with_item on the local copy */
    }
    return a;
}
```

Indexing is checked like pointers are: a constant index is checked at compile time, a
run-time index is checked in checked (debug) mode and unchecked in release mode.

A value is never modified item by item, so assigning to an item of a local variable or a
parameter is an error:

```python
def double_first(v: InlineArray[f64, 3]) -> None:
    v[0] = 2 * v[0]   # error
```

Without the error, this function would compile and silently do nothing for the caller.
The message explains it: `InlineArray` is a value type, so return a new array built with
`with_item`, or take a reference to modify the array in place.

## Writing items in memory

An array stored in memory can be written item by item through a reference, exactly like
`r.a.x = 0` on a nested struct (see [gc_ref and raw_ref](node:gc-ref)). Reading a field
of struct or array type through a pointer gives a reference to it, not a copy.

```python
@struct
class Cell:
    rho: f64
    q: InlineArray[f64, 3]

def damp(p: gc_ptr[Cell], k: f64) -> None:
    for i in range(3):
        p.q[i] = p.q[i] * k
```

Here `p.q` is a reference to the array inside the heap-allocated `Cell`, and `p.q[i] = v`
writes the item in place. The lowered code (simplified):

```c
typedef struct { double rho; InlineArray_f64_3 q; } Cell;

void damp(gc_ptr_Cell p, double k) {
    for (int32_t i = 0; i < 3; i++) {
        /* checked mode: verify 0 <= i < 3 */
        p.p->q.items[i] = p.p->q.items[i] * k;
    }
}
```

An item of struct or array type is also reached by reference, which is what makes
`m[i][j] = v` work on a matrix in memory. A matrix is an array of arrays,
`InlineArray[InlineArray[f64, 3], 3]`, stored contiguously row by row.

## Building other types on top

Since `InlineArray` is a value type, a function cannot modify its caller's array.
Python-style code such as `v[0] = 2 * v[0]` needs a type with reference semantics. It is
written in the stdlib or in a package, with the idiom of `Array1d` in
`examples/4_advanced/myarray.spy`: a struct holding a `gc_ptr` to the data.

```python
@struct
class VecData:
    items: InlineArray[f64, 3]

@struct
class Vec3:
    __ll__: gc_ptr[VecData]

    def __getitem__(self, i: i32) -> f64:
        return self.__ll__.items[i]

    def __setitem__(self, i: i32, x: f64) -> None:
        self.__ll__.items[i] = x

def double_first(v: Vec3) -> None:
    v[0] = 2 * v[0]
```

`Vec3` is copied as a pointer, so `double_first` modifies the caller's vector. Its
`__setitem__` writes through the reference `self.__ll__.items`. The lowered code
(simplified):

```c
typedef struct { InlineArray_f64_3 items; } VecData;
typedef struct { gc_ptr_VecData __ll__; } Vec3;

void double_first(Vec3 v) {
    v.__ll__.p->items.items[0] = 2 * v.__ll__.p->items.items[0];
}
```

The same layer defines the arithmetic: item-by-item `+` and `*`, scalar broadcasting, a
matrix product, and so on, each library choosing the meaning of `*` that suits it. The
stdlib can provide blue-generic helpers that apply an operation to every item, so these
types do not repeat the loops.

## Design choices compared to other languages

- **Name.** C, Rust, Go and Zig call it just "array" and give the heap-allocated one
  another name. `InlineArray` is the name used by Swift and Mojo (C# has an
  `[InlineArray]` attribute). It also avoids a clash with the heap-allocated `array` of
  `array.spy`.
- **Value type with the length in the type.** As in Rust, Go and C++ `std::array`, and
  unlike C, where an array turns into a pointer when passed to a function.
- **No special syntax for the length.** `InlineArray[f64, 3]` is an ordinary generic type
  whose parameter `N` is a blue value, comparable to Rust const generics.
- **Immutable local variables.** Rust (`let mut`), Go, C++ and Zig (`var`) allow
  `a[i] = v` on a local array. In Python, `def double_first(v): v[0] = 2 * v[0]` is the
  natural way to modify an argument, and with a value type it would silently modify a
  copy. SPy makes it an error, as it already does for assignments to fields of struct and
  SIMD values. `with_item` plays the role of `setindex` on Julia's immutable `SVector`;
  the role of Julia's mutable `MVector` is played by library types with reference
  semantics.
- **Checked indexing.** Rust and Go reject a constant out-of-range index at compile time
  and always check run-time indices. C and C++ never check. SPy sits in between: checked
  in debug mode only, as for pointers.
- **No operators in the core.** Rust, Go and C++ `std::array` define no operators on
  arrays either. Item-by-item arithmetic lives in library types, as with Eigen or Julia's
  StaticArrays, which are libraries too.
- **Matrices.** Nested arrays, as in C, Rust and Go, rather than a dedicated
  two-dimensional type like Eigen's `Matrix<T, 3, 3>` or Julia's `SMatrix`.
