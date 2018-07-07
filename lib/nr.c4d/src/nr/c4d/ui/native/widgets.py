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

__all__ = [
  'Group', 'Text', 'Spacer', 'Separator', 'Button', 'Input',
  'UserArea', 'MenuGroup', 'MenuItem', 'Checkbox', 'Combobox', 'Item',
  'Quicktab', 'DialogPin', 'Component', 'get_layout_flags', 'get_scroll_flags'
]

import c4d
import os
import sys
from .base import BaseWidget, BaseGroupWidget
from .manager import WidgetManager
from ..utils.xml import load_xml_widgets


def load_xml_string(xml, globals, insert_widget=None, _stackframe=0):
  if insert_widget is None:
    def insert_widget(parent, child):
      parent.pack(child)

  if globals is None:
    globals = sys._getframe(_stackframe+1).f_globals
  globals = dict(globals)
  globals.update(__builtins__['globals']())  # Make default widgets available

  return load_xml_widgets(xml, globals, insert_widget)


def load_xml_file(filename, globals, insert_widget=None, _stackframe=0):
  if isinstance(filename, str):
    if not os.path.isabs(filename):
      parent_dir = os.path.dirname(sys._getframe(_stackframe+1).f_globals['__file__'])
      filename = os.path.join(parent_dir, filename)
    with open(filename, 'r') as fp:
      xml = fp.read()
  else:
    xml = filename.read()
  return load_xml_string(xml, globals, insert_widget, _stackframe=_stackframe+1)


_layout_map = {
  'fill': c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
  'fill-x': c4d.BFH_SCALEFIT,
  'fill-y': c4d.BFV_SCALEFIT,
  'fit': c4d.BFH_FIT | c4d.BFV_FIT,
  'fit-x': c4d.BFH_FIT,
  'fit-y': c4d.BFV_FIT,
  'left': c4d.BFH_LEFT,
  'center': c4d.BFH_CENTER,
  'right': c4d.BFH_RIGHT,
  'top': c4d.BFV_TOP,
  'middle': c4d.BFV_CENTER,
  'bottom': c4d.BFV_BOTTOM
}

_border_map = {
  'none': c4d.BORDER_NONE,
  'thin_in': c4d.BORDER_THIN_IN,
  'thin_out': c4d.BORDER_THIN_OUT,
  'in': c4d.BORDER_IN,
  'out': c4d.BORDER_OUT,
  'group_in': c4d.BORDER_GROUP_IN,
  'group_out': c4d.BORDER_GROUP_OUT,
  'out2': c4d.BORDER_OUT2,
  'out3': c4d.BORDER_OUT3,
  'black': c4d.BORDER_BLACK,
  'active_1': c4d.BORDER_ACTIVE_1,
  'active_2': c4d.BORDER_ACTIVE_2,
  'active_3': c4d.BORDER_ACTIVE_3,
  'active_4': c4d.BORDER_ACTIVE_4,
  'group_top': c4d.BORDER_GROUP_TOP,
  'round': c4d.BORDER_ROUND,
  'scheme_edit': c4d.BORDER_SCHEME_EDIT,
  'scheme_edit_numeric': c4d.BORDER_SCHEME_EDIT_NUMERIC,
  'out3l': c4d.BORDER_OUT3l,
  'out3r': c4d.BORDER_OUT3r
}

_scroll_map = {
  'none': 0,
  'vertical': c4d.SCROLLGROUP_VERT,
  'vertical-auto': c4d.SCROLLGROUP_VERT | c4d.SCROLLGROUP_AUTOVERT,
  'horizontal': c4d.SCROLLGROUP_HORIZ,
  'horizontal-auto': c4d.SCROLLGROUP_HORIZ | c4d.SCROLLGROUP_AUTOHORIZ,
  'noblit': c4d.SCROLLGROUP_NOBLIT,
  'scroll-left': c4d.SCROLLGROUP_LEFT,
  'border-in': c4d.SCROLLGROUP_BORDERIN,
  'statusbar': c4d.SCROLLGROUP_STATUSBAR,
  'statusbar-ext-group': c4d.SCROLLGROUP_STATUSBAR_EXT_GROUP,
  'noscroller': c4d.SCROLLGROUP_NOSCROLLER,
  'novgap': c4d.SCROLLGROUP_NOVGAP
}

_unit_map = {
  'float': c4d.FORMAT_FLOAT,
  'int': c4d.FORMAT_INT,
  'percent': c4d.FORMAT_PERCENT,
  'degree': c4d.FORMAT_DEGREE,
  'meter': c4d.FORMAT_METER,
  'frames': c4d.FORMAT_FRAMES,
  'seconds': c4d.FORMAT_SECONDS,
  'smpte': c4d.FORMAT_SMPTE
}


def get_layout_flags(layout):
  layout_flags = 0
  for flag_name in layout.split(','):
    layout_flags |= _layout_map[flag_name]
  return layout_flags


def get_scroll_flags(scroll):
  scroll_flags = 0
  for flag_name in scroll.split(','):
    scroll_flags |= _scroll_map[flag_name]
  return scroll_flags


def bool_cast(obj):
  if isinstance(obj, basestring):
    obj = obj.encode().strip().lower()
    if obj == 'true':
      return True
    return False
  else:
    return bool(obj)


class Group(BaseGroupWidget):
  """
  A Cinema 4D group widget.

  # Parameters
  layout (str): One of the following flags, or a combination separated
    by commas: fill, fill-x, fill-y, fit, fit-x, fit-y, left, center, right,
    top, middle, bottom.
  rows (str, int): The number of rows.
  cols (str, int): The number of columns.
  title (str): The group title (only visible when a *border* is set).
  title_bold (bool, str): Whether the group title should be displayed in
    bold letters.
  initw (int, str): The initial width.
  inith (int, str): The initial height.
  border (str): The border type, one of the following values: none, thin_in,
    thin_out, in, out, group_in, group_out, out2, out3, black, active_1,
    active_2, active_3, active_4, group_top, round, scheme_edit,
    scheme_edit_numeric, out3l, out3r
  borderspace (tuple of (int, int, int, int), str): Group border space.
  itemspace (tuple of (int, int), str): Item spacing.
  scroll (str): One of the following flags, or a combination separated
    by commas: vertical, horizontal, vertical-auto, horizontal-auto,
    noblit, scroll-left, border-in, statusbar, statusbar_ext_group,
    noscroller, novgap.
  """

  def __init__(self, layout='fill', rows='0', cols='0', title='',
      title_bold='false', initw='0', inith='0', border='none',
      borderspace=None, itemspace=None, scroll='none', checkbox=False,
      id=None):
    BaseGroupWidget.__init__(self, id)
    self.layout = layout
    self.rows = rows
    self.cols = cols
    self.title = title
    self.initw = initw
    self.inith = inith
    self.border = border
    self.borderspace = borderspace
    self.itemspace = itemspace
    self.scroll = scroll
    self.checkbox = bool_cast(checkbox)
    self._value = False
    self._layout_changed = False

  def layout_changed(self):
    self._layout_changed = True
    manager = self.manager
    if manager is not None:
      manager.layout_changed()
    # Don't call parent method as it will notify the Group's parent about
    # the change, and we only want to rebuild the closes parent group.

  def render(self, dialog):
    # Prepare style attributes.
    border_flags = _border_map[self.border]
    layout_flags = get_layout_flags(self.layout)
    scroll_flags = get_scroll_flags(self.scroll)
    cols = int(self.cols)
    rows = int(self.rows)
    initw = int(self.initw)
    inith = int(self.inith)
    if isinstance(self.borderspace, (unicode, str)):
      borderspace = map(int, self.borderspace.split(','))
    else:
      borderspace = self.borderspace
    if isinstance(self.itemspace, (unicode, str)):
      itemspace = map(int, self.itemspace.split(','))
    else:
      itemspace = self.itemspace
    groupflags = 0
    if self.checkbox:
      groupflags |= c4d.BFV_BORDERGROUP_CHECKBOX

    group_id = self.alloc_id('group')

    if scroll_flags:
      dialog.GroupBegin(0, layout_flags, 1, 0, self.title, groupflags)
    else:
      dialog.GroupBegin(group_id, layout_flags, cols, rows,
        self.title, groupflags, initw, inith)
      if borderspace:
        dialog.GroupBorderSpace(*borderspace)
    if self.title:
      dialog.GroupBorder(border_flags)
    else:
      dialog.GroupBorderNoTitle(border_flags)

    if scroll_flags:
      dialog.ScrollGroupBegin(
        self.alloc_id('scrollgroup'),
        c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
        scroll_flags,
        initw,
        inith
      )
      dialog.GroupBegin(
        group_id,
        c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
        cols,
        rows,
        "",
        0
      )
      if borderspace:
        dialog.GroupBorderSpace(*borderspace)

    if itemspace:
      dialog.GroupSpace(*itemspace)

    BaseGroupWidget.render(self, dialog)

    if scroll_flags:
      dialog.GroupEnd()
      dialog.GroupEnd()

    dialog.GroupEnd()
    self._layout_changed = False

  def init_values(self, dialog):
    super(Group, self).init_values(dialog)
    if self.checkbox:
      dialog.SetBool(self.get_named_id('group'), self._value)

  def update(self, dialog):
    id = self.get_named_id('group', None)
    if self._layout_changed and id is not None:
      # No update() call when child elements are re-rendered.
      self._layout_changed = False
      for child in self.children:
        child.save_state()
      dialog.LayoutFlushGroup(id)
      for child in self.children:
        child.on_render_begin()
      for child in self.children:
        child.render(dialog)
        child.update_state(dialog)
      self.update_state(dialog)
      dialog.queue_layout_changed(id)
    else:
      BaseGroupWidget.update(self, dialog)

  def command_event(self, id, msg):
    if self.checkbox and id == self.get_named_id('group'):
      self._value = self.dialog.GetBool(id)
      return self.send_event('value-changed', self)[1]
    return super(Group, self).command_event(id, msg)

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    self._value = value
    dialog = self._dialog
    if dialog:
      dialog.SetBool(self.get_named_id('group'), value)


class Text(BaseWidget):

  def __init__(self, text='', layout='left,middle', color=None, id=None):
    BaseWidget.__init__(self, id)
    self.layout = layout
    self.text = text
    self.color = color

  def render(self, dialog):
    layout_flags = get_layout_flags(self.layout)
    dialog.AddStaticText(self.alloc_id('text'), layout_flags, name=self.text)
    if self.color:
      dialog.set_color(self.get_named_id('text'), c4d.COLOR_TEXT, self.color)

  def set_color(self, color):
    dialog = self.dialog
    if dialog:
      dialog.set_color(self.get_named_id('text'), c4d.COLOR_TEXT, color)
    color = self.color


class Spacer(Text):

  def __init__(self, layout='fill-x', **kwargs):
    Text.__init__(self, text='', layout=layout, **kwargs)


class Separator(BaseWidget):

  def __init__(self, type='horizontal', id=None):
    BaseWidget.__init__(self, id)
    self.type = type

  def render(self, dialog):
    if isinstance(self.parent, MenuGroup):
      dialog.MenuAddSeparator()
    elif isinstance(self.parent, Combobox):
      dialog.AddChild(self.parent.get_named_id('box'), -1, '')
    elif self.type == 'vertical':
      dialog.AddSeparatorV(0)
    elif self.type == 'horizontal':
      dialog.AddSeparatorH(0)
    else:
      raise ValueError('invalid separator type: {!r}'.format(self.type))


class Button(BaseWidget):

  def __init__(self, layout='left,middle', text='', iconid=None, id=None):
    BaseWidget.__init__(self, id)
    self.layout = layout
    self.text = text
    self.iconid = iconid
    self._bmp_gui = None

  def render(self, dialog):
    layout_flags = get_layout_flags(self.layout)
    if self.iconid is not None:
      try:
        iconid = int(self.iconid)
      except ValueError:
        iconid = getattr(c4d, self.iconid, 0)
      icon = c4d.gui.GetIcon(iconid) or {}
      bc = c4d.BaseContainer()
      bc[c4d.BITMAPBUTTON_BUTTON] = True
      bc[c4d.BITMAPBUTTON_ICONID1] = 0
      self._bmp_gui = dialog.AddCustomGui(self.alloc_id('btn'),
        c4d.CUSTOMGUI_BITMAPBUTTON, "", layout_flags,
        icon.get('w', 0), icon.get('h', 0)/2, bc)
      if icon:
        self._bmp_gui.SetImage(icon)
    else:
      self._bmp_gui = None
      dialog.AddButton(self.alloc_id('btn'), layout_flags, name=self.text)

  def command_event(self, id, msg):
    if id == self.get_named_id('btn', None):
      return self.send_event('click', self)[1]
    return False


class Checkbox(BaseWidget):

  def __init__(self, layout='left,middle', text='', value='false', id=None):
    BaseWidget.__init__(self, id)
    self.layout = layout
    self.text = text
    self._value = value

  def render(self, dialog):
    layout_flags = get_layout_flags(self.layout)
    id = self.alloc_id('chk')
    dialog.AddCheckbox(id, layout_flags, 0, 0, name=self.text)
    value = self._value
    if isinstance(value, basestring):
      value = (value == 'true')
    dialog.SetBool(id, value)

  def command_event(self, id, bc):
    if id == self.get_named_id('chk', None):
      return self.send_event('value-changed', self)[1]
    return False

  def save_state(self):
    if self.get_named_id('chk', None) is not None:
      self._value = self.value

  @property
  def value(self):
    return self.dialog.GetBool(self.get_named_id('chk'))

  @value.setter
  def value(self, value):
    self._value = value
    self.dialog.SetBool(self.get_named_id('chk', value))


class Combobox(BaseGroupWidget):
  """
  Represents a Cinema 4D combo-box widget. When constructing from XML,
  one can use #Item elements for its children or pass a comma-separated
  list for its *items* parameter.

  When passing a string for *items*, `--` can be used to insert a separator.

  # Events
  - value-changed
  """

  def __init__(self, items=None, layout='fit-x,middle', value=None, id=None):
    BaseGroupWidget.__init__(self, id)
    if isinstance(items, basestring):
      items = items.split(',')
    if items is not None:
      for item in items:
        if isinstance(item, basestring):
          item = Separator() if item == '--' else Item(item)
        self.pack(item)
    self.layout = layout
    self._value = value
    self._index = None
    self._layout_changed = True
    self._items = []

  def save_state(self):
    self._index = self.active_index

  def render(self, dialog):
    if self._index is None and self._value is not None:
      # Search for a matching item with the specified value or ID.
      for index, child in enumerate(self._children):
        if child.text == self._value:
          break
      else:
        for index, child in enumerate(self._children):
          if child.ident == self._value:
            break
        else:
          index = None
      self._index = index

    layout_flags = get_layout_flags(self.layout)
    box_id = self.alloc_id('box')
    dialog.AddComboBox(box_id, layout_flags)

    if self._children:
      self._items = []
    BaseGroupWidget.render(self, dialog)

    if self._index is None and self._children:
      self._index = 0
    if self._index is not None:
      self.active_index = self._index

  def layout_changed(self):
    self._layout_changed = True
    manager = self.manager
    if manager:
      manager.layout_changed()

  def update(self, dialog):
    id = self.get_named_id('box', None)
    if self._layout_changed and id is not None:
      self._layout_changed = False
      self.save_state()
      self.update_state(dialog)
      dialog.FreeChildren(id)
      for index, name in enumerate(self._items):
        dialog.AddChild(id, index, name)
      self.active_index = self._index
    else:
      BaseGroupWidget.update(self, dialog)

  def pack(self, widget):
    if not isinstance(widget, (Item, Separator)):
      raise TypeError('Combobox can only contain Item/Separator')
    BaseGroupWidget.pack(self, widget)

  def command_event(self, id, bc):
    if id == self.get_named_id('box', None):
      self._index = self.dialog.GetInt32(id)
      return self.send_event('value-changed', self)[1]
    return False

  def add(self, name):
    self._items.append(name)

  @property
  def active_index(self):
    return self._index

  @active_index.setter
  def active_index(self, value):
    id = self.get_named_id('box', None)
    if value is None:
      self._index = None
      if id is not None:
        self.dialog.SetInt32(id, -1)
    else:
      self._index = int(value)
      self.dialog.SetInt32(id, self._index)

  @property
  def active_item(self):
    if self._index is not None and self._index in xrange(len(self.children)):
      return self.children[self._index]
    return None

  @active_item.setter
  def active_item(self, item):
    if not isinstance(item, Item):
      for child in self.children:
        if child.ident == item:
          item = child
          break
      else:
        raise ValueError('no Item with ident {!r}'.format(item))
    try:
      index = self.children.index(item)
    except ValueError:
      raise ValueError('this Item is not in the Combobox')
    self.active_index = index


class Item(BaseWidget):
  """
  An item inside a #Combobox. Additionally to its displayed *text* and
  #BaseWidget.id, it also has an *ident* member which can be used to store
  additional information to identify the Item.
  """

  def __init__(self, text='???', ident=None, delegate=None, id=None):
    BaseWidget.__init__(self, id)
    self.text = text
    self.ident = ident
    self.delegate = delegate

  def render(self, dialog):
    parent = self.parent
    if self.delegate:
      self.delegate(parent)
    else:
      parent.add(self.text)


class Quicktab(BaseGroupWidget):
  """
  Represents a Quicktab Custom GUI. Unlike the #Combobox, it does not accept
  any child widgets but is instead managed manually and filled from code.

  # Events
  - value-changed
  """

  def __init__(self, layout='fill-x,middle', multiselect='true', value=None,
               id=None):
    BaseGroupWidget.__init__(self, id)
    self.layout = layout
    self.multiselect = bool_cast(multiselect)
    self._value = value
    self._textcol = None
    self._items = []
    self._checked_count = 0
    self._gui = None
    self._layout_changed = False

  def clear(self):
    try:
      return self._items
    finally:
      self._items = []
      if self._gui:
        self._gui.ClearStrings()
      self.layout_changed()

  def add(self, string, color=None, checked=False, visible=True):
    item = {'string': str(string), 'color': color, 'checked': checked, 'visible': visible}
    self._items.append(item)
    self.layout_changed()

  def is_checked(self, index):
    if isinstance(index, basestring):
      for item_index, item in enumerate(self._children):
        if item.ident == index:
          index = item_index
          break
      else:
        return False
    return self._items[index]['checked']

  def set_checked(self, index, checked, mode='new'):
    assert mode in ('new', 'add')
    checked = bool(checked)
    item = self._items[index]
    if item['checked'] == checked:
      return
    item['checked'] = checked
    gui = self._gui

    if mode == 'new':
      self._checked_count = 1
      # Deselect all other items.
      for i, item in enumerate(self._items):
        if i != index:
          item['checked'] = False
          if gui: gui.Select(i, False)
    else:
      self._checked_count += int(checked)

    # Update the GUI of the current item.
    if gui: gui.Select(index, checked)

  def set_color(self, index, color):
    item = self._items[index]
    item['color'] = color
    if self._gui:
      self._gui.SetTextColor(index, color)

  def set_visible(self, index, visible):
    item = self._items[index]
    if item['checked']:
      self._checked_count -= 1
    item['visible'] = visible
    if self._checked_count == 0:
      # Check the first available item instead.
      for index, item in enumerate(self._items):
        if item['visible']:
          self.set_checked(index, True)
          break
    self.layout_changed()

  def layout_changed(self):
    self._layout_changed = True
    manager = self.manager
    if manager:
      manager.layout_changed()

  def render(self, dialog):
    layout_flags = get_layout_flags(self.layout)
    multiselect = self.multiselect
    bc = c4d.BaseContainer()
    bc[c4d.QUICKTAB_BAR] = False
    bc[c4d.QUICKTAB_SHOWSINGLE] = True
    bc[c4d.QUICKTAB_SPRINGINGFOLDERS] = True # ??
    bc[c4d.QUICKTAB_SEPARATOR] = False
    bc[c4d.QUICKTAB_NOMULTISELECT] = not multiselect
    self._gui = dialog.AddCustomGui(
      self.alloc_id('gui'),
      c4d.CUSTOMGUI_QUICKTAB,
      "",
      layout_flags,
      0,
      0,
      bc
    )
    self._layout_changed = True
    if self._children:
      self._items = []
    BaseGroupWidget.render(self, dialog)

  def command_event(self, id, bc):
    if id == self.get_named_id('gui', None):
      # Update the selection state of all elements.
      gui = self._gui
      self._checked_count = 0
      for index, item in enumerate(self._items):
        item['checked'] = gui.IsSelected(index)
        if item['checked'] and item['visible']:
          self._checked_count += 1
      return self.send_event('value-changed', self)[1]
    return False

  def update(self, dialog):
    id = self.get_named_id('gui', None)
    if self._layout_changed and id is not None:
      self._layout_changed = False
      gui = self._gui
      gui.ClearStrings()

      visible_count = 0
      self._checked_count = 0
      first_visible_index = None

      for index, item in enumerate(self._items):
        if not item['visible']: continue
        if first_visible_index is None:
          first_visible_index = index
        visible_count += 1
        if item['checked']:
          self._checked_count += 1
        gui.AppendString(index, item['string'], item['checked'])
        if item['color'] is not None:
          gui.SetTextColor(index, item['color'])

      # Make sure that at least one item is selected.
      if visible_count > 0 and self._checked_count == 0:
        self.set_checked(first_visible_index, True)
      gui.DoLayoutChange()

    BaseGroupWidget.update(self, dialog)

  def init_values(self, dialog):
    if self._value is not None:
      values = self._value.split(',')
      mode = 'new'
      for index, item in enumerate(self._children):
        if self._value == '*' or item.ident in values:
          self.set_checked(index, True, mode)
          mode = 'add'
          if not self.multiselect:
            break

  @property
  def active_item(self):
    if len(self._items) != len(self.children):
      raise RuntimeError("Quicktab._items out of sync with Quicktab.children")
    for item, child in zip(self._items, self.children):
      if item['checked']:
        return child
    return None


class LinkBox(BaseWidget):
  """
  Represents a link box GUI.

  # Events
  - value-changed
  """

  def __init__(self, layout='fill-x,middle', id=None):
    BaseWidget.__init__(self, id)
    self.layout = layout
    self._layout_changed = False
    self._gui = None

  def get_link(self, doc=None, instanceof=0):
    if self._gui:
      return self._gui.GetLink(doc, instanceof)
    return None

  def set_link(self, node):
    if self._gui:
      self._gui.SetLink(node)

  def layout_changed(self):
    self._layout_changed = True
    manager = self.manager
    if manager:
      manager.layout_changed()

  def render(self, dialog):
    layout_flags = get_layout_flags(self.layout)
    bc = c4d.BaseContainer()
    self._gui = dialog.AddCustomGui(
      self.alloc_id('gui'),
      c4d.CUSTOMGUI_LINKBOX,
      "",
      layout_flags,
      0,
      0,
      bc
    )
    self._layout_changed = True

  def command_event(self, id, bc):
    if id == self.get_named_id('gui', None):
      return self.send_event('value-changed', self)[1]
    return False


class Input(BaseWidget):

  def __init__(self, layout='left,middle', type='string', slider='false',
      arrows='true', min=None, max=None, minslider=None, maxslider=None,
      helptext=None, is_password='false', unit='float', quadscale='false',
      step='1', minw='0', minh='0', id=None, value=None):
    BaseWidget.__init__(self, id)
    assert type in ('string', 'integer', 'float')
    actual_type = {'string': str, 'integer': int, 'float': float}[type]

    if value is None:
      value = actual_type()

    self.layout = layout
    self.type = type
    self.slider = bool_cast(slider)
    self.arrows = bool_cast(arrows)
    self.min = actual_type(min) if min is not None else None
    self.max = actual_type(max) if max is not None else None
    self.minslider = actual_type(minslider) if minslider is not None else None
    self.maxslider = actual_type(maxslider) if maxslider is not None else None
    self.helptext = helptext
    self.is_password = bool_cast(is_password)
    self.unit = _unit_map[unit] if isinstance(unit, str) else unit
    self.quadscale = bool_cast(quadscale)
    self.step = actual_type(step)
    self.minw = int(minw)
    self.minh = int(minh)
    self._value = value

    self.add_event_listener('visibility-changed', self.__visibility_changed)

  def __visibility_changed(self, _):
    value = self.value
    self.value = ''
    yield
    self.value = value

  def save_state(self):
    if self.get_named_id('field', None) is not None:
      self._value = self.value

  def render(self, dialog):
    layout_flags = get_layout_flags(self.layout)
    id = self.alloc_id('field')
    if self.type == 'string':
      edtflags = c4d.EDITTEXT_PASSWORD if (self.is_password == 'true') else 0
      dialog.AddEditText(id, layout_flags, self.minw, self.minh,
        editflags=edtflags)
    elif self.type in ('integer', 'float'):
      if self.slider:
        method = dialog.AddEditSlider if self.arrows else dialog.AddSlider
      else:
        method = dialog.AddEditNumberArrows if self.arrows else dialog.AddEditNumber
      method(id, layout_flags, self.minw, self.minh)
    else:
      raise RuntimeError("Input.type invalid: {0!r}".format(self.type))
    if self._value is not None:
      self.value = self._value
    if self.helptext:
      dialog.SetString(id, self.helptext, False, c4d.EDITTEXT_HELPTEXT)
    self._update_color(dialog)

  def _update_color(self, dialog):
    if self.helptext and not self.value:
      color = c4d.Vector(0.4)
    else:
      color = None
    dialog.set_color(self.get_named_id('field'), c4d.COLOR_TEXT_EDIT, color)

  def command_event(self, id, bc):
    if id == self.get_named_id('field', None):
      if self.type == 'string':
        data = {'in_edit': bc.GetBool(c4d.BFM_ACTION_STRCHG)}
        self._update_color(self.dialog)
      else:
        data = {'in_drag': bc.GetBool(c4d.BFM_ACTION_INDRAG)}
      res = bool(self.send_event('input-changed', self, data)[1])
      res = res | bool(self.send_event('value-changed', self)[1])
      return res
    return False

  @property
  def value(self):
    dialog = self.dialog
    id = self.get_named_id('field')
    if self.type == 'string':
      return dialog.GetString(id)
    elif self.type == 'integer':
      return dialog.GetInt32(id)
    elif self.type == 'float':
      return dialog.GetFloat(id)
    else:
      raise RuntimeError("Input.type invalid: {0!r}".format(self.type))

  @value.setter
  def value(self, value):
    dialog = self.dialog
    id = self.get_named_id('field')
    if self.type == 'string':
      if value is None:
        value = ''
      dialog.SetString(id, value)
      self._update_color(dialog)
    elif self.type == 'integer':
      min, max, minslider, maxslider = self._get_limit_props(
        c4d.MINLONGl, c4d.MAXLONGl)
      self.dialog.SetInt32(id, int(value), min, max, self.step,
        False, minslider, maxslider)
    elif self.type == 'float':
      min, max, minslider, maxslider = self._get_limit_props(
        sys.float_info.min, sys.float_info.max)
      self.dialog.SetFloat(id, float(value), min, max, self.step,
        self.unit, minslider, maxslider, self.quadscale, False)
    else:
      raise RuntimeError("Input.type invalid: {0!r}".format(self.type))

  def set_helptext(self, text):
    if text is None:
      text = ''
    dialog = self.dialog
    if dialog:
      dialog.SetString(self.get_named_id('field'), text, False, c4d.EDITTEXT_HELPTEXT)
    update = bool(self.helptext) != bool(text)
    self.helptext = text
    if update:
      self._update_color(dialog)

  def _get_limit_props(self, lower_limit, upper_limit):
    conv = int if self.type == 'integer' else float
    either = lambda a, b: a if a is not None else b
    min = either(self.min, lower_limit)
    max = either(self.max, upper_limit)
    # Invert min/minslider and max/maxslider to match the C4D behavour.
    if self.minslider is not None:
      min, minslider = either(self.minslider, min), min
    else:
      minslider = min
    if self.maxslider is not None:
      max, maxslider = either(self.maxslider, max), max
    else:
      maxslider = max
    return conv(min), conv(max), conv(minslider), conv(maxslider)


class FileSelector(Group):
  """
  Represents a file selector widget.
  """

  def __init__(self, layout='fill-x,middle', type='load', id=None):
    super(FileSelector, self).__init__(layout=layout, id=id)
    self.type = type
    self.def_path = None
    self._input = Input(type='string', layout='fill-x,middle')
    self._input.add_event_listener('value-changed', self._on_input_change)
    self._button = Button(text='...')
    self._button.add_event_listener('click', self._on_button_press)
    self.pack(self._input)
    self.pack(self._button)

  def _on_input_change(self, input):
    self.send_event('value-changed', self)

  def _on_button_press(self, button):
    flags = {
      'load': c4d.FILESELECT_LOAD,
      'save': c4d.FILESELECT_SAVE,
      'directory': c4d.FILESELECT_DIRECTORY
    }[self.type]
    path = c4d.storage.LoadDialog(flags=flags, def_path=self.def_path)
    if path:
      self._input.value = path
      self.send_event('value-changed', self)
    return True

  def set_helptext(self, text):
    self._input.set_helptext(text)

  @property
  def value(self):
    return self._input.value

  @value.setter
  def value(self, value):
    self._input.value = value


class UserArea(BaseWidget):

  def __init__(self, layout='left,middle', id=None):
    BaseWidget.__init__(self, id)
    self.layout = layout
    self._user_area = None
    self._layout_changed = False

  def layout_changed(self):
    self._layout_changed = True
    manager = self.manager
    if manager:
      manager.layout_changed()

  @property
  def user_area(self):
    return self._user_area

  @user_area.setter
  def user_area(self, user_area):
    self._user_area = user_area
    try:
      id = self.get_named_id('ua')
    except KeyError:
      pass
    else:
      self.dialog.AttachUserArea(user_area, id)
      self.layout_changed()

  def render(self, dialog):
    layout_flags = get_layout_flags(self.layout)
    id = self.alloc_id('ua')
    dialog.AddUserArea(id, layout_flags)
    if self.user_area:
      dialog.AttachUserArea(self.user_area, id)
    self._layout_changed = True

  def update(self, dialog):
    id = self.get_named_id('ua', None)
    if self._layout_changed and id is not None:
      self.update_state(dialog)
      self.dialog.queue_layout_changed(id)
    else:
      BaseWidget.update(self, dialog)


class MenuGroup(BaseGroupWidget):
  """
  Represents a group for a menu. There should be one and only one #MenuGroup
  for every dialog. The root #MenuGroup does not require a name.

  Can only container other #MenuGroup, #MenuItem and #Separator instances.
  """

  def __init__(self, name='???', id=None):
    BaseGroupWidget.__init__(self, id)
    self.name = name

  def pack(self, widget):
    #if not isinstance(widget, (MenuItem, MenuGroup, Separator)):
    #  raise TypeError('MenuGroup can only have MenuItem/MenuGroup/Separator as children')
    BaseGroupWidget.pack(self, widget)

  def render(self, dialog):
    id = self.alloc_id('menu')
    is_outter = True
    parent = self.parent
    while parent:
      if isinstance(parent, MenuGroup):
        is_outter = False
        break
      parent = parent.parent
    if is_outter:
      dialog.MenuFlushAll()
    else:
      dialog.MenuSubBegin(self.name)
    BaseGroupWidget.render(self, dialog)
    if is_outter:
      dialog.MenuFinished()
    else:
      dialog.MenuSubEnd()


class MenuItem(BaseWidget):
  """
  Represents a menu item.

  # Events
  - click: The menu item has been clicked (not received for plugin ID items).
  """

  def __init__(self, name='???', plugin=None, id=None):
    BaseWidget.__init__(self, id)
    self.name = name
    self.plugin = plugin

  def render(self, dialog):
    if self.plugin is not None:
      if isinstance(self.plugin, basestring):
        try:
          plugin_id = int(self.plugin)
        except ValueError:
          plugin_id = getattr(c4d, self.plugin)
      else:
        plugin_id = self.plugin
      dialog.MenuAddCommand(plugin_id)
    else:
      id = self.alloc_id('menu')
      dialog.MenuAddString(id, self.name)

  def command_event(self, id, bc):
    if id == self.get_named_id('menu', None):
      if self.send_event('click', self)[1]:
        return True
      # Also propagate the event up the MenuGroup hierarchy.
      parent = self.parent
      while isinstance(parent, MenuGroup):
        if parent.send_event('click', self):
          return True
        parent = parent.parent
      return False
    return False


class DialogPin(BaseWidget):
  """
  The dialog "pin" that allows a user to click and drag the dialog to embedd
  it into another dialog window and the Cinema 4D layout.
  """

  def render(self, dialog):
    dialog.AddGadget(c4d.DIALOG_PIN, 0)


class Component(BaseGroupWidget):
  """
  Wraps another widget in a sub #WidgetManager.
  """

  def __init__(self, id=None):
    super(Component, self).__init__(id)
    self.sub_manager = WidgetManager(dialog=None, parent=None, root=self)

  def __getitem__(self, widget_id):
    return self.sub_manager[widget_id]

  @BaseGroupWidget.manager.setter
  def manager(self, manager):
    # Important: Do not use BaseGroupWidget.manager.__set__() as that
    # will propagate the parent manager to the child widgets!
    BaseWidget.manager.__set__(self, manager)
    self.sub_manager.remove()
    if manager:
      manager.add_child(self.sub_manager)

  def pack(self, widget):
    if not isinstance(widget, BaseWidget):
      raise TypeError('expected BaseWidget')
    widget.remove()
    widget.parent = self
    widget.manager = self.sub_manager
    self._children.append(widget)
    self.layout_changed()

  def load_xml_string(self, xml, globals=None, _stackframe=0):
    self.pack(load_xml_string(xml, globals, _stackframe=_stackframe+1))

  def load_xml_file(self, filename, globals=None, _stackframe=0):
    self.pack(load_xml_file(filename, globals, _stackframe=_stackframe+1))
