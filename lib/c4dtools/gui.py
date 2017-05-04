# -*- coding: utf8; -*-
#
# Copyright (C) 2015  Niklas Rosenstein
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
import collections
import time
import traceback


class Rect(object):
  ''' Represents an axis-aligned rectangle in two dimensional space
  represented as four integer numbers. For floating-point precision
  pixel-arithmetic, compute the components manually. '''

  def __init__(self, x1, y1, x2=None, y2=None, w=None, h=None):
    super(Rect, self).__init__()
    self.x1 = int(x1)
    self.y1 = int(y1)

    if x2 is None:
      if w is None:
        raise ValueError('neither x2 nor w specified')
      x2 = self.x1 + w
    if y2 is None:
      if h is None:
        raise ValueError('neither y2 nor h specified')
      y2 = self.y1 + h

    self.x2 = int(x2)
    self.y2 = int(y2)

  def __iter__(self):
    yield self.x1
    yield self.y1
    yield self.x2
    yield self.y2

  def __contains__(self, other):
    if isinstance(other, (list, tuple)):
      if len(other) != 2:
        message, 'list/tuple for __contains__ must have 2 elements'
        raise ValueError(message, len(other))
      x, y = other
      if x < self.x1 or x > self.x2:
        return False
      if y < self.y1 or y > self.y2:
        return False
      return True
    elif type(other) is Rect:
      if other.x2 < self.x1 or other.y2 < self.y1:
        return False
      if other.x1 > self.x2 or other.y1 > self.y2:
        return False
      return True
    else:
      raise TypeError('unsupported type for __contains__', type(other))

  def __repr__(self):
    return 'Rect{0}'.format(self.tup())

  def __copy__(self, **overrides):
    copy = Rect(self.x1, self.y1, self.x2, self.y2)
    for k, v in overrides.iteritems():
      setattr(copy, k, v)
    return copy

  def tup(self, grow=0, relative=False):
    if relative:
      return self.x1, self.y1, self.w + grow, self.h + grow
    else:
      return self.x1, self.y1, self.x2 + grow, self.y2 + grow

  def get_normalized(self):
    x1, y1, x2, y2 = self.tup()
    if x2 < x1: x1, x2 = x2, x1
    if y2 < y1: y1, y2 = y2, y1
    return Rect(x1, y1, x2, y2)

  def get_width(self):
    return self.x2 - self.x1

  def get_height(self):
    return self.y2 - self.y1

  def set_width(self, w):
    self.x2 = self.x1 + int(w)

  def set_height(self, h):
    self.y2 = self.y1 + int(h)

  def center(self):
    return (self.x1 + self.w / 2), (self.y1 + self.h / 2)

  copy = __copy__
  width = w = property(get_width, set_width)
  height = h = property(get_height, set_height)


class ExtendedUserArea(c4d.gui.GeUserArea):
  ''' The *ExtendedUserArea* provides a bunch of helper functions and
  pre-implemented overrides of the *GeUserArea* class to make it easier
  to implement custom user interfaces. '''

  def SendAction(self, bc=None):
    if bc is None:
      bc = c4d.BaseContainer()
    bc.SetId(c4d.BFM_ACTION)
    bc.SetInt32(c4d.BFM_ACTION_ID, self.GetId())
    return self.SendParentMessage(bc)

  def GetMouse(self, msg, drag=False):
    if drag:
      return (msg.GetInt32(c4d.BFM_DRAG_SCREENX), msg.GetInt32(c4d.BFM_DRAG_SCREENY))
    else:
      return (msg.GetInt32(c4d.BFM_INPUT_X), msg.GetInt32(c4d.BFM_INPUT_Y))

  def GetMouseLocal(self, msg, drag=False):
    x, y = self.GetMouse(msg, drag)
    if drag:
      conv = self.Screen2Local()
    else:
      conv = self.Global2Local()

    return (x + conv['x'], y + conv['y'])

  def GenerateMouseDrag(self, msg, state=None, only_mouse_change=False):
    device = msg.GetInt32(c4d.BFM_INPUT_DEVICE)
    channel = msg.GetInt32(c4d.BFM_INPUT_CHANNEL)
    if state is None:
      state = c4d.BaseContainer()
    prev_mouse = None
    while self.GetInputState(device, channel, state):
      if not state.GetInt32(c4d.BFM_INPUT_VALUE):
        break

      mouse = self.GetMouseLocal(state)
      if not only_mouse_change or prev_mouse != mouse:
        yield mouse
        prev_mouse = mouse
      else:
        yield None

  def MouseEvent(self, msg, channel):
    return False

  def KeyboardEvent(self, msg, channel):
    return False

  def DragEvent(self, msg, dragtype, data, dropped):
    return False

  def InputEvent(self, msg):
    device = msg.GetInt32(c4d.BFM_INPUT_DEVICE)
    channel = msg.GetInt32(c4d.BFM_INPUT_CHANNEL)
    if device == c4d.BFM_INPUT_MOUSE:
      return self.MouseEvent(msg, channel)
    elif device == c4d.BFM_INPUT_KEYBOARD:
      return self.KeyboardEvent(msg, channel)
    return False

  def Message(self, msg, result):
    if msg.GetId() == c4d.BFM_DRAGRECEIVE:
      quit = msg.GetInt32(c4d.BFM_DRAG_LOST)
      if not quit: quit = msg.GetInt32(c4d.BFM_DRAG_ESC)
      if not quit: quit = not self.CheckDropArea(msg, True, True)
      if quit:
        return self.SetDragDestination(c4d.MOUSE_FORBIDDEN)

      data = self.GetDragObject(msg)
      dropped = bool(msg.GetInt32(c4d.BFM_DRAG_FINISHED))
      result = self.DragEvent(msg, data['type'], data['object'], dropped)
      if dropped:
        result = True
      return result
    return super(ExtendedUserArea, self).Message(msg, result)


class IconView(ExtendedUserArea):
  ''' Simple User Area to present an icon. If the icon is clicked, it
  will send a `c4d.gui.GeDialog.Command()` event with the ID of the
  user area. '''

  AlignLeft = 'left'
  AlignRight = 'right'
  AlignTop = 'top'
  AlignBottom = 'bottom'
  AlignCenter = 'center'

  def __init__(self, icon, alignh=AlignCenter, alignv=AlignCenter,
      width=None, height=None, bgcol=None, cursor=None):
    super(IconView, self).__init__()
    if isinstance(icon, int):
      icon = c4d.gui.GetIcon(icon)
    elif isinstance(icon, c4d.bitmaps.BaseBitmap):
      w, h = icon.GetSize()
      icon = {'bmp': icon, 'x': 0, 'y': 0, 'w': w, 'h': h}
    elif not (icon is None or isinstance(icon, dict)):
      raise TypeError('expected int, BaseBitmap or dict', type(icon))

    self.icon = icon
    self.alignh = alignh
    self.alignv = alignv
    self.width = width
    self.height = height
    self.cursor = cursor
    self.bgcol = bgcol
    self.pressed = False
    self.double_buffered = True
    self.on_click = None

  def get_icon(self):
    return self.icon

  def _get_icon_dict(self):
    bmp = self.get_icon()
    if isinstance(bmp, c4d.bitmaps.BaseBitmap):
      bmp = {'bmp': bmp, 'x': 0, 'y': 0, 'w': bmp.GetBw(), 'h': bmp.GetBh()}
    elif not isinstance(bmp, dict) and not bmp is None:
      message = '{0}.get_banner_image() must return BaseBitmap or dict'
      warnings.warn(message.format(type(self).__name__), RuntimeWarning)
    return bmp

  # ExtendedUserArea

  def MouseEvent(self, msg, channel):
    if channel == c4d.BFM_INPUT_MOUSELEFT:
      rect = Rect(0, 0, self.GetWidth(), self.GetHeight())
      mouse = self.GetMouseLocal(msg)
      framerate = 1.0 / 15
      for mouse in self.GenerateMouseDrag(msg):
        self.pressed = mouse in rect
        self.Redraw()
        time.sleep(framerate)
      if self.pressed:
        if self.on_click:
          try:
            self.on_click()
          except Exception as exc:
            traceback.print_exc()
        self.SendAction()
      self.pressed = False
      self.Redraw()
      return True
    return False

  # c4d.gui.GeUserArea

  def DrawMsg(self, x1, y1, x2, y2, msg):
    if self.double_buffered:
      self.OffScreenOn()

    if self.bgcol:
      bgcol = self.bgcol
    elif self.pressed:
      bgcol = c4d.COLOR_BGFOCUS
    else:
      bgcol = c4d.COLOR_BG

    self.DrawSetPen(bgcol)
    self.DrawRectangle(x1, y1, x2 - 1, y2 - 1)
    icon = self._get_icon_dict()

    if icon:
      bmp, bx, by, bw, bh = (icon[n] for n in 'bmp x y w h'.split())
      dw, dh = self.GetMinSize()
      width, height = self.GetWidth(), self.GetHeight()

      if self.alignh == self.AlignRight:
        xpos = width - dw
      elif self.alignh == self.AlignCenter:
        xpos = (width - dw) / 2
      elif self.alignh == self.AlignLeft or True:
        xpos = 0

      if self.alignv == self.AlignBottom:
        ypos = height - dh
      elif self.alignv == self.AlignCenter:
        ypos = (height - dh) / 2
      elif selg.alignv == self.AlignTop or True:
        ypos = 0

      flags = c4d.BMP_ALLOWALPHA
      self.DrawBitmap(bmp, xpos, ypos, dw, dh, bx, by, bw, bh, flags)

    if self.pressed:
      self.DrawBorder(
        c4d.BORDER_THIN_IN, 0, 0,
        self.GetWidth() - 1, self.GetHeight() - 1)

  def GetMinSize(self):
    icon = self._get_icon_dict()
    if not icon:
      return (0, 0)
    else:
      bw, bh = icon['w'], icon['h']
      width, height = bw, bh
      if self.width is None:
        if self.height is not None:
          width = (self.height / float(bh)) * bw
      else:
        width = self.width
      if self.height is None:
        if self.width is not None:
          height = (self.width / float(bw)) * bh
      else:
        height = self.height
      return (int(width), int(height))


  def Message(self, msg, result):
    if self.cursor is not None and msg.GetId() == c4d.BFM_GETCURSORINFO:
      result.SetId(c4d.BFM_GETCURSORINFO)
      result.SetLong(c4d.RESULT_CURSOR, self.cursor)
      return True
    return super(IconView, self).Message(msg, result)



def handle_file_select(dialog, param, type=c4d.FILESELECTTYPE_ANYTHING,
  title='', flags=c4d.FILESELECT_LOAD, force_suffix=''):
  ''' Opens a file selection dialog for which the result will be filled
  into the parameter in the *dialog* identified with *paramid*. The
  Cinema 4D filename widget is a little buggy, and using this function
  is convenient if your dialog uses a string and button widget instead.

  :param dialog: :class:`c4d.gui.GeDialog`
  :param param: :class:`int` -- The id of the string widget.
  :param type: :class:`int` -- Passed to `c4d.storage.LoadDialog`
  :param title: :class:`str` -- See :func:`c4d.storage.LoadDialog`
  :param flags: :class:`int` -- See :func:`c4d.storage.LoadDialog`
  :param force_suffix: :class:`str` -- See :func:`c4d.storage.LoadDialog`
  :return: True if the file selection was handled and the parameter
    set, False if not.
  '''

  def_path = dialog.GetString(param)
  filename = c4d.storage.LoadDialog(type, title, flags, force_suffix, def_path)
  if filename:
    dialog.SetString(param, filename)
    return True
  return False

