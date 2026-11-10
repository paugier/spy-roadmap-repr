!!! note "Definition: native launcher"
    A native binary built by SPy that starts without Python and does what it can alone.
    For the other tasks, it starts a Python program (or several) as subprocesses.

Python is started only for the rare cases, so its startup cost is paid only when needed.
The launcher needs a nicer command-line API than the raw arguments SPy already provides
([argparse](node:mod-argparse)) and a way to start a Python program and exchange data
with it ([subprocess](node:mod-subprocess)). Python mode is enough to write it: no
low-level SPy feature is needed for a command-line tool.

The first large example is the `spy` command itself, see
[level 2 of self-hosting](node:selfhost-cli).
