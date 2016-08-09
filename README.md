# c4ddev

Cinema 4D plugin that makes Python scripting and plugin development
in general much easier. Be sure to check out the [Wiki][] for a lot of
useful resources on Python and even C++ development in Cinema 4D.

## Features

- Ready-to-use [Python modules][] like [requests][]
- [Export plugin resource symbols][] to Python code as class or module or JSON
- Manage plugin resources and translations more efficiently with
  [Resource Packages][]
- Extensive [Wiki][] with tips & tricks for C++ & Python development
  - [Scripting with c4ddev](https://github.com/nr-plugins/c4ddev/wiki/c4ddev_scripting)
  - [c4ddev Extension Plugins](https://github.com/nr-plugins/c4ddev/wiki/c4ddev_ext)
  - [How to use 3rd Part modules](https://github.com/nr-plugins/c4ddev/wiki/python_third_party_modules)
  - and much more..

[requests]: https://github.com/kennethreitz/requests
[Python modules]: https://github.com/nr-plugins/c4ddev/wiki/c4ddev_modules
[Export plugin resource symbols]: https://github.com/nr-plugins/c4ddev/wiki/c4ddev_resource_symbols
[Resource Packages]: https://github.com/nr-plugins/c4ddev/wiki/c4ddev_resource_packages
[Wiki]: https://github.com/nr-plugins/c4ddev/wiki

## Installation

Head to the [Releases][] page and download the latest ZIP archive. Unpack the
contents of this archive into your Cinema 4D plugins directory. If you want to
make use of the c4ddev Commandline, you will have to install a few additional
required components. You can do that easily with `pip`:

    pip install -r bin/requirements.txt

[Releases]: https://github.com/nr-plugins/c4ddev/releases

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
