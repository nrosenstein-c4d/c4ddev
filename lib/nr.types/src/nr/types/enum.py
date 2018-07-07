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
"""
This module implements a simple framework for creating C-like enumerations in
Python using classes. Simply inherit from the #Enumeration class.

```python
>>> class Color(enum.Enumeration):
...   red = 0
...   green = 1
...   blue = 2
>>> print Color.red
<Color: red>
>>> print Color('green')
<Color: green>
>>> print Color(2)
<Color: blue>
>>> print Color('red') is Color.red
True
>>> print Color.blue.name
blue
>>> Color(343)
Traceback (most recent call last):
  File "test.py", line 10, in <module>
  Color(343)
  File "C:\\repositories\\py-nr.utils\\nr\\utils\\enum.py", line 159, in __new__
  raise NoSuchEnumerationValue(cls.__name__, value)
nr.utils.enum.NoSuchEnumerationValue: ('Color', 343)
```

If you want to disable that an invalid enumeration value will raise an error,
a `__fallback__` value can be specified on class-level.

```python
>>> class Color(enum.Enumeration):
...   red = 0
...   green = 1
...   blue = 2
...   __fallback__ = -1
>>> print Color(42)
<Color -invalid->
>>> print Color(7).value
-1
>>> print Color(16).name
-invalid-
```

You can also iterate over an enumeration class. Note that the order of the
items yielded is value-sorted and the order of declaration does not play any
role.

```python
>>> class Color(enum.Enumeration):
...   red = 0
...   green = 1
...   blue = 2
...   __fallback__ = -1
>>> for color in Color:
...   print color
<Color: red>
<Color: green>
<Color: blue>
```

You can add data or actual methods to an enumeration class by wrapping it with
the #Data class.

```python
class Color(enum.Enumeration):
  red = 0
  green = 1
  blue = 2

  @enum.Data
  @property
  def astuple(self):
    if self == Color.red:
      return (1, 0, 0)
    elif self == Color.green:
      return (0, 1, 0)
    elif self == Color.blue:
      return (0, 0, 1)
    else:
      assert False

print Color.red.astuple
# (1, 0, 0)
```
"""

import ctypes
import six
import sys


class NoSuchEnumerationValue(ValueError):
  r""" Raised when an Enumeration object was attempted to be
  created from an integer value but there was no enumeration
  object for this value.

  Note that you can specify ``__fallback_value__`` on an
  Enumeration class to not let it raise an exception. """

  pass


class Data(object):
  """
  Small class that can be used to specify data on an enumeration that should
  not be converted and interpreted as an enumeration value.

  ```python
  class Color(enum.Enumeration):
    red = 0
    green = 1
    blue = 2

    @enum.Data
    @property
    def astuple(self):
      if self == Color.red:
        return (1, 0, 0)
      elif self == Color.green:
        return (0, 1, 0)
      elif self == Color.blue:
        return (0, 0, 1)
      else:
        assert False

  print Color.red.astuple
  # (1, 0, 0)
  ```

  This class can be subclassed to add new sugar to the already very sweet pie.
  """

  def __init__(self, value):
    super(Data, self).__init__()
    self.value = value

  def unpack(self):
    return self.value


class _EnumerationMeta(type):
  """
  This is the meta class for the #Enumeration base class which handles the
  automatic conversion of integer values to instances of the #Enumeration
  class. There are no other types allowed other than int or #Data which
  will be unpacked on the Enumeration class.

  If a `__fallback__` was defined on class-level as an integer, the
  #Enumeration constructor will not raise a #NoSuchEnumerationValue exception
  if the passed value did not match the enumeration values, but instead return
  that fallback value.

  This fallback is not taken into account when attempting to create a new
  #Enumeration object by a string.
  """

  _values = None
  __fallback__ = None

  def __new__(cls, name, bases, data):

    # Unpack all Data objects and create a dictionary of
    # values that will be converted to instances of the
    # enumeration class later.
    enum_values = {}
    collections = {}
    for key, value in data.items():
      # Unpack Data objects into the class.
      if isinstance(value, Data):
        data[key] = value.unpack()

      # Integers will be enumeration values.
      elif isinstance(value, int):
        enum_values[key] = value

      # Lists and tuples will be converted to
      # collections of the Enumeration values.
      elif isinstance(value, (list, tuple)):
        collections[key] = value

      # We don't accept anything else.
      elif not key.startswith('_'):
        message = 'Enumeration must consist of ints or Data objects ' \
              'only, got %s for \'%s\''
        raise TypeError(message % (value.__class__.__name__, key))

    # Create the new class object and give it the dictionary
    # that will map the integral values to the instances.
    class_ = type.__new__(cls, name, bases, data)
    class_._values = {}

    # Iterate over all entries in the data entries and
    # convert integral values to instances of the enumeration
    # class.
    for key, value in six.iteritems(enum_values):

      # Create the new object. We must not use the classes'
      # __new__() method as it resolves the object from the
      # existing values.
      obj = object.__new__(class_)
      object.__init__(obj)

      obj.value = value
      obj.name = key

      if key == '__fallback__':
        obj.name = '-invalid-'
      else:
        class_._values[value] = obj
      setattr(class_, key, obj)


    # Convert the collections.
    for key, value in six.iteritems(collections):
      value = type(value)(class_(v) for v in value)
      setattr(class_, key, value)

    return class_

  def __iter__(self):
    " Iterator over value-sorted enumeration values. "

    return iter(self.__values__())

  def __values__(self):
    return sorted(six.itervalues(self._values), key=lambda x: x.value)

  def __getattr__(self, name):
    if self.__bases__ == (object,) and name == 'Data':
      return Data
    raise AttributeError(name)


class Enumeration(six.with_metaclass(_EnumerationMeta)):
  """
  This is the base class for listing enumerations. All components of the class
  that are integers will be automatically converted to instances of the
  #Enumeration class. Creating new instances of the class will only work if the
  value is an existing enumeration value.

  The hash of an enumeration value is its name, but indexing a container
  corresponds to its value.
  """

  def __new__(cls, value, _allow_fallback=True):
    """
    Creates a new instance of the Enumeration. *value* must be the integral
    number of one of the existing enumerations. #NoSuchEnumerationValue is
    raised in any other case.

    If a fallback was defined, it is returned only if *value* is an integer,
    not if it is a string.
    """

    # Try to find the actual instance of the Enumeration class
    # for the integer value and return it if it is available.
    if isinstance(value, six.integer_types):
      try:
        value = cls._values[value]
      except KeyError:

        # If a fallback value was specified, use it
        # instead of raising an exception.
        if _allow_fallback and cls.__fallback__ is not None:
          return cls.__fallback__

        raise NoSuchEnumerationValue(cls.__name__, value)

    # Or by name?
    elif isinstance(value, six.string_types):
      try:
        new_value = getattr(cls, value)
        if type(new_value) != cls:
          raise AttributeError
      except AttributeError:
        raise NoSuchEnumerationValue(cls.__name__, value)

      value = new_value

    # At this point, value must be an object of the Enumeration
    # class, otherwise an invalid value was passed.
    if type(value) == cls:
      return value

    raise TypeError('value must be %s or int, got %s' % (cls.__name__, type(value).__name__))

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, other):
    if type(other) == self.__class__:
      return other.value == self.value
    elif isinstance(other, six.string_types):
      return other == self.name
    else:
      return self.value == other

  def __ne__(self, other):
    return not (self == other)

  def __int__(self):
    return self.value

  def __str__(self):
    class_name = self.__class__.__name__
    return '<%s: %s>' % (class_name, self.name)

  def __repr__(self):
    class_name = self.__class__.__name__
    return '<%s: [%d] %s>' % (class_name, self.value, self.name)

  def __index__(self):
    return self.value

  def __nonzero__(self):
    return False
  __bool__ = __nonzero__ # Py3

  # ctypes support

  @property
  def _as_parameter_(self):
    return ctypes.c_int(self.value)

  @Data
  @classmethod
  def from_param(cls, obj):
    if isinstance(obj, (int,) + six.string_types):
      obj = cls(obj)
    if type(obj) != cls:
      c1 = cls.__name__
      c2 = obj.__class__.__name__
      raise TypeError('can not create %s from %s' % (c1, c2))

    return ctypes.c_int(obj.value)
