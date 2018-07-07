## `nr.c4d` &mdash; A Cinema 4D utility library.

### Components

* `nr.c4d.aabb`
* `nr.c4d.geometry`
* `nr.c4d.gv`
* `nr.c4d.math`
* `nr.c4d.menuparser`
* `nr.c4d.modeling`
* `nr.c4d.normalalign`
* `nr.c4d.octree`
* `nr.c4d.ui` &ndash; Cinema 4D User Interface library.
* `nr.c4d.utils`

---

### `nr.c4d.ui`

*C4DUI* is a library that provides a new and object-oriented API to build
user interfaces for Cinema 4D Python plugins. There are two distinct APIs
available for `GeUserArea` and `GeDialog` user interfaces.

* __Widget-based__ &mdash;
In *C4DUI*, every element in the user interface is represented by a widget
object. It allows you to alter the properties of a single element and 
update the user interface dynamically.

* __Native look__ &mdash;
Build native-looking user interfaces with the *C4DUI* dialog abstraction API.

* __Custom & flexible__ &mdash;
With the *C4DUI* user-area widget API, you can create arbitrarily complex
user interface with your own style. It is based on a flow-based layout model
similar to (but simpler than) HTML webpages.

* __XML-based static layouts__ &mdash;
*C4DUI* enables you to build static interfaces using XML, then modify them
dynamically in your code!

#### Getting Started

1. Create an XML static dialog layout and save it under `res/ui/mydialog.xml`

    ```xml
    <Group borderspace="4,4,4,4" layout="fill" cols="1">
      <!-- The MenuGroup can be placed anywhere in the structure. -->
      <MenuGroup id="menu">
        <MenuGroup name="File">
          <MenuItem id="menu:save" name="Save..."/>
          <MenuItem id="menu:load" name="Load..."/>
          <Separator/>
          <MenuItem plugin="IDM_CM_CLOSEWINDOW"/>
        </MenuGroup>
      </MenuGroup>

      <Group layout="fill-x" rows="1">
        <UserArea id="brand-logo"/>
        <Text id="brand-name" text="Brand Name"/>
      </Group>

      <Group id="table" layout="fill" cols="2">
        <!-- We will fill this group dynamically. -->
      </Group>

      <Button id="btn:add" layout="right" text="Add"/>
    </Group>
    ```

2. Now, start a new Cinema 4D [Node.py] plugin. To do this, you can generate a
"loader" script with [C4DDev]:

    ```
    > c4ddev build-loader -co loader.pyp -e myplugin
    ```

3. In `myplugin.py`, we'll start with this very straight-forward code:

    ```python
    import os
    import c4d
    import c4dui from '@NiklasRosenstein/c4dui'

    PLUGIN_ID = 1039533

    dialog = c4dui.DialogWindow()
    dialog.load_xml_file(os.path.join(__directory__, 'res/ui/mydialog.xml'))
    dialog.register_opener_command(PLUGIN_ID, "Test Dialog", icon=None)
    ```

4. Let's attach a user area that renders an image to our "brand logo" widget.

    ```python
    logo = dialog.widgets['brand-logo']
    logo.user_area = c4dui.ImageView(os.path.join(__directory__, 'res/logo.png'), max_width=32)
    ```

5. In order to execute an action when the "Add" button is pressed, we can
register a listener on button-press:

    ```python
    def add_field(button):
      field = c4dui.Input(type='string')
      button = c4dui.Button(text='X')

      # Callback for the new button that we create.
      @button.add_event_listener('click')
      def on_click(btn):
        field.remove()
        button.remove()

      # Add the two new elements to the group.
      group = dialog.widgets['table']
      group.pack(field)
      group.pack(button)
    
    dialog.widgets['btn:add'].add_event_listener('click', add_field)
    ```

6. Reacting to a click on an item in the menuline is the same procedure. A
special case here is that the `click` event can be received on the `MenuItem`
itself but also on any parent `MenuGroup`.

    ```python
    menu = dialog.widgets['menu']

    @menu.add_event_listener('click')
    def on_menu_click(item):
      if item.id == 'menu:save':
        # ...
      elif item.id == 'menu:load':
        # ...
    ```

---

<p align="center">Copyright &copy; 2018 Niklas Rosenstein</p>
