# Copyright (C) 2017  Niklas Rosenstein
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

from setuptools import setup, find_packages
from pip.req import parse_requirements

import functools
import os
import pip
import sys

# parse_requirements() interface has changed in Pip 6.0
if pip.__version__ >= '6.0':
  parse_requirements = functools.partial(
      parse_requirements, session=pip.download.PipSession())

def readme():
  if os.path.isfile('README.md') and any('dist' in x for x in sys.argv[1:]):
    if os.system('pandoc -s README.md -o README.rst') != 0:
      print('-----------------------------------------------------------------')
      print('WARNING: README.rst could not be generated, pandoc command failed')
      print('-----------------------------------------------------------------')
      if sys.stdout.isatty():
        input("Enter to continue... ")
    else:
      print("Generated README.rst with Pandoc")

  if os.path.isfile('README.rst'):
    with open('README.rst') as fp:
      return fp.read()
  return ''

def find_files(directory, strip='.'):
  """
  Using glob patterns in ``package_data`` that matches a directory can
  result in setuptools trying to install that directory as a file and
  the installation to fail.
  This function walks over the contents of *directory* and returns a list
  of only filenames found. The filenames will be stripped of the *strip*
  directory part.
  """

  result = []
  for root, dirs, files in os.walk(directory):
    for filename in files:
      filename = os.path.join(root, filename)
      result.append(os.path.relpath(filename, strip))
  return result

def as_data_files(root, files):
  """
  Prepares all files as a list of data_files that will be copied into *roo*.
  Requires that all filenames in *files* are relative.
  """

  dirs = {}
  for filename in files:
    dirname = os.path.dirname(filename)
    dirs.setdefault(dirname, []).append(filename)
  result = []
  for dirname, files in dirs.items():
    result.append((os.path.join(root, dirname), files))
  return result

# Collect the files to install.
files = find_files('lib/c4ddev')

setup(
  name = 'c4ddev',
  version = '1.2.0',
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'Cinema 4D plugin development tools',
  long_description = readme(),
  url = 'https://github.com/NiklasRosenstein/c4ddev',
  install_requires = [str(x.req) for x in parse_requirements('requirements.txt')],
  package_dir = {'': 'cli'},
  packages = ['c4ddev'],
  entry_points = dict(
    console_scripts = [
      'c4ddev = c4ddev.__main__:main'
    ]
  ),
  data_files = as_data_files('c4ddev', files)
)
