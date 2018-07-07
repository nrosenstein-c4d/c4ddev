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
This module contains tools for modifying function objects and anything else
related to the Python function type like artificial function closure creation.
"""

__all__ = ['new_closure_cell', 'new_closure', 'replace_closure']

import collections
import functools
import types


def new_closure_cell(x):
  """
  Creates a new Python cell object that can usually be found in a functions
  `__closure__` tuple. The values in a `__closure__` must match the free
  variables defined in the function's code object's `co_freevars` member.

  x (any): The cell contents.
  return (cell): A function closure cell object containing *x*.
  """

  return (lambda: x).__closure__[0]


def new_closure(cell_values):
  """
  Creates a function closure from the specified list/iterable of value. The
  returned object is a tuple of cell objects created with #new_closure_cell().

  cell_values (iterable): An iterable of cell values.
  return (tuple of cell): A tuple containing only cell objects.
  """

  return tuple(map(new_closure_cell, cell_values))


def replace(function, code=None, globals=None, name=None,
            argdefs=None, closure=None):
  """
  Creates a new function object from the reference *function* where its
  members can be replaced using the specified arguments.

  # Closure

  If *closure* is a dictionary, only the free variables expected by the
  function are read from it. If a variable is not defined in the dictionary,
  its value will not be changed.

  If *closure* is a list/iterable instead it must have exactly as many
  elements as free variables required by the function's code object. If
  this condition is not satisfied, a #ValueError is raised.

  function (types.FunctionType): A function object.
  code (code): The functions new code object.
  globals (dict):
  """

  if not isinstance(function, types.FunctionType):
    raise TypeError('expected FunctionType, got {}'.format(
                      type(function).__name__))

  if code is None:
    code = function.__code__

  if globals is None:
    globals = function.__globals__

  if name is None:
    name = function.__name__

  if argdefs is None:
    argdefs = function.__defaults__

  if closure is None:
    closure = function.__closure__
  else:
    if isinstance(closure, collections.Mapping):
      closure = [
        closure.get(x, function.__closure__[i].cell_contents)
        for i, x in enumerate(function.__code__.co_freevars)]
    closure = new_closure(closure)
    if len(closure) != len(function.__code__.co_freevars):
      raise ValueError('function requires {} free closure, only '
                      '{} values are specified'.format(
                        len(function.__code__.co_freevars),
                        len(closure)))

  new_func = types.FunctionType(code, globals, name, argdefs, closure)
  functools.update_wrapper(new_func, function)
  return new_func
