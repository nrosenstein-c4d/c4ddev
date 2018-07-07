
from nose.tools import *
from nr import parse

def test_seek():
  s = parse.Scanner("foo\nbar")
  assert_equal(s.char, 'f')
  assert_equal(s.cursor, parse.Cursor(0, 1, 0))

  s.next()
  assert_equal(s.char, 'o')
  assert_equal(s.cursor, parse.Cursor(1, 1, 1))

  s.seek(5)
  assert_equal(s.char, 'a')
  assert_equal(s.cursor, parse.Cursor(5, 2, 1))

  s.seek(-1, 'cur')
  assert_equal(s.char, 'b')
  assert_equal(s.cursor, parse.Cursor(4, 2, 0))

  s.seek(-1, 'cur')
  assert_equal(s.char, '\n')
  assert_equal(s.cursor, parse.Cursor(3, 1, 3))

  s.seek(-1, 'cur')
  assert_equal(s.char, 'o')
  assert_equal(s.cursor, parse.Cursor(2, 1, 2))

  s.seek(-1, 'cur')
  assert_equal(s.char, 'o')
  assert_equal(s.cursor, parse.Cursor(1, 1, 1))

  s.seek(-1, 'cur')
  assert_equal(s.char, 'f')
  assert_equal(s.cursor, parse.Cursor(0, 1, 0))

  # At the start, seek ingored.
  s.seek(-1, 'cur')
  assert_equal(s.char, 'f')
  assert_equal(s.cursor, parse.Cursor(0, 1, 0))

  s.seek(0, 'end')
  assert_equal(s.char, '')
  assert_equal(s.cursor, parse.Cursor(7, 2, 3))

  s.seek(-20, 'cur')
  assert_equal(s.char, 'f')
  assert_equal(s.cursor, parse.Cursor(0, 1, 0))
