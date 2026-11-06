`sizeof` returns 8 for any pointer (4 bytes of address plus 4 of length, the checked
layout on wasm32) and `alignof` returns 4. A native 64-bit program has 8-byte addresses,
and a release build has no length at all. `sizeof(raw_ptr[T])` in the interpreter can
thus differ from the `sizeof` of the generated C.

The source comment asks the open question: does the target platform have to be chosen
*before* redshifting? As long as it is not answered, a struct containing a pointer cannot
have a layout that is both computed during redshifting and identical to C.
