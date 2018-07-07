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

__all__ = ['OrderedDict', 'ObjectAsMap', 'MapAsObject', 'ChainMap', 'HashDict']

import six
from . import generic

try:
  from collections import OrderedDict
except ImportError:
  from ._ordereddict import OrderedDict

if six.PY2:
  _can_iteritems = lambda x: hasattr(x, 'iteritems')
  _can_iterkeys = lambda x: hasattr(x, 'keys')
else:
  _can_iteritems = lambda x: hasattr(x, 'items')
  _can_iterkeys = lambda x: hasattr(x, 'keys')


class ObjectAsMap(object):
  """
  This class wraps an object and exposes its members as mapping.
  """

  def __new__(cls, obj):
    if isinstance(obj, MapAsObject):
      return obj._MapAsObject__mapping
    return super(ObjectAsMap, cls).__new__(cls)

  def __init__(self, obj):
    self.__obj = obj

  def __repr__(self):
    return 'ObjectAsMap({!r})'.format(self.__obj)

  def __iter__(self):
    return self.keys()

  def __len__(self):
    return len(dir(self.__obj))

  def __contains__(self, key):
    return hasattr(self.__obj, key)

  def __getitem__(self, key):
    try:
      return getattr(self.__obj, key)
    except AttributeError:
      raise KeyError(key)

  def __setitem__(self, key, value):
    setattr(self.__obj, key, value)

  def __delitem__(self, key):
    delattr(self.__obj, key)

  def keys(self):
    return iter(dir(self.__obj))

  def values(self):
    return (getattr(self.__obj, k) for k in dir(self.__obj))

  def items(self):
    return ((k, getattr(self.__obj, k)) for k in dir(self.__obj))

  def get(self, key, default=None):
    return getattr(self.__obj, key, default)

  def setdefault(self, key, value):
    try:
      return getattr(self.__obj, key)
    except AttributeError:
      setattr(self.__obj, key, value)
      return value


class MapAsObject(object):
  """
  This class wraps a dictionary and exposes its values as members.
  """

  def __new__(cls, mapping, name=None):
    if isinstance(mapping, ObjectAsMap):
      return mapping._ObjectAsMap__obj
    return super(MapAsObject, cls).__new__(cls)

  def __init__(self, mapping, name=None):
    self.__mapping = mapping
    self.__name = name

  def __getattribute__(self, key):
    if key.startswith('_MapAsObject__'):
      return super(MapAsObject, self).__getattribute__(key)
    try:
      return self.__mapping[key]
    except KeyError:
      raise AttributeError(key)

  def __setattr__(self, key, value):
    if key.startswith('_MapAsObject__'):
      super(MapAsObject, self).__setattr__(key, value)
    else:
      self.__mapping[key] = value

  def __delattr__(self, key):
    if key.startswith('_MapAsObject__'):
      super(MapAsObject, self).__delattr__(key)
    else:
      del self.__mapping[key]

  def __dir__(self):
    return sorted(self.__mapping.keys())

  def __repr__(self):
    if self.__name:
      return '<MapAsObject name={!r}>'.format(self.__name)
    else:
      return '<MapAsObject {!r}>'.format(self.__mapping)


class ChainMap(object):
  """
  A dictionary that wraps a list of dictionaries. The dictionaries passed
  into the #ChainMap will not be mutated. Setting and deleting values will
  happen on the first dictionary passed.
  """

  def __init__(self, *dicts):
    if not dicts:
      raise ValueError('need at least one argument')
    self._major = dicts[0]
    self._dicts = list(dicts)
    self._deleted = set()
    self._in_repr = False

  def __contains__(self, key):
    if key not in self._deleted:
      for d in self._dicts:
        if key in d:
          return True
    return False

  def __getitem__(self, key):
    if key not in self._deleted:
      for d in self._dicts:
        try: return d[key]
        except KeyError: pass
    raise KeyError(key)

  def __setitem__(self, key, value):
    self._major[key] = value
    self._deleted.discard(key)

  def __delitem__(self, key):
    if key not in self:
      raise KeyError(key)
    self._major.pop(key, None)
    self._deleted.add(key)

  def __iter__(self):
    return six.iterkeys(self)

  def __len__(self):
    return sum(1 for x in self.keys())

  def __repr__(self):
    if self._in_repr:
      return 'ChainMap(...)'
    else:
      self._in_repr = True
      try:
        return 'ChainMap({})'.format(dict(six.iteritems(self)))
      finally:
        self._in_repr = False

  def __eq__(self, other):
    return dict(self.items()) == other

  def __ne__(self, other):
    return not (self == other)

  def pop(self, key, default=NotImplemented):
    if key not in self:
      if default is NotImplemented:
        raise KeyError(key)
      return default
    self._major.pop(key, None)
    self._deleted.add(key)

  def popitem(self):
    if self._major:
      key, value = self._major.popitem()
      self._deleted.add(key)
      return key, value
    for d in self._dicts:
      for key in six.iterkeys(d):
        if key not in self._deleted:
          self._deleted.add(key)
          return key, d[key]
    raise KeyError('popitem(): dictionary is empty')

  def clear(self):
    self._major.clear()
    self._deleted.update(six.iterkeys(self))

  def copy(self):
    return type(self)(*self._dicts[1:])

  def setdefault(self, key, value=None):
    try:
      return self[key]
    except KeyError:
      self[key] = value
      return value

  def update(self, E, *F):
    if _can_iteritems(E):
      for k, v in six.iteritems(E):
        self[k] = v
    elif _can_iterkeys(E):
      for k in six.iterkeys(E):
        self[k] = E[k]
    elif hasattr(E, 'items'):
      E = E.items()
    for k, v in E:
      self[k] = v
    for Fv in F:
      for k, v in six.iteritems(Fv):
        self[k] = v

  def keys(self):
    seen = set()
    for d in self._dicts:
      for key in six.iterkeys(d):
        if key not in seen and key not in self._deleted:
          yield key
          seen.add(key)

  def values(self):
    seen = set()
    for d in self._dicts:
      for key, value in six.iteritems(d):
        if key not in seen and key not in self._deleted:
          yield value
          seen.add(key)

  def items(self):
    seen = set()
    for d in self._dicts:
      for key, value in six.iteritems(d):
        if key not in seen and key not in self._deleted:
          yield key, value
          seen.add(key)

  if six.PY2:
    iterkeys = keys
    keys = lambda self: list(self.iterkeys())
    itervalues = values
    values = lambda self: list(self.itervalues())
    iteritems = items
    items = lambda self: list(self.iteritems())


class HashDict(generic.Generic['key_hash']):
  """
  This dictionary type can be specialized by specifying a hash function,
  allowing it to be used even with unhashable types as keys.

  Example:

  ```python
  # Specialization through subclassing:
  class MyDict(HashDict):
    def key_hash(self, key):
      return ...

  # Explicit type specialization:
  def my_key_hash(x):
    return ...
  MyDict = HashDict[my_key_hash]
  ```
  """

  class KeyWrapper(object):
    def __init__(self, key, hash_func):
      self.key = key
      self.hash_func = hash_func
    def __repr__(self):
      return repr(self.key)
    def __hash__(self):
      return self.hash_func(self.key)
    def __eq__(self, other):
      return self.key == other.key
    def __ne__(self, other):
      return self.key != other.key

  def __init__(self):
    generic.assert_initialized(self)
    self._dict = {}

  def __repr__(self):
    return repr(self._dict)

  def __getitem__(self, key):
    key = self.KeyWrapper(key, self.key_hash)
    return self._dict[key]

  def __setitem__(self, key, value):
    key = self.KeyWrapper(key, self.key_hash)
    self._dict[key] = value

  def __delitem__(self, key):
    key = self.KeyWrapper(key, self.key_hash)
    del self._dict[key]

  def __iter__(self):
    return self.iterkeys()

  def __contains__(self, key):
    return self.KeyWrapper(key, self.key_hash) in self._dict

  def items(self):
    return list(self.iteritems())

  def keys(self):
    return list(self.iterkeys())

  def values(self):
    return self._dict.values()

  def iteritems(self):
    for key, value in self._dict.iteritems():
      yield key.key, value

  def iterkeys(self):
    for key in self._dict.keys():
      yield key.key

  def itervalues(self):
    return self._dict.itervalues()

  def get(self, key, *args):
    key = self.KeyWrapper(key, self.key_hash)
    return self._dict.get(key, *args)

  def setdefault(self, key, value):
    key = self.KeyWrapper(key, self.key_hash)
    return self._dict.setdefault(key, value)
