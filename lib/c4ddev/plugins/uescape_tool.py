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

import c4d
import cStringIO
from c4ddev import utils


def unicode_refreplace(ustring):
    ''' Replaces all non-ASCII characters in the supplied unicode
    string with Cinema 4D stringtable unicode escape sequences.

    :param ustring: :class:`unicode` or :class:`str`
    :return: :class:`str` '''

    fp = cStringIO.StringIO()
    for char in ustring:
        if ord(char) not in xrange(32, 127) and char not in '\n\r\t':
            char = '\\u' + ('%04x' % ord(char)).upper()
        fp.write(char)

    return fp.getvalue()


class UnicodeEscapeToolDialog(c4d.gui.GeDialog):

    EDT_SOURCE = 1000
    EDT_OUTPUT = 1001
    BTN_CONVERT = 1002
    BTN_CONVERT_COPY = 1003

    def __init__(self):
        super(UnicodeEscapeToolDialog, self).__init__()
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)

    def color(self, id):
        col = self.GetColorRGB(id)
        return c4d.Vector(col['r'], col['g'], col['b']) ^ c4d.Vector(1.0 / 255)

    # c4d.gui.GeDialog

    def CreateLayout(self):
        self.SetTitle("c4ddev: Unicode Escape Tool")
        self.GroupBorderSpace(4, 4, 4, 4)

        fullfit = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT

        self.GroupBegin(0, fullfit, cols=2, rows=0)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Input")
        style = c4d.DR_MULTILINE_MONOSPACED
        self.AddMultiLineEditText(self.EDT_SOURCE, fullfit, style=style)

        self.AddStaticText(0, c4d.BFH_LEFT, name="Output")
        style = c4d.DR_MULTILINE_MONOSPACED | c4d.DR_MULTILINE_READONLY
        self.AddMultiLineEditText(self.EDT_OUTPUT, fullfit, style=style)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, rows=1)
        self.AddStaticText(0, c4d.BFH_SCALEFIT)
        self.AddButton(self.BTN_CONVERT_COPY, 0, name="Convert & Copy")
        self.AddButton(self.BTN_CONVERT, 0, name="Convert")
        self.GroupEnd()

        # Change the background color of the output field.
        self.SetDefaultColor(
            self.EDT_OUTPUT, c4d.COLOR_BGEDIT, self.color(c4d.COLOR_BGFOCUS))

        return True

    def Command(self, id, msg):
        if id in [self.BTN_CONVERT_COPY, self.BTN_CONVERT]:
            string = self.GetString(self.EDT_SOURCE).decode("utf-8")
            output = unicode_refreplace(string)
            self.SetString(self.EDT_OUTPUT, output)
        if id == self.BTN_CONVERT_COPY:
            c4d.CopyStringToClipboard(output)
        return True


class UnicodeEscapeToolCommand(c4d.plugins.CommandData):

    PLUGIN_ID = 1033712
    PLUGIN_INFO = c4d.PLUGINFLAG_HIDEPLUGINMENU
    PLUGIN_NAME = "Unicode Escape Tool"
    PLUGIN_HELP = "UI to escape special characters for C4D stringtables."

    @property
    def dialog(self):
        if not getattr(self, '_dialog', None):
            self._dialog = UnicodeEscapeToolDialog()
        return self._dialog

    def Execute(self, doc):
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, self.PLUGIN_ID,
                defaultw=400, defaulth=400, xpos=-2, ypos=-2)

    def RestoreLayout(self, secret):
        return self.dialog.Restore(self.PLUGIN_ID, secret)


utils.register_command(UnicodeEscapeToolCommand)
