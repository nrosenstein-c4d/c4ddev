# Contents

## Third-party Modules

When **c4ddev** is installed to Cinema 4D, it provides some useful modules
out-of-the-box. These are intended to be used for scripting only! Plugins
should never rely on these modules to be available and instead distribute
them with the plugin using [`c4ddev pypkg`](cli#pypkg) and
[`localimport`](localimport).

- [`requests`](https://github.com/kennethreitz/requests)
- [`py-require`](https://github.com/NiklasRosenstein/py-require)

## Require Modules

These modules must be loaded using the `require` module.

- [`c4ddev`](api)
- [`localimport`](https://github.com/NiklasRosenstein/py-localimport)

## Cinema 4D Plugins

c4ddev comes with a bunch of useful plugins for Cinema 4D. These are loaded
from `.py` files in the plugin's `ext/` directory.

### Unicode Escape Tool

String resources require special characters to be escaped with unicode
escape sequences in the format of `\UXXXX`. The "Unicode Escape Tool"
can handle this for you. Just enter or paste the stringtable or text
and you can convert it.

![Unicode Escape Tool Screenshot](https://i.imgur.com/Phon0PT.png)

### PyShader

This simple Cinema 4D plugin allows you to write shaders on-the-fly or
prototype for a native shader plugin.

![PyShader Screenshot](http://i.imgur.com/3NKksrW.png)

### PyDrawHelper

This is a very old plugin that I wrote in 2011. It's a Python Object in which you can
write Python code and that code is executed during the `Draw()` function. Very useful
for testing and prototyping.

> __Note__: The code also looks like it was written back in 2011! I will update it
> soon to bring it up to speed with my current standards.

![PyDrawHelper Screenshot](https://i.imgur.com/xyY4btk.png)

### Python Batch Compiler

This simple command lets you select a directory and it will compile all
Python `*.py` files it can find to `*.pyc` files using the built-in
Cinema 4D Python Interpreter. This is useful to avoid Python magic
number issues if you try to use `python -m compileall` from the command
line since Cinema 4D uses `Python 2.6` and you may have a different
version installed.

### Egg Maker

Create a Python `*.egg` from a directory. Optionally, it will include
non-Python files and prefer compiled Python over source files.
