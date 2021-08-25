# Py4D Imports: How-To

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

!!! warn "Warning"
    Using the naive approach shown above is dangerous and can lead to
    incompatibilties between plugins.

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

!!! note "Note"
    C4DDev currently provides no mechanism to automatically compile Python sources
    and package them as it does with the `c4ddev pypkg` command. There is an
    outstanding task to bring this feature to C4DDev:
    [NiklasRosenstein/c4ddev#8](https://github.com/NiklasRosenstein/c4ddev/issues/8)

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
# localimport-v1.7.3-blob-mcw99
import base64 as b, types as t, zlib as z; m=t.ModuleType('localimport');
m.__file__ = __file__; blob=b'\
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'
exec(z.decompress(b.b64decode(blob)), vars(m)); _localimport=m;localimport=getattr(m,"localimport")
del blob, b, t, z, m;
```

## Using localimport + pypkg

If you're using [`c4ddev pypkg`](../../cli#c4ddev-pypkg) to package additional Python
modules, it is common to have a `devel/` directory with all the dependencies.
In development mode, you can make `localimport` load the dependencies from
that directory, and otherwise load it from the Python Egg generated with
`c4ddev pypkg`.

```python
if _debug:
  _importer = localimport(['devel'])
else:
  _importer = localimport('res/lib-{0}.egg'.format(sys.version[:3].replace('.', '-')))

with _importer:
    import res
    import requests
    from nr.c4d.utils import load_bitmap
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

!!! note "Note"
    You don't need this file in release mode when your third-party modules
    are packaged with [`c4ddev pypkg`](../../cli#c4ddev-pypkg).
