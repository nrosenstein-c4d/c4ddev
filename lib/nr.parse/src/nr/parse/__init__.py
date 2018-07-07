# -*- coding: utf8 -*-
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
This is a simple library to tokenize and parse languages ranging from simple
to complex grammatics and semantics. It has been developed specifically for
the recursive decent parser technique, although it might work well with other
parsing techniques as well.

The most basic class is the #Scanner which is a simple wrapper for a string
that counts line and column numbers as it allows you to step through every
character in that string. The #Scanner is sufficient in many simple parsing
tasks.

Next up is the #Lexer which converts characters yielded by the #Scanner into a
stream of #Token#s using a set of #Rule#s.
"""

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '1.0.0'

import string
import nr.types
import os
import re
import sys

eof = 'eof'
string_types = (str,) if sys.version_info[0] == 3 else (str, unicode)

Cursor = nr.types.Record.new('Cursor', 'index lineno colno')
Token = nr.types.Record.new('Token', 'type cursor value string_repr')


class Scanner(object):
  """
  This class is used to step through text character by character and keep track
  of the line and column numbers of each passed character. The Scanner will
  only tread line-feed as a newline.

  # Parameters
  text (str): The text to parse. Must be a `str` in Python 3 and may also be
    a `unicode` object in Python 2.

  # Attributes

  text (str): The *text* passed to the constructor.
  index (int): The cursor position in the text.
  lineno (int): The line-number of the cursor in the text.
  colno (int): The column-number of the cursor in the text.
  cursor (Cursor): The combination of #index, #lineno and #colno.
  char (str): The current character at the Scanner's position. Is
    an empty string at the end of the #text.
  """

  def __init__(self, text):
    if not isinstance(text, string_types):
      raise TypeError('expected str or unicode', type(text))
    self.text = text
    self.index = 0
    self.lineno = 1
    self.colno = 0

  def __repr__(self):
    return '<Scanner at {0}:{0}>'.format(self.lineno, self.colno)

  def __bool__(self):
    return self.index < len(self.text)

  __nonzero__ = __bool__  # Python 2

  @property
  def cursor(self):
    return Cursor(self.index, self.lineno, self.colno)

  @property
  def char(self):
    if self.index >= 0 and self.index < len(self.text):
      return self.text[self.index]
    else:
      return type(self.text)()

  def seek(self, offset, mode='set', renew=False):
    """
    Moves the cursor of the Scanner to or by *offset* depending on the *mode*.
    Is is similar to a file's `seek()` function, however the *mode* parameter
    also accepts the string-mode values `'set'`, `'cur'` and `'end'`.

    Note that even for the `'end'` mode, the *offset* must be negative to
    actually reach back up from the end of the file.

    If *renew* is set to True, the line and column counting will always begin
    from the start of the file. Keep in mind that this could can be very slow
    because it has to go through each and every character until the desired
    position is reached.

    Otherwise, if *renew* is set to False, it will be decided if counting from
    the start is shorter than counting from the current cursor position.
    """

    mapping = {os.SEEK_SET: 'set', os.SEEK_CUR: 'cur', os.SEEK_END: 'end'}
    mode = mapping.get(mode, mode)
    if mode not in ('set', 'cur', 'end'):
      raise ValueError('invalid mode: "{}"'.format(mode))

    # Translate the other modes into the 'set' mode.
    if mode == 'end':
      offset = len(self.text) + offset
      mode = 'set'
    elif mode == 'cur':
      offset = self.index + offset
      mode = 'set'

    assert mode == 'set'
    if offset < 0:
      offset = 0
    elif offset > len(self.text):
      offset = len(self.text) + 1

    if self.index == offset:
      return

    # Figure which path is shorter:
    # 1) Start counting from the beginning of the file,
    if offset <= abs(self.index - offset):
      text, index, lineno, colno = self.text, 0, 1, 0
      while index != offset:
        # Find the next newline in the string.
        nli = text.find('\n', index)
        if nli >= offset or nli < 0:
          colno = offset - index
          index = offset
          break
        else:
          colno = 0
          lineno += 1
          index = nli + 1

    # 2) or step from the current position of the cursor.
    else:
      text, index, lineno, colno = self.text, self.index, self.lineno, self.colno

      if offset < index:  # backwards
        while index != offset:
          nli = text.rfind('\n', 0, index)
          if nli < 0 or nli <= offset:
            if text[offset] == '\n':
              assert (offset - nli) == 0, (offset, nli)
              nli = text.rfind('\n', 0, index-1)
              lineno -= 1
            colno = offset - nli - 1
            index = offset
            break
          else:
            lineno -= 1
            index = nli - 1
      else:  # forwards
        while index != offset:
          nli = text.find('\n', index)
          if nli < 0 or nli >= offset:
            colno = offset - index
            index = offset
          else:
            lineno += 1
            index = nli + 1

    assert lineno >= 1
    assert colno >= 0
    assert index == offset
    self.index, self.lineno, self.colno = index, lineno, colno

  def next(self):
    " Move on to the next character in the text. "

    char = self.char
    if char == '\n':
      self.lineno += 1
      self.colno = 0
    else:
      self.colno += 1
    self.index += 1
    return self.char

  def readline(self):
    " Reads a full line from the scanner and returns it. "

    start = end = self.index
    while end < len(self.text):
      if self.text[end] == '\n':
        end += 1
        break
      end += 1
    result = self.text[start:end]
    self.index = end
    if result.endswith('\n'):
      self.colno = 0
      self.lineno += 1
    else:
      self.colno += end - start
    return result

  def match(self, regex, flags=0):
    """
    Matches the specified *regex* from the current character of the *scanner*
    and returns the result. The Scanners column and line numbers are updated
    respectively.

    # Arguments
    regex (str, Pattern): The regex to match.
    flags (int): The flags to use when compiling the pattern.
    """

    if isinstance(regex, str):
      regex = re.compile(regex, flags)
    match = regex.match(self.text, self.index)
    if not match:
      return None
    start, end = match.start(), match.end()
    lines = self.text.count('\n', start, end)
    self.index = end
    if lines:
      self.colno = end - self.text.rfind('\n', start, end) - 1
      self.lineno += lines
    else:
      self.colno += end - start
    return match

  def getmatch(self, regex, group=0, flags=0):
    """
    The same as #Scanner.match(), but returns the captured group rather than
    the regex match object, or None if the pattern didn't match.
    """

    match = self.match(regex, flags)
    if match:
      return match.group(group)
    return None

  def restore(self, cursor):
    " Moves the scanner back (or forward) to the specified cursor location. "

    if not isinstance(cursor, Cursor):
      raise TypeError('expected Cursor object', type(cursor))
    self.index, self.lineno, self.colno = cursor


class Lexer(object):
  """
  This class is used to split text into #Token#s using a #Scanner and a list
  of #Rule#s.

  # Parameters
  scanner (Scanner): The scanner to read from.
  rules (list of Rule): A list of rules to match. The order in the list
    determines the order in which the rules are matched.

  # Attributes
  scanner (Scanner):
  rules (list of Rule):
  rules_map (dict of (object, Rule)):
    A dictionary mapping the rule name to the rule object. This is
    automatically built when the Lexer is created. If the #rules
    are updated in the lexer directly, #update() must be called.
  skippable_rules (list of Rule):
    A list of skippable rules built from the #rules list. #update() must be
    called if any of the rules or the list of rules are modified.
  token (Token):
    The current token. After the Lexer is created and #next() method has NOT
    been called, the value of this attribute is #None. At the end of the input,
    the token is type #eof.
  """

  def __init__(self, scanner, rules=None):
    self.scanner = scanner
    self.rules = list(rules) if rules else []
    self.update()
    self.token = None

  def __repr__(self):
    ctok = self.token.type if self.token else None
    return '<Lexer with current token {0!r}>'.format(ctok)

  def __iter__(self):
    if not self.token:
      self.next()
    while not self.token.type == eof:
      yield self.token
      self.next()

  def __bool__(self):
    if self.token and self.token.type == eof:
      return False
    return True

  __nonzero__ = __bool__  # Python 2

  def update(self):
    """
    Updates the #rules_map dictionary and #skippable_rules list based on the
    #rules list. Must be called after #rules or any of its items have been
    modified. The same rule name may appear multiple times.

    # Raises
    TypeError: if an item in the `rules` list is not a rule.
    """

    self.rules_map = {}
    self.skippable_rules = []
    for rule in self.rules:
      if not isinstance(rule, Rule):
        raise TypeError('item must be Rule instance', type(rule))
      self.rules_map.setdefault(rule.name, []).append(rule)
      if rule.skip:
        self.skippable_rules.append(rule)

  def expect(self, *names):
    """
    Checks if the current #token#s type name matches with any of the specified
    *names*. This is useful for asserting multiple valid token types at a
    specific point in the parsing process.

    # Arguments
    names (str): One or more token type names. If zero are passed,
      nothing happens.

    # Raises
    UnexpectedTokenError: If the current #token#s type name does not match
      with any of the specified *names*.
    """

    if not names:
      return
    if not self.token or self.token.type not in names:
      raise UnexpectedTokenError(names, self.token)

  def accept(self, *names, **kwargs):
    """
    Extracts a token of one of the specified rule names and doesn't error if
    unsuccessful. Skippable tokens might still be skipped by this method.

    # Arguments
    names (str): One or more token names that are accepted.
    kwargs: Additional keyword arguments for #next().

    # Raises
    ValueError: if a rule with the specified name doesn't exist.
    """

    return self.next(*names, as_accept=True, **kwargs)

  def next(self, *expectation, **kwargs):
    """
    Parses the next token from the input and returns it. The new token can be
    accessed from the #token attribute after the method was called.

    If one or more arguments are specified, they must be rule names that are to
    be expected at the current position. They will be attempted to be matched
    first (in the specicied order). If the expectation could not be met, an
    #UnexpectedTokenError is raised.

    An expected Token will not be skipped, even if its rule defines it so.

    # Arguments
    expectation (str): The name of one or more rules that are expected from the
      current position of the parser. If empty, the first matching token of ALL
      rules will be returned. In this case, skippable tokens will be skipped.
    as_accept (bool): If passed True, this method behaves the same as the
      #accept() method. The default value is #False.
    weighted (bool): If passed True, the tokens specified with *expectations*
      are checked first, effectively giving them a higher priority than other
      they would have from the order in the #rules list. The default value is
      #False.

    # Raises
    ValueError: if an expectation doesn't match with a rule name.
    UnexpectedTokenError: Ff an expectation is given and the expectation
      wasn't fulfilled. Only when *as_accept* is set to #False.
    TokenizationError: if a token could not be generated from the current
      position of the Scanner.
    """

    as_accept = kwargs.pop('as_accept', False)
    weighted = kwargs.pop('weighted', False)
    for key in kwargs:
      raise TypeError('unexpected keyword argument {0!r}'.format(key))

    if self.token and self.token.type == eof:
      if not as_accept and expectation and eof not in expectation:
        raise UnexpectedTokenError(expectation, self.token)
      elif as_accept and eof in expectation:
        return self.token
      elif as_accept:
        return None
      return self.token

    token = None
    while token is None:
      # Stop if we reached the end of the input.
      cursor = self.scanner.cursor
      if not self.scanner:
        token = Token(eof, cursor, None, None)
        break

      value = None

      # Try to match the expected tokens.
      if weighted:
        for rule_name in expectation:
          if rule_name == eof:
            continue
          rules = self.rules_map.get(rule_name)
          if rules is None:
            raise ValueError('unknown rule', rule_name)
          for rule in rules:
            value = rule.tokenize(self.scanner)
            if value:
              break
          if value:
            break
          self.scanner.restore(cursor)

      # Match the rest of the rules, but only if we're not acting
      # like the accept() method that doesn't need the next token
      # for raising an UnexpectedTokenError.
      if not value:
        if as_accept and weighted:
          # Check only skippable rules if we're only trying to accept
          # a certain token type and may consume any skippable tokens
          # until then.
          check_rules = self.skippable_rules
        else:
          check_rules = self.rules
        for rule in check_rules:
          if weighted and expectation and rule.name in expectation:
            # Skip rules that we already tried.
            continue
          value = rule.tokenize(self.scanner)
          if value:
            break
          self.scanner.restore(cursor)

      if not value:
        if as_accept:
          return None
        token = Token(None, cursor, self.scanner.char, None)
      else:
        assert rule, "we should have a rule by now"
        if type(value) is not Token:
          if isinstance(value, tuple):
            value, string_repr = value
          else:
            string_repr = None
          value = Token(rule.name, cursor, value, string_repr)
        token = value

        expected = rule.name in expectation
        if not expected and rule.skip:
          # If we didn't expect this rule to match, and if its skippable,
          # just skip it. :-)
          token = None
        elif not expected and as_accept:
          # If we didn't expect this rule to match but are just accepting
          # instead of expecting, restore to the original location and stop.
          self.scanner.restore(cursor)
          return None

    self.token = token
    if as_accept and token and token.type == eof:
      if eof in expectation:
        return token
      return None

    if token.type is None:
      raise TokenizationError(token)
    if not as_accept and expectation and token.type not in expectation:
      raise UnexpectedTokenError(expectation, token)
    assert not as_accept or (token and token.type in expectation)
    return token


class Rule(object):
  """
  Base class for rule objects that are capable of extracting a #Token from
  the current position of a #Scanner.

  # Attributes
  name (str): The name of the rule. This name must be passed to the
    #Token.type member when #tokenize() returns a valid token.
  skip (bool): If #True, the rule is treated as a skippable rule. If the
    rule is encountered in the #Lexer and matched, the generated token will
    be discarded entirely.
  """

  def __init__(self, name, skip=False):
    self.name = name
    self.skip = skip

  def tokenize(self, scanner):
    """
    Attempt to extract a token from the position of the *scanner* and return it.
    If a non-#Token instance is returned, it will be used as the tokens value.
    Any value that evaluates to #False will make the Lexer assume that the rule
    couldn't capture a Token.

    The #Token.value must not necessarily be a string though, it can be any data
    type or even a complex datatype, only the user must know about it and handle
    the token in a special manner.
    """

    raise NotImplementedError


class Regex(Rule):
  """
  A rule to match a regular expression. The #Token generated by this rule
  contains the match object as its value, not a plain string.

  # Attributes
  regex (Pattern): A compiled regular expression.
  """

  def __init__(self, name, regex, flags=0, skip=False):
    super(Regex, self).__init__(name, skip)
    if isinstance(regex, string_types):
      regex = re.compile(regex, flags)
    self.regex = regex

  def tokenize(self, scanner):
    result = scanner.match(self.regex)
    if result is None or result.start() == result.end():
      return None
    return result, result.group()


class Keyword(Rule):
  """
  This rule matches an exact string (optionally case insensitive)
  from the scanners current position.

  # Attributes
  string (str): The keyword string to match.
  case_sensitive (bool): Whether matching is case-senstive or not.
  """

  def __init__(self, name, string, case_sensitive=True, skip=False):
    super(Keyword, self).__init__(name, skip)
    self.string = string
    self.case_sensitive = case_sensitive

  def tokenize(self, scanner):
    string = self.string if self.case_sensitive else self.string.lower()
    char = scanner.char
    result = type(char)()
    for other_char in string:
      if not self.case_sensitive:
        char = char.lower()
      if char != other_char:
        return None
      result += char
      char = scanner.next()
    return result


class Charset(Rule):
  """
  This rule consumes all characters of a given set and returns all characters
  it consumes.

  # Attributes
  charset (frozenset of str): A set of characters to consume.
  at_column (int): Match the charset only at a specific column index in
    the input text. This is useful to create a separate indentation token type
    apart from the typical whitespace token. Defaults to #-1.
  """

  def __init__(self, name, charset, at_column=-1, skip=False):
    super(Charset, self).__init__(name, skip)
    self.charset = frozenset(charset)
    self.at_column = at_column

  def tokenize(self, scanner):
    if self.at_column >= 0 and self.at_column != scanner.colno:
      return None
    char = scanner.char
    result = type(char)()
    while char and char in self.charset:
      result += char
      char = scanner.next()
    return result


class TokenizationError(Exception):
  """
  This exception is raised if the stream can not be tokenized at a given
  position. The `Token` object that an object is initialized with is an invalid
  token with the cursor position and current scanner character as its value.
  """

  def __init__(self, token):
    if type(token) is not Token:
      raise TypeError('expected Token object', type(token))
    if token.type is not None:
      raise ValueError('can not be raised with a valid token')
    self.token = token

  def __str__(self):
    message = 'could not tokenize stream at {0}:{1}:{2!r}'.format(
      self.token.cursor.lineno, self.token.cursor.colno, self.token.value)
    return message


class UnexpectedTokenError(Exception):
  """
  This exception is raised when the #Lexer.next() method was given one or more
  expected token types but the extracted token didn't match the expected types.
  """

  def __init__(self, expectation, token):
    if not isinstance(expectation, (list, tuple)):
      message = 'expectation must be a list/tuple of rule names'
      raise TypeError(message, type(expectation))
    if len(expectation) < 1:
      raise ValueError('expectation must contain at least one item')
    if type(token) is not Token:
      raise TypeError('token must be Token object', type(token))
    if token.type is None:
      raise ValueError('can not be raised with an invalid token')
    self.expectation = expectation
    self.token = token

  def __str__(self):
    message = 'expected token '.format(self.token.cursor.lineno, self.token.cursor.colno)
    if len(self.expectation) == 1:
      message += '"' + self.expectation[0] + '"'
    else:
      message += '{' + ','.join(map(str, self.expectation)) + '}'
    return message + ', got "{0}" instead (value={1!r} at {2}:{3})'.format(
      self.token.type, self.token.string_repr or self.token.value,
      self.token.cursor.lineno, self.token.cursor.colno)
