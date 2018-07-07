# Copyright (c) 2016  Niklas Rosenstein
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

from nr.types import Record
from nose.tools import *


def test_class_style():
  class MyRecord(Record):
    __slots__ = 'foo bar ham egg'.split()
    __defaults__ = {'egg': 'yummy'}
  _test_record(MyRecord)

def test_function_style():
  MyRecord = Record.new('MyRecord', 'foo bar ham', egg='yummy')
  _test_record(MyRecord)

def _test_record(MyRecord):
  data = MyRecord('the-foo', 42, ham="spam")
  assert_equals(data.foo, 'the-foo')
  assert_equals(data.bar, 42)
  assert_equals(data.ham, 'spam')
  assert_equals(data.egg, 'yummy')
