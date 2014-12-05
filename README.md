# Devtools for Cinema 4D

*Devtools* is a collection of Cinema 4D plugins, tools and module that
make Cinema 4D plugin development easier.

## Unicode Escape Tool

String resources require special characters to be escaped with unicode
escape sequences in the format of `\UXXXX`. The "Unicode Escape Tool"
can handle this for you. Just enter or paste the stringtable or text
and you can convert it.

*todo: add preview image*

## Python Batch Compiler

This simple command lets you select a directory and it will compile all
Python `*.py` files it can find to `*.pyc` files using the built-in
Cinema 4D Python Interpreter. This is useful to avoid Python magic
number issues if you try to use `python -m compileall` from the command
line since Cinema 4D uses `Python 2.6` and you may have a different
version installed.

## Egg Maker

Create a Python `*.egg` from a directory. Optionally, it will include
non-Python files and prefer compiled Python over source files.

## Scripting Context

The *Devtools* plugin provides a `devtools` module in Cinema 4D that you
can use in your Python Tags and Generators. It provides functionality to
make using third-party Python packages and modules a breeze, you can just
keep it with your scene without the need to install it manually to the
Cinema 4D preferences folder!

The following is an example folder structure:

    my_file.c4d
    python/
      some_module.py

Using `devtools`, you can easily use `some_module` from Python Tags or
Generators.

```python
import devtools
context = devtools.scripting.context(doc)
with context.import_():
    import some_module

def main():
    # You can use some_module now
    return c4d.BaseObject(c4d.Ocube)
```

----

Copyright (C) 2014 Niklas Rosenstein
