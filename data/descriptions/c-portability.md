Packed and aligned structs (see [Layout control](node:layout-control)) and bit
intrinsics (see [Bit-level operations](node:bit-ops)) have no standard spelling in C99:
GCC and Clang provide them as extensions (`__attribute__`, `__builtin_*`), MSVC as
pragmas and intrinsics.

SPy builds with `--std=c99`, using Clang-based compilers (`zig cc`, `emcc`) or the system
`cc`. The proposal is to move to C11, for `_Static_assert` (used by
[the layout check](node:layout-agree-check)), and to hide every extension behind a macro
of one libspy header (`SPY_PACKED`, `SPY_ALIGNED(N)`, `SPY_POPCOUNT`, ...), so that
supporting another compiler means redefining those macros.

Open question: whether MSVC must be supported at all. There is no reason to support a C
version older than C11.
