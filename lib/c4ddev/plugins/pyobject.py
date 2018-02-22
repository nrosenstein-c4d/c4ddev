# Copyright (C) 2011-2016  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function
from c4ddev import res
__res__ = res.__res__

import c4d
import os
import traceback
import types


class PyObjectEditor(c4d.gui.GeDialog):
    DRAWHELPER_EDITOR   = 10001
    BTN_COMMIT          = 10002
    EDT_SOURCE          = 10003

    def __init__(self, op, title=None, target_id=res.NR_PYOBJECT_SOURCE):
        self.op = op
        self.title = title
        self.target_id = target_id

    def SetTarget(self, op):
        self.op = op
        if self.IsOpen():
            self.SetSource(op[self.target_id])

    def CreateLayout(self):
        self.LoadDialogResource(self.DRAWHELPER_EDITOR, flags = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        if self.title:
            self.SetTitle(str(self.title))
        return True

    def InitValues(self):
        if self.op:
            self.SetSource(self.op[self.target_id])
        return True

    def Command(self, id, msg):
        if id == self.BTN_COMMIT:
            self.Commit()
        return True

    def DestroyWindow(self):
        self.Commit()

    def Commit(self):
        self.op[self.target_id] = self.GetString(self.EDT_SOURCE)
        c4d.DrawViews()

    def SetSource(self, code):
        self.SetString(self.EDT_SOURCE, code)

class PyObject(c4d.plugins.ObjectData):
    PLUGIN_ID = 1027193
    PLUGIN_NAME = "PyObject"
    Editor = PyObjectEditor(None)

    def __init__(self):
        self.scope = None
        self.code_hash = 0

    def Init(self, op):
        with open(res.path('res/PyObject.py')) as fp:
            op[res.NR_PYOBJECT_SOURCE] = fp.read()
        return True

    def AddToExecution(self, op, list):
        if self.scope and hasattr(self.scope, 'AddToExecution'):
            return self.scope.AddToExecution(op, list)
        return False

    def Execute(self, op, doc, bt, prority, flags):
        if self.scope and hasattr(self.scope, 'Execute'):
            return self.scope.Execute(op, doc, bt, priority, flags)
        return True

    def Message(self, op, msg, data):
        if msg == c4d.MSG_DESCRIPTION_COMMAND:
            id = data['id'][0].id
            if id == res.NR_PYOBJECT_OPENEDITOR:
                self.Editor.SetTarget(op)
                self.Editor.Open(c4d.DLG_TYPE_ASYNC, self.PLUGIN_ID, 250, 200, 600, 500)
        elif msg in (c4d.MSG_UPDATE, c4d.MSG_DESCRIPTION_POSTSETPARAMETER):
            code = op[res.NR_PYOBJECT_SOURCE]
            if hash(code) != self.code_hash:
                self.code_hash = hash(code)
                try:
                    self.scope = types.ModuleType(op.GetName())
                    exec(compile(code, op.GetName(), 'exec'), vars(self.scope))
                except:
                    traceback.print_exc()
        if self.scope and hasattr(self.scope, 'Message'):
            self.scope.Message(op, msg, data)
        return True

    def Draw(self, op, drawpass, bd, bh):
        if self.scope and hasattr(self.scope, 'Draw'):
            return self.scope.Draw(op, drawpass, bd, bh)
        return True

    def GetVirtualObjects(self, op, hh):
        if self.scope and hasattr(self.scope, 'GetVirtualObjects'):
            return self.scope.GetVirtualObjects(op, hh)
        return c4d.BaseObject(c4d.Onull)

    @classmethod
    def Register(cls):
        icon = res.bitmap('res', 'icons', 'PyDrawHelper.tif')
        info = c4d.OBJECT_MODIFIER | c4d.OBJECT_GENERATOR | c4d.OBJECT_INPUT |\
               c4d.OBJECT_PARTICLEMODIFIER | c4d.OBJECT_CALL_ADDEXECUTION |\
               c4d.PLUGINFLAG_HIDEPLUGINMENU
        c4d.plugins.RegisterObjectPlugin(
            cls.PLUGIN_ID, "PyObject", cls, "nr_pyobject", info, icon)

PyObject.Register()
