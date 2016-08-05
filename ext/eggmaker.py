# Copyright (C) 2014-2016  Niklas Rosenstein
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

import os
import c4d
import zipfile
utils = require('c4ddev/utils')


PLUGIN_ID = 1033713


def create_egg(dirname, prefer_compiled, include_resources, eggname=None):
    ''' Creates a ``*.egg`` file from the directory *dirname* with
    the specified options.

    :param dirname: The name of the directory to package.
    :param prefer_compiled: If this is set to True, ``.pyc`` files
        will be preferred over ``.py`` files when packaging.
    :param include_resources: If this is set to True, non-Python
        files will be included in the Egg file.
    :param egg: If specified, the Egg will be placed under this
        filename, otherwise it will be the same name as *dirname* but
        suffixed with ``.egg``.
    '''

    if eggname is None:
        eggname = dirname + '.egg'

    # Open the Zip file and write all files it can find to it.
    zfile = zipfile.ZipFile(eggname, 'w')
    for currdir, subdirs, files in os.walk(dirname):
        for filename in files:
            filename = os.path.join(currdir, filename)
            if filename.endswith('.py'):
                # If we prefer byte-compiled Python files and
                # such a file exists, we'll simply skip this
                # file.
                if prefer_compiled and os.path.isfile(filename + 'c'):
                    filename = None
            elif filename.endswith('.pyc'):
                # If we do not prefer byte-compiled Python files
                # and a normal source file exists, we'll simply
                # skip this file.
                if not prefer_compiled and os.path.isfile(filename[:-1]):
                    filename = None
            else:
                if not include_resources:
                    filename = None

            if filename:
                arcname = os.path.relpath(filename, dirname)
                zfile.write(filename, arcname)

    zfile.close()
    return eggname


class CreateEggDialog(c4d.gui.GeDialog):

    CHK_PREFER_COMPILED = 1000
    CHK_INCLUDE_RESOURCE = 1001
    EDT_FILENAME = 1002

    BTN_MAKEEGG = 2000
    BTN_CLOSE = 2001

    @classmethod
    def make_egg(cls, instance, dirname=None):
        if instance is None:
            print "Loading global Settings"
            data = cls.load_settings(None)
        else:
            print "Loading instance Settings"
            data = instance.save_settings(save=False)

        if dirname is None:
            dirname = data.GetString(cls.EDT_FILENAME)
        prefer_compiled = data.GetBool(cls.CHK_PREFER_COMPILED)
        include_resources = data.GetBool(cls.CHK_INCLUDE_RESOURCE)

        if not dirname or not os.path.isdir(dirname):
            c4d.gui.MessageDialog("%r is not a directory" % dirname)
            return False

        c4d.StatusSetSpin()
        c4d.StatusSetText("Creating egg...")
        print "Creating egg..."

        try:
            eggname = create_egg(dirname, prefer_compiled, include_resources)
        except (OSError, IOError) as exc:
            print "Failed:", exc
            c4d.gui.MessageDialog(str(exc))
            return False
        else:
            print "Egg created at", eggname
            return True
        finally:
            c4d.StatusClear()

    @classmethod
    def load_settings(cls, instance):
        # Load the data-container from the World settings.
        bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)
        bc = bc or c4d.BaseContainer()

        # If a dialog instance is specified, update the widget values.
        if instance:
            instance.SetBool(
                cls.CHK_PREFER_COMPILED,
                bc.GetBool(cls.CHK_PREFER_COMPILED, False))
            instance.SetBool(
                cls.CHK_INCLUDE_RESOURCE,
                bc.GetBool(cls.CHK_INCLUDE_RESOURCE, True))
            instance.SetFilename(
                cls.EDT_FILENAME,
                bc.GetString(cls.EDT_FILENAME))

        return bc

    def save_settings(self, save=True):
        data = c4d.BaseContainer()
        data[self.CHK_PREFER_COMPILED] = self.GetBool(self.CHK_PREFER_COMPILED)
        data[self.CHK_INCLUDE_RESOURCE] = self.GetBool(self.CHK_INCLUDE_RESOURCE)
        data[self.EDT_FILENAME] = self.GetFilename(self.EDT_FILENAME)
        if save:
            c4d.plugins.SetWorldPluginData(PLUGIN_ID, data)
        return data

    def __init__(self):
        super(CreateEggDialog, self).__init__()
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)

    # c4d.gui.GeDialog

    def CreateLayout(self):
        flags = c4d.BFH_LEFT
        self.SetTitle("c4ddev: Egg Maker")
        self.GroupBorderSpace(6, 6, 6, 6)

        self.GroupBegin(0, c4d.BFH_SCALEFIT, cols=2, rows=0)
        self.GroupBegin(0, c4d.BFH_SCALEFIT, cols=1, rows=0)
        self.AddCheckbox(self.CHK_PREFER_COMPILED, flags, 0, 0, "Prefer *.pyc over *.py Files")
        self.AddCheckbox(self.CHK_INCLUDE_RESOURCE, flags, 0, 0, "Include non-Python Files")
        self.GroupEnd()
        self.GroupBegin(0, c4d.BFH_RIGHT, cols=0, rows=1)
        self.AddButton(self.BTN_MAKEEGG, 0, name="Create Egg")
        self.AddButton(self.BTN_CLOSE, 0, name="Close")
        self.GroupEnd()
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, rows=1)
        self.AddStaticText(0, 0, name="Source Directory")
        bc = c4d.BaseContainer()
        bc.SetBool(c4d.FILENAME_DIRECTORY, True)
        self.AddCustomGui(
            self.EDT_FILENAME, c4d.CUSTOMGUI_FILENAME, "",
            c4d.BFH_SCALEFIT, 0, 0, bc)
        self.GroupEnd()
        return True

    def InitValues(self):
        self.Activate(self.EDT_FILENAME)
        CreateEggDialog.load_settings(self)
        return True

    def Command(self, id, msg):
        if id == self.BTN_MAKEEGG:
            self.make_egg(self)
        elif id == self.BTN_CLOSE:
            self.Close()
        return True

    def DestroyWindow(self):
        self.save_settings()


class CreateEggCommand(c4d.plugins.CommandData):

    PLUGIN_ID = PLUGIN_ID
    PLUGIN_NAME = "Egg Maker"
    PLUGIN_HELP = "Creates a *.egg file from the selected directory."
    PLUGIN_INFO = c4d.PLUGINFLAG_COMMAND_HOTKEY | \
                  c4d.PLUGINFLAG_COMMAND_OPTION_DIALOG

    @property
    def dialog(self):
        if not getattr(self, '_dialog', None):
            self._dialog = CreateEggDialog()
        return self._dialog

    def Execute(self, doc):
        flags = c4d.FILESELECT_DIRECTORY
        title = 'Select a Directory to compile'
        dirname = c4d.storage.LoadDialog(title=title, flags=flags)
        if dirname:
            CreateEggDialog.make_egg(instance=None, dirname=dirname)
        return True

    def ExecuteOptionID(self, doc, plugid, subid):
        self._dlg = CreateEggDialog()
        self._dlg.Open(c4d.DLG_TYPE_ASYNC)
        return True


utils.register_command(CreateEggCommand)
