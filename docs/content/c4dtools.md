+++
title = "C4DTools"
+++

  [Node.Py runtime]: {{< ref "py4d-imports-howto.md#using-the-node-py-runtime" >}}

The **C4DTools** is a Python library that can be used by other plugins that
use the [Node.Py runtime]. To use C4DTools from a Python plugin, you have to
install C4DDev locally with **nodepy-pm**.

    $ nodepy-pm instal c4ddev --save
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

## MenuParser

*Note: This module requires the [`nr`][nr] Python third-party package.*

  [nr]: https://github.com/NiklasRosenstein/py-nr

This module implements parsing a menu resources and rendering them
into a dialog. The following is an example resource file:

    MENU MENU_FILE {
      MENU_FILE_OPEN;
      MENU_FILE_SAVE;
      --------------;         # Adds a separator.
      COMMAND COMMAND_ID;     # Uses GeDialog.MenuAddCommand().
      COMMAND 5159;           # Same here.

      # Create a sub-menu.
      MENU MENU_FILE_RECENTS {
        # Will be filled programatically later in the example.
      }
    }
    # More menus may follow ...

This file can be parsed into a `MenuContainer` and then rendered into a
dialog like this:

```python
res = require('./res')  # generated with 'c4ddev symbols -f file'

menuparser = require('c4ddev/lib/c4dtools/menuparser')
menu = menuparser.parse_file('path/to/my.menu')

# Render the menu into the dialog.
my_dialog.MenuFlushAll()
menu.render(my_dialog, res)
my_dialog.MenuFinished()
```

Before the menu is rendered into the dialog, it can be modified
programmatically.

```python
recents = menu.find_node(res.MENU_FILE_RECENTS)
for i, fn in get_recent_files():  # arbitrary function
  node = menuparser.MenuItem(RECENT_FILES_ID_BEGIN + i, str(fn))
  recents.add(node)
```
