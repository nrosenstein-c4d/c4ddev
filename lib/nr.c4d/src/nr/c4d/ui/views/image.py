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
from ..utils.calculate import calc_bitmap_size


class ImageView(c4d.gui.GeUserArea):
  """
  A GeUserArea that displays an image centered vertically/horizontally.
  """

  def __init__(self, image, max_width=None, max_height=None, scale_up=False,
               fill=True, bgcolor=None):
    c4d.gui.GeUserArea.__init__(self)
    if isinstance(image, basestring):
      bmp = c4d.bitmaps.BaseBitmap()
      res = bmp.InitWith(image)
      if res[0] != c4d.IMAGERESULT_OK:
        bmp = None
      image = bmp
    self.image = image
    self.flags = c4d.BMP_ALLOWALPHA | c4d.BMP_NORMAL
    self.additional_flags = 0
    self.max_width = max_width
    self.max_height = max_height
    self.scale_up = scale_up
    self.fill = fill
    self.bgcolor = bgcolor

  def get_icon_data(self):
    icon = self.image
    if isinstance(icon, c4d.bitmaps.BaseBitmap):
      icon = {'bmp': icon, 'x': 0, 'y': 0, 'w': icon.GetBw(), 'h': icon.GetBh()}
    return icon

  def DrawMsg(self, x1, y1, x2, y2, bc):
    icon = self.get_icon_data()
    self.OffScreenOn()
    bgcolor = self.bgcolor
    if bgcolor is None:
      bgcolor = c4d.COLOR_BG if icon else c4d.COLOR_BGEDIT
    self.DrawSetPen(bgcolor)
    self.DrawRectangle(x1, y1, x2, y2)
    if not icon:
      return

    dw, dh = self.GetMinSize()
    xoff = (self.GetWidth() - dw) / 2
    yoff = (self.GetHeight() - dh) / 2
    flags = self.flags | self.additional_flags
    self.DrawBitmap(icon['bmp'], xoff, yoff, dw, dh,
                    icon['x'], icon['y'], icon['w'], icon['h'], flags)

  def GetMinSize(self):
    icon = self.get_icon_data()
    if icon:
      sw, sh = icon['w'], icon['h']
      mw, mh = self.max_width, self.max_height
      if self.scale_up:
        if not mw: mw = self.GetWidth()
        if not mh: mh = self.GetHeight()
      else:
        if not mw: mw = sw
        if not mh: mh = sh
      dw, dh = calc_bitmap_size(sw, sh, mw, mh, fill=self.fill)
      return int(dw), int(dh)
    return 10, 10
