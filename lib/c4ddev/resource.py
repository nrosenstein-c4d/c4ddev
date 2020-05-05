# coding: utf8
# Copyright (C) 2016  Niklas Rosenstein
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
"""
Utilities for Cinema 4D resource symbols.
"""

from __future__ import print_function
from . import __version__

try:
  from nr import strex as parse
except ImportError:
  try:
    from nr import parse
  except ImportError:
    import nr.parsing.core as parse

import collections
import codecs
import errno
import glob
import json
import os
import re
import string
import sys
import textwrap

TEMPLATE_CLASS = textwrap.dedent('''
  exec ("""class res(object):
   # Automatically generated with c4ddev v{0}.
   project_path = os.path.dirname(__file__)
   def string(self, name, *subst):
    result = __res__.LoadString(getattr(self, name))
    for item in subst: result = result.replace('#', item, 1)
    return result
   def tup(self, name, *subst):
    return (getattr(self, name), self.string(name, *subst))
   def path(self, *parts):
    path = os.path.join(*parts)
    if not os.path.isabs(path):
     path = os.path.join(self.project_path, path)
    return path
   file = path  # backwards compatibility
   def bitmap(self, *parts):
    b = c4d.bitmaps.BaseBitmap()
    if b.InitWith(self.path(*parts))[0] != c4d.IMAGERESULT_OK: return None
    return b
   {{symbols}}
   res=res()""")'''.format(__version__))

TEMPLATE_FILE = textwrap.dedent('''
  # Automatically generated with c4ddev v{0}.

  import os
  import sys
  import c4d

  _frame = sys._getframe(1)
  while _frame and not '__res__' in _frame.f_globals:
    _frame = _frame.f_back

  project_path = os.path.dirname(_frame.f_globals['__file__'])
  project_path = os.path.normpath(os.path.join(project_path, {{project_path}}))
  resource = __res__ = _frame.f_globals['__res__']

  del _frame

  def string(name, *subst, **kwargs):
    disable = kwargs.pop('disable', False)
    checked = kwargs.pop('checked', False)
    if kwargs:
      raise TypeError('unexpected keyword arguments: ' + ','.join(kwargs))

    if isinstance(name, str):
      name = globals()[name]
    elif not isinstance(name, (int, long)):
      raise TypeError('name must be str, int or long')

    result = resource.LoadString(name)
    for item in subst:
      result = result.replace('#', str(item), 1)

    if disable:
      result += '&d&'
    if checked:
      result += '&c&'
    return result

  def tup(name, *subst, **kwargs):
    if isinstance(name, str):
      name = globals()[name]
    return (name, string(name, *subst))

  def path(*parts):
    """
    Joins the path parts with the #project_path, which is initialized with the
    parent directory of the file that first imported this module (which is
    usually the Python plugin file).
    """
    path = os.path.join(*parts)
    if not os.path.isabs(path):
      path = os.path.join(project_path, path)
    return path

  def localpath(*parts, **kwargs):
    """
    Joins the path parts with the parent directory of the Python file that
    called this function.
    """
    _stackdepth = kwargs.get('_stackdepth', 0)
    parent_dir = os.path.dirname(sys._getframe(_stackdepth+1).f_globals['__file__'])
    return os.path.normpath(os.path.join(parent_dir, *parts))

  def bitmap(*parts):
    bitmap = c4d.bitmaps.BaseBitmap()
    result, ismovie = bitmap.InitWith(path(*parts))
    if result != c4d.IMAGERESULT_OK:
      return None
    return bitmap

  {{symbols}}'''.format(__version__))


def parse_symbols(filename_or_fp):
  '''
  Parses a Cinema 4D resource symbol header and returns a dictionary that
  maps the symbol names with their ID and a list that contains all symbols
  that are masked by other fields declared later.

  :param string: The string containing the C enumeration.
  :return: A tuple of `(dict, list)`
  '''

  if isinstance(filename_or_fp, str):
    with open(filename_or_fp) as fp:
      return parse_symbols_string(fp.read())
  else:
    return parse_symbols_string(filename_or_fp.read())


def parse_symbols_string(string):
  # Remove all comments from the source.
  string = ' '.join(line.split('//')[0] for line in string.splitlines())
  string = ' '.join(re.split(r'\/\*.*\*\/', string))

  # Extract all enumeration declarations from the source.
  enumerations = [
    text.split('{')[1].split('}')[0]
    for text in re.split(r'\benum\b', string)[1:]
  ]

  # Load the symbols.
  symbols = {}
  masked_symbols = []
  for enum in enumerations:
    last_value = -1
    for name in enum.split(','):
      if '=' in name:
        name, value = name.split('=')
        value = int(value)
      else:
        value = last_value + 1

      name = name.strip()
      if name:
        if name in symbols and symbols[name] != value:
          masked_symbols.append((name, symbols[name]))
        last_value = value
        if not name.startswith('_'):
          symbols[name] = value

  return (symbols, masked_symbols)


def get_resource_files(res_dir):
  '''
  Returns a dictionary with the following contents:

  .. code:: python

    {
      'res': res_dir,
      'c4d_symbols': 'path/to/res/c4d_symbols.h',
      'description': ['path/to/res/description/XXX.h', ...]
    }

  or None if *res_dir* is not a Cinema 4D resource directory.
  '''

  c4d_symbols = os.path.join(res_dir, 'c4d_symbols.h')
  if not os.path.isdir(res_dir) or not os.path.isfile(c4d_symbols):
    return None

  results = {
    'res': res_dir,
    'c4d_symbols': c4d_symbols,
    'description': [],
    }

  for desc in glob.iglob(os.path.join(res_dir, 'description', '*.h')):
    results['description'].append(desc)

  return results


def export_symbols(format, res_dir=None, outfile=None, settings=None):
  '''
  Parses the symbols of one or more resource directories
  and formats them according to *format*.

  :param format: ``json``, ``class`` or ``file``
  :param res_dir:
    A string pointing to a C4D plugin resource directory or a list of such.
    Defaults to the ``res/`` directory of the current working directory.
  :param outfile: The output file name or None to print to stdout.
  '''

  if format not in ('json', 'file', 'class'):
    raise ValueError('invalid format: {0!r}'.format(format))

  if settings is None:
    settings = {}
  if res_dir is None:
    res_dir = 'res'

  if isinstance(res_dir, str):
    dirlist = [res_dir]
  else:
    dirlist = res_dir

  # Symbol name -> tuple of (value, filename).
  symbols = {}
  desc_symbols = {}

  def merge_symbols(filename, dest):
    print(filename)
    symbols, masked = parse_symbols(filename)
    for symbol, value in masked:
      print("Warning ({0}): {1} ({2}) masked".format(
        os.path.relpath(filename), symbol, value), file=sys.stderr)
    for symbol, value in symbols.items():
      has_value, source = dest.get(symbol, (None, None))
      if source is not None and has_value != value:
        print("Warning ({0}): {1} ({2}) masking same symbol from {3} ({4})".format(
          os.path.relpath(filename), symbol, value, os.path.relpath(source),
          has_value), file=sys.stderr)
      dest[symbol] = (value, filename)

  for dirname in dirlist:
    files = get_resource_files(dirname)
    if files is None:
      raise ValueError('not a resource directory: {!r}'.format(dirname))

    merge_symbols(files['c4d_symbols'], symbols)
    for filename in files['description']:
      merge_symbols(filename, desc_symbols)

  # Unpack the values from the (value, filename) tuples.
  unpack = lambda x: dict((k, v) for k, (v, __) in x.items())
  symbols = unpack(symbols)
  desc_symbols = unpack(desc_symbols)

  fn = globals()['format_symbols_' + format]
  if outfile:
    with open(outfile, 'w') as fp:
      fn(symbols, desc_symbols, fp, settings)
  else:
    fn(symbols, desc_symbols, sys.stdout, settings)
    print()


def format_symbols_json(symbols, desc_symbols, fp, settings):
  all_syms = symbols.copy()
  all_syms.update(desc_symbols)
  json.dump(all_syms, fp)


def format_symbols_file(symbols, desc_symbols, fp, settings):
  project_path = settings.get('project_path') or ''
  formatted = preformat_symbols(symbols, desc_symbols)
  print(render_template(TEMPLATE_FILE, symbols=formatted,
    project_path=repr(project_path)), file=fp)


def format_symbols_class(symbols, desc_symbols, fp, settings):
  formatted = preformat_symbols(symbols, desc_symbols)
  print(render_template(TEMPLATE_CLASS, symbols=formatted), file=fp)


def preformat_symbols(symbols, desc_symbols):
  def preprocess(symbols):
    if not symbols: return
    for name, value in sorted(symbols.items(), key=lambda x: (x[0], x[1])):
      if not name.startswith('_'):
        yield name + ' = ' + str(value)
  formatted = []
  formatted.extend(preprocess(symbols))
  formatted.extend('')
  formatted.extend(preprocess(desc_symbols))
  if not symbols and not desc_symbols:
    formatted.append('pass')
  return '\n'.join(formatted)


def render_template(__template_string, **context):
  '''
  Renders the template string *__template_string* into a new string
  replacing variables annotated with ``{{varname}}`` from variables
  in the *context*. The indentation of the variables is kept.
  '''

  expr = r'^(.*)\{(\w+)\}'
  def replace(match):
    pre = match.group(1)
    name = match.group(2)
    value = context[name]
    lines = value.split('\n')

    if not lines:
      return pre

    result = []
    result.append(pre + lines[0])
    for line in lines[1:]:
      result.append(' ' * len(pre) + line)

    return '\n'.join(result)

  return re.sub(expr, replace, __template_string, flags=re.M)


def makedirs(path, parent = False):
  if parent:
    path = os.path.dirname(path)
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno != errno.EEXIST:
      raise


def escape_unicode(string):
  def generator():
    for c in string:
      if ord(c) in range(32, 128):
        yield c
      else:
        yield '\\u%04x' % ord(c)
  return ''.join(generator())


class ResourcePackage(object):
  '''
  Represents the data of an ``.rpkg`` file that can be converted to
  the Cinema 4D resource format.

  .. attribute:: name

    The name of the description resource. This is deduced from the
    filename. The package is automatically treated as a C4D symbols
    file if its name is ``c4d_symbols``.

  .. attribute:: symbols

    A dictionary mapping symbol names to their integer IDs.

  .. attribute:: localizations

    A dictionary that maps language codes to a dictionary of localized
    strings for the :attr:`symbols`. Keys to this dictionary are the
    symbol names (not IDs!).

  .. attribute:: autoid_counter

    A number that is the next free ID for automatic incrementing. This
    is only used in `c4d_symbols.rpkg` files.
  '''

  Token_Newline = '\n'
  Token_Def = ':'
  Token_Number = 'number'
  Token_Symbol = 'symbol'
  Token_Indent = 'indent'
  Token_Whitespace = 'ws'
  Token_Comment = 'comment'
  Token_Popen = '('
  Token_Pclose = ')'
  Token_SetPrefix = 'SetPrefix'
  Token_EOF = parse.eof

  Rules = [
    parse.Keyword(Token_Newline, Token_Newline),
    parse.Keyword(Token_Def, Token_Def),
    parse.Keyword(Token_Popen, Token_Popen),
    parse.Keyword(Token_Pclose, Token_Pclose),
    parse.Keyword(Token_SetPrefix, Token_SetPrefix),
    parse.Charset(Token_Number, string.digits),
    parse.Charset(Token_Symbol, string.ascii_letters + '_' + string.digits),
    parse.Charset(Token_Indent, string.whitespace, at_column=0),
    parse.Charset(Token_Whitespace, string.whitespace, skip=True),
    parse.Regex(Token_Comment, '#.*$', re.M, skip=True)
  ]

  # Seems like these are the only supported language codes for Cinema 4D.
  LangCodes = frozenset(['us', 'de', 'jp', 'cz', 'es', 'fr', 'it', 'pl'])

  class ParseError(Exception):
    pass

  def __init__(self, name):
    self.name = name
    self.symbols = collections.OrderedDict()
    self.localizations = collections.OrderedDict()
    self.autoid_counter = 10000

  def __repr__(self):
    return '<ResourcePackage name={!r}>'.format(self.name)

  @classmethod
  def parse(cls, content, filename):
    lexer = strex.Lexer(strex.Scanner(content), cls.Rules)
    error = cls._error(lexer, filename)

    basename = os.path.basename(filename).rpartition('.')[0]
    if not basename:
      raise ValueError('no resource name')

    cls._skip_newline(lexer)

    if lexer.next(cls.Token_Symbol).value != 'ResourcePackage':
      error('expected "ResourcePackage"')
    if lexer.accept(cls.Token_Popen):
      basename = lexer.next(cls.Token_Symbol).value
      lexer.next(cls.Token_Pclose)

    is_c4d_symbols = (basename == 'c4d_symbols')
    pkg = cls(basename)

    cls._skip_newline(lexer)

    # Parse the resource symbols.
    current_prefix = ''
    while lexer.next(cls.Token_Symbol, cls.Token_SetPrefix, cls.Token_EOF):
      token = lexer.token
      if token.type == cls.Token_EOF: break
      if token.type == cls.Token_SetPrefix:
        lexer.next(cls.Token_Popen)
        prefix_token = lexer.next(cls.Token_Symbol, cls.Token_Pclose)
        if prefix_token.type == cls.Token_Symbol:
          current_prefix = prefix_token.value
          lexer.next(cls.Token_Pclose)
        else:
          current_prefix = ''
      else:
        name = current_prefix + token.value
        if name in pkg.symbols:
          error('duplicate symbol "{0}"'.format(name))

        lexer.next(cls.Token_Def)
        lexer.next(cls.Token_Number, cls.Token_Newline, cls.Token_EOF)

        value = None
        if lexer.token.type == cls.Token_Number:
          value = int(lexer.token.value)
          lexer.next(cls.Token_Newline, cls.Token_EOF)
        elif is_c4d_symbols:
          value = pkg.autoid_counter
          pkg.autoid_counter += 1

        if value is not None:
          pkg.symbols[name] = value

        for lang_code, string in cls._parse_localization(lexer, error).items():
          try:
            table = pkg.localizations[lang_code]
          except KeyError:
            pkg.localizations[lang_code] = table = collections.OrderedDict()
          table[name] = string

      cls._skip_newline(lexer)

    return pkg

  @classmethod
  def _skip_newline(cls, lexer):
    while lexer.accept(cls.Token_Newline):
      pass

  @classmethod
  def _parse_localization(cls, lexer, error):
    result = {}
    cls._skip_newline(lexer)
    while lexer.accept(cls.Token_Indent):
      lang = lexer.next(cls.Token_Symbol).value
      if lang not in cls.LangCodes:
        error('unsupported language code "{0}"'.format(lang))
      if lang in result:
        error('localization for "{0}" already defined'.format(lang))
      lexer.next(cls.Token_Def)
      content = lexer.scanner.readline().strip()
      # xxx: There might be better ways to expand \n and \t.
      content = re.sub('(?<!\\\\)\\\\n', '\n', content)
      content = re.sub('(?<!\\\\)\\\\t', '\t', content)
      result[lang] = content
      cls._skip_newline(lexer)
    return result

  @classmethod
  def _error(cls, lexer, filename):
    def error(message):
      # xxx: include contextual information with line number and filename
      raise cls.ParseError('%s (at %s)' % (message, lexer.token))
    return error


def build_rpkg(files, res_dir, no_header):
  '''
  Convert one or many resource packages to Cinema 4D resource files.
  A resource package file is usually suffixed with .rpkg . The filename
  without the suffix is used the resource name. Resource package files
  must be UTF-8 encoded. An example file:

  ::

    ResourcePackage
    PRIM_CUBE_LENGTH: 1001
      us: Size
      de: Größe
    PRIM_CUBE_SEGMENTS: 1002
      us: Segments
      de: Segmente

  :param files: A list of ``.rpkg`` files.
  :param res_dir: The target resource directory.
  :param no_header: Don't output a header into the files.
  '''

  if not os.path.isdir(res_dir):
    raise OSError('directory "{}" does not exist'.format(res_dir))
  for fname in files:
    with codecs.open(fname, 'r', encoding='utf8') as fp:
      content = fp.read().replace('\r\n', '\n')
    rpkg = ResourcePackage.parse(content, fname)
    if rpkg.name == 'c4d_symbols':
      header = os.path.join(res_dir, 'c4d_symbols.h')
      strings_dir = ''
      strings_name = 'c4d_strings'
    else:
      header = os.path.join(res_dir, 'description', rpkg.name + '.h')
      strings_dir = 'description'
      strings_name = rpkg.name

    makedirs(header, parent = True)
    print('Writing {} ...'.format(os.path.relpath(header, res_dir)))
    with open(header, 'w') as fp:
      if not no_header:
        fp.write('// Automatically generated with c4ddev v{}\n'.format(__version__))
      guard = '__{}_H_'.format(rpkg.name)
      fp.write('#ifndef {}\n'.format(guard))
      fp.write('#define {}\n'.format(guard))
      fp.write('enum\n')
      fp.write('{\n')
      for name, value in rpkg.symbols.items():
        fp.write('  {} = {},\n'.format(name, value))
      fp.write('};\n')
      fp.write('#endif // {}\n'.format(guard))

    for lang_code, table in rpkg.localizations.items():
      strfile = os.path.join(res_dir, 'strings_' + lang_code, strings_dir, strings_name + '.str')
      makedirs(strfile, parent = True)
      print('Writing {} ...'.format(os.path.relpath(strfile, res_dir)))
      with open(strfile, 'w') as fp:
        fp.write('STRINGTABLE ')
        if rpkg.name != 'c4d_symbols':
          fp.write(rpkg.name)
        fp.write('\n{\n')
        for symbol, string in table.items():
          # xxx: escape unicode characters
          fp.write('  {} "{}";\n'.format(symbol, escape_unicode(string)))
        fp.write('}\n')
