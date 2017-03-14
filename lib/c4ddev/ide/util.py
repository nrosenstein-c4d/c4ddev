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

from functools import partial

import os
import c4d
import collections

# Indices for a margin/padding tuple.
Left = 0
Top = 1
Right = 2
Bottom = 3


class Rect(object):
  ''' Axis-aligned 2D rectangle. '''

  __slots__ = 'x y w h'.split()

  def __init__(self, x, y, w, h):
    super(Rect, self).__init__()
    self.x = x
    self.y = y
    self.w = w
    self.h = h

  @property
  def x2(self):
    return self.x + self.w

  @property
  def y2(self):
    return self.y + self.h

  def __getitem__(self, index):
    return getattr(self, Rect.__slots__[index])

  def __setitem__(self, index, value):
    setattr(self, Rect.__slots__[index], value)

  def __contains__(self, other):
    if isinstance(other, (list, tuple)):
      x, y = other
      if x < self.x or x >= self.x2:
        return False
      if y < self.y or y >= self.y2:
        return False
      return True
    raise TypeError('expected list/tuple')

  def __repr__(self):
    return '<Rect {0!r}>'.format(list(self))

  def __iter__(self):
    yield int(self.x)
    yield int(self.y)
    yield int(self.x + self.w) - 1
    yield int(self.y + self.h) - 1

  def __add__(self, other):
    return Rect(self.x + other[0], self.y + other[1], self.w, self.h)


class Element(object):

  def __init__(self):
    super(Element, self).__init__()
    self.frame = Rect(0, 0, 0, 0)

  def compute_size(self, area):
    self.frame.x = 0
    self.frame.y = 0

  def compute_layout(self, parent, area):
    if parent:
      self.frame.x += parent.frame.x
      self.frame.y += parent.frame.y

  def render(self, area):
    pass

  def mouse_event(self, mouse, channel, bc, handled):
    return False


class Text(Element):

  def __init__(self, value, color=c4d.COLOR_TEXT, font=c4d.FONT_DEFAULT):
    super(Text, self).__init__()
    self.changed = True
    self._value = ''
    self.value = value
    self.color = color
    self.font = font

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    if not isinstance(value, str):
      raise TypeError('expected str')
    if value != self._value:
      self._value = value
      self.changed = True

  def compute_size(self, area):
    if self.changed:
      area.DrawSetFont(self.font)
      self.frame.w = area.DrawGetTextWidth(self.value)
      self.frame.h = area.DrawGetFontHeight()

  def render(self, area):
    area.DrawSetFont(self.font)
    area.DrawSetTextCol(self.color, c4d.COLOR_TRANS)
    area.DrawText(self.value, self.frame.x, self.frame.y)


class Icon(Element):

  def __init__(self, icon, on_click=None, width=None, height=None):
    super(Icon, self).__init__()
    if isinstance(icon, int):
      icon = c4d.gui.GetIcon(icon)
    elif isinstance(icon, c4d.bitmaps.BaseBitmap):
      icon = {'bmp': icon, 'x': 0, 'y': 0, 'w': icon.GetBw(), 'h': icon.GetBh()}
    elif not isinstance(icon, dict):
      raise TypeError('expected int, BaseBitmap or icon dict')
    self.icon = icon
    self.on_click = on_click
    self.width = width
    self.height = height

  @staticmethod
  def _calc_prop(current, original, scalar):
    return

  def compute_size(self, area):
    calc = lambda curr, orig, scalar: int(float(curr) / float(orig) * scalar)
    self.frame.w = self.frame.h = 0
    if self.width is not None:
      self.frame.w = self.width
      if self.height is None:
        self.frame.h = calc(self.width, self.icon['w'], self.icon['h'])
      else:
        self.frame.h = self.height
    elif self.height is not None:
      self.frame.h = self.height
      self.frame.w = calc(self.height, self.icon['h'], self.icon['w'])
    else:
      self.frame.w = self.icon['w']
      self.frame.h = self.icon['h']

  def render(self, area):
    area.DrawBitmap(self.icon['bmp'], self.frame.x, self.frame.y,
      self.frame.w, self.frame.h, self.icon['x'], self.icon['y'],
      self.icon['w'], self.icon['h'], c4d.BMP_ALLOWALPHA)

  def mouse_event(self, mouse, children, bc, handled):
    if not handled and mouse in self.frame:
      if self.on_click:
        self.on_click()
        return True
    return handled


class Container(Element):

  def __init__(self, margin=(0, 0, 0, 0)):
    super(Container, self).__init__()
    self.children = []
    self.margin = list(margin)
    self.background_color = c4d.COLOR_BGEDIT
    self.on_click = None

  def compute_size(self, area):
    x = self.margin[Left]
    y = self.margin[Top]
    h = 0

    max_margin = max((self.margin[Left], self.margin[Right]))
    last_index = len(self.children) - 1
    for index, elem in enumerate(self.children):
      elem.compute_size(area)
      elem.frame.x = x
      elem.frame.y = y

      x += elem.frame.w
      h = max((elem.frame.h, h))
      if index == last_index:
        x += self.margin[Right]
      else:
        x += max_margin

    # Center elements vertically.
    for elem in self.children:
      elem.frame.y += (h - elem.frame.h) / 2

    self.frame.w = x
    self.frame.h = h + self.margin[Top] + self.margin[Bottom]

  def compute_layout(self, parent, area):
    super(Container, self).compute_layout(parent, area)
    for elem in self.children:
      elem.compute_layout(self, area)

  def render(self, area):
    if self.background_color:
      area.DrawSetPen(self.background_color)
      area.DrawRectangle(*self.frame)
    for elem in self.children:
      elem.render(area)

  def mouse_event(self, mouse, channel, bc, handled):
    if mouse in self.frame:
      for elem in self.children:
        handled = elem.mouse_event(mouse, channel, bc, handled) or handled
      if not handled and self.on_click:
        self.on_click()
        handled = True
    return handled


class TabView(c4d.gui.GeUserArea):
  ''' This class implements a horizontal tab bar with close buttons.
  Callbacks are used for data exchange and notifications. '''

  def __init__(self, editor):
    super(TabView, self).__init__()
    self.editor = editor
    self.padding = [4, 4, 4, 4, 4]
    self.close_size = 14
    self.plus_size = 26
    self.layout = None
    self.background_color = c4d.COLOR_BGEDIT

  def refresh(self):
    layout = Container(margin=(4, 4, 4, 4))

    tab = Icon(c4d.CINEMAN_ROOTFILE, width=self.plus_size)
    tab.on_click = self.editor.open_document
    layout.children.append(tab)

    tab = Icon(c4d.RESOURCEIMAGE_AMDUPLICATE, width=self.plus_size)
    tab.on_click = self.editor.new_document
    layout.children.append(tab)

    tab = Icon(c4d.RESOURCEIMAGE_BROWSER_PLAY, width=self.plus_size)
    tab.on_click = self.editor.run_code
    layout.children.append(tab)

    active_doc = self.editor.get_active_document()
    for doc in self.editor.documents:
      tab = Container(margin=(8, 4, 8, 4))
      name = os.path.basename(doc.filename) if doc.filename else 'untitled'  # xxx: todo
      font = c4d.FONT_BOLD if doc.status == doc.Edited else c4d.FONT_DEFAULT
      tab.children.append(Text(name, font=font))
      tab.children.append(Icon(
        c4d.RESOURCEIMAGE_CLEARSELECTION,
        on_click=partial(self.editor.remove_document, doc),
        width=self.close_size))
      if doc == active_doc:
        tab.background_color = c4d.COLOR_BG
        tab.children[0].color = c4d.COLOR_TEXTFOCUS
      tab.on_click = partial(self.editor.set_active_document, doc)
      layout.children.append(tab)

    self.layout = layout
    self.compute_layout()
    self.LayoutChanged()

  def compute_layout(self, force=False):
    if not self.layout:
      self.refresh()
    self.layout.compute_size(self)
    self.layout.compute_layout(None, self)

  def DrawMsg(self, x1, y1, x2, y2, msg):
    if not self.layout:
      self.refresh()
    self.OffScreenOn()
    self.DrawSetPen(self.background_color)
    self.DrawRectangle(x1, y1, x2 - 1, y2 - 1)
    self.layout.render(self)

  def Sized(self, w, h):
    self.compute_layout()

  def GetMinSize(self):
    self.compute_layout()
    return self.layout.frame.w, self.layout.frame.h

  def InputEvent(self, msg):
    device = msg.GetLong(c4d.BFM_INPUT_DEVICE)
    channel = msg.GetLong(c4d.BFM_INPUT_CHANNEL)
    if device == c4d.BFM_INPUT_MOUSE and self.layout:
      g2l = self.Global2Local()
      xpos = msg.GetLong(c4d.BFM_INPUT_X) + g2l['x']
      ypos = msg.GetLong(c4d.BFM_INPUT_Y) + g2l['y']
      handled = self.layout.mouse_event((xpos, ypos), channel, msg, False)
      return handled
    return False

  def CoreMessage(self, msg, bc):
    if msg == c4d.EVMSG_CHANGE:
      self.refresh()
      self.Redraw()
    return True
