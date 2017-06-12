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

struct PyAliasTrans : PyObject {
  AliasTrans* _at;
};

static void PyAliasTrans_dealloc(PyAliasTrans* self) {
  AliasTrans::Free(self->_at);
  Py_TYPE(self)->tp_free(self);
}

static PyObject* PyAliasTrans_new(PyTypeObject* type, PyObject* args, PyObject* kwargs) {
  static char* keywords[] = {"doc", nullptr};
  PyObject* pydoc;
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", keywords, &pydoc)) {
    return nullptr;
  }

  auto doc = (BaseDocument*) c4ddev::PyGeListNode_Get(pydoc);
  if (!doc || !doc->IsInstanceOf(Tbasedocument)) {
    PyErr_Clear();
    PyErr_SetString(PyExc_TypeError, "expected BaseDocument for argument 0|doc");
    return nullptr;
  }

  auto self = (PyAliasTrans*) type->tp_alloc(type, 0);
  if (self) {
    self->_at = AliasTrans::Alloc();
    if (!self->_at || !self->_at->Init(doc)) {
      Py_DECREF(self);
      return nullptr;
    }
  }
  return self;
}

static PyObject* PyAliasTrans_GetClone(PyAliasTrans* self, PyObject* args, PyObject* kwargs) {
  static char* keywords[] = {"node", "flags", nullptr};
  PyObject* pynode;
  int flags = COPYFLAGS_0;
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|i", keywords, &pynode, &flags)) {
    return nullptr;
  }

  // Extract the GeListNode.
  auto node = c4ddev::PyGeListNode_Get(pynode);
  if (!node) {
    PyErr_Clear();
    PyErr_SetString(PyExc_TypeError, "expected GeListNode for argument 0|node");
    return nullptr;
  }

  auto clone = (GeListNode*) node->GetClone((COPYFLAGS) flags, self->_at);
  if (!clone) {
    PyErr_SetString(PyExc_MemoryError, "GeListNode could not be cloned");
    return nullptr;
  }

  return c4ddev::PyGeListNode_New(clone, true);
}

static PyObject* PyAliasTrans_Translate(PyAliasTrans* self, PyObject* args, PyObject* kwargs) {
  static char* keywords[] = {"connect_goals", nullptr};
  int connect_goals = true;
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|i", keywords, &connect_goals)) {
    return nullptr;
  }
  self->_at->Translate(connect_goals);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef PyAliasTrans_methods[] = {
  {"GetClone", (PyCFunction) PyAliasTrans_GetClone, METH_VARARGS | METH_KEYWORDS},
  {"Translate", (PyCFunction) PyAliasTrans_Translate, METH_VARARGS | METH_KEYWORDS},
  {nullptr} // sentinel
};

static PyTypeObject PyAliasTrans_Type {
  PyVarObject_HEAD_INIT(NULL, 0)
  "_hantmade_stage.AliasTrans",      // tp_name
  sizeof(PyAliasTrans),              // tp_basicsize
  0,                                 // tp_itemsize
  (destructor) PyAliasTrans_dealloc, // tp_dealloc
  0,                                 // tp_print
  0,                                 // tp_getattr
  0,                                 // tp_setattr
  0,                                 // tp_reserved
  0,                                 // tp_repr
  0,                                 // tp_as_number
  0,                                 // tp_as_sequence
  0,                                 // tp_as_mapping
  0,                                 // tp_hash
  0,                                 // tp_call
  0,                                 // tp_str
  0,                                 // tp_getattro
  0,                                 // tp_setattro
  0,                                 // tp_as_buffer
  Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE,             // tp_flags
  "AliasTrans implementation",       // tp_doc
  0,                                 // tp_traverse
  0,                                 // tp_clear
  0,                                 // tp_richcompare
  0,                                 // tp_weaklistoff
  0,                                 // tp_iter
  0,                                 // tp_iternext
  PyAliasTrans_methods,              // tp_methods
  0,                                 // tp_members
  0,                                 // tp_getset
  0,                                 // tp_base
  0,                                 // tp_dict
  0,                                 // tp_descr_get
  0,                                 // tp_descr_set
  0,                                 // tp_dictoffset
  0,                                 // tp_init
  0,                                 // tp_alloc
  PyAliasTrans_new,                  // tp_new
};

Bool Register_PyAliasTrans(PyObject* module) {
  if (PyType_Ready(&PyAliasTrans_Type) < 0) return false;
  Py_INCREF((PyObject*) &PyAliasTrans_Type);
  PyModule_AddObject(module, "AliasTrans", (PyObject*) &PyAliasTrans_Type);
  return true;
}
