+++
title = "APEX"
+++

<p align="right" style="float: right; margin-left: 1em; margin-bottom: 1em"><img src="apex.png"></p>

APEX stands for "Cinema 4D API Extensions". It is a C++ plugin that provides
additions to the Python for Cinema 4D API but also for the C++ SDK. It was
originally a side-project, but is now merged into the **C4DDev** codebase.

{{< note title="Note" >}}
  The C++ component of **C4DDev** must be installed, otherwise the API
  extensions will not be available. Pre-compiled binaries are available in
  the [GitHub Releases](https://github.com/NiklasRosenstein/c4ddev/releases)
  of C4DDev.
{{< /note >}}

## C4D Command-line

### `-apex-protect-source <filename>`

When APEX is available in a Cinema 4D installation, this command-line argument
can be used to protect the source code of a Cinema 4D Python Plugin (`.pyp`),
creating a `.pype` (before R15) or `.pypv` file (R15 and later). The argument
can be specified multiple times to protected multiple files with a single
invocation.

The [`c4ddev source-protector`]({{< ref "cli.md#c4ddev-source-protector" >}})
command can be used to protect source files from the Command-line conveniently.

    $ c4ddev source-protector myplugin.pyp
    ...
    [apex / INFO]: Calling Source Protector for 'myplugin.pyp'.

Alternatively, you can run Cinema 4D directly via the command-line or use
the [`c4ddev run`]({{< ref "cli.md#c4ddev-run" >}}) command.

    $ /Applications/Cinema 4D R16/plugins/myplugin $ "..\..\CINEMA 4D.exe" -nogui -apex-protect-source myplugin.pyp

## Message Extensions

APEX installs a SceneHook that takes special messages which are usually only
sent to nodes in a document and redirects them as a global plugin message.
Currently, the following messages sent to that scene hook are supported:

- `MSG_DOCUMENTINFO`
- `MSG_MULTI_RENDERNOTIFICATION`

There's a little bit of effort involved in receiving these in Python, though. The
data sent will by a `PyCObject` and you have to use APEX to read the data from these
objects.

```python
import c4d.apex

def PluginMessage(msg, data):
  if msg == c4d.MSG_MULTI_RENDERNOTIFICATION:
    data = c4d.apex.RenderNotificationData(data)
    print data
  elif msg == c4d.MSG_DOCUMENTINFO:
    data = c4d.apex.DocumentInfoData(data)
    print data
  return True
```

### `c4d.apex.DocumentInfoData(pycobject) -> dict`

> Pass the `PyCObject` received on `MSG_DOCUMENTINFO` to this function to get a
dictionary of the structures data. __Important__: This will result in undefined
behaviour (likely a crash) if you pass a wrong PyCObject!

### `c4d.apex.RenderNotificationData(pycobject) -> dict`

> Pass the `PyCObject` received on `MSG_MULTI_RENDERNOTIFICATION` this this function
to get a dictionary of the structures data. __Important__: This will result in
undefined behaviour (likely a crash) if you pass a wrong PyCObject!

## Python API Extensions

### `c4d.apex.cast_node(pycobject) -> c4d.GeListNode`

> Given a `PyCObject` from which you know it is a Cinema 4D `GeListNode` instance,
> you can use this function to get a real Python object out of it. __Important__:
> This will result in undefined behaviour (likely a crash) if you pass a wrong PyCObject!

### `c4d.apex.fileselect_put(path)`

> This extension allows you to prevent file selection dialogs from popping up
> and make them return a specific value. This is *very* useful if you want to
> streamline Cinema 4D commands that usually do open a file selection dialog.
>
> ```python
> import c4d
> c4d.apex.fileselect_put('/Users/me/Desktop')
> print(c4d.storage.LoadDialog())
> # Doesn't open a dialog and prints /Users/me/Desktop
> ```

### `c4d.apex.fileselect_pop()`

> Pop an element from the elements added to the FileSelect Hook queue with
> `fileselect_put()`.

### `c4d.apex.fileselect_size()`

> Returns the number of elemenets in the queue added to the FileSelect Hook
> with `fileselect_put()`.

### `c4d.apex.handlemousedrag(area, msg, type, data, flags)`

> This function calls `GeUserArea::HandleMouseDrag()` on the *area* object,
> which is missing in the Py4D API. Currently supported values for *type*
> are:
>
> - `DRAGTYPE_FILES` (str)
> - `DRAGTYPE_FILENAME_IMAGE` (str)
> - `DRAGTYPE_FILENAME_SCENE` (str)
> - `DRAGTYPE_FILENAME_OTHER` (str)
> - `DRAGTYPE_ATOMARRAY` (list of c4d.GeListNode)
>
> The type of *data* is specified in the parentheses above. *msg* must be
> a `c4d.BaseContainer`, ideally the one passed from `GeUserArea.InputEvent()`.
