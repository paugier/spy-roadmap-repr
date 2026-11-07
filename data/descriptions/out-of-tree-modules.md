An out-of-tree builtin module is a Python package, outside the SPy source tree, that
exposes a `MODULE` (a `ModuleRegistry`) and a `build_info` function. The example
`examples/out-of-tree/spyvm_qrcodegen` wraps the QR-code library qrcodegen. A SPy program
uses it like any module:

```python
import qrcodegen


def main(argv: list[str]) -> i32:
    qr = qrcodegen.encode(argv[1])
    size = qrcodegen.get_size(qr)
    if size == 0:
        print("failed to encode QR code")
        return 1
    return 0
```

Each wrapped function needs three pieces, which is why this is a stopgap.

## The C glue

`src/spyvm_qrcodegen.c` includes the headers of libspy and of the wrapped library. It
converts SPy objects to C types and back, and exports functions named
`spy_<module>$<function>`. `WASM_EXPORT` makes them WASM exports and does nothing on native
targets:

```c
int32_t WASM_EXPORT(spy_qrcodegen$get_size)(spy_BytesObject *qr) {
    if (qr->length == 0) {
        return 0;
    }
    return qrcodegen_getSize(spy_BytesObject_DATA(qr));
}
```

## The Python binding

`__init__.py` declares the functions visible from SPy. In the interpreter, `vm.ll.call`
calls the WASM export; the C backend calls the same C function directly, by its C name:

```python
MODULE = ModuleRegistry("qrcodegen")


@MODULE.builtin_func
def w_get_size(vm: "SPyVM", w_qr: W_Bytes) -> W_I32:
    size = vm.ll.call("spy_qrcodegen$get_size", w_qr.ptr)
    return vm.wrap(size)
```

## The build information

`build_info(target, build_type)` returns the include directories, the headers, and the
static archive built by the module's Makefile
(`build/<target>/<build-type>/spyvm_qrcodegen.a`), plus linker flags such as `-lmagic`. SPy
picks the archive matching the current target. A project lists its modules in `spy.toml`
(`extra-vm-modules = ["../spyvm_qrcodegen"]`); the command line has the equivalent
`--extra-vm-module` option.

## What works where

The interpreter can call the library only if a WASM build of it exists:

|             | `spyvm_qrcodegen`          | `spyvm_libmagic`         |
| ----------- | -------------------------- | ------------------------ |
| Library     | vendored in the repository | installed on the system  |
| WASM build  | yes                        | no                       |
| Interpreter | works                      | `NotImplementedError`    |
| C backend   | works                      | works, linking `-lmagic` |

The direct mechanism that would remove the glue is [`@extern`](node:extern).
