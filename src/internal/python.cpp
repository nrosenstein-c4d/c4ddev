/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_internal/python_ext.cpp
/// \brief Implements the Python C-Extensions.

#include <c4d.h>
#include <lib_py.h>
#include <c4ddev/python.hpp>
#include <c4ddev/fileselectqueue.hpp>

using c4ddev::PyAutoDecref;
using c4ddev::PyGeListNode_New;
using c4ddev::PyString_FromString;
namespace FileSelectQueue = c4ddev::FileSelectQueue;

/// A small helper to define a Python method.
#define METHODDEF(name, argstype) {#name, py_##name, argstype, name##_docstring}

/// Docstrings for the module.
static char module_docstring[] =
  "Cinema 4D C4DDev API extensions. https://github.com/NiklasRosenstein/c4ddev";
static char cast_node_docstring[] =
  "cast_node(pycobject) -> c4d.GeListNode\n\n"
  "Convert a PyCObject pointing to a Cinema 4D C++ GeListNode to a Python\n"
  "GeListNode object. Note: Undefined behaviour if an invalid memory address\n"
  "or not-GeListNode is passed (likely to crash).";
static char RenderNotificationData_docstring[] =
  "RenderNotificationData(pycobject) -> dict";
static char DocumentInfoData_docstring[] =
  "DocumentInfoData(pycobject) -> dict";
static char fileselect_put_docstring[] =
  "fileselect_put(filename)\n\n"
  "Put a filename on the queue that will be retrieve automatically on\n"
  "the next call to Filename::FileSelect(). This allows you to work around\n"
  "file selection dialogs and even automate commands that usually require\n"
  "user interaction.";
static char fileselect_pop_docstring[] =
  "fileselect_pop() -> str\n\n"
  "Pop a filename from the queue (the one that would also be retrieved\n"
  "by the next Filename::FileSelect() call) and return it.";
static char fileselect_size_docstring[] =
  "fileselect_size() -> int\n\n"
  "Returns the size of the FileSelect queue.";
static char handlemousedrag_docstring[] =
  "handlemousedrag(area, msg, type, data, flags) -> Bool\n\n"
  "Calls GeUserArea::HandleMouseDrag().";

/// Method forward declaration.
static PyObject* py_cast_node(PyObject* self, PyObject* args);
static PyObject* py_RenderNotificationData(PyObject* self, PyObject* args);
static PyObject* py_DocumentInfoData(PyObject* self, PyObject* args);
static PyObject* py_fileselect_put(PyObject* self, PyObject* args);
static PyObject* py_fileselect_pop(PyObject* self, PyObject* args);
static PyObject* py_fileselect_size(PyObject* self, PyObject* args);
static PyObject* py_handlemousedrag(PyObject* self, PyObject* args);

/// Method definition for the Python module.
static PyMethodDef module_methods[] = {
  METHODDEF(cast_node, METH_VARARGS),
  METHODDEF(RenderNotificationData, METH_VARARGS),
  METHODDEF(DocumentInfoData, METH_VARARGS),
  METHODDEF(fileselect_put, METH_VARARGS),
  METHODDEF(fileselect_pop, METH_VARARGS),
  METHODDEF(fileselect_size, METH_VARARGS),
  METHODDEF(handlemousedrag, METH_VARARGS),
  {nullptr, nullptr, 0, nullptr},
};


Bool InitPython() {
  GePythonGIL gil;

  PyAutoDecref<PyObject> c4d = PyImport_ImportModule("c4d");
  if (!c4d) {
    GePrint("[c4ddev / ERROR]: Could not import c4d module.");
    return false;
  }
  PyObject* mod = Py_InitModule3("c4ddev", module_methods, module_docstring);
  if (!mod) {
    GePrint("[c4ddev / ERROR]: Could not create c4ddev module.");
    return false;
  }
  PyObject_SetAttrString(c4d, "c4ddev", mod);
  return true;
}


static PyObject* py_cast_node(PyObject* self, PyObject* args) {
  GePythonGIL gil;
  PyObject* obj = nullptr;
  if (!PyArg_ParseTuple(args, "O", &obj)) return nullptr;
  if (!PyCObject_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "expected PyCObject");
    return nullptr;
  }
  GeListNode* node = (GeListNode*) PyCObject_AsVoidPtr(obj);
  return PyGeListNode_New(node, false);
}


static PyObject* py_RenderNotificationData(PyObject* self, PyObject* args) {
  GePythonGIL gil;
  PyObject* obj = nullptr;
  if (!PyArg_ParseTuple(args, "O", &obj)) return nullptr;
  if (!PyCObject_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "expected PyCObject");
    return nullptr;
  }

  auto const* data = (RenderNotificationData*) PyCObject_AsVoidPtr(obj);
  PyAutoDecref<PyObject> res = PyDict_New();
  if (!res) return nullptr;

  obj = PyGeListNode_New(data->doc, false);
  if (PyDict_SetItemString(res, "doc", obj) != 0) return nullptr;
  obj = PyBool_FromLong(data->start);
  if (PyDict_SetItemString(res, "start", obj) != 0) return nullptr;
  obj = PyBool_FromLong(data->animated);
  if (PyDict_SetItemString(res, "animated", obj) != 0) return nullptr;
  obj = PyBool_FromLong(data->external);
  if (PyDict_SetItemString(res, "external", obj) != 0) return nullptr;
  // todo: No member flags?
  // obj = PyInt_FromLong(data->flags);
  // if (PyDict_SetItemString(res, "flags", obj) != 0) return nullptr;
  obj = PyCObject_FromVoidPtr(data->render, nullptr);
  if (PyDict_SetItemString(res, "render", obj) != 0) return nullptr;

  return res.Release();
}


static PyObject* py_DocumentInfoData(PyObject* self, PyObject* args) {
  GePythonGIL gil;
  PyObject* obj = nullptr;
  if (!PyArg_ParseTuple(args, "O", &obj)) return nullptr;
  if (!PyCObject_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "expected PyCObject");
    return nullptr;
  }

  auto const* data = (DocumentInfoData*) PyCObject_AsVoidPtr(obj);
  PyAutoDecref<PyObject> res = PyDict_New();
  if (!res) return nullptr;

  obj = PyInt_FromLong(data->type);
  if (PyDict_SetItemString(res, "type", obj) != 0) return nullptr;
  obj = PyInt_FromLong(data->fileformat);
  if (PyDict_SetItemString(res, "fileformat", obj) != 0) return nullptr;
  obj = PyGeListNode_New(data->doc, false);
  if (PyDict_SetItemString(res, "doc", obj) != 0) return nullptr;
  obj = PyString_FromString(data->filename.GetString());
  if (PyDict_SetItemString(res, "filename", obj) != 0) return nullptr;
  obj = PyGeListNode_New(data->bl, false);
  if (PyDict_SetItemString(res, "bl", obj) != 0) return nullptr;
  obj = PyBool_FromLong(data->gui_allowed);
  if (PyDict_SetItemString(res, "gui_allowed", obj) != 0) return nullptr;
  obj = PyCObject_FromVoidPtr(data->data, nullptr);
  if (PyDict_SetItemString(res, "data", obj) != 0) return nullptr;

  return res.Release();
}


static PyObject* py_fileselect_put(PyObject* self, PyObject* args) {
  GePythonGIL gil;
  const char* str = nullptr;
  if (!PyArg_ParseTuple(args, "s", &str)) return nullptr;
  if (!FileSelectQueue::Put(str)) {
    PyErr_SetString(PyExc_MemoryError, "Failed to put string on stack.");
    return nullptr;
  }
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* py_fileselect_pop(PyObject* self, PyObject* args) {
  GePythonGIL gil;
  if (!PyArg_ParseTuple(args, "")) return nullptr;
  if (FileSelectQueue::Size() <= 0) {
    PyErr_SetString(PyExc_ValueError, "FileSelect Stack is empty.");
    return nullptr;
  }
  Filename fn;
  if (!FileSelectQueue::Pop(fn)) {
    PyErr_SetString(PyExc_MemoryError, "Failed to pop string from stack.");
    return nullptr;
  }
  return PyString_FromString(fn.GetString());
}


static PyObject* py_fileselect_size(PyObject* self, PyObject* args) {
  GePythonGIL gil;
  if (!PyArg_ParseTuple(args, "")) return nullptr;
  return PyInt_FromLong(FileSelectQueue::Size());
}



PyObject* py_handlemousedrag(PyObject* self, PyObject* args) {
  PyObject* py_area = nullptr;
  PyObject* py_msg = nullptr;
  int type = 0;
  PyObject* py_data = nullptr;
  int flags = 0;
  if (!PyArg_ParseTuple(args, "OOiOi", &py_area, &py_msg, &type,
      &py_data, &flags)) return nullptr;

  GeUserArea* area = c4ddev::PyGeUserArea_Get(py_area);
  if (!area) return nullptr;
  BaseContainer msg;
  if (!c4ddev::PyBaseContainer_Get(py_msg, &msg)) return nullptr;

  Bool result = false;
  switch (type) {
    case DRAGTYPE_FILES:
    case DRAGTYPE_FILENAME_IMAGE:
    case DRAGTYPE_FILENAME_SCENE:
    case DRAGTYPE_FILENAME_OTHER: {
      String s;
      if (!c4ddev::PyString_AsString(py_data, &s)) return nullptr;
      Filename f(s);
      result = area->HandleMouseDrag(msg, type, &f, flags);
      break;
    }
    case DRAGTYPE_ATOMARRAY: {
      AutoAlloc<AtomArray> array;
      if (!array) {
        PyErr_SetString(PyExc_MemoryError, "AtomArray could not be allocated.");
        return nullptr;
      }
      PyObject* it = PyObject_GetIter(py_data);
      if (!it) return nullptr;
      PyObject* item = nullptr;
      Bool error = false;
      while ((item = PyIter_Next(it)) && !error) {
        GeListNode* node = c4ddev::PyGetListNode_Get(item);
        Py_DECREF(item);
        if (node) array->Append(node);
        else error = true;
      }
      Py_DECREF(it);
      if (error) return nullptr;
      result = area->HandleMouseDrag(msg, type, array, flags);
      break;
    }
    default: {
      String warn = "handlemousedrag() unsupported dragtype " + String::IntToString(type);
      AutoGeFree<Char> cwarn(warn.GetCStringCopy());
      PyErr_Warn(PyExc_RuntimeWarning, cwarn);
      break;
    }
  }

  PyObject* pyresult = result ? Py_True : Py_False;
  Py_INCREF(pyresult);
  return pyresult;
}
