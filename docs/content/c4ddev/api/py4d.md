+++
title = "Py4D API Extensions"
+++

<p align="right" style="float: right; margin-left: 1em; margin-bottom: 1em"><img src="apex.png"></p>

The C4DDev Py4D API Extensions are a C++ plugin that provide additional
functions that can be used from Python.

!!! note "Note"
    The C++ component of **C4DDev** must be installed, otherwise the API
    extensions will not be available. Pre-compiled binaries are available in
    the [GitHub Releases](https://github.com/NiklasRosenstein/c4ddev/releases)
    of C4DDev.

## Members

### `c4ddev.__version__`

The installed version of C4DDev.

### `c4ddev.has_cpp_extensions`

`True` if the C4DDev C++ extensions are installed, otherwise `False`. Note
that if the C++ extensions are **not** installed and you try to import
`c4ddev` from a Cinema 4D plugin, importing `c4ddev` could fail if your plugin
is executed before the C4DDev Python entrypoint.

## Functions

### `c4ddev.GeListNodeFromAddress(pycobject) -> c4d.GeListNode`

Given a `PyCObject` from which you know it is a Cinema 4D `GeListNode` instance,
you can use this function to get a real Python object out of it. __Important__:
This will result in undefined behaviour (likely a crash) if you pass a wrong PyCObject!

### `c4ddev.FileSelectPut(path)`

This extension allows you to prevent file selection dialogs from popping up
and make them return a specific value. This is *very* useful if you want to
streamline Cinema 4D commands that usually do open a file selection dialog.

```python
import c4d
import c4ddev

c4ddev.FileSelectPut('/Users/me/Desktop')
print(c4d.storage.LoadDialog())
# Doesn't open a dialog and prints /Users/me/Desktop
```

### `c4ddev.FileSelectPop()`

Pop an element from the elements added to the FileSelect Hook queue with
`FileSelectPut()`.

### `c4ddev.FileSelectQueueSize()`

Returns the number of elemenets in the queue added to the FileSelect Hook
with `FileSelectPut()`.

### `c4ddev.DocumentInfoData(pycobject) -> dict`

Pass the `PyCObject` received on `MSG_DOCUMENTINFO` to this function to get a
dictionary of the structures data. __Important__: This will result in undefined
behaviour (likely a crash) if you pass a wrong PyCObject!

### `c4ddev.RenderNotificationData(pycobject) -> dict`

Pass the `PyCObject` received on `MSG_MULTI_RENDERNOTIFICATION` this this function
to get a dictionary of the structures data. __Important__: This will result in
undefined behaviour (likely a crash) if you pass a wrong PyCObject!

### `c4ddev.GetUserAreaHandle() -> PyCObject`

### `c4ddev.GetClipMapHandle() -> PyCObject`

### `c4ddev.BlitClipMap(dst, src, dx, dy, dw, dh, sx, sy, sw, sh, mode)`

This function implements the missing functionality of the `GeClipMap` to copy
another bitmap into another, with the ability to copy only parts and in a
different scale and aspect ratio (like `GeUserArea.DrawBitmap()`).

Parameters | Description
-----------|------------
__dst__ | The destination `GeClipMap`
__src__ | The source `GeClipMap`
__dx__ | The destination X coordinate.
__dy__ | The destination Y coordinate.
__dw__ | The destination width.
__dh__ | The destination height.
__sx__ | The destination X coordinate.
__sy__ | The destination X coordinate.
__sw__ | The destination X coordinate.
__sh__ | The destination X coordinate.
__mode__ | One of `c4ddev.BLIT_NN`, `BLIT_BILINEAR` or `BLIT_BICUBIC`

!!! note "Limitation"
    Currently this function can only accept two `GeClipMap` objects as we
    haven't figured out how to retrieve the actual C pointer to a `BaseBitmap`
    from a Python `c4d.bitmaps.BaseBitmap` object. You can convert a bitmap
    to a `GeClipMap` using the following code:

    ```
    map = c4d.bitmaps.GeClipMap()
    map.InitWithBitmap(bmp, bmp.GetInternalChannel())
    ```

    However, keep in mind that this process is relatively slow as it creates
    a new copy of the image. It is thus recommended to do this operation only
    once after a bitmap is loaded and keep it as a `GeClipMap`.

## Plugin Messages

The C4DDev C++ component installs a SceneHook that takes special messages
which are usually only sent to nodes in a document and redirects them as a
global plugin message. Currently, the following messages sent to that scene
hook are supported:

- `MSG_DOCUMENTINFO`
- `MSG_MULTI_RENDERNOTIFICATION`

There's a little bit of effort involved in receiving these in Python, though. The
data sent will by a `PyCObject` and you have to use C4DDev to read the data from these
objects.

```python
import c4d
import c4ddev

def PluginMessage(msg, data):
  if msg == c4d.MSG_MULTI_RENDERNOTIFICATION:
    data = c4ddev.RenderNotificationData(data)
    print data
  elif msg == c4d.MSG_DOCUMENTINFO:
    data = c4ddev.DocumentInfoData(data)
    print data
  return True
```

---

### `c4ddev.gui.HandleMouseDrag(area, msg, type, data, flags)`

This function calls `GeUserArea::HandleMouseDrag()` on the *area* object,
which is missing in the Py4D API. Currently supported values for *type*
are:

- `DRAGTYPE_FILES` (str)
- `DRAGTYPE_FILENAME_IMAGE` (str)
- `DRAGTYPE_FILENAME_SCENE` (str)
- `DRAGTYPE_FILENAME_OTHER` (str)
- `DRAGTYPE_ATOMARRAY` (list of c4d.GeListNode)

The type of *data* is specified in the parentheses above. *msg* must be
a `c4d.BaseContainer`, ideally the one passed from `GeUserArea.InputEvent()`.

---

### `c4ddev.am.RegisterMode(id, name, callback)`

Registers a new mode in the Attribute Manager. The *callback* parameter
is currently not used. Raises a `RuntimeError` when the registration failed.

### `c4ddev.am.SetMode(id, open)`

Sets the current attribute manager mode. Optionally opens the attribute
manager window.

### `c4ddev.am.SetObject(id, op, flags, activepage)`

Sets the object *op* as the active object in the attribute manager specified
by *id*. The *activepage* parameter is currently unused, but must be `None`
or a `c4d.DescID` object.

### `c4ddev.am.Open()`

Opens the attribute manager window.

### `c4ddev.am.EditObjectModal(op, title)`

Opens a modal attribute manager to edit the object *op*. The window title will
be set to *title*. Returns `True` on success, `False` on failure.

## Command-line

### `-c4ddev-protect-source <filename>`

When the C4DDev C++ extensions are available in a Cinema 4D installation,
this command-line argument can be used to protect the source code of a
Cinema 4D Python Plugin (`.pyp`), creating a `.pype` (before R15) or `.pypv`
file (R15 and later). The argument can be specified multiple times to protected
multiple files with a single invocation.

The [`c4ddev source-protector`](cli#c4ddev-source-protector) command can be
used to protect source files from the Command-line conveniently.

    $ c4ddev source-protector myplugin.pyp
    ...
    [c4ddev / INFO]: Calling Source Protector for 'myplugin.pyp'.

Alternatively, you can run Cinema 4D directly via the command-line or use
the [`c4ddev run`](cli#c4ddev-run) command.

    $ /Applications/Cinema 4D R16/plugins/myplugin $ "..\..\CINEMA 4D.exe" -nogui -c4ddev-protect-source myplugin.pyp
