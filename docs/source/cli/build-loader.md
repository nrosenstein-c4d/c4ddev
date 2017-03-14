    Usage: c4ddev build-loader [OPTIONS]

      Generate a Cinema 4D Python plugin that uses Node.py to load an
      entrypoint.

    Options:
      -e, --entry-point ENTRYPOINT
      -c, --compress
      -m, --minify
      -o, --output FILENAME
      --help                  Show this message and exit.

Creates a Cinema 4D `.pyp` file that loads the specified ENTRYPOINT with
[Node.py]. From that point on, the complete Node.py environment may be used
and plugins can use `require()` to load other components. Also, the plugin
will be automatically loaded completely isolated in a [`localimport`](localimport)
context, as it comes built-in with Node.py.

  [Node.py]: https://github.com/nodepy/nodepy

