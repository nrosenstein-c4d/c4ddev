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

import abc
import types
import weakref
from .manager import WidgetManager


class AwaitingListeners(list):

  def next(self):
    for item in self:
      try:
        next(item)
      except StopIteration:
        pass

  __next__ = next


class BaseWidget(object):
  """
  Base class for C4D native widgets. Widgets are usually bound to a
  #WidgetManager, only then they can allocate IDs and take part in the
  dialog layout.

  # Members
  id (str): The ID of the widget. May be #None.
  manager (WidgetManager): A #WidgetManager (internally stored as a weak
    reference). If this member is set to #None, the widget is "unbound".
    Unbound widgets can not allocate IDs and are not part of any dialog.
  enabled (bool): Whether the widget is enabled.
  visible (bool): Whether the widget is visible.
  parent (Widget): The parent #Widget (internally stored as a weak reference).
  """

  __metaclass__ = abc.ABCMeta

  def __init__(self, id=None):
    self.id = id
    self._manager = None
    self._allocated_ids = []
    self._free_id_offset = 0  # Index of the next free ID in _allocated_ids
    self._named_ids = {}
    self._render_dirty = 0  # Dirty-count after rendering, set by WidgetManager
    self._enabled = self._enabled_temp = True
    self._visible = self._visible_temp = True
    self._parent = None
    self._listeners = {}

  @property
  def manager(self):
    if self._manager is None:
      manager = None
    else:
      manager = self._manager()
      if manager is None:
        raise RuntimeError('lost reference to WidgetManager')
    return manager

  @manager.setter
  def manager(self, manager):
    if manager is not None and not isinstance(manager, WidgetManager):
      raise TypeError('expected WidgetManager')

    # Remove the widget from the previous manager.
    old = self._manager() if self._manager is not None else None
    if old:
      old._id_widget_map.pop(self.id, None)

    if manager is None:
      self._manager = None
    else:
      self._manager = weakref.ref(manager)
      manager._id_widget_map[self.id] = weakref.ref(self)

  @property
  def dialog(self):
    manager = self.manager
    if manager:
      return manager.dialog()
    return dialog

  @property
  def enabled(self):
    return self._enabled_temp

  @enabled.setter
  def enabled(self, value):
    self._enabled_temp = bool(value)
    manager = self.manager
    if self._enabled_temp != self._enabled and manager:
      manager.layout_changed()

  @property
  def visible(self):
    while self:
      if not self._visible_temp:
        return False
      self = self.parent
    return True

  @visible.setter
  def visible(self, value):
    self._visible_temp = bool(value)
    manager = self.manager
    if self._visible_temp != self._visible and manager:
      manager.layout_changed()

  @property
  def parent(self):
    if self._parent is None:
      return None
    else:
      parent = self._parent()
      if parent is None:
        raise RuntimeError('lost reference to parent')
      return parent

  @parent.setter
  def parent(self, parent):
    if parent is not None and not isinstance(parent, BaseGroupWidget):
      raise TypeError('expected BaseGroupWidget')
    if parent is None:
      self._parent = None
    else:
      self._parent = weakref.ref(parent)

  @property
  def previous_sibling(self):
    parent = self.parent
    if parent:
      index = parent._children.index(self) - 1
      if index < 0: return None
      return parent._children[index]
    return None

  @property
  def next_sibling(self):
    parent = self.parent
    if parent:
      index = parent._children.index(self) + 1
      if index >= len(parent._children): return None
      return parent._children[index]
    return None

  def remove(self):
    """
    Removes the widget from the hierarchy.
    """

    parent = self.parent
    if parent is not None:
      parent._children.remove(self)
      parent.layout_changed()
    self._parent = None

  def alloc_id(self, name=None):
    """
    Allocates a new, unused ID for a dialog element. If a *name* is specified,
    the returned ID will be saved under that name and can be retrieved using
    #get_named_id().
    """

    manager = self.manager
    if self._free_id_offset < len(self._allocated_ids):
      # Re-use existing IDs.
      result = self._allocated_ids[self._free_id_offset]
      self._free_id_offset += 1
    else:
      result = manager.alloc_id()
      self._allocated_ids.append(result)
      self._free_id_offset = len(self._allocated_ids)

    if name is not None:
      self._named_ids[name] = result
    return result

  def get_named_id(self, name, default=NotImplemented):
    """
    Returns the value of a named ID previously created with #alloc_id().
    Raises a #KeyError if the named ID does not exist. If *default* is
    specified, it will be returned instead of a #KeyError being raised.
    """

    try:
      return self._named_ids[name]
    except KeyError:
      if default is NotImplemented:
        raise
      return default

  def add_event_listener(self, name, func=None):
    """
    Adds an event listener. If *func* is omitted, returns a decorator.
    """

    def decorator(func):
      self._listeners.setdefault(name, []).append(func)
      return func

    if func is not None:
      decorator(func)
      return None
    else:
      return decorator

  def send_event(self, __name, *args, **kwargs):
    """
    Sends an event to all listeners listening to that event. If any listener
    returns a value evaluating to #True, the event is no longer propagated
    to any other listeners and #True will be returned. If no listener returns
    #True, #False is returned from this function.

    A listener may return a generator object in which case the first yielded
    value is used as the True/False response. The initiator of the event may
    query the generator a second time (usually resulting in #StopIteration).

    Returns an #AwaitingListeners object and the result value.
    """

    awaiting_listeners = AwaitingListeners()
    result = False
    for listener in self._listeners.get(__name, []):
      obj = listener(*args, **kwargs)
      if isinstance(obj, types.GeneratorType):
        awaiting_listeners.append(obj)
        obj = next(obj)
      if obj:
        result = True
        break
    return awaiting_listeners, result

  def save_state(self):
    """
    Save the state and value of the widget so it can be restored in the
    same way the next time the widget is rendered.
    """

    pass

  def on_render_begin(self):
    """
    This method is called on all widgets that are about to be rendered.
    """

    # We don't flush already allocated IDs, but we want to be able to
    # re-use them.
    self._free_id_offset = 0

    # Also flush the named IDs mapping.
    self._named_ids.clear()

  @abc.abstractmethod
  def render(self, dialog):
    """
    Called to render the widget into the #c4d.gui.GeDialog. Widgets that
    encompass multiple Cinema 4D dialog elements should enclose them in
    their own group, unless explicitly documented for the widget.

    Not doing so can mess up layouts in groups that have more than one
    column and/or row.

    # Example
    ```python
    def render(self, dialog):
      id = self.alloc_id(name='edit_field')
      dialog.AddEditNumberArrows(id, c4d.BFH_SCALEFIT)
    ```
    """

    pass

  def init_values(self, dialog):
    pass

  def command_event(self, id, bc):
    """
    Called when a Command-event is received. Returns #True to mark the
    event has being handled and avoid further progression.
    """

    pass

  def input_event(self, bc):
    """
    Called when an Input-event is received. Returns #True to mark the
    event has being handled and avoid further progression.
    """

    pass

  def layout_changed(self):
    """
    Should be called after a widget changed its properties. The default
    implementation will simply call the parent's #layout_changed() method,
    if there is a parent. The #WidgetManager will also be notified. At the
    next possible chance, the widget will be re-rendered (usually requiring
    a re-rendering of the whole parent group).
    """

    manager = self.manager
    if manager is not None:
      manager.layout_changed()
    parent = self.parent
    if parent is not None:
      parent.layout_changed()

  def update_state(self, dialog):
    """
    This function is called from #update() by default. It should perform a
    non-recursive update of the dialog. The default implementation updates
    the enabled and visibility state of the allocated widget IDs.
    """

    changed = False
    parent = self.parent
    parent_id = parent.get_named_id('group', None) if isinstance(parent, Group) else None
    awaiting_listeners = AwaitingListeners()

    if self._enabled_temp != self._enabled:
      awaiting_listeners = self.send_event('enabling-changed', self)[0]
      changed = True
      self._enabled = self._enabled_temp
      for v in self._allocated_ids:
        dialog.Enable(v, self._enabled)
    if self._visible_temp != self._visible:
      awaiting_listeners = self.send_event('visibility-changed', self)[0]
      changed = True
      self._visible = self._visible_temp
      for v in self._allocated_ids:
        dialog.HideElement(v, not self._visible)
        if parent_id is None:  # Notify the elements themselves
          dialog.queue_layout_changed(v)

    if changed and parent_id is not None:
      dialog.queue_layout_changed(parent_id)

    if awaiting_listeners:
      dialog.widgets.queue(next, awaiting_listeners)

  def update(self, dialog):
    """
    Called to update the visual of the element. Groups will use this to
    re-render their contents when their layout has changed.
    """

    self.update_state(dialog)


class BaseGroupWidget(BaseWidget):

  def __init__(self, id=None):
    BaseWidget.__init__(self, id)
    self._children = []
    self._forward_events = set(['enabling-changed', 'visibility-changed'])

  @property
  def children(self):
    return self._children

  def pack(self, widget):
    """
    Adds a child widget.
    """

    if not isinstance(widget, BaseWidget):
      raise TypeError('expected BaseWidget')
    widget.remove()
    widget.parent = self
    widget.manager = self.manager
    self._children.append(widget)
    self.layout_changed()

  def flush_children(self):
    """
    Removes all children.
    """

    for child in self._children[:]:
      assert child.parent is self, (child, parent)
      child.remove()
    assert len(self._children) == 0

  # BaseWidget overrides

  @BaseWidget.manager.setter
  def manager(self, manager):
    # Propagate the new manager to child widgets.
    for child in self._children:
      child.manager = manager
    BaseWidget.manager.__set__(self, manager)

  def on_render_begin(self):
    BaseWidget.on_render_begin(self)
    for child in self._children:
      child.on_render_begin()

  def render(self, dialog):
    for child in self._children:
      child.render(dialog)

  def init_values(self, dialog):
    for child in self._children:
      child.init_values(dialog)

  def command_event(self, id, bc):
    for child in self._children:
      if child.command_event(id, bc):
        return True
    return False

  def input_event(self, bc):
    for child in self._children:
      if child.input_event(bc):
        return True
    return False

  def update(self, dialog):
    BaseWidget.update(self, dialog)
    for child in self._children:
      child.update(dialog)

  def save_state(self):
    for child in self._children:
      child.save_state()

  def send_event(self, __name, *args, **kwargs):
    awaiting_listeners, result = super(BaseGroupWidget, self).send_event(
      __name, *args, **kwargs)
    if __name in self._forward_events:
      for child in self._children:
        awaiting_listeners += child.send_event(__name, *args, **kwargs)[0]
    return awaiting_listeners, result


from .widgets import Group
