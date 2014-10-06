# -*- coding: utf8 -*-
#
# Copyright (C) 2014  Niklas Rosenstein
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

__author__ = 'Niklas Rosenstein <rosensteinniklas (at) gmail.com>'
__version__ = '1.0'

import os, sys
import c4d
import cStringIO
import compileall
import zipfile

def register_command(cmd):
    """
    Registers a :class:`c4d.plugins.CommandData` instance to
    Cinema 4D and reads the required information from its attributes.

    * ``PLUGIN_ID``
    * ``PLUGIN_NAME``
    * ``PLUGIN_ICON`` \* _(string or :class:`c4d.bitmaps.BaseBitmap`)_
    * ``PLUGIN_HELP`` \*
    * ``PLUGIN_INFO`` \*

    \*: _Optional attributes_
    """

    if isinstance(cmd, type):
        cmd = cmd()
    cmd.__class__.global_instance = cmd

    icon = getattr(cmd, 'PLUGIN_ICON', None)
    if isinstance(icon, str):
        path = icon
        icon = c4d.bitmaps.BaseBitmap()
        if icon.InitWith(path)[0] != c4d.IMAGERESULT_OK:
            icon = None

    info = getattr(cmd, 'PLUGIN_INFO', c4d.PLUGINFLAG_COMMAND_HOTKEY)
    helpstr = getattr(cmd, 'PLUGIN_HELP', '')
    return c4d.plugins.RegisterCommandPlugin(
        cmd.PLUGIN_ID, cmd.PLUGIN_NAME, info, icon, helpstr, cmd)

#
# Unicode Escape Tool
#

def unicode_refreplace(ustring):
    """
    Replaces all non-ASCII characters in the supplied unicode
    string with Cinema 4D stringtable unicode escape sequences.

    :param ustring: :class:`unicode` or :class:`str`
    :return: :class:`str`
    """

    fp = cStringIO.StringIO()
    for char in ustring:
        if char not in '\n\t\r' and ord(char) < 32 or ord(char) > 127:
            char = ('\U%04x' % ord(char)).upper()
        fp.write(char)

    return fp.getvalue()

class UnicodeEscapeDialog(c4d.gui.GeDialog):
    """
    Displays a Multi-Line input field, an output field
    and a button to convert unicode-characters from the input
    field to Unicode escape sequences.
    """

    EDT_SOURCE = 1000
    EDT_OUTPUT = 1001
    BTN_CONVERT = 1002

    def CreateLayout(self):
        self.SetTitle("UTF-Escape Tool")

        flags = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT
        style = c4d.DR_MULTILINE_MONOSPACED
        self.AddMultiLineEditText(self.EDT_SOURCE, flags, style=style)

        style = c4d.DR_MULTILINE_MONOSPACED | c4d.DR_MULTILINE_READONLY
        self.AddMultiLineEditText(self.EDT_OUTPUT, flags, style=style)

        self.GroupBegin(0, c4d.BFH_SCALEFIT, rows=1)
        self.AddStaticText(0, c4d.BFH_SCALEFIT)
        self.AddButton(self.BTN_CONVERT, 0, name="Convert")
        self.GroupEnd()

        return True

    def Command(self, id, msg):
        if id == self.BTN_CONVERT:
            string = self.GetString(self.EDT_SOURCE).decode("utf-8")
            self.SetString(self.EDT_OUTPUT, unicode_refreplace(string))

        return True

class UnicodeEscapeCommand(c4d.plugins.CommandData):

    PLUGIN_ID = 1033712
    PLUGIN_NAME = "Unicode Escape Tool"
    PLUGIN_HELP = "Converts special characters to Unicode escape sequences."

    @property
    def dialog(self):
        if not getattr(self, '_dialog', None):
            self._dialog = UnicodeEscapeDialog()
        return self._dialog

    def Execute(self, doc):
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, self.PLUGIN_ID,
                defaultw=400, defaulth=400, xpos=-2, ypos=-2)

    def RestoreLayout(self, secret):
        return self.dialog.Restore(self.PLUGIN_ID, secret)

#
# Egg Packaging Tool
#

class CreateEggDialog(c4d.gui.GeDialog):

    CHK_PREFER_COMPILED = 1000
    CHK_INCLUDE_RESOURCE = 1001
    EDT_FILENAME = 1002

    BTN_MAKEEGG = 2000
    BTN_CLOSE = 2001

    @staticmethod
    def load_settings(self=None):
        bc = c4d.plugins.GetWorldPluginData(CreateEggCommand.PLUGIN_ID)
        if not bc:
            bc = c4d.BaseContainer()
        if self:
            self.SetBool(self.CHK_PREFER_COMPILED, bc.GetBool(self.CHK_PREFER_COMPILED, False))
            self.SetBool(self.CHK_INCLUDE_RESOURCE, bc.GetBool(self.CHK_INCLUDE_RESOURCE, True))
            self.SetFilename(self.EDT_FILENAME, bc.GetString(self.EDT_FILENAME))
        return bc

    def save_settings(self):
        bc = c4d.BaseContainer()
        bc[self.CHK_PREFER_COMPILED] = self.GetBool(self.CHK_PREFER_COMPILED)
        bc[self.CHK_INCLUDE_RESOURCE] = self.GetBool(self.CHK_INCLUDE_RESOURCE)
        bc[self.EDT_FILENAME] = self.GetFilename(self.EDT_FILENAME)
        c4d.plugins.SetWorldPluginData(CreateEggCommand.PLUGIN_ID, bc)

    def CreateLayout(self):
        flags = c4d.BFH_LEFT
        self.SetTitle("Create *.egg")
        self.GroupBorderSpace(6, 6, 6, 6)

        self.AddCheckbox(self.CHK_PREFER_COMPILED, flags, 0, 0, "Prefer compiled Python files")
        self.AddCheckbox(self.CHK_INCLUDE_RESOURCE, flags, 0, 0, "Include non-Python files")

        self.GroupBegin(0, c4d.BFH_SCALEFIT, rows=1)
        self.AddStaticText(0, 0, name="Directory")
        bc = c4d.BaseContainer()
        bc.SetBool(c4d.FILENAME_DIRECTORY, True)
        self.AddCustomGui(self.EDT_FILENAME, c4d.CUSTOMGUI_FILENAME,
                "", c4d.BFH_SCALEFIT, 0, 0, bc)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, rows=1)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, name="")
        self.AddButton(self.BTN_MAKEEGG, 0, name="Make Egg")
        self.AddButton(self.BTN_CLOSE, 0, name="Close")
        self.GroupEnd()
        return True

    def InitValues(self):
        CreateEggDialog.load_settings(self)
        return True

    def Command(self, id, msg):
        if id == self.BTN_MAKEEGG:
            dirname = self.GetFilename(self.EDT_FILENAME)
            prefer_compiled = self.GetBool(self.CHK_PREFER_COMPILED)
            include_resources = self.GetBool(self.CHK_INCLUDE_RESOURCE)
            CreateEggCommand.create_egg(dirname, prefer_compiled, include_resources)
        elif id == self.BTN_CLOSE:
            self.Close()
        return True

    def DestroyWindow(self):
        self.save_settings()

class CreateEggCommand(c4d.plugins.CommandData):
    """
    Asks the User for a directory name and creates
    a Python *.egg file from it.
    """

    PLUGIN_ID = 1033713
    PLUGIN_NAME = "Create *.egg"
    PLUGIN_HELP = "Creates a *.egg file from the selected directory."
    PLUGIN_INFO = c4d.PLUGINFLAG_COMMAND_HOTKEY | \
                  c4d.PLUGINFLAG_COMMAND_OPTION_DIALOG

    @staticmethod
    def create_egg(dirname, prefer_compiled, include_resources):
        print "create_egg(%r, %r, %r)" % (dirname, prefer_compiled, include_resources)
        if not os.path.isdir(dirname):
            c4d.gui.MessageDialog("'%s' is not a directory." % dirname)
            return

        # Ask the user if the egg-file should be overwritten
        # if it exists already.
        eggname = dirname + '.egg'
        if os.path.isfile(eggname):
            result = c4d.gui.MessageDialog(
                    "The file '%s' exists already, do you want to "
                    "overwrite it?" % eggname, c4d.GEMB_YESNO)
            if result != c4d.GEMB_R_YES:
                return
        elif os.path.exists(eggname):
            c4d.gui.MessageDialog(
                    "'%s' is a directory and can not be overwritten." % eggname)
            return

        # Create the new ZipFile.
        zfile = zipfile.ZipFile(eggname, 'w')
        print "Creating .egg at", eggname

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
                    print "    %s -> %s" % (filename, arcname)

        zfile.close()

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
            cls = CreateEggDialog
            bc = cls.load_settings()
            prefer_compiled = bc.GetBool(cls.CHK_PREFER_COMPILED, False)
            include_resources = bc.GetBool(cls.CHK_INCLUDE_RESOURCE, True)
            CreateEggCommand.create_egg(dirname, prefer_compiled, include_resources)
        return True

    def ExecuteOptionID(self, doc, plugid, subid):
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, plugid, defaultw=450)

    def RestoreLayout(self, secret):
        return self.dialog.Restore(self.PLUGIN_ID, secret)

#
# Python Batch-compile Tool
#

class BatchCompileCommand(c4d.plugins.CommandData):
    """
    Asks the User for a directory name and compiles
    all Python source files into byte-code files using the
    builting Python 2.6 interpreter.
    """

    PLUGIN_ID = 1033714
    PLUGIN_NAME = "Compile Directory"
    PLUGIN_HELP = "Compiles all Python source files in the selected " \
                  "directory to *.pyc files."

    def Execute(self, doc):
        flags = c4d.FILESELECT_DIRECTORY
        title = 'Select a Directory to compile'
        dirname = c4d.storage.LoadDialog(title=title, flags=flags)
        if not dirname:
            return True

        compileall.compile_dir(dirname, force=1)
        return True

#
# Plugin Registration
#

def main():
    register_command(BatchCompileCommand)
    register_command(CreateEggCommand)
    register_command(UnicodeEscapeCommand)

if __name__ == "__main__":
    main()

