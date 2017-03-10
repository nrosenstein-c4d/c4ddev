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
import c4d
import os
import traceback

__res__ = require('c4ddev/__res__')
utils = require('c4ddev/utils')

class DrawPassHelperEditor(c4d.gui.GeDialog):
    DRAWHELPER_EDITOR   = 10001
    BTN_COMMIT          = 10002
    EDT_SOURCE          = 10003

    def __init__(self, op):
        self.op = op

    def SetDrawHelper(self, op):
        self.op = op
        if self.IsOpen():
            self.SetSource(op[c4d.DRAWHELPER_SOURCE])

    def CreateLayout(self):
        self.LoadDialogResource(self.DRAWHELPER_EDITOR, flags = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        return True

    def InitValues(self):
        if self.op:
            self.SetSource(self.op[c4d.DRAWHELPER_SOURCE])
        return True

    def Command(self, id, msg):
        if id == self.BTN_COMMIT:
            self.Commit()
        return True

    def DestroyWindow(self):
        self.Commit()

    def Commit(self):
        self.op[c4d.DRAWHELPER_SOURCE] = self.GetString(self.EDT_SOURCE)
        c4d.DrawViews()

    def SetSource(self, code):
        self.SetString(self.EDT_SOURCE, code)

class DrawPassHelper(c4d.plugins.ObjectData):
    PLUGIN_ID = 1027193
    PLUGIN_NAME = "c4ddev Draw Helper"
    Editor = DrawPassHelperEditor(None)

    @staticmethod
    def get_initial_source():
        filename = os.path.join(utils.plugin_dir, "res", "PyDrawHelper_InitialSource.py")
        try:
            with open(filename) as fp:
                return fp.read()
        except (OSError, IOError) as exc:
            print(exc)
            return "import c4d\n\ndef main(op, drawpass, bd, bh):\n    pass\n"

    def __init__(self):
        self.op = None
        self.func = None
        self.code_hash = 0

    def Init(self, op):
        self.op = op
        self.InitAttr(op, str, [c4d.DRAWHELPER_SOURCE])
        op[c4d.DRAWHELPER_SOURCE] = self.get_initial_source()
        return True

    def Execute(self, op, doc, bt, prority, flags):
        return True

    def Message(self, op, msg, data):
        if msg == c4d.MSG_DESCRIPTION_COMMAND:
            id = data['id'][0].id
            if id == c4d.DRAWHELPER_OPENEDITOR:
                self.Editor.SetDrawHelper(self)
                self.Editor.Open(c4d.DLG_TYPE_ASYNC, self.PLUGIN_ID, 250, 200, 600, 500)
        elif msg in (c4d.MSG_UPDATE, c4d.MSG_DESCRIPTION_POSTSETPARAMETER):
            code = op[c4d.DRAWHELPER_SOURCE]
            if code and (not self.func or hash(code) != self.code_hash):
                self.func = None
                try:
                    scope = {'op': op, 'doc': op.GetDocument()}
                    exec(compile(code, op.GetName(), 'exec'), scope)
                except BaseException as exc:
                    traceback.print_exc()
                else:
                    if 'main' not in scope:
                        print("{0!r}: main function not found".format(op.GetName()))
                    elif not callable(scope['main']):
                        print("{0!r}: main must be callable".format(op.GetName()))
                    else:
                        self.func = scope['main']
                        self.code_hash = hash(code)
            elif not code:
                self.func = None
        return True

    def Draw(self, op, drawpass, bd, bh):
        if op.GetDeformMode() and self.func:
            try:
                self.func(op, drawpass, bd, bh)
            except BaseException as exc:
                traceback.print_exc()
        return True

    @classmethod
    def Register(cls):
        icon = utils.load_resource_bitmap('res', 'icons', 'PyDrawHelper.tif')
        c4d.plugins.RegisterObjectPlugin(cls.PLUGIN_ID,
          "c4ddev Python Draw Helper", cls, "Odrawhelper",
          c4d.OBJECT_MODIFIER, icon)

DrawPassHelper.Register()
