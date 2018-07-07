
from nose.tools import *
from nr.types.named import Named


def test_has_initializer_member():
  assert hasattr(Named, 'Initializer')
  class Person(Named):
    pass
  assert not hasattr(Person, 'Initializer')
