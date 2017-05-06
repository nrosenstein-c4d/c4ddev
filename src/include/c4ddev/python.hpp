/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file c4ddev/python.hpp
/// \brief Includes the Python header and defines useful classes
///   and functions to work with the Python and Cinema 4D API.

#pragma once
#include <c4d.h>

/// Cinema 4D does not come with a debug binary distribution of Python,
/// so we make sure that Python does not assume debug mode.
#pragma push_macro("_DEBUG")
#ifdef _DEBUG
  #undef _DEBUG
#endif
#include <Python.h>
#pragma pop_macro("_DEBUG")

namespace c4ddev {

  /// Utility class to automatically decrement the reference count of
  /// an object when the wrapper is destroyed.
  template <typename T>
  class PyAutoDecref {
  public:
    PyAutoDecref(T* ptr) : ptr(ptr) { }
    ~PyAutoDecref() { Free(); }
    T* Release() { T* tmp = ptr; ptr = nullptr; return tmp; }
    void Free() { if (ptr) { Py_DECREF(ptr); } ptr = nullptr; }
    operator T* () const { return ptr; }
    T* operator -> () const { return ptr; }
  private:
    T* ptr;
  };

  /// Converts a Cinema 4D GeListNode to a Python Object. Returns
  /// a new reference. If *owner* is false, the owner of the pointed
  /// object is Cinema 4D. If it is true, the owner is the Python API.
  PyObject* PyGeListNode_New(GeListNode* node, Bool owner);

  /// Returns a GeListNode from a Python Object.
  GeListNode* PyGetListNode_Get(PyObject* obj);

  /// Convert a Cinema 4D String to a Python String.
  PyObject* PyString_FromString(
    String const& str, STRINGENCODING encoding=STRINGENCODING_UTF8);

  /// Convert a Python String to a Cinema 4D String.
  Bool PyString_AsString(PyObject* obj, String* dest);

  /// Retrieve the GeUserArea pointer from a PyObject.
  GeUserArea* PyGeUserArea_Get(PyObject* obj);

  /// Retrieve a BaseContainer pointer from a PyObject.
  Bool PyBaseContainer_Get(PyObject* obj, BaseContainer* dest);

} // namespace c4ddev
