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

import c4d
import traceback
import weakref
import Queue


class WidgetManager(object):
  """
  A #WidgetManager takes care of all #BaseWidget instances in a single dialog.
  It contains a command-queue that is being executed everytime the dialog
  gets priority in the main-thread, manages widget ID assignment and more.

  # Members
  dialog: A #weakref.ref to the dialog that owns this #WidgetManager.
  cid (int): The current and ever increading widget ID. Every widget
    automatically saves the IDs that it allocated when using the
    #BaseWidget.alloc_id() method.
  """

  def __init__(self, dialog, parent=None, root=None):
    if dialog and not isinstance(dialog, c4d.gui.GeDialog):
      raise TypeError('expected GeDialog')
    if parent and not isinstance(parent, WidgetManager):
      raise TypeError('parent, if specified, must be a WidgetManager')
    self._dialog = weakref.ref(dialog) if dialog else None
    self.parent = parent
    self.root = root
    self.cid = 1000
    self._queue = Queue.Queue()
    self._id_widget_map = {}  # ID to weakref of BaseWidget
    self._layout_changed = False
    self._children = []
    if parent:
      parent._children.append(self)

  def __getitem__(self, id):
    return self._id_widget_map[id]()

  def dialog(self):
    if self.parent:
      return self.parent.dialog()
    elif self._dialog:
      return self._dialog()
    else:
      return None

  def layout_changed(self):
    self._layout_changed = True

  def update(self, root):
    if self._layout_changed:
      self._layout_changed = False
      root.update(self.dialog())
    for child in self._children:
      if child.root:
        child.update(child.root)

  def process_queue(self, exc_handler=None):
    """
    Call all functions that have been queued for execution in the main thread
    (must be called from the main thread).
    """

    while True:
      try:
        __func, args, kwargs = self._queue.get(block=False)
      except Queue.Empty:
        break
      try:
        __func(*args, **kwargs)
      except:
        if exc_handler:
          exc_handler()
        else:
          traceback.print_exc()

    for child in self._children:
      child.process_queue(exc_handler)

  def queue(self, __func, *args, **kwargs):
    """
    Queue a function that will be invoked from the main thread.
    """

    self._queue.put((__func, args, kwargs), block=False)

  def alloc_id(self):
    """
    Returns the value if #cid and increments it.
    """

    if self.parent:
      return self.parent.alloc_id()
    else:
      try:
        return self.cid
      finally:
        self.cid += 1

  def remove(self):
    if self.parent:
      self.parent._children.remove(self)
      self.parent = None

  def add_child(self, child_manager):
    assert isinstance(child_manager, WidgetManager), type(child_manager)
    child_manager.remove()
    child_manager.parent = self
    self._children.append(child_manager)
