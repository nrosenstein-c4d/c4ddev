#!node.py
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

from __future__ import print_function
from six.moves import input
from getpass import getpass

import bs4
import click
import json
import nodepy
import os
import re
import requests
import subprocess
import sys
import textwrap

try:
  from urllib.request import urlopen
except ImportError:
  from urllib2 import urlopen

try:
  from shlex import quote as _quote
except ImportError:
  from pipes import quote as _quote

with open(os.path.join(__directory__, 'package.json')) as fp:
  version = json.load(fp)['version']

resource = require('./lib/c4ddev/resource')
_pypkg = require('./lib/c4ddev/pypkg')


def quote(s):
  if os.name == 'nt' and os.sep == '\\':
    s = s.replace('"', '\\"')
    if re.search('\s', s):
      s = '"' + s + '"'
  else:
    s = _quote(s)
  return s


def get_c4d_dir(c4d_dir=None):
  if not c4d_dir:
    # Search the parent directories.
    c4d_dir = os.getcwd()
    while True:
      res_modules = os.path.join(c4d_dir, 'resource/modules')
      if os.path.isdir(res_modules):
        break
      dirname = os.path.dirname(c4d_dir)
      if dirname == c4d_dir:
        raise ValueError('C4D application directory could not be determined')
      c4d_dir = dirname
  return c4d_dir


def get_c4d_python(c4d_dir):
  # TODO: Support R15 with the old folder structure.
  name = 'Python.win64.framework' if os.name == 'nt' else 'Python.mac.framework'
  # TODO: Make sure that 'python' is the right executable name on Mac OS.
  binname = 'python.exe' if os.name == 'nt' else 'python'
  return os.path.join(c4d_dir, 'resource/modules/python', name, binname)


@click.group()
def main():
  pass


@main.command()
@click.option('-f', '--format', default='class', metavar='FORMAT',
    help='The output format, one of {class,file,json}. Defaults to class.')
@click.option('-o', '--outfile', metavar='FILENAME')
@click.option('-d', '--res-dir', metavar='DIRECTORY', multiple=True,
    help='One or more resource directories to parse for symbols. If the '
    'option is not specified, `res/` will be used.')
def symbols(format, outfile, res_dir):
  """
  Extracts resource symbols.
  """

  if not res_dir:
    res_dir = ['res']
  resource.export_symbols(format, res_dir, outfile=outfile)


@main.command()
@click.argument('files', metavar='RPKG', nargs=-1)
@click.option('-r', '--res', metavar='DIRETORY', default='res')
@click.option('--no-header', default=False)
def rpkg(files, res, no_header):
  """
  Converts a resource package file to description resource files.
  """

  if not files:
    click.echo("error: no input files", err=True)
    return 1
  resource.build_rpkg(files, res, no_header)


@main.command()
@click.argument('config', default='.pypkg')
def pypkg(config):
  """
  Reads a JSON configuration file, by default named `.pypkg`, and uses
  that information to build a Python Egg from the distributions specified in
  the file.

  # Example Configuration

  \b
    {
      // required fields
      "output": "res/pymodules-{target}.egg",
      "include": [
        "devel/res.py",
        "devel/requests/requests",
        "etc.."
      ]
      // default fields
      "zipped": true,
      "targets": {
        "2.6": "python2.6",
        "2.7": "python2.7"
      },
    }
  """

  with open(config) as fp:
    config = json.load(fp)
  config.setdefault('zipped', True)
  config.setdefault('targets', {'2.6': 'python2.6', '2.7': 'python2.7'})

  egg = _pypkg.Egg(config['include'], None, config['zipped'])

  for target, binary in config['targets'].items():
    outfile = config['output'].format(target=target)

    # TODO: Support setuptools packages
    #for package in setuptools_packages:
    #  if not os.path.isabs(package):
    #    package = os.path.join(source_dir, package)
    #  bdist_egg(pybin, package, outdir)
    #  # XXX: Find output filename of egg.

    egg.build(binary, target, outfile)
    _pypkg.purge(egg.files)


@main.command("build-loader")
@click.option('-e', '--entry-point', default='entrypoint', metavar='ENTRYPOINT')
@click.option('-c', '--compress', is_flag=True)
@click.option('-m', '--minify', is_flag=True)
@click.option('-o', '--output', metavar='FILENAME')
def build_loader(entry_point, compress, minify, output):
  """
  Generate a Cinema 4D Python plugin that uses Node.py to load an entrypoint.
  """

  build_standalone = require('nodepy-standalone-builder').build

  template = textwrap.dedent('''
  # Cinema 4D Python Plugin Loader
  # Generated with c4ddev/scripts/build-loader.py v{version}

  # Node.py v{nodepy_version}
  {nodepy_standalone_blob}

  import os
  directory = os.path.dirname(__file__)
  context = nodepy.Context(directory)
  context.register_binding('nodepy', nodepy)
  context.register_binding('localimport', nodepy.localimport)
  with context:
    filename = context.resolve({entry_point!r}, directory, is_main=True)
    module = context.load_module(filename, is_main=True, exec_=False)
    module.namespace.__res__ = __res__
    module.exec_()

  if hasattr(module.namespace, 'PluginMessage'):
    PluginMessage = module.namespace.PluginMessage
  ''').lstrip()

  result = template.format(
    version=version,
    nodepy_version=nodepy.__version__,
    nodepy_standalone_blob = build_standalone(
        compress=compress, minify=minify, fullblob=True),
    entry_point=str(entry_point))

  if output:
    with open(output, 'w') as fp:
      fp.write(result)
  else:
    print(result)


@main.command("get-pip")
@click.option('--c4d', metavar='DIRECTORY')
def get_pip(c4d):
  """
  Installs Pip into the Cinema 4D Python distribution. Specify the path to
  Cinema 4D explicitly or run this command from inside the Cinema 4D application
  directory.
  """

  c4d = get_c4d_dir(c4d)
  python = get_c4d_python(c4d)

  print('Grabbing recent get-pip.py ...')
  with urlopen('https://bootstrap.pypa.io/get-pip.py') as fp:
    script = fp.read()

  print('Running get-pip.py ...')
  process = subprocess.Popen([python, '-'], stdin=subprocess.PIPE)
  process.communicate(input=script)
  res = process.wait()
  if res != 0:
    print('Error: get-pip.py failed')


@main.command(context_settings={'ignore_unknown_options': True})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('--c4d', metavar='DIRECTORY')
def pip(c4d, args):
  """
  Invokes Pip in the current Cinema 4D Python distribution. Must be used from
  inside the Cinema 4D applications directory or specified with --c4d.
  """

  c4d = get_c4d_dir(c4d)
  python = get_c4d_python(c4d)
  res = subprocess.call([python, '-m', 'pip'] + list(args))
  sys.exit(res)


@main.command(context_settings={'ignore_unknown_options': True})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('-e', '--exe', default='CINEMA 4D',
    help='Name of the C4D executable to run. Defaults to "CINEMA 4D".')
def run(exe, args):
  """
  Starts C4D.
  """

  c4d = get_c4d_dir()
  if sys.platform.startswith('win32'):
    exe = os.path.join(c4d, exe)
    if not exe.endswith('.exe'):
      exe += '.exe'
    cmd = [exe] + list(args)
    cmd = 'start /b /wait "parentconsole" ' + ' '.join(quote(x) for x in cmd)
  elif sys.platform.startswith('darwin'):
    if exe.endswith('.app'):
      name = exe = exe[:-4]
    exe = os.path.join(c4d, exe + '.app', 'Contents', 'MacOS', name)
    cmd = [exe] + args
  else:
    print('error: unsupported platform:', sys.platform)
    sys.exit(1)

  res = subprocess.call(cmd, shell=isinstance(cmd, str))
  sys.exit(res)


@main.command('source-protector')
@click.argument('filenames', metavar='FILENAME [FILENAME [...]]', nargs=-1)
@click.pass_context
def source_protector(ctx, filenames):
  """
  Protect .pyp files (C++ extensions must installed).
  """

  if not filenames:
    ctx.fail('no input files')
  args = ['--', '-nogui']
  for fname in filenames:
    args.append('-c4ddev-protect-source')
    args.append(os.path.abspath(fname))
  return run(args)


@main.command('get-pluginid')
@click.argument('titles', nargs=-1)
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.pass_context
def get_pluginid(ctx, titles, username, password):
  """
  Get one or more plugin IDs from the plugincafe. If the username and/or
  password are not specified on the command-line, they will be queried
  during execution.
  """

  if not titles:
    print(ctx.get_help())
    return
  if not username:
    username = input("PluginCafe Username: ").strip()
    if not username: return
  if not password:
    password = getpass("PluginCafe Password: ")
    if not password: return

  session = requests.Session()
  response = session.post(
    url = 'http://www.plugincafe.com/forum/login_user.asp',
    data = {'password': password, 'login': username, 'NS': 1})

  def gettext(node):
    return re.sub('\s+', ' ', ' '.join(node.find_all(text=True))).strip()

  doc = bs4.BeautifulSoup(response.text, 'html.parser')
  err = doc.find('table', class_='errorTable')
  if err:
    msg = err.find_all('td')[-1]
    ctx.fail(gettext(msg))
  if 'successful login' not in response.text.lower():
    print(response.text)
    ctx.fail('Login failed, unknown error occured. Response HTML above.')

  for title in titles:
    title = title.strip()
    if len(title) < 3 or len(title) > 100:
      ctx.fail('title must be at least 3 characters and at max 100 characters')
    response = session.post(
      url = 'http://www.plugincafe.com/forum/developer.asp',
      data = {'pname': title, 'formaction': 'Get PluginID'}
    )
    match = re.search('your\s+plugin\s+number\s+for.*?is:\s*(\d+)', response.text, re.I)
    if not match:
      sys.stdout.buffer.write(response.text.encode('utf8'))
      ctx.fail('Plugin ID for "{}" could not be retrieved. Response HTML above.'.format(title))
    print('{}: {}'.format(title, match.group(1)))


if require.main == module:
  main()
