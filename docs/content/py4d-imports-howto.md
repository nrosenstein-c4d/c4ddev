+++
title = "Py4D Imports: How-To"
+++

When using and distributing third-party modules in a Cinema 4D Python plugin,
many problems can arise when used incorrectly. Some users have hundreds of
Cinema 4D plugins, and many of them use third-party modules. Some plugins will
stop working when another plugin delivers the same third-party module in a
different version or even one with the same name but completely different
functionality!

When you import modules from your Python Plugin's directory, you should
**never** do it the naive way, unless you EXPLICITLY WANT these third-party
modules to be accessible from the outside (eg. when exposing a Python API
for your plugin).

```python
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import some_module  # The module will live on in sys.modules after the plugin finished loading
```

{{< warning title="Warning" >}}
  Using the naive approach shown above is dangerous and can lead to
  incompatibilties between plugins.
{{< /warning >}}

## Using the Node.Py Runtime

It is generally recommended to make use of the [Node.Py] runtime. This can
be achieved by generating a stand-alone version using the `c4ddev build-loader`
command.

    $ c4ddev build-loader -cmo loader.pyp -e myentrypoint

The generated `loader.pyp` contains the [Node.Py] runtime and its dependencies
and will load `myentrypoint.py` when the plugin is loaded. This file will then
have full access to the Node.Py runtime and can make use of the **nodepy-pm**
package manager.

  [Node.Py]: https://github.com/nodepy/nodepy

    $ nodepy-pm install py/numpy
    $ tree
    | loader.pyp
    | myentrypoint.py
    | utils.py
    | nodepy_modules/
    \-| .pip/
      \-| Lib/
        \-| site-packages/
          \-| numpy/ ...
            | numpy-1.9.2.dist-info/ ...
    $ cat myentrypoint

```python
# myentrypoint.py
import numpy  # loaded from nodepy_modules/.pip/Lib/site-packages
utils = require('./utils')

# Register your C4D Python plugins ...
```

The Node.Py runtime will manage the full isolation of the module environment
(using [localimport][]) and imported Python modules will not be visible to
other plugins.

{{< note title="Note" >}}
C4DDev currently provides no mechanism to automatically compile Python sources
and package them as it does with the `c4ddev pypkg` command. There is an
outstanding task to bring this feature to C4DDev:
[NiklasRosenstein/c4ddev#8](https://github.com/NiklasRosenstein/c4ddev/issues/8)
{{< /note >}}

## Using localimport

  [localimport]: https://github.com/NiklasRosenstein/py-localimport

Using the `localimport` module allows you to import Python modules in an
isolated environment and will ensure that other plugins will not see the
modules that another plugin has imported.

```python
with localimport(['lib']) as _importer:
  # This line would not be necessary if everyone would use localimport,
  # but since we can not garuantee that...
  _importer.disable(['some_module'])
  import some_module
  assert 'some_module' in sys.modules
assert 'some_module' not in sys.modules
```

But how do you use `localimport` when it is a module, too?

The answer is a minified version that you can copy&paste directly into your
plugins source code. Below is a minified version of `localimport-v1.5`. Other
(and eventually newer) versions are available [**here**][1].

  [1]: https://gist.github.com/NiklasRosenstein/f5690d8f36bbdc8e5556

```python
# localimport-v1.5_b64_lw=99
exec("""import base64 as b, zlib as z; s={}; blob=b"\
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"
exec(z.decompress(b.b64decode(blob)), s)
localimport=s["localimport"]; del blob, b, z, s;""")
```

## Using localimport + pypkg

If you're using [`c4ddev pypkg`](cli#pypkg) to package additional Python
modules, it is common to have a `devel/` directory with all the dependencies.
In development mode, you can make `localimport` load the dependencies from
that directory, and otherwise load it from the Python Egg generated with
`c4ddev pypkg`.

```python
if _debug:
  _importer = localimport(['devel'])
else:
  _importer = localimport('res/modules{0}/cloudui.egg'.format(sys.version[:3]))

with _importer:
    _importer.disable(['res', 'c4dtools', 'cloudui', 'res', 'nr'])

    import res
    import c4dtools
    import cloudui
    import nr.concurrency

    from c4dtools.gui import handle_file_select
    from c4dtools.utils import load_bitmap
    from cloudui.utils import (
        get_frame_range, check_region, iter_rdata, calc_tile_size,
        fit_tile_count, Point
    )
```

Note that in most cases, the `devel/` directory will not contain just the
source code of the modules that you want to use, but the complete repository
(eg. when you're using Git submodules, which I highly recommend).

    devel/
      requests/
        requests/
        README.md
        setup.py
        ...

In order to have the correct `sys.path` setup when loading modules from the
`devel/` directory, you can place a `.pth` file into that directory.

    devel/
      devel.pth       <<
      requests/
        requests/
        README.md
        setup.py
      ...

This file can list an additional include directory per line. So for the above
example, in order to be able to import the `requests` module in development mode,
we simply add the following line to the `devel.pth` file.

    requests/requests

{{< note title="Note" >}}
  You don't need this file in release mode when your third-party modules
  are packaged with [`c4ddev pypkg`](cli#pypkg).
{{< /note >}}
