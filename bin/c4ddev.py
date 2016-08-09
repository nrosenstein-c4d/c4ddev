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

import argparse
import os
import sys

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')
sys.path.append(os.path.join(libdir, 'py-require'))
print(libdir)
import require
require.path.append(libdir)
require.path.append(os.path.join(libdir, 'py-localimport'))

def main():
  parser = argparse.ArgumentParser('c4ddev')
  subparsers = parser.add_subparsers(dest='command')
  symbols_parser = subparsers.add_parser('symbols')
  symbols_parser.add_argument('-f', '--format', default='class')
  symbols_parser.add_argument('-o', '--outfile')
  symbols_parser.add_argument('-d', '--res-dir', default=[], action='append')
  args = parser.parse_args()

  if args.command == 'symbols':
    resource = require('c4ddev/resource')
    if not args.res_dir:
      args.res_dir = ['res']
    resource.export_symbols(args.format, args.res_dir, outfile=args.outfile)
    return 0

  parser.error('invalid command: {0!r}'.format(args.command))

if __name__ == "__main__":
  sys.exit(main())
