# Copyright (C) 2014-2016  Niklas Rosenstein
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

import os
import sys
import c4d

_added_paths = []
def add_path(path, module=sys):
  if not os.path.isabs(path):
    path = os.path.join(os.path.dirname(__file__), path)
  if path not in module.path:
    module.path.append(path)
    _added_paths.append((module, path))

# The third party modules in this plugin should be available globally.
add_path('lib/py-shroud')
add_path('lib/requests')

import shroud
add_path('lib', module=shroud)
add_path('lib/py-localimport', module=shroud)

def load_extensions():
  extensions = []
  ext_dir = os.path.join(os.path.dirname(__file__), 'ext')
  for file in os.listdir(ext_dir):
    if file.endswith('.py'):
      extensions.append(shroud.require(os.path.join(ext_dir, file)))
  return extensions

extensions = load_extensions()

def PluginMessage(msg_type, data):
  if msg_type == c4d.C4DPL_RELOADPYTHONPLUGINS:
    for mod, path in _added_paths:
      try: mod.path.remove(path)
      except ValueError: pass

  for extension in extensions:
    if hasattr(extension, 'PluginMessage'):
      extension.PluginMessage(msg_type, data)

  return True
