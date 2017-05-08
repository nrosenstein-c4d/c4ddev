+++
title = "Getting Started"
+++

## Installing C4DDev

There are multiple components of C4DDev can be installed separately. To
install the Cinema 4D plugins, you should go to the [GitHub Releases] page
and download the appropriate release for your Cinema 4D version and platform.
This download will contain the full C4DDev Python and prebuilt binaries of
the C++ components.

  [GitHub Releases]: https://github.com/NiklasRosenstein/c4ddev/releases


You install the C4DDev plugin the same as you would do with any other plugin.
Simply extract the archive into the Cinema 4D plugins directory. For
development, I generally recommend working in the Cinema 4D's application
plugin directory, **not** in the user preferences plugin directory.

    Cinema 4D R18/
      plugins/
        c4ddev/
          ...

## Installing C4DDev CLI

You need [Python 2 or 3][python] installed on your system and the [Pip]
package manager. If you don't have Pip installed in your Python installation,
download [get-pip.py] and run it. Then install [Node.py]. If you are own macOS,
you might need to prepend the work `sudo` before the command.

    $ pip install node.py

After this step is complete, you can install the C4DDev Command-line tools
by running

    $ ppym install --global c4ddev

Depending on your System and installation of Python, the Command-line Tools
will have been installed to either `~/.local/bin` or somewhere in
`~/AppData/Local/Programs/Python`. You should make sure that this path is
in your `PATH` environment variable. Now run the following and see if it
works.

    $ c4ddev
    Usage: c4ddev [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      build-loader      Generate a Cinema 4D Python plugin that uses...
      get-pip           Installs Pip into the Cinema 4D Python...
      pip               Invokes Pip in the current Cinema 4D Python...
      pypkg             Reads a JSON configuration file, by default...
      rpkg              Converts a resource package file to...
      run               Starts C4D.
      source-protector  Protect .pyp files (requires APEX).
      symbols           Extracts resource symbols.

  [Pip]: https://pypi.python.org/pypi/pip
  [Node.py]: https://github.com/nodepy/nodepy
  [get-pip.py]: https://bootstrap.pypa.io/get-pip.py
  [python]: https://python.org/

## Beginner's Guide: Python

{{< note title="Todo" >}}
{{< /note >}}

## Beginner's Guide: C++

{{< note title="Todo" >}}
{{< /note >}}
