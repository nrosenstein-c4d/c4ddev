# Copyright (c) 2015  Niklas Rosenstein
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

from c4ddev import ide, res
from c4ddev.ide import ScriptEditor

import c4d


class OpenScriptEditor(c4d.plugins.CommandData):

    PLUGIN_ID = ScriptEditor.GLOBAL_PLUGIN_ID
    PLUGIN_NAME = res.string('IDC_SCRIPT_EDITOR')
    PLUGIN_HELP = res.string('IDC_SCRIPT_EDITOR_HELP')
    PLUGIN_INFO = c4d.PLUGINFLAG_HIDEPLUGINMENU
    PLUGIN_ICON = res.bitmap('img', 'script-editor.tif')

    @classmethod
    def Register(cls):
        return c4d.plugins.RegisterCommandPlugin(
                    cls.PLUGIN_ID, cls.PLUGIN_NAME, cls.PLUGIN_INFO,
                    cls.PLUGIN_ICON, cls.PLUGIN_HELP, cls())

    # c4d.plugins.CommandData

    def Execute(self, doc):
        return ScriptEditor.OpenDefault()

    def RestoreLayout(self, secret):
        return ScriptEditor.RestoreDefault(secret)


class OpenEditorWindow(c4d.plugins.CommandData):

  PLUGIN_ID = 1038999
  PLUGIN_NAME = res.string('IDS_EDITOR')
  PLUGIN_HELP = res.string('IDS_EDITOR_HELP')
  PLUGIN_INFO = c4d.PLUGINFLAG_HIDEPLUGINMENU
  PLUGIN_ICON = res.bitmap('img', 'editor.png')

  @classmethod
  def Register(cls):
    return c4d.plugins.RegisterCommandPlugin(
      cls.PLUGIN_ID, cls.PLUGIN_NAME, cls.PLUGIN_INFO,
      cls.PLUGIN_ICON, cls.PLUGIN_HELP, cls())

  # c4d.plugins.CommandData

  def Execute(self, doc):
    return ide.main_window.Open(c4d.DLG_TYPE_ASYNC, self.PLUGIN_ID, 0)

  def RestoreLayout(self, secret):
    return ide.main_window.Restore(self.PLUGIN_ID, secret)


OpenScriptEditor.Register()
OpenEditorWindow.Register()
