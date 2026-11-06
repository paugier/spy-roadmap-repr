SPy already has the basics of a low-level language: `@struct` types stored on the stack
and passed by value, `raw_ptr`/`gc_ptr` pointers with optional alignment,
`@force_inline`, and bulk memory operations (`ptr_copy`, `ptr_move`, ...). The nodes of
this pillar list what is still missing for writing numerical kernels, binary-format
parsers and wrappers around C libraries. SIMD and parallelism are out of scope.

All spellings (`InlineArray`, `@noalias`, `ll_union`, ...) are **proposals**. The C code
shown in the descriptions is what the compiler would generate "along these lines", with
simplified names. The features are ordered from the most to the least urgent for
scientific code; the layout defects (the `problem`, `bug` and `task` nodes) are not
features but must be fixed first, because several features rely on the layout
computation.

Calling C libraries and exchanging arrays with other libraries belong to the
[SPy/C integration](node:c-integration) pillar.
