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
Provides simple sumtype declarations.
"""

from six.moves import zip
from six import iteritems, with_metaclass

import re
import types
import six

__all__ = ['Constructor', 'MemberOf', 'Sumtype', 'AddIsMethods']


class Constructor(object):
  """
  Represents a constructor for a sumtype.
  """

  def __init__(self, *args):
    self.name = None
    self.type = None
    self.args = args
    self.members = {}

  def bind(self, type, name):
    obj = Constructor(*self.args)
    obj.type = type
    obj.name = name
    obj.members = self.members.copy()
    return obj

  def accept_args(self, *args):
    if self.type is None or self.name is None:
      raise RuntimeError('unbound Constructor')
    if len(args) != len(self.args):
      raise TypeError('{}.{}() expected {} arguments, got {}'.format(
        self.type.__name__, self.name, len(self.args), len(args)))
    return dict(zip(self.args, args))

  def __call__(self, *args):
    if self.type is None or self.name is None:
      raise RuntimeError('unbound Constructor')
    return self.type(self, self.accept_args(*args))


class MemberOf(object):
  """
  A decorator for functions or values that are supposed to be members of
  only a specific sumtype's constructor (or multiple constructors). Instances
  of this class will be automatically unpacked by the :class:`_TypeMeta`
  constructor and moved into the :attr:`Constructor.members` dictionary.
  """

  def __init__(self, constructors=None, value=None, name=None):
    if isinstance(constructors, Constructor):
      constructors = [constructors]
    self.constructors = constructors
    self.value = value
    self.name = name

    if name:
      for c in constructors:
        c.members[name] = value

  def __call__(self, value):
    if not self.name:
      self.name = value.__name__
    for c in self.constructors:
      c.members[self.name] = value
    return self

  def update_constructors(self, attrname):
    for constructor in self.constructors:
      constructor.members[attrname] = self.value


class _TypeMeta(type):

  def __new__(cls, name, bases, attrs):
    subtype = type.__new__(cls, name, bases, attrs)

    # Collect all new constructors.
    constructors = getattr(subtype, '__constructors__', {}).copy()
    for key, value in iteritems(vars(subtype)):
      if isinstance(value, Constructor):
        constructors[key] = value

    # Update constructors from MemberOf declarations.
    for key, value in list(iteritems(vars(subtype))):
      if isinstance(value, MemberOf):
        delattr(subtype, key)

    # Bind constructors.
    for key, value in iteritems(constructors):
      setattr(subtype, key, value.bind(subtype, key))
    subtype.__constructors__ = constructors

    # Invoke addons.
    for addin in getattr(subtype, '__addins__', []):
      addin.init_type(subtype)

    return subtype

  def __getattr__(self, name):
    if self.__bases__ == (object,) and name in __all__:
      return globals()[name]
    raise AttributeError(name)


class Sumtype(with_metaclass(_TypeMeta)):
  """
  Base class for sumtypes. You can access all members of the sumtype
  module via this type (but not through subclasses).

  ```python
  from nr.types import Sumtype

  class Result(Sumtype):
    Ok = Sumtype.Constructor()
    Error = Sumtype.Constructor('message')

  assert not hasattr(Result, 'Constructor')
  ```
  """

  __addins__ = []
  __constructors__ = {}

  def __init__(self, constructor, attrs):
    assert isinstance(constructor, Constructor), type(constructor)
    assert isinstance(attrs, dict), type(attrs)
    self.__constructor__ = constructor
    for key, value in iteritems(constructor.members):
      if isinstance(value, types.FunctionType):
        value = value.__get__(self, constructor.type)
      setattr(self, key, value)
    for key in constructor.args:
      if key not in attrs:
        raise ValueError('missing key in attrs: {!r}'.format(key))
    for key, value in iteritems(attrs):
      if key not in constructor.args:
        raise ValueError('unexpected key in attrs: {!r}'.format(key))
      setattr(self, key, value)

  def __getitem__(self, index):
    if hasattr(index, '__index__'):
      index = index.__index__()
    if isinstance(index, int):
      return getattr(self, self.__constructor__.args[index])
    elif isinstance(index, slice):
      return tuple(getattr(self, k) for k in self.__constructor__.args[index])
    else:
      raise TypeError('indices must be integers or slices, not str')

  def __iter__(self):
    for k in self.__constructor__.args:
      yield getattr(self, k)

  def __len__(self):
    return len(self.__constructor__.args)

  def __repr__(self):
    return '{}.{}({})'.format(type(self).__name__, self.__constructor__.name,
      ', '.join('{}={!r}'.format(k, getattr(self, k)) for k in self.__constructor__.args))


class AddIsMethods(object):

  @staticmethod
  def init_type(type):
    def create_is_check(func_name, constructor_name):
      def check(self):
        constructor = getattr(self, constructor_name)
        return self.__constructor__ == constructor
      check.__name__ = name
      check.__qualname__ = name
      return check
    for name in type.__constructors__.keys():
      func_name = 'is_' + '_'.join(re.findall('[A-Z]+[^A-Z]*', name)).lower()
      setattr(type, func_name, create_is_check(func_name, name))


Sumtype.__addins__.append(AddIsMethods)
