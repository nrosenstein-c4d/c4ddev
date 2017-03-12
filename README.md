# C4DDev

<a href="https://niklasrosenstein.github.io/c4ddev/">
  <img src="https://cdn2.iconfinder.com/data/icons/bitsies/128/EditDocument-32.png"
      style="vertical-align:middle" align="right"></img>
</a>

The C4DDev project is a set of Cinema 4D plugins, command-line tools and
scripting utilities for Cinema 4D that aims to make the prototyping, development
and distribution of Cinema 4D plugins easier. The documentation also contains
some interesting resources for Python and C++ plugin development.

## Installing the Command-line Tools

To install the C4DDev command-line tools, you first need to install [Node.py]
via [Pip] (the Python package manager), preferrably using Python 2.7 since
Cinema 4D is also equipped with this version. Then you can install C4DDev via
[PPYM] and you're ready to go.

    $ pip install node.py
    $ ppym install --global @niklas/c4ddev
    $ c4ddev version

For a information on the available sub-commands, check out the
[documentation](https://niklasrosenstein.github.io/c4ddev/cli/).

  [Node.py]: https://github.com/nodepy/nodepy
  [Pip]: https://pypi.python.org/pypi/pip
  [PPYM]: https://ppym.org/

## Installing the C4DDev Plugins and Scripting Utilities

Check the [Releases][] page and download the latest ZIP archive. Unpack the
contents your Cinema 4D plugins directory, and you're done. Check out the
documentation on the available [plugins](https://niklasrosenstein.github.io/c4ddev/plugins/)
and the [scripting utilities](https://niklasrosenstein.github.io/c4ddev/api/).

  [Releases]: https://github.com/nr-plugins/c4ddev/releases

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
