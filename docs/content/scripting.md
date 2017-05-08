+++
title = "Scripting"
+++

The **C4DDev** API provides some utilities that are especially useful for
scripting and prototyping in Cinema 4D.

## Per-Project libraries

This is extremely useful when using third party libraries in scripts or
Python Objects/Tags. You can keep the dependencies together with your
Cinema 4D scene file and only make sure that **C4DDev** is installed if
you move the scene around.

```python
from c4ddev import require
localimport = require('c4ddev/scripting/localimport')
# This is a version of localimport that is tuned to work from inside any
# scripting context in Cinema 4D (Tag, Object, XPresso Node).

with localimport(doc):
  import twitter

def main():
  # TODO: Some clever example
```

See also: [C4DTools]({{< ref "c4dtools.md" >}})

> **TODO**: Ability to create a `require()` function for the script, so you
> can not only `import` modules from the project location but also use
> `require()` for modules in the project directory.

## Script Server

Originally the **SublimeScript** plugin, this allows you to turn on a socket
listening for scripts to be executed in Cinema 4D. In the `extras/` directory
of C4DDev, you can find a plugin for Sublime Text that allows you to send a
script to Cinema 4D.

![](../plugins/sublimescript.png)

{{< warning title="Caution" >}}
  Note that enabling the Script Server can make your computer vulnerable
  to **targeted attacks**. Use only for development purpose and do not use on
  production servers.
{{< /warning >}}
