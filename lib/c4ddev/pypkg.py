# Copyright (C) 2015 Niklas Rosenstein
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

from __future__ import print_function

import errno
import glob
import json
import os
import pipes
import py_compile
import random
import re
import shlex
import shutil
import subprocess
import sys
import zipfile


# =====================================================================
#  Resource symbol stuff
# =====================================================================

def parse_symbols(filename_or_fp):
  if isinstance(filename_or_fp, str):
    with open(filename_or_fp) as fp:
      return parse_symbols_string(fp.read())
  else:
    return parse_symbols_string(filename_or_fp.read())


def parse_symbols_string(string):
  ''' Parses a Cinema 4D resource symbol header and returns a
  dictionary that maps the symbol names with their ID and a list that
  contains all symbols that are masked by other fields declared later.

  Returns:
    tuple: `(dict, list)` '''

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
  ''' Returns a dictionary with various contents about a plugin's
  resource folder. Returns None if there is not resource folder. '''

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


def export_res_symbols(format, res_dir='res', outfile=None):
  ''' Parses the symbols of one or more resource directories
  and formats them according to *format*.

  :param format: ``json``, ``class`` or ``file``
  :param res_dir: A string pointing to a C4D plugin resource
    directory or a list of such. Defaults to the ``res/``
    directory of the currently executed module.
  :param outfile: The output file name or None to print to stdout. '''

  if format not in ('json', 'file', 'class'):
    raise ValueError('invalid format: {0!r}'.format(format))

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
      raise ValueError('no resource directory in {!r}'.format(dirname))

    merge_symbols(files['c4d_symbols'], symbols)
    for filename in files['description']:
      merge_symbols(filename, desc_symbols)

  # Unpack the values from the (value, filename) tuples.
  unpack = lambda x: dict((k, v) for k, (v, __) in x.items())
  symbols = unpack(symbols)
  desc_symbols = unpack(desc_symbols)

  fn = globals()['symbols_format_' + format]
  if outfile:
    with open(outfile, 'w') as fp:
      fn(symbols, desc_symbols, fp)
  else:
    fn(symbols, desc_symbols, sys.stdout)
    print()


def symbols_format_json(symbols, desc_symbols, fp):
  all_syms = symbols.copy()
  all_syms.update(desc_symbols)
  json.dump(all_syms, fp)


def symbols_format_file(symbols, desc_symbols, fp):
  template = load_template('symbols_file')
  formatted = symbols_preformat(symbols, desc_symbols)
  print(render_template(template, symbols=formatted), file=fp)


def symbols_format_class(symbols, desc_symbols, fp):
  template = load_template('symbols_class')
  formatted = symbols_preformat(symbols, desc_symbols)
  print(render_template(template, symbols=formatted), file=fp)


def symbols_preformat(symbols, desc_symbols):
  def preprocess(symbols):
    if not symbols: return
    for name, value in sorted(symbols.items(), key=lambda x: (x[1], x[0])):
      if not name.startswith('_'):
        yield name + ' = ' + str(value)
  formatted = []
  formatted.extend(preprocess(symbols))
  formatted.extend('')
  formatted.extend(preprocess(desc_symbols))
  if not symbols and not desc_symbols:
    formatted.append('pass')
  return '\n'.join(formatted)


def load_template(name):
  ''' Loads the contents of a template from the `resource` directory. '''

  dirname = os.path.dirname(__file__)
  filename = os.path.join(dirname, 'resource', name + '.template')
  with open(filename, 'r') as fp:
    return fp.read()


def render_template(__template_string, **context):
  ''' Renders the template string *__template_string* into a new string
  replacing variables annotated with ``{{varname}}`` from variables
  in the *context*. The indentation of the variables is kept. '''

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


# =====================================================================
#  Py-Compile Stuff
# =====================================================================

def getsuffix(filename):
  index = filename.rfind('.')
  if index > filename.replace('\\', '/').rfind('/'):
    return filename[index:]
  return ''


def shell_quote(s):
  if os.name == 'nt' and os.sep == '\\':
    s = s.replace('"', '\\"')
    if re.search('\s', s):
      s = '"' + s + '"'
    return s
  else:
    return pipes.quote(s)


def shell_run(command, **kwargs):
  if isinstance(command, (list, tuple)):
    command = ' '.join(shell_quote(x) for x in command)
  print(command)
  return subprocess.call(command, shell=True, **kwargs)


def get_pyfile_pair(filename):
  ''' Given the filename of a Python source or byte compiled filename,
  returns a pair of the source and byte compiled filename. '''

  if filename.endswith('.py'):
    filename = filename[:-3]
  elif filename.endswith('.pyc'):
    filename = filename[:-4]
  else:
    raise ValueError('filename does not end with .py or .pyc')

  return (filename + '.py', filename + '.pyc')


def bytecompile(pybin, source, outdir=None):
  ''' Compiles the specified *source* file or package directory to the
  output file (or package directry) to the specified output directory
  *outdir*. Regardless of PEP 3147, this will always place the byte
  compiled files in the old-style place. '''

  if pybin is not None:
    if outdir is None:
      outdir = os.path.dirname(source)
    command = [pybin, __file__, 'bytecompile', source, outdir]
    code = shell_run(command)
    if code != 0:
      raise RuntimeError('{} exited with {}'.format(command, code))

  def recurse(filename, basedir):
    if os.path.isfile(filename) and filename.endswith('.py'):
      cfile = filename[:-3] + '.pyc'
      cfile = os.path.join(outdir, os.path.relpath(cfile, basedir))
      print("  [c]", os.path.relpath(filename))
      py_compile.compile(filename, cfile)
    elif os.path.isdir(filename):
      for item in os.listdir(filename):
        recurse(os.path.join(filename, item), basedir)

  print("Bytecompiling", os.path.relpath(source))
  recurse(source, os.path.dirname(source))


def bdist_egg(pybin, package, outdir, exclude_source=True, quiet=True):
  ''' Assuming *package* is the path to a directory that contains a
  `setup.py` script, this script will generate a Python binary egg
  distribution of the package to the specified *outdir*. '''

  if not os.path.isdir(outdir):
    os.makedirs(outdir)
  command = [pybin, 'setup.py']
  if quiet:
    command.append('-q')
  command += ['bdist_egg', '--dist-dir', outdir]
  if exclude_source:
    command.append('--exclude-source-files')
  print("\nCreating Binary distribution of", os.path.relpath(package),
    "at", os.path.relpath(outdir))

  code = shell_run(command, cwd=package)
  if code != 0:
    raise RuntimeError('{} exited with {}'.format(command, code))


def create_egg(pybin, source, dest, exclude_source=True):
  ''' Creates a Python Egg (without EGG-INFO) from the specified *source*
  python module using the specified *pybin*. The egg will be saved to *dest*.
  Unlike `bdist_egg()`, this function really creates the zipfile at *dest*.

  If *source* is a list, its items are assumed to be filenames instead
  that are all supposed to be packed into the output egg. '''

  if not source:
    raise ValueError('no sources specified')
  if isinstance(source, str):
    source = [source]

  if pybin is not None:
    command = shlex.split(pybin) + [__file__, 'create_egg'] + source + [dest, str(bool(exclude_source))]
    code = shell_run(command)
    if code != 0:
      raise RuntimeError('{} exited with {}'.format(command, code))
    return 0

  dirname = os.path.dirname(dest)
  if not os.path.exists(dirname):
    os.makedirs(dirname)

  # Alternative for PyZipFile.writepy() do ignore missing files, eg.
  # when a file can not be compiled due to a SyntaxError.
  # TODO: Options to control behaviour (strict/loose).
  def writepy(egg, path, basename=''):
    if os.path.isfile(path) and path.endswith('.py'):
      try:
        egg.writepy(path, basename)
      except OSError as exc:
        if exc.errno == errno.ENOENT:
          print('Warning:', exc)
    elif os.path.isdir(path):
      basename = (basename + '/' + os.path.basename(path)).lstrip('/')
      for name in os.listdir(path):
        name = os.path.join(path, name)
        writepy(egg, name, basename)

  print("\nCreating python egg at", os.path.relpath(dest))
  egg = zipfile.PyZipFile(dest, 'w')
  for filename in source:
    # Make sure that the file/s is/are being recompiled.
    if filename.endswith('.py'):
      bin_file = get_pyfile_pair(filename)[1]
      if os.path.isfile(bin_file):
        os.remove(bin_file)
    elif os.path.isdir(filename):
      purge(filename)

    print("  [+]", filename)
    if not os.path.exists(filename):
      raise IOError('does not exist: {0}'.format(filename))
    writepy(egg, filename)
    #egg.writepy(filename)
    if not os.path.isdir(filename):
      continue

    parent_dir = os.path.dirname(filename)

    # PyZipFile.writepy() already works recursively, but it only
    # takes Python files into consideration. The module directory
    # may contain additional data files which we want to include.
    for root, dirs, files in os.walk(filename):
      arcroot = os.path.relpath(root, parent_dir)
      for fn in files:
        if getsuffix(fn) not in ('.py', '.pyc', '.pyo'):
          arcname = os.path.join(arcroot, fn)
          print("     [+]", arcname)
          egg.write(os.path.join(root, fn), arcname)

  return 0


def purge(directories, suffix='.pyc'):
  ''' Purge the specified *directories* and all its subfolders from
  byte-compile python cache folders. *directories* may also be a string
  of a single directory. '''

  if isinstance(directories, str):
    directories = [directories]

  def recurse(dirname):
    if os.path.isfile(dirname):
      if dirname.endswith('.py') or dirname.endswith('.pyc'):
        py, pyc = get_pyfile_pair(dirname)
        if os.path.isfile(pyc):
          os.remove(pyc)
    elif os.path.isdir(dirname):
      for item in os.listdir(dirname):
        item = os.path.join(dirname, item)
        if item.endswith(suffix) and os.path.isfile(item):
          os.remove(item)
        elif os.path.isdir(item):
          recurse(item)

  for dirname in directories:
    recurse(dirname)


class Egg(object):
  ''' This class is used to describe the build information for a
  Python egg. Note that eggs can also be created without putting
  them into a Zipfile. '''

  def __init__(self, files, base_dir=None, zipped=True):
    self.files = files
    self.zipped = zipped
    self.base_dir = base_dir

  def build(self, pybin, pyversion, outfile):
    if os.path.isfile(outfile):
      os.remove(outfile)
    elif os.path.isdir(outfile):
      shutil.rmtree(outfile)

    files = []
    for file in self.files:
      if not os.path.isabs(file) and self.base_dir:
        file = os.path.join(self.base_dir, file)
      files.append(file)

    create_egg(pybin, files, outfile)
    if not self.zipped:
      dirname = os.path.dirname(outfile)
      tempdir = os.path.join(dirname, '.temp_egg_' + str(random.randint(0, 999)))
      if not os.path.isdir(tempdir):
        os.makedirs(tempdir)
      with zipfile.ZipFile(outfile) as fp:
        fp.extractall(tempdir)
      os.remove(outfile)
      os.rename(tempdir, outfile)

    return outfile

# =====================================================================
#  Python source protection
# =====================================================================

def protect_pyp(c4d_exe, filename):
  ''' Runs the Cinema 4D source protect over the specified *filename*.
  Important: Requires the Apex plugin installed. '''

  c4d_exe = os.path.abspath(c4d_exe)
  cwd = os.path.dirname(c4d_exe)
  command = [app, '-apex-protect-source', filename, '-nogui']
  code = shell_run(command, cwd=cwd)
  if code != 0:
    raise RuntimeError('{} exited with {}'.format(command, code))

# =====================================================================
#  Main - invoked by some functions in this script in new processes
# =====================================================================

def main():
  if sys.argv[1] == 'bytecompile':
    bytecompile(None, sys.argv[2], sys.argv[3])
  elif sys.argv[1] == 'create_egg':
    sources = sys.argv[2:-2]
    dest = sys.argv[-2]
    exclude_source = True if sys.argv[-1] == 'True' else False
    create_egg(None, sources, dest, exclude_source)
  else:
    print("error: Unexpected command", sys.argv[1], file=sys.stderr)


if __name__ == "__main__":
  main()
