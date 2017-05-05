# -*- coding: utf8; -*-
#
# Copyright (C) 2015  Niklas Rosenstein
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

import collections


def f_attrs(self=False, **attrs):
    r"""
    - *New in 1.2.6*.
    - *Changed in 1.3.0*

        - Moved from ``utils`` to ``decorators``
        - Added *self* parameter.

    This function returns a decorator adding all passed keyword arguments
    as attributes to the decorated function. If the parameter *self* is
    given True, the function object itself will be passed as first argument
    to the function.

    .. code-block:: python

        @f_attrs(attr='value here')
        def func1(arg):
            print func1.attr
            return arg ** 2

        @f_attrs(True, attr='value here')
        def func2(self, arg):
            print self.attr
            return arg ** 2
    """

    def wrapper(func):
        for k, v in attrs.iteritems():
            setattr(func, k, v)
        if self:
            f_save = func
            def func(*args, **kwargs):
                return f_save(f_save, *args, **kwargs)
        return func

    return wrapper


def override(fnc=None):
    r"""
    *New in 1.3.0*. Decorator for class-methods. Use in combination with
    the :func:`subclass` decorator.

    This decorator will raise a :class:`NotImplementedError`
    when the decorated function does not override a method implemented
    in one of the base classes.


    Call without arguments before decorating to prevent the checking and
    use it as code annotation only.
    """

    if fnc is None:
        return lambda x: x
    else:
        return _Override(fnc)


def subclass(cls):
    r"""
    A class decorator checking each :class:`override` decorated
    function. Use it as follows:

    .. code-block:: python

        @subclass
        class Subclass(Superclass):

            @override
            def overriden_function(self):
                # ...
                pass

    """

    for key in dir(cls):
        value = getattr(cls, key)
        if isinstance(value, _Override):
            value.check(cls)
            setattr(cls, key, value.func)

    return cls


class _Override(object):

    def __init__(self, func):
        super(_Override, self).__init__()
        self.func = func
        self.__name__ = getattr(func, '__name__', None)
        self.func_name = func.func_name

    def check(self, cls):
        for base in cls.__bases__:
            has = hasattr(base, self.func_name)
            func = getattr(base, self.func_name, None)
            if has and isinstance(func, collections.Callable):
                return

        raise NotImplementedError('No baseclass of %s '
                'implements a method %s()' % (cls.__name__, self.func_name))
