# Copyright (c) 2014  Niklas Rosenstein
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

import os
import sys
import c4d
import traceback

def image_from_file(filename):
    r""" Returns a :class:`c4d.bitmaps.BaseBitmap` from a filename
    or None if the file does not exist or could not be loaded. """

    if not os.path.isfile(filename):
        return None

    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(filename)[0] == c4d.IMAGERESULT_OK:
        return bmp

    return None

def print_traceback(exc, tb, limit=None, file=None):
    r""" Prints the traceback *tb* in an exception format. """

    if file is None:
        file = sys.stderr

    print >> sys.stderr, "Traceback (most recent call last):"
    traceback.print_tb(sys.exc_info()[2].tb_next, limit, file)
    print >> sys.stderr, '%s:' % exc.__class__.__name__, str(exc)

def get_last_traceback():
    r""" Returns the last traceback node of the current exc-info.
    This function is preferred as :data:`sys.last_traceback` is not
    always set. """

    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next

    return tb

def xor(a, b):
    return bool(a) ^ bool(b)

