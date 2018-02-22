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
from c4ddev import res
from zlib import adler32
from .pyobject import PyObjectEditor

import os, sys
import c4d
import traceback
import types

__res__ = res.__res__


class PyShader(c4d.plugins.ShaderData):
  ''' Cinema 4D shader plugin that executes Python code that can be
  edited during runtime in the shader parameters. '''

  PluginID = 1036204
  PluginName = 'PyShader'
  PluginFlags = c4d.PLUGINFLAG_HIDEPLUGINMENU
  PluginDesc = 'nr_pyshader'
  Editor = PyObjectEditor(None, title='PyShader Editor', target_id=res.NR_PYSHADER_CODE)

  def __init__(self):
    super(PyShader, self).__init__()
    self.first_output = False
    self.customdata = None
    self.scope = None
    self.code_hash = None

  def _reload(self, sh):
    # Re-evaluate the shader code in case it changed.
    code = sh[res.NR_PYSHADER_CODE]
    code_hash = adler32(code)
    if code_hash != self.code_hash:
      self.scope = types.ModuleType(sh.GetName())
      try:
        exec(compile(code, sh.GetName(), 'exec'), vars(self.scope))
      except BaseException as exc:
        traceback.print_exc()
        sh[res.NR_PYSHADER_INFO] = str(exc)
      else:
        sh[res.NR_PYSHADER_INFO] = ''

  def Init(self, sh):
    with open(res.path('res/PyShader.py')) as fp:
      sh[res.NR_PYSHADER_CODE] = fp.read()
    return True

  def Message(self, sh, msg, data):
    if msg == c4d.MSG_DESCRIPTION_POSTSETPARAMETER:
      self._reload(sh)
    if msg == c4d.MSG_DESCRIPTION_COMMAND:
      id = data['id'][0].id
      if id == res.NR_PYSHADER_OPENEDITOR:
        self.Editor.SetTarget(sh)
        self.Editor.Open(c4d.DLG_TYPE_ASYNC, self.PluginID, 250, 200, 600, 500)
    if self.scope and hasattr(self.scope, 'Message'):
      self.scope.Message(sh, msg, data)
    return True

  def InitRender(self, sh, irs):
    self._reload(sh)
    self.customdata = {}
    self.first_output = True
    if self.scope and hasattr(self.scope, 'InitRender'):
      res = self.scope.InitRender(sh, irs, self.customdata)
    else:
      res = None
    if res is None:
      res = c4d.INITRENDERRESULT_OK
    return res

  def FreeRender(self, sh):
    if self.scope and hasattr(self.scope, 'FreeRender'):
      try:
        self.scope.FreeRender(sh, self.customdata)
      finally:
        self.first_output = False
        self.customdata = None

  def Output(self, sh, cd):
    output = getattr(self.scope, 'Output')
    if output is not None:
      try:
        return output(sh, cd, self.customdata, self.first_output)
      finally:
        self.first_output = False
    return c4d.Vector(1.0, 1.0, 0.0)

  @classmethod
  def Register(cls):
    return c4d.plugins.RegisterShaderPlugin(
      cls.PluginID, cls.PluginName, cls.PluginFlags, cls, cls.PluginDesc)


PyShader.Register()
