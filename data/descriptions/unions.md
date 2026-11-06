!!! note "Definition: union and tagged union"
    A *union* is a type whose fields all share the same bytes: its size is the size of its
    largest field, and only one field is meaningful at a time. A *tagged union* (also
    called variant or sum type) pairs a union with a small integer, the *tag*, which
    records which field is meaningful.

The low-level building block is `ll_union`, which is unsafe: nothing prevents reading a
field other than the one that was written. It is a blue function that returns a type; it
takes a dict from field names to types.

```python
Number = ll_union({"i": i64, "f": f64})

n = Number(i=42)
print(n.i)  # 42
print(n.f)  # the bits of 42 read as an f64: a tiny denormal number
```

## Variants

Variants (see the book page on inheritance, variants and protocols) are lowered to a
tagged union: a struct holding the tag and an `ll_union` of the payloads. Written by hand
for a variant with two cases, `Circle` and `Rect`:

```python
@struct
class Circle:
    r: f64

@struct
class Rect:
    w: f64
    h: f64

ShapeData = ll_union({"circle": Circle, "rect": Rect})

@struct
class Shape:
    tag: u8  # 0: circle, 1: rect
    data: ShapeData

def area(s: Shape) -> f64:
    if s.tag == 0:
        return 3.14159 * s.data.circle.r * s.data.circle.r
    else:
        return s.data.rect.w * s.data.rect.h
```

```c
typedef struct { double r; } Circle;
typedef struct { double w; double h; } Rect;
typedef union { Circle circle; Rect rect; } ShapeData;
typedef struct { uint8_t tag; ShapeData data; } Shape;   /* size 24 */
```

`Shape` has size 24, not 17: `data` must be 8-byte aligned, so 7 bytes of padding follow
`tag`. A variant is therefore the sum of a tag and the *largest* case, rounded up by the
alignment.
