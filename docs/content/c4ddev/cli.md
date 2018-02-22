+++
title = "Command-line Tools"
+++

## Installation

To install the command-line tools, you need [Node.Py][].

    $ pip install node.py
    $ nodepy-pm install --global c4ddev

*(Note: You can also install the command-line tools locally for your project
by omitting the `--global` option and adding `nodepy_modules/.bin` to your
`PATH`)*

  [Node.Py]: https://github.com/nodepy/nodepy

## `c4ddev`

    Usage: c4ddev [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      build-loader      Generate a Cinema 4D Python plugin that uses...
      get-pip           Installs Pip into the Cinema 4D Python...
      init              Create template source and description files...
      pip               Invokes Pip in the current Cinema 4D Python...
      pypkg             Reads a JSON configuration file, by default...
      rpkg              Converts a resource package file to...
      run               Starts C4D.
      source-protector  Protect .pyp files (requires APEX).
      symbols           Extracts resource symbols.

## `c4ddev disable`

    Usage: c4ddev.exe disable [OPTIONS] [PLUGIN]

      Disable the Cinema 4D PLUGIN by moving it to a `plugins_disabled`
      directory. Use the `c4ddev enable` command to reverse the process. If
      PLUGIN is not the name of a directory in the Cinema 4D plugins directory,
      the closest match will be used.

      When no PLUGIN is specified, a list of the directories in the plugins
      directory will be printed.

    Options:
      --help  Show this message and exit.

## `c4ddev enable`

    Usage: c4ddev.exe enable [OPTIONS] [PLUGIN]

      Enable a disabled plugin.

    Options:
      --help  Show this message and exit.

## `c4ddev build-loader`

    Usage: c4ddev build-loader [OPTIONS]

      Generate a Cinema 4D Python plugin that uses Node.py to load an
      entrypoint.

    Options:
      -e, --entry-point ENTRYPOINT
      -c, --compress
      -m, --minify
      -o, --output FILENAME
      --help                        Show this message and exit.

Generates a Cinema 4D plugin that contains a stand-alone version of
[Node.Py][] and loads the entrypoint specified with `-e,--entry-point`.
The file loaded by this "loader plugin" has full access to the [Node.Py][]
runtime. Access to the underlying module objects can be retrieved using
`require.contenx.binding()`.

```python
nodepy = require.context.binding('nodepy')
localimport = require.context.binding('localimport')
```

## `c4ddev init`

    Usage: c4ddev init [OPTIONS] DESCRIPTION_NAME ...

      Create template source and description files for one or more Cinema 4D
      plugins.

    Options:
      -O, --object TEXT
      -T, --tag TEXT
      -X, --shader TEXT
      -Gv, --xnode TEXT
      -M, --material TEXT
      --main               Generate a main.cpp template.
      -R, --rpkg           Create .rpkg files instead of description header and
                          stringtable files.
      --src TEXT           Source code directory. If not specified, defaults to
                          src/ or source/, depending on which exists.
      -P, --pluginid       Grab plugin IDs from the PluginCafe for the plugins
                          that are being created.
      --overwrite
      --help               Show this message and exit.

## `c4ddev license`

  Usage: c4ddev.exe license [OPTIONS] NAME

    Output a license string, optionally formatted for a specific language.

  Options:
    -l, --list        Output a list of available licenses.
    --short / --long  Outputs the short or long license version (default is
                      --short).
    --python          Output the license as Python comments (#).
    --c               Output the license as C comments (/* */).
    --java            Output the license as Java comments (/** */)
    --help            Show this message and exit.

Currently supported license types:

* apache-v2
* gpl-v2
* gpl-v3
* mit
* unlicense

## `c4ddev get-pip`

    Usage: c4ddev get-pip [OPTIONS]

      Installs Pip into the Cinema 4D Python distribution. Specify the path to
      Cinema 4D explicitly or run this command from inside the Cinema 4D
      application directory.

    Options:
      --c4d DIRECTORY
      --help           Show this message and exit

## `c4ddev pip`

    Usage: c4ddev pip [OPTIONS] [ARGS]...

      Invokes Pip in the current Cinema 4D Python distribution. Must be used
      from inside the Cinema 4D applications directory or specified with --c4d.

    Options:
      --c4d DIRECTORY
      --help           Show this message and exit.

## `c4ddev pluginid`

    Usage: c4ddev pluginid [OPTIONS] [TITLES]...

      Get one or more plugin IDs from the plugincafe. If the username and/or
      password are not specified on the command-line, they will be queried
      during execution.

    Options:
      -u, --username TEXT
      -p, --password TEXT
      -l, --list           List all registered plugin IDs.
      --help               Show this message and exit.

__Example__:

    $ c4ddev pluginid -u nux95 MyPluginId
    PluginCafe Password:
    MyPluginId: 1039296
    $ c4ddev pluginid -u nux95 --list | wc
    PluginCafe Password:
        536    1180   15994

## `c4ddev pypkg`

    Usage: c4ddev pypkg [OPTIONS] [CONFIG]

    Options:
      --help  Show this message and exit.

The **pypkg** command compiles Python modules and packages into `.pyc` files
and merges them into a Python Egg archive or directory. This is useful to
protect your Python code and to distribute your Python plugin.

!!!note
    Keep in mind that you should always use [`localimport`](localimport)
    to import any third-party Python modules from a Cinema 4D plugin in
    order to keep the global importer state clean.

__Example Configuration__ (`.pypkg`)

This is a real-world example configuration file.

```json
{
  "zipped": true,
  "output": "res/modules{target}/mylibs.egg",
  "include": [
    "devel/res.py",
    "../vendor/py-nr/nr"
  ]
}
```

## `c4ddev rpkg`

    Usage: c4ddev rpkg [OPTIONS] RPKG

      Converts a resource package file to description resource files.

    Options:
      -r, --res DIRETORY
      --no-header TEXT
      --help              Show this message and exit.

See also: [Resource Packages]({{< ref "resource-packages.md" >}})

## `c4ddev run`

    Usage: c4ddev run [OPTIONS] [ARGS]...

      Starts C4D.

    Options:
      -e, --exe TEXT  Name of the C4D executable to run. Defaults to "CINEMA 4D".
      --help          Show this message and exit.

Finds the Cinema 4D application directory from the current working directory
and starts `CINEMA 4D.exe` or `CINEMA 4D.app/Contents/MacOS/CINEMA 4D`,
depending on your platform. Additional arguments are passed to Cinema 4D.

On Windows, Cinema 4D is started with the `start /b /wait "parentconsole"`
command, which will cause the current terminal to inherit the output instead
of Cinema 4D creating a separate terminal window.

## `c4ddev source-protector`

    Usage: c4ddev source-protector [OPTIONS] FILENAME [FILENAME [...]]

      Protect .pyp files (requires APEX).

    Options:
      --help  Show this message and exit.

Protects a Cinema 4D Python Plugin (`.pyp`). Requires the **C4DDev** C++
parts installed. More information on the [API Extensions]({{< ref "apiext.md" >}}) page.
If the C++ parts are not installed, nothing will happen and no error will
be printed.

## `c4ddev symbols`

    Usage: c4ddev symbols [OPTIONS]

    Options:
      -f, --format FORMAT      The output format, one of {class,file,json}.
                               Defaults to class.
      -o, --outfile FILENAME
      -d, --res-dir DIRECTORY  One or more resource directories to parse for
                               symbols. If the option is not specified, `res/`
                               will be used.
      --help                   Show this message and exit.

Extracts the resource symbols from all header files in `res/` directory or the
directory/ies specified via `-d,--res-dir` and formats them as a Python class,
Python file or JSON.

```
$ pwd
/Users/niklas/Applications/Cinema 4D R18/plugins/myplugin
$ c4ddev symbols

exec ("""class res(object):
 # Automatically generated with c4ddev v1.3.
 project_path = os.path.dirname(__file__)
 def string(self, name, *subst):
  result = __res__.LoadString(getattr(self, name))
  for item in subst: result = result.replace('#', item, 1)
  return result
 def tup(self, name, *subst):
  return (getattr(self, name), self.string(name, *subst))
 def path(self, *parts):
  path = os.path.join(*parts)
  if not os.path.isabs(path):
   path = os.path.join(self.project_path, path)
  return path
 file = path  # backwards compatibility
 def bitmap(self, *parts):
  b = c4d.bitmaps.BaseBitmap()
  if b.InitWith(self.path(*parts))[0] != c4d.IMAGERESULT_OK: return None
  return b
 MYSYMBOL = 1000
 MYOTHERSYMBOLS = 1001
 res=res()""")
```

__Available Formats__

  - Python class (`class`) [default] -- Can be copied into the Python plugin source
  - Python file (`file`)  -- Can be loaded as a module (make use of [`localimport`](localimport))
  - JSON (`json`) -- Can be loaded using the `json` module
