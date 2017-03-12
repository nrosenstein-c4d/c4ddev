# C4DDev Plugins

C4DDev comes with a bunch of useful plugins.

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
