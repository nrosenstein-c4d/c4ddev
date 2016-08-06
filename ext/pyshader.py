# Copyright (C) 2015-2016  Niklas Rosenstein
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
__res__ = require('c4ddev/__res__')

import os, sys
import c4d
import traceback

from zlib import adler32

__author__ = 'Niklas Rosenstein <rosensteinniklas(at)gmail.com>'
__version__ = '1.0-dev'


class PyShader(c4d.plugins.ShaderData):
  ''' Cinema 4D shader plugin that executes Python code that can be
  edited during runtime in the shader parameters. '''

  PluginID = 1036204
  PluginName = 'c4ddev PyShader'
  PluginFlags = 0
  PluginDesc = 'nr_pyshader'

  def __init__(self):
    super(PyShader, self).__init__()
    self._scope = None
    self._code_hash = None

  def Init(self, sh):
    sh[c4d.NR_PYSHADER_CODE] = (
      '# c4ddev PyShader v{version} by Niklas Rosenstein\n'
      '# https://github.com/nr-plugins/c4ddev\n'
      '#\n'
      '# Note: Use print() as a function instead of as a statement\n'
      '\n'
      'import c4d\n'
      '\n'
      'def message(msg_type, data):\n'
      '    return True\n'
      '\n'
      'def init_render(ud, irs):\n'
      '    return c4d.INITRENDERRESULT_OK\n'
      '\n'
      'def free_render(ud):\n'
      '    pass\n'
      '\n'
      'def output(ud, cd, once):\n'
      '    return c4d.Vector(0.0, 0.0, 0.0)\n').format(version=__version__)
    return True

  def Message(self, sh, msg_type, data):
    if msg_type == c4d.MSG_DESCRIPTION_POSTSETPARAMETER:
      # Re-evaluate the shader code in case it changed.
      code = sh[c4d.NR_PYSHADER_CODE]
      code_hash = adler32(code)
      if code_hash != self._code_hash:
        self._scope = {'op': sh, 'doc': sh.GetDocument()}
        self._output = None
        try:
          exec compile(code, sh.GetName(), 'exec') in self._scope
        except BaseException as exc:
          self._scope = None
          traceback.print_exc()
          sh[c4d.NR_PYSHADER_INFO] = str(exc)
        else:
          self._code_hash = code_hash
          sh[c4d.NR_PYSHADER_INFO] = 'Ok'

    if self._scope is not None:
      return self._scope['message'](msg_type, data)
    return True

  def InitRender(self, sh, irs):
    if self._scope is not None:
      self._ud = {}
      self._first_output = True
      return self._scope['init_render'](self._ud, irs)
    return c4d.INITRENDERRESULT_OK

  def FreeRender(self, sh):
    if self._scope is not None:
      try:
        self._scope['free_render'](self._ud)
      finally:
        del self._ud
        del self._first_output

  def Output(self, sh, cd):
    if self._scope is not None:
      first_output = self._first_output
      if first_output:
        self._first_output = False
      return self._scope['output'](self._ud, cd, first_output)
    return c4d.Vector(1.0, 1.0, 0.0)

  def CopyTo(self, dest, snode, dnode, flags, trn):
    dest._scope = self._scope
    dest._code_hash = self._code_hash
    return True

  @classmethod
  def Register(cls):
    return c4d.plugins.RegisterShaderPlugin(
      cls.PluginID, cls.PluginName, cls.PluginFlags, cls, cls.PluginDesc)


PyShader.Register()
