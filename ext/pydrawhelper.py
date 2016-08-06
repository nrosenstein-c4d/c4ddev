# Copyright (C) 2011-2016  Niklas Rosenstein
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import  c4d
from    c4d.plugins         import ObjectData, RegisterObjectPlugin
from    c4d.bitmaps         import BaseBitmap
from    c4d.gui             import GeDialog

from    os.path             import join, split, exists

__res__ = require('c4ddev/__res__')
utils = require('c4ddev/utils')

def GetMessageID(data):
    """
    Returns the ID the data-object carries,
    i.e. when a button is pressed, or None
    if no ID could be obtained.
    """
    if data is None:
        return
    try:
        return data["id"][0].id
    except:
        return

class DrawPassHelperEditor(GeDialog):
    DRAWHELPER_EDITOR   = 10001
    BTN_COMMIT          = 10002
    EDT_SOURCE          = 10003

    def __init__(self, drawPassHelperInstance):
        self.dphInstance    = drawPassHelperInstance

    def CreateLayout(self):
        self.LoadDialogResource(self.DRAWHELPER_EDITOR, flags = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)

        return True

    def Command(self, id, msg):
        if id == self.BTN_COMMIT:
            self.Commit()

        return True

    def DestroyWindow(self):
        self.Commit()

    def Commit(self):
        self.dphInstance.SendSourcecode( self.GetString(self.EDT_SOURCE) )
        c4d.DrawViews()

    def SetSourcecode(self, code):
        self.SetString( self.EDT_SOURCE, code )

class DrawPassHelper(ObjectData):
    PLUGIN_ID           = 1027193

    try:
        fl              = open( join( utils.plugin_dir, "res", "PyDrawHelper_InitialSource.py" ), "r")

        INIT_SOURCECODE = ""
        for i in fl:
            INIT_SOURCECODE    += i


    except IOError:
        INIT_SOURCECODE = "import c4d\n\ndef main():\n    pass\nmain()"

    finally:
        fl.close()


    def __init__(self):
        self.op     = None
        self.editor = DrawPassHelperEditor(self)

    def __repr__(self):
        return "<DrawPassHelper instance>"

    def Init(self, op):
        self.op     = op
        self.InitAttr(op, str, [c4d.DRAWHELPER_SOURCE])

        op[c4d.DRAWHELPER_SOURCE]   = self.INIT_SOURCECODE

        return True

    def Execute(self, op, doc, bt, prority, flags):
        return True

    def Message(self, op, type, data):
        if data is None: return True

        id      = GetMessageID(data)

        if id == c4d.DRAWHELPER_OPENEDITOR:
            self.editor.Open( c4d.DLG_TYPE_ASYNC, self.PLUGIN_ID, 250, 200, 600, 500)
            self.editor.SetSourcecode( op[c4d.DRAWHELPER_SOURCE] )

        return True

    def Draw(self, op, drawpass, bd, bh):
        if op.GetDeformMode() == True:
            code    = op[c4d.DRAWHELPER_SOURCE]

            globals = {
                "raw":      self,
                "op":       op,
                "drawpass": drawpass,
                "bd":       bd,
                "bh":       bh,
            }

            exec compile(code, "<string>", "exec") in globals, globals

        return True

    def SendSourcecode(self, code):
        if self.op is None:
            return False

        self.op[c4d.DRAWHELPER_SOURCE]  = code

        return True

    @classmethod
    def Register(cls):
        icon    = utils.load_resource_bitmap('res', 'icons', 'PyDrawHelper.tif')

        data    = {
            "id":           cls.PLUGIN_ID,   # Registered !
            "str":          "Python Draw Helper",
            "g":            cls,
            "description":  "Odrawhelper",
            "info":         c4d.OBJECT_MODIFIER,
            "icon":         icon,
        }

        RegisterObjectPlugin( **data )

DrawPassHelper.Register()
