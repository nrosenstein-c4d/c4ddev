# Welcome to C4DDev!

The C4DDev project aims to make the development of Cinema 4D plugins easier.
It comes with a bunch of utilities in the form of C4D Plugins and command-line
tools, as well as a C++ Py4D API extensions and knowledge resources.

The Cinema 4D Plugins can be found in the "Script > C4DDev" menu.

![](https://i.imgur.com/bz3OHnD.png)

## Features

__Prototyping__

* A better version of the Python Generator object which allows you to
  implement `ObjectData.Draw()` inside Cinema 4D
* A Python Shader that allows you to prototype Python shader plugins
* A Python ID (very early WIP!! Contributions are welcome   )

__Description Resources__

* A tool to generate unicode escape code sequences compatible with Cinema
  4D STRINGTABLE files (Unicode Escape Tool Plugin)

__Python Extensions__

* Provides new functions to the Cinema 4D Python API implemented in C++ for
  functionality that was not formerly accessible in Cinema 4D in the `c4ddev`
  module (only if C++ extensions are available, which they are when installing
  a release from the Releases page if not otherwise noted)

__Python Plugins__

  [localimport]: https://github.com/NiklasRosenstein/py-localimport

* A command-line tool to generate a Python plugin with the [localimport]
  bootstrapping code &ndash; `c4ddev bootstrapper`
* A command-line tool to generate Python code or JSON data from the resource
  symbols of your plugin &ndash; `c4ddev symbols`
* A command-line tool to build a byte-compiled distribution of additional
  Python modules as `.egg` files. &ndash; `c4ddev pypkg`
* A command-line tool to protect a Python Plugin File (`.pyp`). Note that
  this requires C4DDev with the C++ extensions installed in the Cinema 4D
  version that you are working with. &ndash; `c4ddev source-protector`

__Python Scripting__

* Provides some additional Python modules
  * `c4ddev` (module that implements this plugin)
  * [`localimport`][localimport] (used in `c4ddev.scripting.localimport`)
  * `nr` (mostly generic programming tools used in c4ddev)
  * `nr.c4d` (Cinema 4D algorithms and UI tools)
  * **To do**: Some common mathematical libraries such as Numpy
* A context-manager to import Python modules from Python Objects/Expression
  Tags without polluting the global importer state, which also automatically
  re-imports the modules if you modified the code. &ndash; `c4ddev.scripting.localimport()`
* A "Python Scripting Server" which can receive Python scripts to execute
  inside Cinema 4D via a Socket + a *Sublime Text* plugin (see `extras/sublime-script-sender/`)

## License

```
The MIT License (MIT)

Copyright (c) 2014  Niklas Rosenstein

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
