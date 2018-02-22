# Copyright (C) 2016  Niklas Rosenstein
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
"""
This file is an adaption for the ``localimport`` module which is optimized
to be used in Python Expressions (Tags, Generators, XPresso Nodes) inside
of Cinema 4D.

.. code:: python

  import c4d
  from c4ddev.scripting.localimport import localimport

  with localimport(doc):
    import twitter

  def main():
    # ...
"""

import os
import localimport as _localimport

importer_cache = {}

def localimport(doc):
  """
  This function creates an object of the real ``localimport`` module for
  the specified :class:`c4d.BaseDocument` object and returns it. We use
  this technique to avoid re-importing modules evertime you recompile a
  Python Expression in Cinema 4D.
  """

  path = doc.GetDocumentPath()
  if not path or not os.path.isdir(path):
    raise ValueError('document directory is invalid: {0!r}'.format(doc))

  importer = importer_cache.get(path)
  if not importer:
    importer = _localimport.localimport(['.', './python'], path)
    importer_cache[path] = importer

  return importer
