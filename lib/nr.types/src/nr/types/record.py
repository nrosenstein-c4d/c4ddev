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

class Record(object):
  """
  This class can be considered a new base for all classes that implement
  the `__slots__` interface. It provides convenient methods to treat the
  class instances like mutable versions of #:collections.namedtuple.

  # Example
  ```python
  class MyRecord(Record):
    __slots__ = 'foo bar ham egg'.split()
    __defaults__ = {'egg': 'yummy'}
  # or
  MyRecord = Record.new('MyRecord', 'foo bar ham', egg='yummy')

  data = MyRecord('the-foo', 42, ham="spam")
  assert data.egg = 'yummy'
  ```
  """

  def __init__(self, *args, **kwargs):
    defaults = getattr(self, '__defaults__', None) or {}
    if len(args) > len(self.__slots__):
      msg = '__init__() takes {0} positional arguments but {1} were given'
      raise TypeError(msg.format(len(self.__slots__), len(args)))
    for key, arg in zip(self.__slots__, args):
      if key in kwargs:
        msg = 'multiple values for argument {0!r}'.format(key)
        raise TypeError(msg)
      kwargs[key] = arg
    for key, arg in kwargs.items():
      setattr(self, key, arg)
    for key in self.__slots__:
      if key not in kwargs:
        if key in defaults:
          setattr(self, key, defaults[key])
        else:
          raise TypeError('missing argument {0!r}'.format(key))
      else:
        kwargs.pop(key)
    if kwargs:
      msg = '__init__() got an unexpected keyword argument {0!r}'
      raise TypeError(msg.format(next(iter(kwargs))))

  def __repr__(self):
    parts = ['{0}={1!r}'.format(k, v) for k, v in self.items()]
    return '{0}('.format(type(self).__name__) + ', '.join(parts) + ')'

  def __iter__(self):
    """
    Iterate over the values of the record in order.
    """

    for key in self.__slots__:
      yield getattr(self, key)

  def __len__(self):
    """
    Returns the number of slots in the record.
    """

    return len(self.__slots__)

  def __getitem__(self, index_or_key):
    """
    Read the value of a slot by its index or name.

    :param index_or_key:
    :raise TypeError:
    :raise IndexError:
    :raise KeyError:
    """

    if isinstance(index_or_key, int):
      return getattr(self, self.__slots__[index_or_key])
    elif isinstance(index_or_key, str):
      if index_or_key not in self.__slots__:
        raise KeyError(index_or_key)
      return getattr(self, index_or_key)
    else:
      raise TypeError('expected int or str')

  def __setitem__(self, index_or_key, value):
    """
    Set the value of a slot by its index or name.

    :param index_or_key:
    :raise TypeError:
    :raise IndexError:
    :raise KeyError:
    """

    if isinstance(index_or_key, int):
      setattr(self, self.__slots__[index_or_key], value)
    elif isinstance(index_or_key, str):
      if index_or_key not in self.__slots__:
        raise KeyError(index_or_key)
      setattr(self, index_or_key, value)
    else:
      raise TypeError('expected int or str')

  def __eq__(self, other):
    for key in self.__slots__:
      try:
        other_value = getattr(other, key)
      except AttributeError:
        return False
      if getattr(self, key) != other_value:
        return False
    return True

  def __setattr__(self, name, value):
    if name in self.__slots__:
      setter = getattr(self, '_set_' + name, None)
      if callable(setter):
        setter(value)
        return
    super(Record, self).__setattr__(name, value)

  def __getattribute__(self, name):
    if name != '__slots__' and name in self.__slots__:
      getter = getattr(self, '_get_' + name, None)
      if callable(getter):
        return getter()
    return super(Record, self).__getattribute__(name)

  def items(self):
    """
    Iterator for the key-value pairs of the record.
    """

    for key in self.__slots__:
      yield key, getattr(self, key)

  def keys(self):
    """
    Iterator for the member names of the record.
    """

    return iter(self.__slots__)

  def values(self):
    """
    Iterator for the values of the object, like :meth:`__iter__`.
    """

    for key in self.__slots__:
      yield getattr(self, key)

  def _asdict(self):
    return dict((k, getattr(self, k)) for k in self.__slots__)

  @classmethod
  def new(cls, __name, __fields, **defaults):
    '''
    Creates a new class that can represent a record with the
    specified *fields*. This is equal to a mutable namedtuple.
    The returned class also supports keyword arguments in its
    constructor.

    :param __name: The name of the Record.
    :param __fields: A string or list of field names.
    :param defaults: Default values for fields. The defaults
      may list field names that haven't been listed in *fields*.
    '''

    name = __name
    fields = __fields
    fieldset = set(fields)

    if isinstance(fields, str):
      if ',' in fields:
        fields = fields.split(',')
      else:
        fields = fields.split()
    else:
      fields = list(fields)

    for key in defaults.keys():
      if key not in fields:
        fields.append(key)

    class _record(cls):
      __slots__ = fields
      __defaults__ = defaults
    _record.__name__ = name
    return _record
