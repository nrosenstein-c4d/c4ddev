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

import bs4
import collections
import c4d
import re

Margin = collections.namedtuple('Margin', 'left top right bottom')


class FlowtextView(c4d.gui.GeUserArea):
  """
  A GeUserArea that can render flow-text. Unlike Cinema 4D's static text
  widgets, it adds line-breaks and supports a very simple form of HTML markup
  (supporting h1, b, i, code and br tags).

  Note that using the #FlowtextView requires the `bs4` module installed.
  """

  # TODO: Maybe switch to using a GeClipMap? It supports italic fonts.

  class _Word(object):
    __slots__ = ('t', 'f', 'x', 'y', 'w', 'h')

    def __init__(self, **kwargs):
      for key, value in kwargs.iteritems():
        setattr(self, key, value)

  def __init__(self, markup, min_width=100, ralign=False, margin=(2, 1, 2, 1),
      bgcol=c4d.COLOR_BG, fgcol=c4d.COLOR_TEXT):
    c4d.gui.GeUserArea.__init__(self)
    self._tree = bs4.BeautifulSoup(markup, "html.parser")
    self._words = [[]]
    for node in self._tree.contents:
      if node.name == u'h1':
        font = c4d.FONT_BOLD
      elif node.name == u'b':
        font = c4d.FONT_BOLD
      elif node.name == u'i':
        font = c4d.FONT_DEFAULT # TODO: Italic font?
      elif node.name == u'code':
        font = c4d.FONT_MONOSPACED
      elif node.name == u'br':
        self._words.append([])
        continue
      else:
        font = c4d.FONT_DEFAULT
      for word in re.split('\s+', node.string):
        self._words[-1].append(self._Word(t=word, f=font, x=0, y=0, w=0, h=0))
      if node.name == u'h1':
        self._words.append([])
    if not self._words[-1]:
      self._words.pop()
    self._min_width = min_width
    self._ralign = ralign
    self._layout = None
    self._last_width = None
    self._last_minsize = None
    self._bgcol = bgcol
    self._fgcol = fgcol
    self._margin = Margin(*margin)

  def GetMinSize(self):
    width = self.GetWidth()
    if width == 0:
      # Catching some misfortunate events that would cause flickering.
      return (0, 0)
    if width == self._last_width:
      # Catch when GetMinSize() is called multiple times while the area's
      # size has not changed.
      return self._last_minsize
    self._last_width = width

    if width < self._min_width:
      width = self._min_width

    xoff, yoff = self._margin.left, self._margin.top
    font = None
    self._layout = [[]]
    for line in self._words:
      for word in line:
        if font != word.f:
          font = word.f
          self.DrawSetFont(word.f)
        word.x = xoff
        word.y = yoff
        word.w = self.DrawGetTextWidth(word.t)
        word.h = self.DrawGetFontHeight()
        if word.x + word.w > width:
          word.y += word.h
          word.x = self._margin.left
          self._layout.append([])
        yoff = word.y
        xoff = word.x + word.w + self.DrawGetTextWidth(' ')
        self._layout[-1].append(word)
      xoff = self._margin.left
      yoff += self.DrawGetFontHeight()
      self._layout.append([])

    if self._ralign:
      for line in self._layout:
        if not line: continue
        right_border = line[-1].x + line[-1].w
        space_left = (width - right_border)
        for i, word in enumerate(line):
          word.x += space_left

    self._last_minsize = self._min_width + self._margin.right, yoff + self._margin.bottom
    return self._last_minsize

  def Sized(self, w, h):
    self.LayoutChanged()

  def DrawMsg(self, x1, y1, x2, y2, msg):
    self.OffScreenOn()
    self.DrawSetPen(self._bgcol)
    self.DrawRectangle(x1, y1, x2, y2)
    self.DrawSetTextCol(self._fgcol, c4d.COLOR_TRANS)

    if self._layout is None:
      return

    font = None
    for line in self._layout:
      for word in line:
        if word.f != font:
          font = word.f
          self.DrawSetFont(font)
        self.DrawText(word.t, word.x, word.y)


exports = FlowtextView
