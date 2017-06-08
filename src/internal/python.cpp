/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_internal/python_ext.cpp
/// \brief Implements the Python C-Extensions.

#include <c4d.h>
#include <lib_py.h>
#include <lib_clipmap.h>
#include <lib_activeobjectmanager.h>
#include <c4ddev/math.hpp>
#include <c4ddev/python.hpp>
#include <c4ddev/fileselectqueue.hpp>

using c4ddev::PyAutoDecref;
using c4ddev::PyGeListNode_New;
using c4ddev::PyString_FromString;
namespace FileSelectQueue = c4ddev::FileSelectQueue;

/// A small helper to define a Python method.
#define METHODDEF(prefix, name, argstype) {#name, py_##prefix##name, argstype, prefix##name##_docstring}

//
static PyObject* py_GeListNodeFromAddress(PyObject* self, PyObject* args);
static char GeListNodeFromAddress_docstring[] =
  "GeListNodeFromAddress(pycobject) -> c4d.GeListNode\n\n"
  "Convert a PyCObject pointing to a Cinema 4D C++ GeListNode to a Python\n"
  "GeListNode object. Note: Undefined behaviour if an invalid memory address\n"
  "or not-GeListNode is passed (likely to crash).";
static PyObject* py_RenderNotificationData(PyObject* self, PyObject* args);
static char RenderNotificationData_docstring[] =
  "RenderNotificationData(pycobject) -> dict";
static PyObject* py_DocumentInfoData(PyObject* self, PyObject* args);
static char DocumentInfoData_docstring[] =
  "DocumentInfoData(pycobject) -> dict";
static PyObject* py_FileSelectPut(PyObject* self, PyObject* args);
static char FileSelectPut_docstring[] =
  "FileSelectPut(filename)\n\n"
  "Put a filename on the queue that will be retrieve automatically on\n"
  "the next call to Filename::FileSelect(). This allows you to work around\n"
  "file selection dialogs and even automate commands that usually require\n"
  "user interaction.";
static PyObject* py_FileSelectPop(PyObject* self, PyObject* args);
static char FileSelectPop_docstring[] =
  "FileSelectPop() -> str\n\n"
  "Pop a filename from the queue (the one that would also be retrieved\n"
  "by the next Filename::FileSelect() call) and return it.";
static PyObject* py_FileSelectQueueSize(PyObject* self, PyObject* args);
static char FileSelectQueueSize_docstring[] =
  "FileSelectQueueSize() -> int\n\n"
  "Returns the size of the FileSelect queue.";
static PyObject* py_GetUserAreaHandle(PyObject* self, PyObject* args);
static char GetUserAreaHandle_docstring[] =
  "GetUserAreaHandle(ua) -> PyCObject\n\n"
  "Returns the C++ pointer address of the specified GeUserArea.";
static PyObject* py_GetClipMapHandle(PyObject* self, PyObject* args);
static char GetClipMapHandle_docstring[] =
  "GetClipMapHandle(dlg) -> PyCObject\n\n"
  "Returns the C++ pointer address of the specified GeClipMap.";
static PyMethodDef c4ddev_methods[] = {
  METHODDEF(, GeListNodeFromAddress, METH_VARARGS),
  METHODDEF(, RenderNotificationData, METH_VARARGS),
  METHODDEF(, DocumentInfoData, METH_VARARGS),
  METHODDEF(, FileSelectPut, METH_VARARGS),
  METHODDEF(, FileSelectPop, METH_VARARGS),
  METHODDEF(, FileSelectQueueSize, METH_VARARGS),
  METHODDEF(, GetUserAreaHandle, METH_VARARGS),
  METHODDEF(, GetClipMapHandle, METH_VARARGS),
  {nullptr, nullptr, 0, nullptr},
};
static char c4ddev_docstring[] =
  "Cinema 4D C4DDev API extensions. https://github.com/NiklasRosenstein/c4ddev";

//
static PyObject* py_am_RegisterMode(PyObject* self, PyObject* args);
static char am_RegisterMode_docstring[] =
  "RegisterMode(id, name, callback)\n\n"
  "Register a new mode in the Attribute Manager. The callback parameter\n"
  "is currently unused and for future extension.";

static PyObject* py_am_SetMode(PyObject* self, PyObject* args);
static char am_SetMode_docstring[] =
  "SetMode(id, open)\n\n"
  "Set the attribute manager mode.";

static PyObject* py_am_SetObject(PyObject* self, PyObject* args);
static char am_SetObject_docstring[] =
  "SetObject(id, op, flags, activepage)\n\n"
  "Sets the active object in the attribute manager for the specified\n"
  "attribute manager ID. The #activepage parameter is currently unused.";

static PyObject* py_am_Open(PyObject* self, PyObject* args);
static char am_Open_docstring[] =
  "Open()\n\n"
  "Opens the attribute manager.";

static PyObject* py_am_EditObjectModal(PyObject* self, PyObject* args);
static char am_EditObjectModal_docstring[] =
  "EditObjectModal(op, title) -> bool\n\n"
  "Shows a modal attribute manager for the specified object.";
static PyMethodDef c4ddev_am_methods[] = {
  METHODDEF(am_, RegisterMode, METH_VARARGS),
  METHODDEF(am_, SetMode, METH_VARARGS),
  METHODDEF(am_, SetObject, METH_VARARGS),
  METHODDEF(am_, Open, METH_VARARGS),
  METHODDEF(am_, EditObjectModal, METH_VARARGS),
  {nullptr, nullptr, 0, nullptr},
};
static char c4ddev_am_docstring[] =
  "Wrappers for <lib_activeobjectmanager.h>";

//
static PyObject* py_gui_HandleMouseDrag(PyObject* self, PyObject* args);
static char gui_HandleMouseDrag_docstring[] =
  "HandleMouseDrag(area, msg, type, data, flags) -> Bool\n\n"
  "Calls GeUserArea::HandleMouseDrag().";
static char c4ddev_gui_docstring[] =
  "Wrappers for the Cinema 4D GUI layer.";
static PyObject* py_gui_Blit(PyObject* self, PyObject* args);
static char gui_Blit_docstring[] =
  "Blit(dst, src, dx, dy, dw, dh, sx, sy, sw, sh, mode)\n\n"
  "Blits the GeClipMap 'dst' onto the GeClipMap 'src' using bicubic interpolation.\n"
  "The mode determines the interpolation quality: 0 for nearest neighbour, 1 for\n"
  "bilinear interpolation, 2 for bicubic interpolation.";
static PyMethodDef c4ddev_gui_methods[] = {
  METHODDEF(gui_, HandleMouseDrag, METH_VARARGS),
  METHODDEF(gui_, Blit, METH_VARARGS),
  {nullptr, nullptr, 0, nullptr},
};


Bool InitPython() {
  GePythonGIL gil;

  PyObject* c4ddev = Py_InitModule3("c4ddev", c4ddev_methods, c4ddev_docstring);
  if (!c4ddev) {
    GePrint("[c4ddev / ERROR]: Could not create c4ddev module.");
    return false;
  }

  PyObject* am = Py_InitModule3("c4ddev.am", c4ddev_am_methods, c4ddev_am_docstring);
  if (am) PyObject_SetAttrString(c4ddev, "am", am);
  else GePrint("[c4ddev / ERROR]: Could not create c4ddev.am module.");

  PyObject* gui = Py_InitModule3("c4ddev.gui", c4ddev_gui_methods, c4ddev_gui_docstring);
  if (gui) PyObject_SetAttrString(c4ddev, "gui", gui);
  else GePrint("[c4ddev / ERROR]: Could not create c4ddev.gui module.");

  return true;
}


PyObject* py_GeListNodeFromAddress(PyObject* self, PyObject* args) {
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


PyObject* py_RenderNotificationData(PyObject* self, PyObject* args) {
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


PyObject* py_DocumentInfoData(PyObject* self, PyObject* args) {
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


PyObject* py_FileSelectPut(PyObject* self, PyObject* args) {
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


PyObject* py_FileSelectPop(PyObject* self, PyObject* args) {
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


PyObject* py_FileSelectQueueSize(PyObject* self, PyObject* args) {
  GePythonGIL gil;
  if (!PyArg_ParseTuple(args, "")) return nullptr;
  return PyInt_FromLong(FileSelectQueue::Size());
}


PyObject* py_am_RegisterMode(PyObject* self, PyObject* args) {
  int id = 0;
  const char* text = nullptr;
  PyObject* callback = nullptr;
  if (!PyArg_ParseTuple(args, "isO", &id, &text, &callback)) return nullptr;
  // TODO: Handle callback.
  Bool res = ActiveObjectManager_RegisterMode((ACTIVEOBJECTMODE) id, String(text), nullptr);
  if (!res) {
    PyErr_SetString(PyExc_RuntimeError, "ActiveObjectManager_RegisterMode() returned false");
    return nullptr;
  }
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* py_am_SetMode(PyObject* self, PyObject* args) {
  int mode = 0;
  int open = 0;
  if (!PyArg_ParseTuple(args, "ii", &mode, &open)) return nullptr;
  ActiveObjectManager_SetMode((ACTIVEOBJECTMODE) mode, Bool(open));
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* py_am_SetObject(PyObject* self, PyObject* args) {
  int mode = 0;
  PyObject* pyop = nullptr;
  int flags = 0;
  PyObject* pydescid = nullptr;  // TODO
  if (!PyArg_ParseTuple(args, "iOiO", &mode, &pyop, &flags, &pydescid)) return nullptr;

  GeListNode* node = c4ddev::PyGetListNode_Get(pyop);
  if (!node) return nullptr;

  DescID activepage = {}; // TODO: Read DescID
  ActiveObjectManager_SetObject((ACTIVEOBJECTMODE) mode, node, flags, activepage);
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* py_am_Open(PyObject* self, PyObject* args) {
  if (!PyArg_ParseTuple(args, "")) return nullptr;
  ActiveObjectManager_Open();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* py_am_EditObjectModal(PyObject* self, PyObject* args) {
  PyObject* pyop = nullptr;
  const char* title = nullptr;
  if (!PyArg_ParseTuple(args, "Os", &pyop, &title)) return nullptr;
  GeListNode* node = c4ddev::PyGetListNode_Get(pyop);
  if (!node) return nullptr;
  Bool res = EditObjectModal(node, String(title));
  return PyBool_FromLong(res);
}


PyObject* py_gui_HandleMouseDrag(PyObject* self, PyObject* args) {
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
      String warn = "c4ddev.HandleMouseDrag() unsupported dragtype " + String::IntToString(type);
      AutoGeFree<Char> cwarn(warn.GetCStringCopy());
      PyErr_Warn(PyExc_RuntimeWarning, cwarn);
      break;
    }
  }

  PyObject* pyresult = result ? Py_True : Py_False;
  Py_INCREF(pyresult);
  return pyresult;
}


PyObject* py_gui_Blit(PyObject* self, PyObject* args) {
  using c4ddev::BilinearInterpolation;
  PyObject* pydst = nullptr;
  PyObject* pysrc = nullptr;
  Int32 dx, dy, dw, dh, sx, sy, sw, sh, mode;
  if (!PyArg_ParseTuple(args, "OOiiiiiiiii", &pydst, &pysrc, &dx, &dy, &dw, &dh,
    &sx, &sy, &sw, &sh, &mode)) return nullptr;
  if (mode < 0 || mode > 2) mode = 0;

  GeClipMap* dstmap = c4ddev::PyGeClipMap_Get(pydst);
  if (!dstmap) return nullptr;
  GeClipMap* srcmap = c4ddev::PyGeClipMap_Get(pysrc);
  if (!srcmap) return nullptr;

  BaseBitmap* dst = dstmap->GetBitmap();
  BaseBitmap* src = srcmap->GetBitmap();
  if (!dst || !src) {
    PyErr_SetString(PyExc_MemoryError, "No internal bitmap.");
    return nullptr;
  }

  UInt16 r[5], g[5], b[5], a[5];

  #pragma omp parallel for private(r, g, b, a)
  for (Int32 y1 = 0; y1 < dh; ++y1) {
    for (Int32 x1 = 0; x1 < dw; ++x1) {
      // Map the coordinates onto the source bitmap.
      Float y = (y1 / Float(dh)) * sh + sx;
      Float x = (x1 / Float(dw)) * sw + sy;
      Int32 iy = Floor(y);
      Int32 ix = Floor(x);
      src->GetPixel(ix+0, iy+1, r+0, g+0, b+0);
      src->GetPixel(ix+0, iy+0, r+1, g+1, b+1);
      src->GetPixel(ix+1, iy+0, r+2, g+2, b+2);
      src->GetPixel(ix+1, iy+1, r+3, g+3, b+3);

      if (mode == 1) {
        // FIXME: Black tear-line appearing in upscaled image.
        r[4] = BilinearInterpolation(r[0], r[1], r[2], r[3], ix, iy, ix+1, iy+1, x, y);
        g[4] = BilinearInterpolation(g[0], g[1], g[2], g[3], ix, iy, ix+1, iy+1, x, y);
        b[4] = BilinearInterpolation(b[0], b[1], b[2], b[3], ix, iy, ix+1, iy+1, x, y);
        a[4] = BilinearInterpolation(a[0], a[1], a[2], a[3], ix, iy, ix+1, iy+1, x, y);
      }
      else if (mode == 2) {
        // FIXME: Implement Bicubic interpolation.
        //r[4] = BicubicInterpolation(r[0], r[1], r[2], r[3], ix, iy, ix+1, iy+1, x, y);
        //g[4] = BicubicInterpolation(g[0], g[1], g[2], g[3], ix, iy, ix+1, iy+1, x, y);
        //b[4] = BicubicInterpolation(b[0], b[1], b[2], b[3], ix, iy, ix+1, iy+1, x, y);
        //a[4] = BicubicInterpolation(a[0], a[1], a[2], a[3], ix, iy, ix+1, iy+1, x, y);
      }
      else {
        // FIXME: Proper nearest neighbour interpolation.
        r[4] = r[0];
        g[4] = g[0];
        b[4] = b[0];
        a[4] = a[0];
      }
      dst->SetPixel(dx+x1, dy+y1, r[4], g[4], b[4]);
    }
  }

  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* py_GetUserAreaHandle(PyObject* self, PyObject* args) {
  PyObject* pyobj = nullptr;
  if (!PyArg_ParseTuple(args, "O", &pyobj)) return nullptr;
  GeUserArea* area = c4ddev::PyGeUserArea_Get(pyobj);
  if (!area) return nullptr;
  return PyCObject_FromVoidPtr(area, nullptr);
}


PyObject* py_GetClipMapHandle(PyObject* self, PyObject* args) {
  PyObject* pyobj = nullptr;
  if (!PyArg_ParseTuple(args, "O", &pyobj)) return nullptr;
  GeClipMap* map = c4ddev::PyGeClipMap_Get(pyobj);
  if (!map) return nullptr;
  return PyCObject_FromVoidPtr(map, nullptr);
}
