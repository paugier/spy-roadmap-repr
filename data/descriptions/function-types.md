This node is about passing functions around at run time. The spelling
`Callable[[...], R]` is a **proposal**.

!!! note "Definition: red and blue"
    A *blue* value is computed at compile time, a *red* value at run time. A call whose
    callee is blue is resolved by the compiler and becomes a direct call.

!!! note "Definition: function type, function pointer"
    The *type of a function* is its signature, without parameter names:
    `def(i32, i32) -> i32` for `add` below. A *function pointer* is the address of compiled
    code. Calling through it is an *indirect call*: the target is read at run time instead
    of being fixed by the compiler.

## What exists today

`W_FuncType` (`spy/vm/function.py`) already represents function types. Each distinct
signature is created once, so two functions with the same signature have the same type
object, and `type(add)` returns it.

No annotation can name such a type: `f: def(i32, i32) -> i32` is a `ParseError`, because
SPy uses Python's parser.

Function values are blue only. In

```python
def add(x: i32, y: i32) -> i32:
    return x + y


def main() -> None:
    g = add
    print(g(1, 2))
```

`g` is never reassigned, so the compiler treats it as an alias and `spy redshift` shows a
direct call of `add`:

```python
def main() -> None:
    `_print::println[i32]`(`c::add`(1, 2))
```

A parameter whose type is a function type cannot be called: `W_Func.op_CALL` requires a
blue callee and fails with an `AssertionError` on a red one. The missing piece is therefore
the *red function value*, not the type.

## Proposed API

```python
from types import Callable


def add(x: i32, y: i32) -> i32:
    return x + y


def apply(f: Callable[[i32, i32], i32], a: i32) -> i32:
    return f(a, a)


def main() -> None:
    print(apply(add, 3))
```

`Callable[[i32, i32], i32]` is a blue function returning the existing function type, so it
is the same object as `type(add)`. The first version accepts only plain functions: no
`*args`, no default values, no closures. A closure needs an environment next to the code
address, which a C function pointer cannot hold.

In the C backend, `f` is a function pointer. Approximately:

```c
typedef int32_t (*fn_i32_i32__i32)(int32_t, int32_t);

int32_t spy_test$add(int32_t x, int32_t y) {
    return x + y;
}

int32_t spy_test$apply(fn_i32_i32__i32 f, int32_t a) {
    return f(a, a);               /* indirect call */
}

/* in main: */
spy_test$apply(&spy_test$add, 3);
```

The `typedef` is named after the signature and emitted in the struct-definitions header, so
that every module sees the same one. In the interpreter, a function value is the function
object itself.

## Implementation plan

Each step has its own tests.

☐ **Syntax.** `Callable[[...], R]` as a blue function calling `W_FuncType.new`. Test:
`Callable[[i32, i32], i32] is type(add)`.

☐ **Red callee in the typechecker.** In `callop.w_CALL`, a red argument whose type is a
`W_FuncType` gets an operation for the indirect call instead of `W_Func.op_CALL`. The blue
path is unchanged, so existing code still redshifts to direct calls.

☐ **Redshift.** The indirect call stays a call of a variable. The `is_direct_call` flag of
`W_OpSpec` already tells the two cases apart.

☐ **C backend.** `w2c` maps a function type to the `typedef` above (`context.py`), a
function used as a value is written as its C name, and the call is emitted by `cwriter.py`
as `f(a, b)`.

☐ **Passing functions to compiled code.** Needed for callbacks such as the comparison
function of `qsort`. In the C backend this is the function pointer above. In the
interpreter, compiled code can only call a function that has an address in the WASM
instance, i.e. a function in the bundle (see [`@extern`](node:extern)); an interpreted
function has none. Two options: restrict callbacks to functions that exist compiled, or
give the interpreter trampolines that call back into it. This choice is open.

☐ **First use.** `qsort` from libc, then `sqlite3_exec`, through [`@extern`](node:extern).
