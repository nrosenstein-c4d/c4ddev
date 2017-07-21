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
from six.moves.configparser import SafeConfigParser
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


cfg_filename = os.path.expanduser('~/.c4ddev.cfg')

def load_cfg():
  cfg = SafeConfigParser()
  if os.path.isfile(cfg_filename):
    cfg.read([cfg_filename])
  return cfg


def save_cfg(cfg):
  with open(cfg_filename, 'w') as fp:
    cfg.write(fp)
  os.chmod(cfg_filename, int('600', 8))


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
@click.option('--blob/--no-blob', is_flag=True, default=True)
@click.option('-e', '--entry-point', default='entrypoint', metavar='ENTRYPOINT')
@click.option('-c', '--compress', is_flag=True)
@click.option('-m', '--minify', is_flag=True)
@click.option('-o', '--output', metavar='FILENAME')
def build_loader(blob, entry_point, compress, minify, output):
  """
  Generate a Cinema 4D Python plugin that uses Node.py to load an entrypoint.
  """

  build_standalone = require('@nodepy/standalone-builder').build

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
    module = context.require({entry_point!r}, directory, is_main=True, exec_=False, exports=False)
    module.namespace.__res__ = __res__
    module.exec_()

  if hasattr(module.namespace, 'PluginMessage'):
    PluginMessage = module.namespace.PluginMessage
  ''').lstrip()

  result = template.format(
    version=version,
    nodepy_version=nodepy.__version__,
    nodepy_standalone_blob = build_standalone(
        compress=compress, minify=minify, fullblob=True, blob=blob),
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
@click.option('--trs', is_flag=True, help='Start the TeamRender Server.')
@click.option('--client', is_flag=True, help='Start the TeamRender Client.')
@click.option('--bp', '--bodypaint', is_flag=True, help='Start BodyPaint.')
@click.option('--cb', '--cinebench', is_flag=True, help='Start CineBench.')
@click.option('--ls', '--license-server', is_flag=True, help='Start the License Server.')
@click.option('--lite', is_flag=True, help='Start Cinema 4D Lite.')
@click.option('--demo', is_flag=True, help='Start the Cinema 4D Demo.')
@click.option('--student', is_flag=True, help='Start Cinema 4D Student.')
@click.option('--cine-ae', is_flag=True, help='Start CineRenderAE.')
@click.option('--cine-nem', is_flag=True, help='Start CineRenderNEM.')
@click.option('--cli', is_flag=True, help='Start the Cinema 4D Commandline.')
@click.pass_context
def run(ctx, args, trs, client, bodypaint, cinebench, license_server, lite,
        demo, student, cine_ae, cine_nem, cli):
  """
  Starts Cinema 4D, or one of its sub-applications.
  """

  if sum(map(bool, [trs, client, bodypaint, cinebench, license_server, lite,
                    student, cine_ae, cine_nem, cli])) > 1:
    ctx.fail('Incompatible arguments')

  if trs:
    exe = 'Cinema 4D TeamRender Server'
  elif client:
    exe = 'Cinema 4D TeamRender Client'
  elif bodypaint:
    exe = 'Bodypoint 3D'
  elif cinebench:
    exe = 'Cinebench'
  elif license_server:
    exe = 'Cinema 4D License Server'
  elif lite:
    exe = 'Cinema 4D Lite'
  elif student:
    exe = 'Cinema 4D Student'
  elif cine_ae:
    exe = 'CineRenderAE'
  elif cine_nem:
    exe = 'CineRenderNEM'
  elif cli:
    exe = 'Commandline'
  else:
    exe = 'Cinema 4D'

  if demo:
    exe += ' Demo'

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


@main.command()
@click.argument('titles', nargs=-1)
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-l', '--list', is_flag=True, help='List all registered plugin IDs.')
@click.option('--save', is_flag=True, help='Save the username and password in ~/.c4ddev.cfg file.')
@click.pass_context
def pluginid(ctx, titles, username, password, list, save):
  """
  Get one or more plugin IDs from the plugincafe. If the username and/or
  password are not specified on the command-line, they will be queried
  during execution.
  """

  if not titles and not list:
    print(ctx.get_help())
    return
  if list and titles:
    ctx.fail('-l,--list can not be used with retrieving new plugin IDs.')

  cfg = load_cfg()
  if not username:
    if cfg.has_option('plugincafe', 'username'):
      username = cfg.get('plugincafe', 'username')
    else:
      username = input("PluginCafe Username: ").strip()
      if not username: return
  if not password:
    if cfg.has_option('plugincafe', 'password'):
      password = cfg.get('plugincafe', 'password')
    else:
      password = getpass("PluginCafe Password: ")
      if not password: return

  if save:
    if not cfg.has_section('plugincafe'):
      cfg.add_section('plugincafe')
    cfg.set('plugincafe', 'username', username)
    cfg.set('plugincafe', 'password', password)
    save_cfg(cfg)

  session = requests.Session()

  def gettext(node):
    return re.sub('\s+', ' ', ' '.join(node.find_all(text=True))).strip()

  # Login.
  response = session.post(
    url = 'http://www.plugincafe.com/forum/login_user.asp',
    data = {'password': password, 'login': username, 'NS': 1})
  doc = bs4.BeautifulSoup(response.text, 'html.parser')
  err = doc.find('table', class_='errorTable')
  if err:
    msg = err.find_all('td')[-1]
    ctx.fail(gettext(msg))
  if 'successful login' not in response.text.lower():
    print(response.text)
    ctx.fail('Login failed, unknown error occured. Response HTML above.')

  if list:
    response = session.get('http://www.plugincafe.com/forum/developer.asp')
    doc = bs4.BeautifulSoup(response.text, 'html.parser')
    # Find the div that contains the Plugin ID table.
    node = doc.find(text=re.compile('Plugin IDS Assigned To:'))
    while node.name != 'div':
      node = node.parent
    # Print all plugin IDs there are.
    result = {}
    for row in node.find_all('table')[2].find_all('tr'):
      cells = row.find_all('td')
      title, pid = gettext(cells[0]), gettext(cells[1])
      result[title] = pid
      print('{}: {}'.format(title, pid))
    return result

  # Retrieve new plugin IDs.
  result = {}
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
    result[title] = int(match.group(1))
    print('{}: {}'.format(title, match.group(1)))

  return result


@main.command()
@click.argument('description_names', metavar='DESCRIPTION_NAME ...', nargs=-1)
@click.option('-O', '--object', 'object_names', multiple=True)
@click.option('-T', '--tag', 'tag_names', multiple=True)
@click.option('-X', '--shader', 'shader_names', multiple=True)
@click.option('-Gv', '--xnode', 'xnode_names', multiple=True)
@click.option('-M', '--material', 'material_names', multiple=True)
@click.option('--main', is_flag=True, help='Generate a main.cpp template.')
@click.option('-R', '--rpkg', is_flag=True, help='Create .rpkg files instead '
    'of description header and stringtable files.')
@click.option('--src', help='Source code directory. If not specified, '
    'defaults to src/ or source/, depending on which exists.')
@click.option('-P', '--pluginid', is_flag=True, help='Grab plugin IDs from '
    'the PluginCafe for the plugins that are being created.')
@click.option('--overwrite', is_flag=True)
@click.pass_context
def init(ctx, description_names, object_names, tag_names, shader_names,
         xnode_names, material_names, main, rpkg, src, pluginid, overwrite):
  """
  Create template source and description files for one or more Cinema 4D
  plugins.
  """

  if not src:
    if os.path.isdir('src'):
      src = 'src'
    else:
      src = 'source'
    print('source directory:', src)

  description_names = list(description_names or ())
  object_names = list(object_names or ())
  tag_names = list(tag_names or ())
  shader_names = list(shader_names or ())
  xnode_names = list(xnode_names or ())
  material_names = list(material_names or ())

  for name in description_names:
    c = name[0].lower()
    if c == 'o': object_names.append(name)
    elif c == 't': tag_names.append(name)
    elif c == 'x': shader_names.append(name)
    elif name[:2].lower() == 'gv': xnode_names.append(name)
    elif c == 'm': material_names.append(name)
    else:
      ctx.fail('Can not determined plugin type: {}'.format(name))

  descriptions = [('object', x) for x in object_names] + \
    [('tag', x) for x in tag_names] + \
    [('shader', x) for x in shader_names] + \
    [('xnode', x) for x in xnode_names] + \
    [('material', x) for x in material_names]
  description_nanes = [x[1] for x in descriptions]

  if pluginid:
    print('retrieving plugin IDs ...')
    ids = globals()['main'](['pluginid'] + description_names, standalone_mode=False)
    print(ids)
  else:
    ids = None

  def mkdir(path):
    if not os.path.isdir(path):
      print('mkdir:', path)
      os.makedirs(path)

  def write(filename, content, allow_overwrite=True):
    if not os.path.isfile(filename) or (overwrite and allow_overwrite):
      print('write:', filename)
      with open(filename, 'w') as fp:
        fp.write(content)
    elif allow_overwrite:
      print('warning: file "{}" already exists'.format(filename))

  mkdir(src)
  mkdir('res')
  mkdir('res/description')
  write('res/c4d_symbols.h', '#pragma once\nenum {};\n', False)
  if not rpkg:
    mkdir('res/strings_us/description')

  for kind, description in descriptions:
    if kind == 'object':
      base, props = 'Obase', ['ID_OBJECTPROPERTIES']
      parent = 'ObjectData'
    elif kind == 'tag':
      base, props = 'Tbase', ['ID_TAGPROPERTIES']
      parent = 'TagData'
    elif kind == 'shader':
      base, props = 'Xbase', ['ID_SHADERPROPERTIES']
      parent = 'ShaderData'
    elif kind == 'shader':
      base, props = 'Gvbase', ['ID_GVPROPERTIES', 'ID_GVPORTS']
      parent = 'GvOperatorData'
    elif kind == 'material':
      base, props = 'Mbase', ['ID_MATERIALPROPERTIES']
      parent = 'MaterialData'
    else:
      assert False

    content = 'CONTAINER {0} {{\n  NAME {0};\n  INCLUDE {1};\n'.format(description, base)
    for prop in props:
      content += '  GROUP {0} {{\n  }}\n'.format(prop)
    content += '}\n'
    write('res/description/{}.res'.format(description), content)

    clsname = '{0}Data'.format(description)
    content = '#include <c4d.h>\n#include "res/description/{}.h"\n\n'.format(description)
    content += 'class {0} : public {1} {{\n'.format(clsname, parent)
    content += 'public:\n  static NodeData* Alloc() { return NewObj(clsname); }\n'
    content += '}}\n\nBool Register{0}() {{\n'.format(clsname)
    content += '  return Register{0}Plugin({1}, /* TODO */);\n'.format(parent[:-4], description)
    content += '}\n'
    write('{0}/{1}.cpp'.format(src, description), content)

    plugid = None
    if ids:
      plugid = ids.get(description, None)
      if plugid is None:
        print('warning: did not receive a Plugin ID for', description)
    if plugid is None:
      plugid = '/* {0} PLUGIN ID HERE */'.format(description)

    if rpkg:
      content = 'ResourcePackage({0})\n{0}: {1}\n  us: {0}\n'.format(description, plugid)
      write('{0}/{1}.rpkg'.format(src, description), content)
    else:
      content = '#pragma once\nenum {{\n  {0} = {1},\n}};\n'.format(description, plugid)
      write('res/description/{}.h'.format(description), content)

      content = 'STRINGTABLE {0} {{\n  {0} "{0}";\n}}\n'.format(description)
      write('res/strings_us/description/{}.str'.format(description), content)


@main.command()
@click.argument('plugin', required=False)
@click.pass_context
def disable(ctx, plugin):
  """
  Disable the Cinema 4D PLUGIN by moving it to a `plugins_disabled`
  directory. Use the `c4ddev enable` command to reverse the process.
  If PLUGIN is not the name of a directory in the Cinema 4D plugins
  directory, the closest match will be used.

  When no PLUGIN is specified, a list of the directories in the
  plugins directory will be printed.
  """

  try:
    path = get_c4d_dir()
  except ValueError as e:
    print('error:', e)
    ctx.exit(1)

  from_ = os.path.join(path, 'plugins')
  to = os.path.join(path, 'plugins_disabled')

  _enable_disable(ctx, from_, to, plugin)


@main.command()
@click.argument('plugin', required=False)
@click.pass_context
def enable(ctx, plugin):
  """
  Enable a disabled plugin.
  """

  try:
    path = get_c4d_dir()
  except ValueError as e:
    print('error:', e)
    ctx.exit(1)

  from_ = os.path.join(path, 'plugins_disabled')
  to = os.path.join(path, 'plugins')

  _enable_disable(ctx, from_, to, plugin)


def _enable_disable(ctx, from_, to, plugin):
  if not os.path.isdir(from_):
    print('error: directory "{}/" does not exist.', os.path.basename(from_))
    ctx.exit(1)
  if not plugin:
    print('{}/'.format(os.path.basename(from_)))
    for name in os.listdir(from_):
      print('  -', name)
  else:
    choices = []
    for name in os.listdir(from_):
      if name.lower().startswith(plugin.lower()):
        choices.append(name)
    if not choices:
      print('error: no match for "{}" in "{}/"'.format(plugin, os.path.basename(from_)))
    elif len(choices) > 1:
      print('error: multiple matches for "{}" in "{}/"'.format(plugin, os.path.basename(from_)))
      for name in choices:
        print('  -', name)
    else:
      if not os.path.isdir(to):
        os.makedirs(to)
      plugin = choices[0]
      print('moving "{}" from "{}/" to "{}/"'.format(
        plugin, os.path.basename(from_), os.path.basename(to)))
      os.rename(os.path.join(from_, plugin), os.path.join(to, plugin))


if require.main == module:
  main()
