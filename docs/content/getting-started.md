+++
title = "Getting Started"
ordering = 1
+++

C4DDev can be installed in two ways: Into your Cinema 4D plugins directory
and as a command-line tool.

## Installing the C4DDev Plugins

  [GitHub Releases]: https://github.com/NiklasRosenstein/c4ddev/releases

Head to the [GitHub Releases] page and download the latest release for your
platform (Windows or macOS). Then unpack the directory into your Cinema 4D
plugins directory.

    Cinema 4D R18/
      plugins/
        c4ddev/
          ...

## Installing the C4DDev command-line tools

You need either Python 2 or 3 installed on your system and the [Pip] package
manager. Pip comes pre-installed with Python 3 on Windows, but with Python 2
you will need to run the [get-pip.py] script first. You may need to start the
terminal with admin privileges to install Pip.

    > python get-pip.py

After this step, you can install the command-line tools by running the
following command (again, you may need admin privileges).

    $ pip install git+https://github.com/NiklasRosenstein/c4ddev.git

Now you should be able to use the `c4ddev` command-line program.

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

!!! todo

## Beginner's Guide: C++

!!! todo
