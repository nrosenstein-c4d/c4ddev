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

def calc_bitmap_size(inw, inh, width=None, height=None, fill=False):
  """
  Calulcates the size of a bitmap that is scaled uniformly to match the
  specified *width* or *height*. If both *widht* and *height* are specified,
  the size is scaled among the larger axis if *fill* is #True, otherwise it
  will be scaled along the shorter axis.
  """

  if width is not None and height is not None:
    if (fill and inw > inh) or (not fill and inw <= inh):
      height = None  # calculate based on width
    else:
      width = None  # calculate based on height

  if inw <= 0 or inh <= 0:
    return 0, 0

  if width is not None:
    assert height is None
    result = width, width * (float(inh) / inw)
  elif height is not None:
    result = height * (float(inw) / inh), height
  else:
    result = (inh, inw)
  return result
