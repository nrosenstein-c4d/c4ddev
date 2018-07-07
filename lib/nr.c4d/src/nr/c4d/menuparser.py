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

import nr.parse
import re
import string

try:
  import cStringIO as StringIO
except ImportError:
  try:
    import StringIO
  except ImportError:
    import io as StringIO


lexer_rules = [
    nr.parse.Regex('comment', '#.*$', re.M, skip=True),
    nr.parse.Regex('ws', '\s+', re.M, skip=True),
    nr.parse.Regex('menu', 'MENU\\b'),
    nr.parse.Regex('command', 'COMMAND\\b'),
    nr.parse.Keyword('bopen', '{'),
    nr.parse.Keyword('bclose', '}'),
    nr.parse.Keyword('end', ';'),
    nr.parse.Charset('sep', '-'),
    nr.parse.Charset('symbol', string.ascii_letters + '_' + string.digits),
    nr.parse.Charset('number', string.digits)
]


class MenuNode(object):

  # Always a MenuContainer instance or None.
  parent = None

  def _assert_symbol(self, symbol, res):
    if not hasattr(res, symbol):
      raise AttributeError('Resource does not have required symbol %r' %
                 symbol)

  def _compare_symbol(self, node_id, res):
    r"""
    Sub-procedure for sub-classes implementing a ``symbol`` attribute.
    """

    if self.symbol:
      if node_id == self.symbol:
        return True

      self._assert_symbol(self.symbol, res)
      if getattr(res, self.symbol) == node_id:
        return True

    return False

  def render(self, dialog, res):
    pass

  def find_node(self, node_id, res):
    r"""
    New in 1.2.7. Find a node by it's identifier.
    """

    return None

  def remove(self):
    r"""
    New in 1.2.8. Remove the node from the tree.
    """

    if self.parent:
      self.parent.children.remove(self)
      self.parent = None

  def copy(self):
    r"""
    New in 1.2.8. Return a copy of the Menu tree.
    """
    raise NotImplementedError


class MenuContainer(MenuNode):
  r"""
  This class represents a container for Cinema 4D dialog menus
  containg menu commands. The class can be rendered recursively
  on a dialog to create such a menu.

  .. attribute:: symbol

    The resource-symbol for the menu-container that can be
    used to obtain the name of the menu. No sub-menu will be
    created with rendering the instance when this value
    evaluates to False (eg. None value).
  """

  def __init__(self, symbol):
    super(MenuContainer, self).__init__()
    self.children = []
    self.symbol = symbol

  def __str__(self):
    lines = ['MenuContainer(%r, ' % self.symbol]
    for child in self.children:
      for l in str(child).split('\n'):
        lines.append('  ' + l)
    if len(lines) > 1:
      lines.append('')
    lines[-1] += ')'
    return '\n'.join(lines)

  def __iter__(self):
    # For partial backwards compatibility where MenuParser.parse()
    # return a list.
    return iter(self.children)

  def add(self, child):
    self.children.append(child)
    child.parent = self

  def render(self, dialog, res):
    if self.symbol:
      self._assert_symbol(self.symbol, res)
      dialog.MenuSubBegin(res.string(self.symbol))
    try:
      for child in self.children:
        child.render(dialog, res)
    finally:
      if self.symbol:
        dialog.MenuSubEnd()

  def find_node(self, node_id, res):
    if self._compare_symbol(node_id, res):
      return self

    for child in self.children:
      node = child.find_node(node_id, res)
      if node:
        return node

  def copy(self):
    new = MenuContainer(self.symbol)
    for child in self.children:
      new.add(child.copy())
    return new


class MenuSeperator(MenuNode):

  def __str__(self):
    return 'MenuSeperator()'

  def render(self, dialog, res):
    dialog.MenuAddSeparator()

  def copy(self):
    return MenuSeperator()

class MenuCommand(MenuNode):

  def __init__(self, command_id=None, symbol=None):
    super(MenuCommand, self).__init__()
    assert command_id or symbol
    self.command_id = command_id
    self.symbol = symbol

  def __str__(self):
    return 'MenuCommand(%s, %r)' % (self.command_id, self.symbol)

  def render(self, dialog, res):
    command_id = self.command_id
    if not command_id:
      self._assert_symbol(self.symbol, res)
      command_id = getattr(res, self.symbol)

    dialog.MenuAddCommand(command_id)

  def find_node(self, node_id, res):
    if self.command_id and self.command_id == node_id:
      return self
    elif self._compare_symbol(node_id, res):
      return self

    return None

  def copy(self):
    return MenuCommand(self.command_id, self.symbol)


class MenuString(MenuNode):

  def __init__(self, symbol):
    super(MenuString, self).__init__()
    self.symbol = symbol

  def __str__(self):
    return 'MenuString(%r)' % (self.symbol,)

  def render(self, dialog, res):
    self._assert_symbol(self.symbol, res)
    dialog.MenuAddString(*res.string(self.symbol))

  def find_node(self, node_id, res):
    if self._compare_symbol(node_id, res):
      return self

  def copy(self):
    return MenuString(self.symbol)


class MenuItem(MenuNode):
  r"""
  This class represents an item added via
  :meth:`c4d.gui.GeDialog.MenuAddString`. It is not created from this
  module but may be used create dynamic menus.

  .. attribute:: id

    The integral number of the symbol to add.

  .. attribute:: string

    The menu-commands item string.
  """

  def __init__(self, id, string):
    super(MenuItem, self).__init__()
    self.id = id
    self.string = string

  def __str__(self):
    return 'MenuItem(%r, %r)' % (self.id, self.string)

  def render(self, dialog, res):
    dialog.MenuAddString(self.id, self.string)

  def find_node(self, node_id, res):
    if node_id == self.id:
      return self

  def copy(self):
    return MenuItem(self.id, self.string)


class MenuParser(object):

  def _assert_type(self, token, *tokentypes):
    for tokentype in tokentypes:
      if not token or token.type != tokentype:
        raise scan.UnexpectedTokenError(token, tokentypes)

  def _command(self, lexer):
    assert lexer.token.type == 'command'
    lexer.next('number', 'symbol')
    command_id = None
    symbol_name = None
    if lexer.token.type == 'number':
      command_id = int(lexer.token.value)
    elif lexer.token.type == 'symbol':
      symbol_name = lexer.token.value
    else:
      assert False

    return MenuCommand(command_id, symbol_name)

  def _menu(self, lexer):
    assert lexer.token.type == 'menu'
    lexer.next('symbol')
    items = MenuContainer(lexer.token.value)
    lexer.next('bopen')

    while True:
      lexer.next('menu', 'command', 'sep', 'symbol', 'bclose')
      if lexer.token.type == 'bclose':
        break

      require_endstmt = True
      if lexer.token.type == 'menu':
        item = self._menu(lexer)
        require_endstmt = False
      elif lexer.token.type == 'command':
        item = self._command(lexer)
      elif lexer.token.type == 'sep':
        item = MenuSeperator()
      elif lexer.token.type == 'symbol':
        item = MenuString(lexer.token.value)
      else:
        assert False

      items.add(item)

      if require_endstmt:
        lexer.next('end')

    return items

  def parse(self, lexer):
    menus = MenuContainer(None)
    lexer.next('menu', 'end')
    print(lexer.token)
    if lexer.token.type == 'menu':
      menu = self._menu(lexer)
      menus.add(menu)
    return menus


def parse_file(filename):
  ''' Parse a ``*.menu`` file from the local file-system.
  Returns a #MenuContainer.
  '''

  return parse_fileobject(open(filename, 'r'))


def parse_string(data):
  ''' Parse a ``*.menu`` formatted string. Returns a #MenuContainer. '''

  fl = StringIO.StringIO(data)
  fl.seek(0)
  return parse_fileobject(fl)


def parse_fileobject(fl):
  ''' Parse a file-like object. Returns a #MenuContainer. '''

  scanner = nr.parse.Scanner(fl.read())
  lexer = nr.parse.Lexer(scanner, lexer_rules)
  parser = MenuParser()
  return parser.parse(lexer)
