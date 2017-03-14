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
Entry-point for when the C4DDev plugin is loaded by Cinema 4D.
"""

import os
import c4d
import sys

require.context.path.append(os.path.join(__directory__, 'lib'))
require('c4ddev/__res__', exports=False).namespace.exports = __res__

# Pre-load all components of the c4ddev library, since some require third
# party Python modules which can not be loaded at a later point when Node.py's
# localimpot context is no longer present.
require('c4ddev/pypkg')
require('c4ddev/resource')
require('c4ddev/utils')
require('c4ddev/scripting/localimport')

def load_extensions():
  extensions = []
  ext_dir = os.path.join(__directory__, 'plugins')
  for file in os.listdir(ext_dir):
    file = os.path.join(ext_dir, file)
    if file.endswith('.py'):
      extensions.append(require(file))
      continue
    file = os.path.join(file, 'main.py')
    if os.path.isfile(file):
      extensions.append(require(file))

  return extensions

def PluginMessage(msg_type, data):
  if msg_type == c4d.C4DPL_RELOADPYTHONPLUGINS:
    reload(require)
    for mod, path in _added_paths:
      try: mod.path.remove(path)
      except ValueError: pass

  for extension in extensions:
    if hasattr(extension, 'PluginMessage'):
      extension.PluginMessage(msg_type, data)

  return True

extensions = load_extensions()
sys.modules['c4ddev'] = module.namespace
