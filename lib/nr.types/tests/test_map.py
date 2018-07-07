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

from nose.tools import *
from nr.types.map import ChainMap, MapAsObject


def test_ChainDict():
  a = {'foo': 42}
  b = {'bar': 'spam'}
  c = {}
  d = ChainMap({}, a, b, c)

  assert_equals(str(d), 'ChainMap({})'.format({'foo': 42, 'bar': 'spam'}))
  assert_equals(d['foo'], a['foo'])
  assert_equals(d['bar'], b['bar'])
  assert_equals(sorted(d.keys()), ['bar', 'foo'])

  d['hello'] = 'World'
  assert_equals(a, {'foo': 42})
  assert_equals(b, {'bar': 'spam'})
  assert_equals(c, {})
  assert_equals(d, {'foo': 42, 'bar': 'spam', 'hello': 'World'})

  del d['foo']
  assert_equals(a, {'foo': 42})
  assert_equals(b, {'bar': 'spam'})
  assert_equals(c, {})
  assert_equals(d, {'bar': 'spam', 'hello': 'World'})

  d['foo'] = 99
  assert_equals(a, {'foo': 42})
  assert_equals(b, {'bar': 'spam'})
  assert_equals(c, {})
  assert_equals(d, {'foo': 99, 'bar': 'spam', 'hello': 'World'})

  d.clear()
  assert_equals(a, {'foo': 42})
  assert_equals(b, {'bar': 'spam'})
  assert_equals(c, {})
  assert_equals(d, {})


def test_ObjectFromMapping():
  d = ChainMap({'a': 42, 'b': 'foo'}, {'c': 'egg'})
  o = MapAsObject(d)
  assert_equals(o.a, 42)
  assert_equals(o.b, 'foo')
  assert_equals(o.c, 'egg')
  assert_equals(dir(o), ['a', 'b', 'c'])
