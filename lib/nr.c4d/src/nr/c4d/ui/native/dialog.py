# Copyright (c) 2017  Niklas Rosenstein
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
# THE SOFTWARE

__all__ = ['DialogWindow']

import c4d
import sys
from .manager import WidgetManager
from .widgets import load_xml_string, load_xml_file
from . import widgets


class DialogWindow(c4d.gui.GeDialog):

  def __init__(self, root=None, title=None, menubar=True):
    c4d.gui.GeDialog.__init__(self)
    if not menubar:
      self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)
    self.widgets = WidgetManager(self)
    self.root = root or widgets.Group()
    self.root.manager = self.widgets
    self._title = title or ''
    self._layout_changed_items = set()
    self._layout_changed_queued = False

  @property
  def title(self):
    return self._title

  @title.setter
  def title(self, title):
    self._title = str(title)
    if self.IsOpen():
      self.SetTitle(self._title)

  def update_layout(self):
    """
    Must be called after modifications to the dialog widgets to update
    existing widgets and render new ones.
    """

    self.widgets.update(self.root)

  def register_opener_command(self, pluginid, title, help='', flags=0, icon=None):
    """
    Registers a Cinema 4D CommandData plugin that opens this dialog.
    """

    if isinstance(icon, str):
      bmp = c4d.bitmaps.BaseBitmap()
      bmp.InitWith(icon)
      icon = bmp

    cmd = DialogOpenerCommand(pluginid, self)
    c4d.plugins.RegisterCommandPlugin(pluginid, title, flags, icon, help, cmd)
    return cmd

  def load_xml_string(self, xml, globals=None, _stackframe=0):
    """
    Loads an XML user interface from the string *xml*. If *globals* is
    specified, it must be a dictionary that contains the view classes that
    can be used as views in the XML string. The default widgets are always
    available.
    """

    self.root = load_xml_string(xml, globals, _stackframe=_stackframe+1)
    self.root.manager = self.widgets

  def load_xml_file(self, filename, globals=None, _stackframe=0):
    """
    Like #load_xml_string() but from a file-object or filename.
    """

    self.root = load_xml_file(filename, globals, _stackframe=_stackframe+1)
    self.root.manager = self.widgets

  def get_color(self, colorid):
    c = self.GetColorRGB(colorid)
    return c4d.Vector(c['r'] / 255., c['g'] / 255., c['b'] / 255.)

  def set_color(self, param_id, colorid, color=None):
    if color is None:
      color = self.get_color(colorid)
    self.SetDefaultColor(param_id, colorid, color)

  def queue_layout_changed(self, param_id):
    self._layout_changed_items.add(param_id)
    if not self._layout_changed_queued:
      def worker():
        items = list(self._layout_changed_items)
        self._layout_changed_items.clear()
        for item in items:
          self.LayoutChanged(item)
        self._layout_changed_queued = False
      self.widgets.queue(worker)
      self._layout_changed_queued = True

  # c4d.gui.GeDialog overrides

  def CreateLayout(self):
    self.SetTitle(self._title)
    self.root.on_render_begin()
    self.root.render(self)
    self.widgets.layout_changed()
    self.update_layout()
    self.widgets.process_queue()
    return True

  def InitValues(self):
    self.root.init_values(self)
    self.widgets.layout_changed()
    self.update_layout()
    self.widgets.process_queue()
    return True

  def Command(self, id, msg):
    self.widgets.process_queue()
    result = self.root.command_event(id, msg)
    self.update_layout()
    self.widgets.process_queue()
    return result

  def InputEvent(self, msg):
    self.widgets.process_queue()
    result = self.root.input_event(msg)
    self.widgets.process_queue()
    self.update_layout()
    return result

  def CoreMessage(self, evid, bc):
    self.widgets.process_queue()
    return c4d.gui.GeDialog.CoreMessage(self, evid, bc)

  def DestroyWindow(self):
    self.widgets.process_queue()
    self.root.save_state()


class DialogOpenerCommand(c4d.plugins.CommandData):

  def __init__(self, plugin_id, dialog):
    c4d.plugins.CommandData.__init__(self)
    self.plugin_id = plugin_id
    self.dialog = dialog

  def Execute(self, doc):
    return self.dialog.Open(c4d.DLG_TYPE_ASYNC, self.plugin_id)

  def RestoreLayout(self, secret):
    return self.dialog.Restore(self.plugin_id, secret)

  def Register(self, name, info=0, icon=None, help=''):
    return c4d.plugins.RegisterCommandPlugin(
      self.plugin_id, name, info, icon, help, self)
