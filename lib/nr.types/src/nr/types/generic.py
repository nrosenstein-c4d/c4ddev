# coding: utf8
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
This module provides the metaclass #GenericMeta and the subclassing helper
#Generic which can be used to create generic subclasses. Example:

```python
import nr.generic

class HashDict(nr.generic.Generic['hash_key']):

  def __init__(self):
    nr.generic.assert_initialized(self)
    self.data = {}

  def __getitem__(self, key):
    return self.data[self.hash_key(key)]

  def __setitem__(self, key, value):
    self.data[self.hash_key(key)] = value
"""

import types
from six.moves import range


class GenericMeta(type):
  """
  Metaclass that can be used for classes that need one or more datatypes
  pre-declared to function properly. The datatypes must be declared using
  the `__generic_args__` member and passed to the classes' `__getitem__()`
  operator to bind the class to these arguments.

  A generic class constructor may check it's `__generic_bind__` member to
  see if its generic arguments are bound or not.
  """

  def __init__(cls, *args, **kwargs):
    if not hasattr(cls, '__generic_args__'):
      raise TypeError('{}.__generic_args__ is not set'.format(cls.__name__))
    had_optional = False
    for index, item in enumerate(cls.__generic_args__):
      if not isinstance(item, tuple):
        item = (item,)
      arg_name = item[0]
      arg_default = item[1] if len(item) > 1 else NotImplemented
      if arg_default is NotImplemented and had_optional:
        raise ValueError('invalid {}.__generic_args__, default argument '
          'followed by non-default argument "{}"'
          .format(cls.__name__, arg_name))
      cls.__generic_args__[index] = (arg_name, arg_default)
    super(GenericMeta, cls).__init__(*args, **kwargs)
    if not hasattr(cls, '__generic_bind__'):
      cls.__generic_bind__ = None
    elif cls.__generic_bind__ is not None:
      assert len(cls.__generic_args__) == len(cls.__generic_bind__)
      for i in range(len(cls.__generic_args__)):
        value = cls.__generic_bind__[i]
        if isinstance(value, types.FunctionType):
          value = staticmethod(value)
        setattr(cls, cls.__generic_args__[i][0], value)
    else:
      collected_args = []
      missing = []
      for i, (arg_name, arg_default) in enumerate(cls.__generic_args__):
        if hasattr(cls, arg_name):
          collected_args.append(getattr(cls, arg_name))
        elif arg_default is not NotImplemented:
          collected_args.append(arg_default)
        else:
          missing.append(arg_name)
      if collected_args and missing:
        raise RuntimeError('{}: no all Generic arguments satisfied by '
          'class members (missing {})'.format(cls.__name__, ','.join(missing)))
      if collected_args:
        cls.__generic_bind__ = collected_args

  def __getitem__(cls, args):
    cls = getattr(cls, '__generic_base__', cls)
    if not isinstance(args, tuple):
      args = (args,)
    if len(args) > len(cls.__generic_args__):
      raise TypeError('{} takes at most {} generic arguments ({} given)'
        .format(cls.__name__, len(cls.__generic_args__), len(args)))
    # Find the number of required arguments.
    for index in range(len(cls.__generic_args__)):
      if cls.__generic_args__[index][1] != NotImplemented:
        break
    else:
      index = len(cls.__generic_args__)
    min_args = index
    if len(args) < min_args:
      raise TypeError('{} takes at least {} generic arguments ({} given)'
        .format(cls.__name__, min_args, len(args)))
    # Bind the generic arguments.
    bind_data = []
    for index in range(len(cls.__generic_args__)):
      arg_name, arg_default = cls.__generic_args__[index]
      if index < len(args):
        arg_value = args[index]
      else:
        assert arg_default is not NotImplemented
        arg_value = arg_default
      bind_data.append(arg_value)
    type_name = '{}[{}]'.format(cls.__name__, ', '.join(repr(x) for x in bind_data))
    data = {
      '__module__': cls.__module__,
      '__generic_bind__': bind_data,
      '__generic_base__': cls
    }
    return type(type_name, (cls,), data)


class _GenericHelperMeta(type):

  def __getitem__(self, args):
    if not isinstance(args, tuple):
      args = (args,)
    data = {'__generic_args__': list(args)}
    return GenericMeta('Generic[{0}]'.format(args), (object,), data)


Generic = _GenericHelperMeta('Generic', (object,), {})


def is_initialized(generic):
  if not isinstance(generic, type):
    generic = type(generic)
  return generic.__generic_bind__ is not None


def assert_initialized(generic):
  if not isinstance(generic, type):
    generic = type(generic)
  if not is_initialized(generic):
    raise RuntimeError('Missing generic arguments for {}'.format(generic.__name__))
