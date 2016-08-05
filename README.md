# c4ddev

Cinema 4D plugin that makes Python development much easier.

## Contents

#### Scripting in Cinema 4D

c4ddev comes with the [shroud][] module built-in and ready to be used in
scripts and Python expressions. In order to use the `c4ddev` library, simply
import the `require()` function and rock on.

```python
import c4d
from shroud import require
my_utils = require('./my_utils', doc.GetDocumentPath())

def main():
  cube = c4d.BaseObject(c4d.Ocube)
  return my_utils.current_state_to_object(cube)
```

If you want to use standard Python modules, you can use [localimport][]
to load these modules without interfering with the global importer state.

```python
from shroud import require
with require('localimport')(doc.GetDocumentPath()):
  import requests

def main():
  op.GetObject()[]
```

> Note: Using the above technique will cause the `requests` module to be
> reloaded everytime you make changes to your script. If you want to
> avoid this, you can use `localimport` from a module that you load with
> `require()`.

#### Unicode Escape Tool

String resources require special characters to be escaped with unicode
escape sequences in the format of `\UXXXX`. The "Unicode Escape Tool"
can handle this for you. Just enter or paste the stringtable or text
and you can convert it.

![Unicode Escape Tool screenshot](https://i.imgur.com/Phon0PT.png)

#### Python Batch Compiler

This simple command lets you select a directory and it will compile all
Python `*.py` files it can find to `*.pyc` files using the built-in
Cinema 4D Python Interpreter. This is useful to avoid Python magic
number issues if you try to use `python -m compileall` from the command
line since Cinema 4D uses `Python 2.6` and you may have a different
version installed.

#### Egg Maker

Create a Python `*.egg` from a directory. Optionally, it will include
non-Python files and prefer compiled Python over source files.

## License

The MIT License (MIT)

Copyright (c) 2016  Niklas Rosenstein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[shroud]: https://github.com/NiklasRosenstein/py-shroud
[localimport]: https://github.com/NiklasRosenstein/py-localimport
