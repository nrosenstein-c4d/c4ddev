/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_public/python_ext.cpp

#include <c4d.h>
#include <lib_py.h>
#include <c4ddev/python.hpp>


PyObject* c4ddev::PyGeListNode_New(GeListNode* node, Bool owner)
{
  PythonLibrary lib;
  if (!node)
    return (PyObject*) lib.ReturnPyNone();

  PythonBase* base = lib.Alloc();
  if (!base) {
    PyErr_SetString(PyExc_MemoryError, "Couldn't allocate PythonBase");
    return nullptr;
  }

  lib.SetGeListNode(base, "node", node, owner);
  _PyObject* result = lib.GetObject(base, "node");
  if (!result) {
    PyErr_SetString(PyExc_MemoryError, "Couldn't create GeListNode reference.");
    return nullptr;
  }

  lib.IncRef(result);
  lib.Free(base);
  return (PyObject*) result;
}


GeListNode* c4ddev::PyGetListNode_Get(PyObject* obj) {
  static PythonLibrary _lib;
  GeListNode* dest = nullptr;
  if (!_lib.GetGeListNode(nullptr, reinterpret_cast<_PyObject*>(obj), dest)) {
    PyErr_SetString(PyExc_TypeError, "expected GeListNode");
    return nullptr;
  }
  return dest;
}


PyObject* c4ddev::PyString_FromString(
  String const& str, STRINGENCODING encoding)
{
  Int32 const length = str.GetCStringLen(encoding);
  AutoGeFree<Char> buffer(NewMemClear(Char, length + 1));
  if (!buffer) {
    PyErr_SetString(PyExc_MemoryError, "String::GetCStringCopy() failed");
    return nullptr;
  }
  str.GetCString(buffer, length + 1, encoding);
  return PyString_FromStringAndSize(buffer, length);
}


Bool c4ddev::PyString_AsString(PyObject* obj, String* dest) {
  if (!dest) {
    PyErr_SetString(PyExc_RuntimeError, "missing String*");
    return false;
  }
  char* str = ::PyString_AsString(obj);
  if (!str) return false;
  *dest = str;
  return true;
}


GeUserArea* c4ddev::PyGeUserArea_Get(PyObject* obj) {
  struct CPyGeUserAreaTemplate : public PyObject {
      GeUserArea* _area;
      Bool _owner;
      PyObject* _weakreflist;
  };

  PyObject* c4d_gui = PyImport_ImportModule("c4d.gui");
  if (!c4d_gui) return nullptr;
  PyObject* ua_type = PyObject_GetAttrString(c4d_gui, "GeUserArea");
  if (!ua_type) return nullptr;
  if (!PyObject_IsInstance(obj, ua_type)) {
    PyErr_SetString(PyExc_TypeError, "expected GeUserArea object");
    return nullptr;
  }

  return static_cast<CPyGeUserAreaTemplate*>(obj)->_area;
}


GeDialog* c4ddev::PyGeDialog_Get(PyObject* obj) {
  // TODO: This strucutre definition is incorrect.
  struct CPyGeDialogTemplate : public PyObject {
      GeDialog* _dlg;
      Bool _owner;
      PyObject* _weakreflist;
  };

  PyObject* c4d_gui = PyImport_ImportModule("c4d.gui");
  if (!c4d_gui) return nullptr;
  PyObject* dlg_type = PyObject_GetAttrString(c4d_gui, "GeDialog");
  if (!dlg_type) return nullptr;
  if (!PyObject_IsInstance(obj, dlg_type)) {
    PyErr_SetString(PyExc_TypeError, "expected GeDialog object");
    return nullptr;
  }

  return static_cast<CPyGeDialogTemplate*>(obj)->_dlg;
}


Bool c4ddev::PyBaseContainer_Get(PyObject* obj, BaseContainer* bc) {
  static PythonLibrary _lib;
  if (!bc) {
    PyErr_SetString(PyExc_RuntimeError, "missing BaseContainer*");
    return false;
  }
  if (!_lib.GetContainer(nullptr, reinterpret_cast<_PyObject*>(obj), *bc)) {
    return false;
  }
  return true;
}
