#!/usr/bin/env python
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

import click
import json
import os
import require
import sys

# Bootup the c4ddev/ require package.
libdir = os.path.join(sys.prefix, 'c4ddev/lib')
if not os.path.isdir(libdir):
  libdir = os.path.normpath(__file__ + '../../../lib')
require.path.append(libdir)
require.path.append(os.path.join(libdir, 'py-localimport'))

resource = require('c4ddev/resource')
_pypkg = require('c4ddev/pypkg')

@click.group()
def cli():
  pass


@cli.command()
@click.option('-f', '--format', default='class')
@click.option('-o', '--outfile')
@click.option('-d', '--res-dir', multiple=True)
def symbols(format, outfile, res_dir):
  if res_dir:
    res_dir = ['res']
  resource.export_symbols(format, res_dir, outfile=outfile)


@cli.command()
@click.argument('files', metavar='RPKG', nargs=-1)
@click.option('-r', '--res', metavar='DIRETORY', default='res')
@click.option('--no-header', default=False)
def rpkg(files, res, no_header):
  if not files:
    click.echo("error: no input files", err=True)
    return 1
  resource.build_rpkg(files, res, no_header)


@cli.command()
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
