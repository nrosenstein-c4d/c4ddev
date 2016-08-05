# c4ddev

Cinema 4D plugin that makes Python development much easier.

#### Available Modules

c4ddev contains these Python modules as they are essential to productive
development inside of Cinema 4D.

- [requests](https://github.com/kennethreitz/requests) - HTTP for Humans
- [shroud](https://github.com/NiklasRosenstein/py-shroud) - `require()` style imports

Modules that can be loaded with `shroud.require()`

- c4ddev - This plugin's utility library
- [localimport](https://github.com/NiklasRosenstein/py-localimport) - Isolated import of Python modules

Modules to be added in future versions

- [numpy](http://www.numpy.org/)
- [scipy](https://www.scipy.org/)

> Supporting these module is not trivial as they need to be built
> separately for Windows and Mac OS (C-extensions). Including these
> builds in the Git source repository is not ideal either.
>
> You can find prebuilt versions of numpy and scipy here:
>  https://public.niklasrosenstein.com/PythonBinaries/

#### Plugins

- Unicode Escape Tool
- Python Batch Compiler
- Egg Maker

## Scripting in Cinema 4D

c4ddev comes with a bunch of useful modules that you can use directly from
your Python Expression Tags, XPresso Nodes or Generators. The `shroud` module
allows you to outsource your into a Python module in your Cinema 4D
project directory and load it from there.

```python
import c4d
import shroud

# Load my_utils.py which is the same directory as the .c4d file.
my_utils = shroud.require('./my_utils', doc.GetDocumentPath())

def main():
  # You can use it like a normal Python module.
  return my_utils.create_freaking_geometry()
```

If you want to use third party modules in Python Expressions, it makes sense
to store these modules with your Cinema 4D scene and not needing them to
be installed on every Cinema 4D installation that you are going to open the
scene with! This ensures that scenes work right away even if you open them
months later in a different Cinema 4D version.

> Note: A little bummer though: Keep in mind that c4ddev itself needs to be
> installed in the Cinema 4D version you are opening the project with!

```python
import c4d
import shroud

localimport = shroud.require('c4ddev/scripting/localimport')
with localimport(doc):
  import twitter

def main():
  # ...
```

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
