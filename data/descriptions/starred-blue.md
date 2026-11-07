A starred expression is a `*` in front of a sequence, which spreads its elements in place:
`f(*args)` calls `f` with the elements of `args` as separate arguments, `[a, *b]` is the
list of `a` followed by the elements of `b`, and `(*x,)` is a tuple of the elements of `x`.

The parser did not accept them. The pull request makes the parser produce a starred node
in tuples, calls and subscripts, and makes blue code evaluate it when every value is
known at compile time. Starred expressions in compiled code are not part of it.
