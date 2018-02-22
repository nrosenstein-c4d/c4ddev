# Copyright (c) 2015  Niklas Rosenstein
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
'''
This package contains the Cinema 4D IDE plugin and all its classes.
Contents of this package can be used to extend the plugin and to have
access to the underlying data and functions.
'''

from . import gui
from .script import ScriptEditor
from c4ddev import res

import os
import sys
import c4d
import datetime
import traceback


class Document(object):
  ''' This class represents a file that is being edited in the IDE
  editor window. '''

  Empty = 'empty'
  Loaded = 'loaded'
  Edited = 'edited'
  Error = 'error'

  Template = datetime.datetime.now().strftime(
    '# Copyright (C) %Y  {0}\n'
    '# All rights reserved.\n'
    '#\n'
    '# File: \n'
    '# Created: %Y-%m-%d\n'
    '# Last Modified: %Y-%m-%d\n'
    '# Description: \n'
    '\n'
    'import c4d\n'
    '\n'
    'def main():\n'
    '    pass\n'
    '\n'
    'if __name__ == "__main__":\n'
    '    main()\n').format(os.getenv('USERNAME', '<Name>'))

  def __init__(self, filename=None):
    super(Document, self).__init__()
    self.filename = filename
    self.content = Document.Template
    self.status = Document.Empty
    self.error_info = None
    self.traceback = None
    self.window = None

    if self.filename:
      self.load()

  def __repr__(self):
    return '<Document {0!r}>'.format(self.filename)

  def load(self, filename=None):
    if filename is not None:
      self.filename = filename
    if not self.filename:
      raise ValueError('Document.filename is not set')

    try:
      with open(self.filename, 'r') as fp:
        content = fp.read()
    except (IOError, OSError) as exc:
      self.status = Document.Error
      self.error_info = str(exc)
      return False
    else:
      self.content = content
      self.status = Document.Loaded
      self.error_info = None
      return True

  def save(self, filename=None):
    if filename is not None:
      self.filename = filename
    elif self.filename is None:
      raise ValueError('Document.filename is not set')

    try:
      with open(self.filename, 'w') as fp:
        fp.write(self.content)
    except (IOError, OSError) as exc:
      self.status = Document.Error
      self.error_info = str(exc)
      return False
    else:
      self.status = Document.Loaded
      self.error_info = None
      return True


class EditorWindow(c4d.gui.GeDialog):
  ''' This class implements the editor window. It can manage multiple
  documents and displays them in tabs. It contains a multiline edit
  text field to edit the active document and also shows the recent
  traceback information of that document. '''

  def __init__(self):
    super(EditorWindow, self).__init__()
    self.documents = []
    self.active_document = -1
    self.tabview = gui.TabView(self)
    self.new_document()

  def _update(self):
    doc = self.get_active_document()
    self.SetString(res.IDS_EDITOR_CODE, doc.content)

  def _tabview_getdata(self):
    for index, doc in enumerate(self.documents):
      active = (index == self.active_document)
      name = os.path.basename(doc.filename) if doc.filename else 'untitled'  # xxx: todo
      yield (active, name, doc)

  def new_document(self):
    self.add_document(Document())

  def add_document(self, doc, set_active=True):
    if not isinstance(doc, Document):
      raise TypeError('expected Document instance')
    if doc in self.documents:
      raise TypeError('already in the document list')
    assert not doc.window

    # Remove the empty documents from the list.
    for other in self.documents[:]:
      if other.status == Document.Empty:
        self.documents.remove(other)

    doc.window = self
    self.documents.append(doc)
    if set_active:
      self.set_active_document(doc)
    c4d.EventAdd()

  def remove_document(self, doc, confirm_close=True):
    if confirm_close and doc.status == Document.Edited:
      message = res.string('IDC_EDITOR_ASKCLOSE')
      result = c4d.gui.MessageDialog(message, c4d.GEMB_YESNOCANCEL)
      if result == c4d.GEMB_R_YES:
        self.save_document(doc)
      elif result == c4d.GEMB_R_CANCEL:
        return
    doc.window = None
    self.documents.remove(doc)
    if not self.documents:
      self.new_document()
    if self.active_document not in xrange(len(self.documents)):
      self.active_document = len(self.documents) - 1
    c4d.EventAdd()

  def get_active_document(self):
    try:
      return self.documents[self.active_document]
    except IndexError:
      return None

  def set_active_document(self, doc):
    if not isinstance(doc, Document):
      raise TypeError('doc must be Document')
    if doc not in self.documents:
      raise ValueError('Document not in document list')
    self.active_document = self.documents.index(doc)
    self.SetMultiLinePos(res.IDS_EDITOR_CODE, 0, 0)
    c4d.EventAdd()

  def save_document(self, doc):
    if doc.filename:
      doc.save()
      return True
    else:
      filename = c4d.storage.SaveDialog()
      if filename:
        doc.save(filename)
        return True
    return False

  def open_document(self):
    filename = c4d.storage.LoadDialog()
    if filename and os.path.isfile(filename):
      self.add_document(Document(filename))

  def run_code(self):
    doc = self.get_active_document()
    code = doc.content
    scope = {
      '__file__': doc.filename or '',
      '__name__': '__main__',
      'doc': c4d.documents.GetActiveDocument(),
    }
    scope['op'] = scope['doc'].GetActiveObject()
    try:
      exec compile(code, doc.filename or 'untitled', 'exec') in scope
    except BaseException as exc:
      doc.traceback = sys.exc_info()
      traceback.print_exc()

  def CreateLayout(self):
    self.GroupBeginInMenuLine()
    self.GroupEnd()
    self.AddUserArea(res.IDS_EDITOR_TABS, c4d.BFH_SCALEFIT)
    self.AttachUserArea(self.tabview, res.IDS_EDITOR_TABS)
    self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
    edit_style = c4d.DR_MULTILINE_MONOSPACED | c4d.DR_MULTILINE_PYTHON | \
      c4d.DR_MULTILINE_STATUSBAR | c4d.DR_MULTILINE_HIGHLIGHTLINE | \
      c4d.DR_MULTILINE_SYNTAXCOLOR
    self.AddMultiLineEditText(res.IDS_EDITOR_CODE,
      c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, style=edit_style)
    self.GroupEnd()
    return True

  def InitValues(self):
    self._update()
    return True

  def Command(self, param, bc):
    if param == res.IDS_EDITOR_CODE:
      doc = self.get_active_document()
      doc.content = self.GetString(param)
      c4d.EventAdd()
      return True
    return False

  def CoreMessage(self, msg, bc):
    if msg == c4d.EVMSG_CHANGE:
      self._update()
    return True


main_window = EditorWindow()
