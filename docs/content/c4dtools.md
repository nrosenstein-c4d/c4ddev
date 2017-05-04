+++
title = "C4DTools"
+++

  [Node.Py runtime]: {{< ref "py4d-imports-howto.md#using-the-node-py-runtime" >}}

The **C4DTools** is a Python library that can be used by other plugins that
use the [Node.Py runtime]. To use C4DTools from a Python plugin, you have to
install C4DDev locally with PPYM.

    $ ppym instal c4ddev --save
    $ ls nodepy_modules/
    c4ddev

Then you can require the desired components of **C4DTools** in your plugin.

```python
aabb = require('c4ddev/lib/c4dtools/misc/aabb')
gui = require('c4ddev/lib/c4dtools/gui')
c4dmath = require('c4ddev/lib/c4dtools/math')
```

Note that from the C4D Script Manager, Python Objects, Tags and Nodes, the
path to require the library components is different:

```python
# in C4D scripting context
import c4ddev
c4dmath = c4ddev.require('c4dtools/math')
```

{{< note title="Note" >}}
  API documentation is not available, yet. Please check out the
  [source code](https://github.com/NiklasRosenstein/c4ddev/tree/master/lib/c4dtools).
{{< /note >}}
