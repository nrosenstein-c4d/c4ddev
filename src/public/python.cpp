/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_public/python_ext.cpp

#include <c4d.h>
#include <lib_py.h>
#include <c4ddev/python.hpp>


PyObject* c4ddev::Py4D_BaseBitmap = nullptr;
PyObject* c4ddev::Py4D_GeClipMap = nullptr;
PyObject* c4ddev::Py4D_GeUserArea = nullptr;
PyObject* c4ddev::Py4D_GeDialog = nullptr;
PyObject* c4ddev::Py4D_GeListNode = nullptr;


void c4ddev::PyTypesInit() {
  PyObject* mod = PyImport_ImportModule("c4d");
  if (mod) {
    Py4D_GeListNode = PyObject_GetAttrString(mod, "GeListNode");
  }
  mod = PyImport_ImportModule("c4d.bitmaps");
  if (mod) {
    Py4D_BaseBitmap = PyObject_GetAttrString(mod, "BaseBitmap");
    Py4D_GeClipMap = PyObject_GetAttrString(mod, "GeClipMap");
  }
  mod = PyImport_ImportModule("c4d.gui");
  if (mod) {
    Py4D_GeUserArea = PyObject_GetAttrString(mod, "GeUserArea");
    Py4D_GeDialog = PyObject_GetAttrString(mod, "GeDialog");
  }
}


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


GeListNode* c4ddev::PyGeListNode_Get(PyObject* obj) {
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
  struct CPyGeUserArea : public PyObject {
      GeUserArea* _area;
      Bool _owner;
      PyObject* _weakreflist;
  };
  if (!PyObject_IsInstance(obj, Py4D_GeUserArea)) {
    PyErr_SetString(PyExc_TypeError, "expected c4d.gui.GeUserArea object");
    return nullptr;
  }
  return static_cast<CPyGeUserArea*>(obj)->_area;
}


GeClipMap* c4ddev::PyGeClipMap_Get(PyObject* obj) {
  struct CPyGeClipMap : public PyObject {
      GeClipMap* _map;
      // Possibly other members we don't know about ...
  };
  if (!PyObject_IsInstance(obj, Py4D_GeClipMap)) {
    PyErr_SetString(PyExc_TypeError, "expected c4d.bitmaps.GeClipMap object");
    return nullptr;
  }
  return static_cast<CPyGeClipMap*>(obj)->_map;
}


BaseBitmap* c4ddev::PyBaseBitmap_Get(PyObject* obj) {
  PyErr_SetString(PyExc_RuntimeError, "PyBaseBitmap_Get() does not work yet.");
  return nullptr;
  #if 0
  struct CPyBaseBitmap : public PyObject {
    // FIXME: Correct structure def?
      BaseBitmap* _bmp;
  };
  if (!PyObject_IsInstance(obj, Py4D_BaseBitmap)) {
    PyErr_SetString(PyExc_TypeError, "expected c4d.bitmaps.BaseBitmap object");
    return nullptr;
  }
  return static_cast<CPyBaseBitmap*>(obj)->_bmp;
  #endif
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
