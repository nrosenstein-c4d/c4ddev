
from nose.tools import *
from localimport import localimport
import os
import sys

modules_dir = os.path.join(os.path.dirname(__file__), 'modules')


def test_localimport_with_autodisable():
  sys.path.append(modules_dir)
  import another_module as mod_a
  try:
    with localimport('modules') as _imp:
      import some_module
      import another_module as mod_b
      assert 'some_module' in sys.modules
      assert sys.modules['another_module'] is mod_b
    assert 'some_module' not in sys.modules
    assert sys.modules['another_module'] is mod_a
    assert mod_a is not mod_b
  finally:
    sys.path.remove(modules_dir)
    del sys.modules['another_module']


def test_localimport_without_autodisable():
  sys.path.append(modules_dir)
  import another_module as mod_a
  try:
    with localimport('modules', do_autodisable=False) as _imp:
      import some_module
      import another_module as mod_b
      assert 'some_module' in sys.modules
      assert sys.modules['another_module'] is mod_b
    assert mod_a is mod_b
    assert 'some_module' not in sys.modules
    assert sys.modules['another_module'] is mod_a
  finally:
    sys.path.remove(modules_dir)
    del sys.modules['another_module']


def test_localimpot_parent_dir():
  with localimport('.', parent_dir=modules_dir) as _imp:
    import some_module
  assert 'some_module' not in sys.modules
  assert 'another_module' not in sys.modules


def test_localimpot_curdir():
  with localimport('.') as _imp:
    import some_module
  assert 'some_module' not in sys.modules
  assert 'another_module' not in sys.modules


def test_discover():
  with localimport('.') as _imp:
    assert_equals(sorted(x.name for x in _imp.discover()), ['another_module', 'some_module', 'test_localimport'])
  with localimport('modules') as _imp:
    assert_equals(sorted(x.name for x in _imp.discover()), ['another_module', 'some_module'])
