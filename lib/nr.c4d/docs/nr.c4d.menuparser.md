
## MenuParser

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
with localimport('lib') as _importer:
  import res  # generated with `c4ddev symbols`
  from nr.c4d import menuparser

menu = menuparser.parse_file(res.path('res/menu/mainmenu.menu')

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
