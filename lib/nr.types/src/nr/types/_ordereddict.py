# The MIT License (MIT)
#
# Copyright (c) 2018 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class OrderedDict(object):
  """
  This class implements a dictionary that can treat non-hashable
  datatypes as keys. It is implemented as a list of key/value pairs,
  thus it is very slow compared to a traditional hash-based dictionary.

  Access times are:

  ==== ======= =====
  Best Average Worst
  ==== ======= =====
  O(1) O(n)    O(n)
  ==== ======= =====
  """

  def __init__(self, iterable=None):
    super(OrderedDict, self).__init__()
    if isinstance(iterable, OrderedDict):
      self.__items = iterable.__items[:]
    elif iterable is not None:
      iterable = dict(iterable)
      self.__items = iterable.items()
    else:
      self.__items = []

  __hash__ = None

  def __contains__(self, key):
    for item in self.__items:
      if item[0] == key:
        return True
    return False

  def __eq__(self, other):
    if other is self:
      return True
    return other == self.asdict()

  def __ne__(self, other):
    return not self == other

  def __len__(self):
    return len(self.__items)

  def __str__(self):
    items = ('{0!r}: {1!r}'.format(k, v) for k, v in self.__items)
    return '{' + ', '.join(items) + '}'

  __repr__ = __str__

  def __iter__(self):
    for item in self.__items:
      yield item[0]

  def __getitem__(self, key):
    for item in self.__items:
      if item[0] == key:
        return item[1]
    raise KeyError(key)

  def __setitem__(self, key, value):
    for item in self.__items:
      if item[0] == key:
        item[1] = value
        return
    self.__items.append([key, value])

  def __delitem__(self, key):
    for index, item in enumerate(self.__items):
      if item[0] == key:
        break
    else:
      raise KeyError(key)

    del self.__items[index]

  def iterkeys(self):
    for item in self.__items:
      yield item[0]

  def itervalues(self):
    for item in self.__items:
      yield item[1]

  def iteritems(self):
    for item in self.__items:
      yield (item[0], item[1])

  def keys(self):
    return list(self.iterkeys())

  def values(self):
    return list(self.itervalues())

  def items(self):
    return list(self.iteritems())

  def get(self, key, default=None):
    try:
      return self[key]
    except KeyError:
      return default

  def pop(self, key, default=NotImplementedError):
    for item in self.__items:
      if item[0] == key:
        break
    else:
      if default is NotImplementedError:
        raise KeyError(key)
      return default

    return key[1]

  def popitem(self, last=True):
    if last:
      return tuple(self.__items.pop())
    else:
      return tuple(self.__items.pop(0))

  def setdefault(self, key, value=None):
    for item in self.__items:
      if item[0] == key:
        return item[1]
    self.__items.append([key, value])
    return value

  def update(self, __data__=None, **kwargs):
    if __data__ is not None:
      data = dict(data)
      for key, value in data.iteritems():
        self[key] = value
    for key, value in kwargs.iteritems():
      self[key] = value

  def clear(self):
    self.__items[:] = []

  def copy(self):
    return OrderedDict(self)

  has_key = __contains__

  def update(self, mapping):
    for key, value in mapping.iteritems():
      self[key] = value

  def sort(self, cmp=None, key=None, reverse=False):
    if key is None:
      key = lambda x: x[0]
    self.__items.sort(key=key)
