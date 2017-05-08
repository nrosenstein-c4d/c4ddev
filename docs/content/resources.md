+++
title = "Python & C++ Resources"
+++

## Python

### Snippets

- [TreeViewCustomGui Example](https://gist.github.com/NiklasRosenstein/632e39a9b4dda391fe54)
- [`copy_preset_texture()`](https://gist.github.com/NiklasRosenstein/fa9c9f72fa819dc001e4)

---

### Scripts

- [Cinema 4D Plugin Skeleton](https://gist.github.com/NiklasRosenstein/a7a406269276d2e0fccc)
  -- Skeleton to kick off Cinema 4D Python plugins from.
- [Set as Startup Scene](https://gist.github.com/NiklasRosenstein/14fe4a9162e90ff90151)
  --  Script to set the current scene as the startup scene.

---

## C++

This page contains a list of resources about Cinema 4D C++ plugin development
and useful links.

### Posts

- [Drawing Text in the Viewport](https://c4dprogramming.wordpress.com/2012/11/20/drawing-text-in-the-viewport/)
- [Saving EXR](http://www.plugincafe.com/forum/forum_posts.asp?TID=12112)
- [Exposing C++ functionality to Python](http://www.plugincafe.com/forum/forum_posts.asp?TID=12865&PID=50965#50965)
- [Viewport HUD API](http://www.plugincafe.com/forum/forum_posts.asp?TID=11764&PID=46315#46315)
- [Saving Custom GUI layouts](http://www.plugincafe.com/forum/forum_posts.asp?TID=12927)

---

### Tools

- [craftr:NiklasRosenstein.maxon.c4d](https://github.com/craftr-build/NiklasRosenstein.maxon.c4d)
  -- Build Cinema 4D Plugins on Windows, macOS and Linux

---

### Snippets

#### Hide Dialog Menubar

There is a non-member function available in the SDK that can be accessed
through the `C4DOS` to add special gadgets to the dialog, and it appears
that the state "no menubar" is also represented internally as a dialog
gadgets.

```cpp
inline Bool AddGadget(GeDialog* dlg, Int32 gadget_type) {
  String const name;
  BaseContainer const bc;
  return C4DOS.Cd->AddGadget(dlg->Get(), gadget_type, 0, &name, 0, 0, 0, 0, &bc, nullptr);
}
```

The gadget to remove the dialog menubar is `DIALOG_NOMENUBAR`. Be aware
when adding this gadget: Adding it inside `CreateLayout()` won't work
and calling it afterwards will crash C4D. You can call the function
in the dialog's constructor though!

```cpp
class MyDialog : public GeDialog() {
public:
  MyDialog() : GeDialog() { AddGadget(this, DIALOG_NOMENUBAR); }
};
```

---
