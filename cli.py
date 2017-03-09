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

if require.main != module:
  raise RuntimeError('should not be require()d')

import click
import json
import nodepy
import os
import sys
import textwrap

with open(os.path.join(__directory__, 'package.json')) as fp:
  version = json.load(fp)['version']

resource = require('./lib/resource')
_pypkg = require('./lib/pypkg')

@click.group()
def main():
  pass


@main.command()
@click.option('-f', '--format', default='class')
@click.option('-o', '--outfile')
@click.option('-d', '--res-dir', multiple=True)
def symbols(format, outfile, res_dir):
  if not res_dir:
    res_dir = ['res']
  resource.export_symbols(format, res_dir, outfile=outfile)


@main.command()
@click.argument('files', metavar='RPKG', nargs=-1)
@click.option('-r', '--res', metavar='DIRETORY', default='res')
@click.option('--no-header', default=False)
def rpkg(files, res, no_header):
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
@click.option('-e', '--entry-point', default='entrypoint.py', metavar='ENTRYPOINT')
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
  context = nodepy.Context()
  context.register_binding('nodepy', nodepy)
  context.register_binding('localimport', nodepy.localimport)
  filename = context.resolve({entry_point!r}, directory, is_main=True)
  module = context.load_module(filename, is_main=True, exec_=False)
  module.namespace.__res__ = __res__
  module.exec_()
  ''').lstrip()

  result = template.format(
    version=version,
    nodepy_version=nodepy.__version__,
    nodepy_standalone_blob = build_standalone(
        compress=compress, minify=minify, fullblob=True),
    entry_point=entry_point)

  if output:
    with open(output, 'w') as fp:
      fp.write(result)
  else:
    print(result)


main()
