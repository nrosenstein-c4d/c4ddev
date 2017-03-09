# Copyright (c) 2017 Niklas Rosenstein
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
Build a Python Plugin loader skeleton that uses the currently installed
version of Node.py.
"""

import argparse
import json
import os

if require.main != module:
  raise RuntimeError('should not be require()d')

build_standalone = require('nodepy-standalone-builder').build

template = '''# Cinema 4D Python Plugin Loader
# Generated with c4ddev/scripts/build-loader.py v{version}
{nodepy_standalone_blob}

import os
directory = os.path.dirname(__file__)
context = nodepy.Context()
filename = context.resolve({entry_point!r}, directory, is_main=True)
module = context.load_module(filename, is_main=True)
'''

def main(argv=None):
  parser = argparse.ArgumentParser()
  parser.add_argument('-e', '--entry-point', default='entrypoint.py')
  parser.add_argument('-c', '--compress', action='store_true')
  parser.add_argument('-m', '--minify', action='store_true')
  parser.add_argument('-f', '--fullblob', action='store_true')
  args = parser.parse_args(argv)

  with open(os.path.join(__directory__, '../package.json')) as fp:
    version = json.load(fp)['version']

  nodepy_standalone_blob =
  print(template.format(
    version = version,
    nodepy_standalone_blob = build_standalone(
        compress=args.compress, minify=args.minify, fullblob=True),
    entry_point = args.entry_point))

main()
