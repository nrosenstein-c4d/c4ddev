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

import glob
import os
import re
import sys
import textwrap

TEMPLATE_CLASS = textwrap.dedent('''
  exec ("""class res(object):
   # Automatically generated with c4ddev.
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
   res=res()""")''')

TEMPLATE_FILE = textwrap.dedent('''
  # Automatically generated with c4ddev.

  import os
  import sys
  import c4d

  _frame = sys._getframe(1)
  while _frame and not '__res__' in _frame.f_globals:
    _frame = _frame.f_back

  project_path = os.path.dirname(_frame.f_globals['__file__'])
  resource = _frame.f_globals['__res__']

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
    path = os.path.join(*parts)
    if not os.path.isabs(path):
      path = os.path.join(project_path, path)
    return path

  def bitmap(*parts):
    bitmap = c4d.bitmaps.BaseBitmap()
    result, ismovie = bitmap.InitWith(file(*parts))
    if result != c4d.IMAGERESULT_OK:
      return None
    return bitmap

  file = path  # backwards compatibility

  {{symbols}}''')


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


def export_symbols(format, res_dir=None, outfile=None):
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
      fn(symbols, desc_symbols, fp)
  else:
    fn(symbols, desc_symbols, sys.stdout)
    print()


def format_symbols_json(symbols, desc_symbols, fp):
  all_syms = symbols.copy()
  all_syms.update(desc_symbols)
  json.dump(all_syms, fp)


def format_symbols_file(symbols, desc_symbols, fp):
  formatted = preformat_symbols(symbols, desc_symbols)
  print(render_template(TEMPLATE_FILE, symbols=formatted), file=fp)


def format_symbols_class(symbols, desc_symbols, fp):
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

  expr = r'^(.*)\{\{(\w+)\}\}'
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
