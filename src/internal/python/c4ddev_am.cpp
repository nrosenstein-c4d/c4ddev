/* Copyright (c) <2017  Niklas Rosenstein
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <c4ddev/python.hpp>
#include "../pymethoddef.hpp"

static char c4ddev_am_docstring[] = "ActiveObjectManager API.";

static char am_RegisterMode_docstring[] =
  "RegisterMode(id, name, callback)\n\n"
  "Register a new mode in the Attribute Manager. The callback parameter\n"
  "is currently unused and for future extension.";

static PyObject* py_am_RegisterMode(PyObject* self, PyObject* args) {
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

static char am_SetMode_docstring[] =
  "SetMode(id, open)\n\n"
  "Set the attribute manager mode.";

static PyObject* py_am_SetMode(PyObject* self, PyObject* args) {
  int mode = 0;
  int open = 0;
  if (!PyArg_ParseTuple(args, "ii", &mode, &open)) return nullptr;
  ActiveObjectManager_SetMode((ACTIVEOBJECTMODE) mode, Bool(open));
  Py_INCREF(Py_None);
  return Py_None;
}

static char am_SetObject_docstring[] =
  "SetObject(id, op, flags, activepage)\n\n"
  "Sets the active object in the attribute manager for the specified\n"
  "attribute manager ID. The #activepage parameter is currently unused.";

static PyObject* py_am_SetObject(PyObject* self, PyObject* args) {
  int mode = 0;
  PyObject* pyop = nullptr;
  int flags = 0;
  PyObject* pydescid = nullptr;  // TODO
  if (!PyArg_ParseTuple(args, "iOiO", &mode, &pyop, &flags, &pydescid)) return nullptr;

  GeListNode* node = c4ddev::PyGeListNode_Get(pyop);
  if (!node) return nullptr;

  DescID activepage = {}; // TODO: Read DescID
  ActiveObjectManager_SetObject((ACTIVEOBJECTMODE) mode, node, flags, activepage);
  Py_INCREF(Py_None);
  return Py_None;
}

static char am_Open_docstring[] =
  "Open()\n\n"
  "Opens the attribute manager.";

static PyObject* py_am_Open(PyObject* self, PyObject* args) {
  if (!PyArg_ParseTuple(args, "")) return nullptr;
  ActiveObjectManager_Open();
  Py_INCREF(Py_None);
  return Py_None;
}

static char am_EditObjectModal_docstring[] =
  "EditObjectModal(op, title) -> bool\n\n"
  "Shows a modal attribute manager for the specified object.";

static PyObject* py_am_EditObjectModal(PyObject* self, PyObject* args) {
  PyObject* pyop = nullptr;
  const char* title = nullptr;
  if (!PyArg_ParseTuple(args, "Os", &pyop, &title)) return nullptr;
  GeListNode* node = c4ddev::PyGeListNode_Get(pyop);
  if (!node) return nullptr;
  Bool res = EditObjectModal(node, String(title));
  return PyBool_FromLong(res);
}

static PyMethodDef c4ddev_am_methods[] = {
  METHODDEF(am_, RegisterMode, METH_VARARGS),
  METHODDEF(am_, SetMode, METH_VARARGS),
  METHODDEF(am_, SetObject, METH_VARARGS),
  METHODDEF(am_, Open, METH_VARARGS),
  METHODDEF(am_, EditObjectModal, METH_VARARGS),
  {nullptr, nullptr, 0, nullptr},
};

Bool Register_c4ddev_am(PyObject* c4ddev) {
  PyObject* am = Py_InitModule3("c4ddev.am", c4ddev_am_methods, c4ddev_am_docstring);
  if (am) {
    PyObject_SetAttrString(c4ddev, "am", am);
    return true;
  }
  return false;
}
