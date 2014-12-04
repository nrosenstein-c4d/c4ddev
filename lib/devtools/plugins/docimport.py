# -*- coding: utf8 -*-
#
# Copyright (C) 2014  Niklas Rosenstein
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
This file implements a Cinema 4D plugin and a Python interface for
loading Python packages and modules from a Cinema 4D scene local
directory.

Instead of installing each and every Python package to the Cinema 4D
preferences folder, you can keep it tied to your scene files. From a
Python Generator or Python Tag, you can now simply do

..code-block:: python

    from devtools.plugins import docimport
    with docimport.importer(doc):
        import package_a
        from package_b import foo
'''

from . import registrar
from .. import utils

import os
import sys
import c4d
import glob
import functools
import contextlib


class DocImportMessageData(c4d.plugins.MessageData):
    ''' This class implements keeping track of the module dictionaries
    for the documents in the Cinema 4D document list. '''

    PLUGIN_ID = 1034170
    PLUGIN_NAME = "devtools.plugins.DocImportMessageData"
    PLUGIN_INFO = 0

    registered_instance = None

    def __init__(self):
        super(DocImportMessageData, self).__init__()
        self.contexts = utils.AtomDict()

        # A reference to the last document that was active in
        # Cinema 4D.
        self.last_doc = None

    def get_context(self, doc):
        ''' Finds (or creates) the module dictionary for the Cinema 4D
        document *doc* and returns it. This module cache is cleaned
        from all Cinema 4D documents that are no longer alive.

        .. note:: This function stores a real reference of the document,
            so you should use :func:`c4d.documents.KillDocument` to
            kill the document and invalidate the reference.
        '''

        try:
            return self.contexts[doc]
        except KeyError:
            context = ScriptingContext(doc)
            self.contexts[doc] = context
            return context

    def clean(self):
        ''' Cleans the module cache of all documents that are no
        longer alive. '''

        new_contexts = utils.AtomDict()
        for key, value in self.contexts.items():
            if key():
                new_contexts[key] = value
        self.contexts = new_contexts

    # c4d.plugins.MessageData

    def CoreMessage(self, msg_type, data):
        if msg_type == c4d.EVMSG_CHANGE:
            doc = c4d.documents.GetActiveDocument()
            if self.last_doc is None or not self.last_doc.IsAlive() or self.last_doc != doc:
                self.clean()
            self.last_doc = doc
        return True


class ScriptingContext(object):
    ''' This class represents a scripting context for a Cinema 4D
    document. It is stored in the :class:`DocImportMessageData`
    for each document. '''

    def __init__(self, doc):
        super(ScriptingContext, self).__init__()
        self.doc = doc
        self.modules = {}

    @contextlib.contextmanager
    def __call__(self, libpath='python', autoeggs=False):
        ''' This is a context-manager for importing modules from a
        Python Generator or Tag for the current document. The imported
        modules will be stripped from :data:`sys.modules` to prevent
        clashes with other modules and are instead moved to the
        :attr:`modules` dictionary of this instance.

        :param libpath:
        :param autoeggs:
        :raise EnvironmentError: If the Cinema 4D document is not saved. '''

        # Read the directory name where the document is saved.
        dirname = self.doc.GetDocumentPath()
        if not dirname:
            raise EnvironmentError('document is not saved')

        # Determine that paths that will be added to sys.path.
        libpath = [os.path.join(dirname, libpath)]
        if autoeggs:
            libpath.extend(glob.glob(os.path.join(libpath[0], '*.egg')))

        # Udpate sys.path
        old_path = sys.path[:]
        sys.path[:] = libpath + sys.path

        yield

        # Restore the old sys.path.
        sys.path[:] = old_path

        # Move any modules that have been imported from the library
        # directory to the document module dictionary.
        transfer = []
        for name, mod in sys.modules.items():
            # Check if the module was imported from one of the
            # added paths and add it to the transfer list if it is.
            for path in libpath:
                if utils.is_local_module(name, mod, path):
                    transfer.append((name, mod))
                    break

        # Now transfer the modules.
        for name, mod in transfer:
            del sys.modules[name]
            self.modules[name] = mod


@functools.wraps(DocImportMessageData.get_context)
def context(doc):
    ref = DocImportMessageData.registered_instance
    if ref:
        return ref().get_context(doc)
    else:
        return ScriptingContext(doc)


@registrar
def register():
    return utils.register_messagedata(DocImportMessageData)
