<img src="logo.png" align="right">

# C4DDev

C4DDev is a project that provides powerful tools and knowledge to Cinema 4D
C++ and Python plugin developers. Check out the [documentation][] for detailed
information on what C4DDev can do for you. It also contains a number of
knowledge resources.

  [documentation]: https://niklasrosenstein.github.io/c4ddev/

## What is C4DDev?

3 things.

- A command-line tool
- A Cinema 4D plugin
- A knowledge resource

The __Command-line Tools__ allow you to extract resource symbols in Python
syntax, prepare third-party Python modules for distribution, install and run
Pip in Python for Cinema 4D, start C4D from the command-line easily, and more.

The __Cinema 4D plugin__ provides you with useful tools such as escaping
unicode characters for Cinema 4D description stringtables, objects and
shaders for rapid prototyping and a small integrated development environment.

Additionally, you can use C4DDev to easily load an optimized version of the
`localimport` context manager into a script, allowing you to use additional
Python modules in Python scripts and generators. In the below example, the
`twitter` module can be either in the same directory as your Cinema 4D scene
file or in a `python/` subdirectory.

```python
import c4ddev
localimport = c4ddev.require('c4ddev/scripting/localimport')

with localimport(doc):
  import twitter
```

## Installation

To install the command-line tools, you need [Node.Py][].

    $ pip install node.py
    $ nodepy-pm install --global @NiklasRosenstein/c4ddev

*(Note: You can also install the command-line tools locally for your project
by omitting the `--global` option and adding `nodepy_modules/.bin` to your
`PATH`)*

  [Node.Py]: https://github.com/nodepy/nodepy

To install the Cinema 4D plugin, download the [latest release][releases]
and unpack it into your Cinema 4D plugins folder.

  [releases]: https://github.com/NiklasRosenstein/c4ddev/releases

## License

```
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
```
