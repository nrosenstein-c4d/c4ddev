# -*- coding: utf8; -*-
#
# Copyright (C) 2015 Niklas Rosenstein
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
import copy


class UserDataManager(object):
  ''' This class manages userdata-value retrieval and storing.
  It accepts a dictionary associating the attribute-name and
  the userdata's sub-id on initialization and the c4d.BaseList2D
  object to use for retrival and storing.

  The values can optionally be cached to improve value retrieval.

  .. code-block:: python

    from c4dtools.misc.userdata import UserDataManager as UDSG
    data = UDSG({
      'count': 1,
      'link': 2,
    }, op)
    print data.count
    print data.link
    # Equal to
    print op[c4d.ID_USERDATA, 1]
    print op[c4d.ID_USERDATA, 2]
  '''

  __slots__ = '_fields _op _cache _do_caching'.split()

  def __init__(self, fields, op, do_caching=True):
    self._fields = copy.copy(fields)
    self._op = op
    self._cache = {}
    self._do_caching = do_caching

  def __getattr__(self, name):
    if name not in self._fields:
      raise AttributeError('no userdata-field %r defined.' % name)
    if self._do_caching and name in self._cache:
      return self._cache[name]
    value = self._op[c4d.ID_USERDATA, self._fields[name]]
    if self._do_caching:
      self._cache[name] = value
    return value

  def __setattr__(self, name, value):
    if name in self.__slots__:
      super(UserDataManager, self).__setattr__(name, value)
      return
    elif name not in self._fields:
      raise AttributeError('no userdata-field %r defined.' % name)

    self._op[c4d.ID_USERDATA, self._fields[name]] = value
    if self._do_caching:
      getattr(self, name)

  def clear_cache(self):
    ''' Clear the cached values. Call this in case the host object's
    parameters have changed by not using the instance of this class.
    '''

    self._cache = {}


exports = UserDataManager
