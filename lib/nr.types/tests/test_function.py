
from nose.tools import *
from nr.types.function import replace_closure


def create_function_with_closure(value):
  def check():
    assert_equals(value, 'foo')
  return check


def test_has_closure():
  func = create_function_with_closure('bar')
  assert_equals(len(func.__closure__), 1)
  with assert_raises(AssertionError):
    func()

  func = replace_closure(func, {'value': 'foo'})
  func()
