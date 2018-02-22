![](.assets/titlepic.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The C4DDev project aims to make the development of Cinema 4D plugins easier.
It comes with a bunch of utilities in the form of C4D Plugins and command-line
tools, as well as a C++ Py4D API extensions and knowledge resources.  
Check out the [Documentation](https://niklasrosenstein.github.io/c4ddev/) for
detailed information.

## Installation

C4DDev has two separately installable components: A Cinema 4D plugin and
a command-line interface. To install the plugin, download the latest release
from the [Releases Page](https://github.com/NiklasRosenstein/c4ddev/releases)
and unpack it into the plugins directory. The command-line tools can be
installed from [PyPI](https://pypi.python.org/pypi/c4ddev). If you want to
make sure you always have the latest version installed, you should install
from the Git repository's master branch instead.

The command-line tools are compatible with both Python 2 and 3.

## Features

__Prototyping__

* A better version of the Python Generator object which allows you to
  implement `ObjectData.Draw()` inside Cinema 4D
* A Python Shader that allows you to prototype Python shader plugins
* A Python ID (very early WIP!! Contributions are welcome)

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

__Python Scripting__

* Makes the `c4ddev`, `c4dtools` and [`localimport`][localimport] modules
  globally available.
* A context-manager to import Python modules from Python Objects/Expression
  Tags without polluting the global importer state, which also automatically
  re-imports the modules if you modified the code. &ndash; `c4ddev.scripting.localimport()`
* A "Python Scripting Server" which can receive Python scripts to execute
  inside Cinema 4D via a Socket + a *Sublime Text* plugin (see `extras/sublime-script-sender/`)

## Building C++ Extensions

  [Craftr]: https://github.com/craftr-build/craftr

To build the C++ Py4D API extensions, you need a compiler and the [Craftr]
build system installed on your system.

> **To do**: Document the build process with Craftr.

---

<p align="center">Copyright &copy; 2018  Niklas Rosenstein</p>
