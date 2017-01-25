# Snippets

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
