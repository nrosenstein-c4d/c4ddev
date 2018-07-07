
from nose.tools import *
from nr.types.enum import Enumeration

def test_enum():
  assert hasattr(Enumeration, 'Data')

  class Color(Enumeration):
    Red = 0
    Green = 2
    Blue = 1
    Fav = Enumeration.Data('Purple')

  assert not hasattr(Color, 'Data')
  assert_equals(Color.Fav, 'Purple')
  assert_equals(Color.Red, Color(0))
  assert_equals(Color.Green, Color(2))
  assert_equals(Color.Blue, Color(1))
  assert_equals(set([Color.Red, Color.Green, Color.Blue]), set(Color))
  assert_equals(set([Color.Red, Color.Green, Color.Blue]), set(Color.__values__()))
