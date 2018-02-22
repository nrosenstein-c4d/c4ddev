# Copyright (c) 2014  Niklas Rosenstein
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


from weakref import ref
from c4ddev import res
from . import undotree, utils
from .utils import xor

import os
import sys
import c4d
import time


class ScriptEditor(c4d.gui.GeDialog):
    r""" This class implements a Script Editor which can be used
    in various ways. It does, however, only support one script at
    a time to be edited and has no support for tabs or multiple
    documents like the Script Editor of Cinema 4D R14+.

    Upon construction of the ScriptEditor, there are some options
    that can be specified.

    - ``status_bar``
    - ``highlight_line``
    - ``send_icon``
    - ``status_line``
    - ``undo_interval``
    - ``display_tracebacks``
    """

    GLOBAL_PLUGIN_ID = 1031950

    MENULINE_START = 1000
    MENULINE_BEFORESEND = 1001
    MENULINE_END = 1002

    MAINGROUP_START = 2000
    MAINGROUP_END = 2001

    # The data is a tuple of (exc, traceback).
    TRACEBACKGROUP_START = 3000
    TRACEBACKGROUP_END = 3001

    @staticmethod
    def global_instance():
        r""" Returns the global instance of this class. """

        if not hasattr(ScriptEditor, '_instance'):
            ScriptEditor._instance = ScriptEditor()
        return ScriptEditor._instance

    @staticmethod
    def OpenWithScript(script):
        r""" Opens the global ScriptEditor instance with the specified
        :class:`ScriptInterface` object. """

        dlg = ScriptEditor.global_instance()
        dlg.AttachScript(script)
        return dlg.Open(c4d.DLG_TYPE_ASYNC, ScriptEditor.GLOBAL_PLUGIN_ID)

    @staticmethod
    def OpenDefault():
        r""" Opens the ScriptEditor with the :class:`DefaultScript`
        attached. """

        dlg = ScriptEditor.global_instance()
        dlg.AttachScript(DefaultScript.global_instance())
        return dlg.Open(c4d.DLG_TYPE_ASYNC, ScriptEditor.GLOBAL_PLUGIN_ID,
            defaultw=500, defaulth=300)

    @staticmethod
    def RestoreDefault(secret):
        r""" Restores the ScriptEditor in the interface. """

        dlg = ScriptEditor.global_instance()
        dlg.AttachScript(DefaultScript.global_instance())
        return dlg.Restore(ScriptEditor.GLOBAL_PLUGIN_ID, secret)


    def __init__(self, title=None, **options):
        super(ScriptEditor, self).__init__()

        self.__script = None
        self.__traceback_data = (None, None)
        self.__traceback_visible = False

        self.title = title or res.string('IDC_SCRIPT_EDITOR')
        self.options = {
                'status_bar': True,
                'highlight_line': True,
                'send_icon': c4d.RESOURCEIMAGE_BROWSER_PLAY,
                'status_line': True,
                'undo_interval': 2.0,
                'display_tracebacks': True,
        }
        self.options.update(options)

    def LayoutCallback(self, kind, data=None):
        r""" This method is callback that is invoked from the
        :meth:`CreateLayout` method which should allow subclasses
        to customize the looks of the dialog at certain points. """

        pass

    def AttachScript(self, script):
        r""" Attach a :class:`ScriptInterface` instance to the
        dialog and initialize the required steps to integrate it. None
        can be passed to detach the current script. """

        if script is None:
            pass
        elif not isinstance(script, ScriptInterface):
            raise TypeError('expected ScriptInterface instance')

        self.__script = script
        self.__last_undo = -1
        if self.IsOpen():
            self.__Update()

    def AddUndo(self, code=None):
        r""" Add an undo for the attached script. For speed reasons,
        if you have the code for which an undo should be added right
        at your hands already, it can be passed for the *code*
        parameter. """

        if not self.__script:
            raise RuntimeError('no script attached')

        if code is None:
            code = self.GetString(res.TEXT_SCRIPT)
        elif not isinstance(code, str):
            raise RuntimeError('expected str, got %s' % code.__class__.__name__)

        self.__script.add_undo(code)
        self.__last_undo = time.time()
        self.__Update()

    def AddBitmapButton(self, id_, flags, minw=0, minh=0, button=True,
                iconid1=None, iconid2=None, tooltip=None):
        r""" Helper method to add a BitmapButton to the dialog. """

        bc = c4d.BaseContainer()
        bc.SetBool(c4d.BITMAPBUTTON_BUTTON, bool(button))
        if iconid1 is not None:
            bc.SetLong(c4d.BITMAPBUTTON_ICONID1, iconid1)
        if iconid2 is not None:
            bc.SetLong(c4d.BITMAPBUTTON_ICONID2, iconid2)
        if tooltip is not None:
            bc.SetString(c4d.BITMAPBUTTON_TOOLTIP, str(tooltip))

        return self.AddCustomGui(
                    id_, c4d.CUSTOMGUI_BITMAPBUTTON, "", flags,
                    minw, minh, customdata=bc)

    def SetScriptCursor(self, line, column):
        r""" Moves the cursor of the script field to the specified
        *line* and *column*. Used by the :class:`DefaultScript` class
        when an exception occurs. """

        # I can't remember which version of Cinema 4D it was,
        # but the c4d.gui.GeDialog.SetMultiLinePos method is
        # not available in all releases.
        if hasattr(self, 'SetMultiLinePos'):
            self.SetMultiLinePos(res.TEXT_SCRIPT, line, column)

    def DisplayTraceback(self, exc=None, traceback=None):
        r""" Display a the traceback below the text field in the
        editor. """

        if xor(exc, traceback):
            raise ValueError('require exc and traceback or neither of them')

        if not exc and not traceback:
            exc, traceback = self.__traceback_data

        self.MenuInitString(res.MENU_VIEW_TRACEBACK, True, True)
        self.LayoutFlushGroup(res.GROUP_TRACEBACK)
        self.LayoutCallback(self.TRACEBACKGROUP_START, (exc, traceback))

        # Add a close button to the top right.
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 0, 0)
        self.GroupBorderSpace(4, 4, 4, 4)

        message = str(exc) if exc else res.string('IDC_NO_TRACEBACK')
        self.AddStaticText(0, c4d.BFH_SCALEFIT, name=message)
        self.AddBitmapButton(
                    res.BUTTON_CLOSE_TRACEBACK, 0,
                    iconid1=c4d.RESOURCEIMAGE_CLEARSELECTION)
        self.GroupEnd()

        # Add the TreeViewCustomGui and the TracebackModel.
        if exc:
            bc = c4d.BaseContainer()
            bc.SetBool(c4d.TREEVIEW_ALTERNATE_BG, True)
            bc.SetBool(c4d.TREEVIEW_NOENTERRENAME, True)
            bc.SetBool(c4d.TREEVIEW_NO_MULTISELECT, True)
            bc.SetBool(c4d.TREEVIEW_FIXED_LAYOUT, True)
            tree = self.AddCustomGui(
                        res.TREE_TRACEBACK, c4d.CUSTOMGUI_TREEVIEW, "",
                        c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 200, 80, bc)
            tree.SetRoot(traceback, TracebackModel(), (exc, ref(self)))

        self.LayoutCallback(self.TRACEBACKGROUP_END, (exc, traceback))
        self.LayoutChanged(res.GROUP_TRACEBACK)

        self.__traceback_data = (exc, traceback)
        self.__traceback_visible = True

    def HideTraceback(self):
        r""" Hide the Traceback view. """

        self.LayoutFlushGroup(res.GROUP_TRACEBACK)
        self.LayoutChanged(res.GROUP_TRACEBACK)
        self.MenuInitString(res.MENU_VIEW_TRACEBACK, True, False)
        self.__traceback_visible = False

    def ToggleTraceback(self):
        if self.__traceback_visible:
            self.HideTraceback()
        else:
            self.DisplayTraceback()

    def ClearTraceback(self):
        self.__traceback_data = (None, None)
        self.HideTraceback()

    def __Update(self):
        # Update the title of the dialog
        title = str(self.title)
        name = self.__script.get_name() if self.__script else None
        if name:
            title += ' - %s' % name
        self.SetTitle(title)

        # Update the menu-line status
        if self.options['status_line']:
            message = self.__script.get_status_string()
            self.SetString(res.STATIC_STATUS, message or '')
            self.LayoutChanged(res.STATIC_STATUS)

        if self.__script:
            self.Enable(res.BUTTON_UNDO, self.__script.undos.can_revert())
            self.Enable(res.BUTTON_REDO, self.__script.undos.can_forward())

    # c4d.gui.GeDialog

    def Timer(self, msg):
        # Add an undo if the time specified in the undo_interval
        # option passed since the last undo.
        delta = time.time() - self.__last_undo
        if delta >= self.options['undo_interval']:
            self.AddUndo()

    def CreateLayout(self):
        HV_SCALEFIT = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT

        self.MenuSubBegin(res.string('MENU_FILE'))
        self.MenuAddString(*res.tup('MENU_FILE_OPEN'))
        self.MenuAddString(*res.tup('MENU_FILE_SAVETO'))
        self.MenuSubEnd()

        self.MenuSubBegin(res.string('MENU_VIEW'))
        self.MenuAddString(*res.tup('MENU_VIEW_TRACEBACK'))
        self.MenuSubEnd()

        self.MenuSubBegin(res.string('MENU_HELP'))
        self.MenuAddString(*res.tup('MENU_HELP_ABOUT'))
        self.MenuSubEnd()

        self.MenuFinished()

        # Build the menu line with the "Send" button. The
        # respective LayoutCallbacks are invoked.
        self.GroupBeginInMenuLine()
        self.LayoutCallback(self.MENULINE_START)

        # Should we also display a status line in the menuline?
        if self.options['status_line']:
            self.AddStaticText(res.STATIC_STATUS, 0)
            self.AddStaticText(0, 0, name=" ") # separator

        self.AddButton(res.BUTTON_UNDO, 0, name=res.string('BUTTON_UNDO'))
        self.AddButton(res.BUTTON_REDO, 0, name=res.string('BUTTON_REDO'))

        # Create the "Send" BitmapButton.
        self.LayoutCallback(self.MENULINE_BEFORESEND)
        self.AddBitmapButton(
                res.BUTTON_SEND, 0, 16, 16,
                iconid1=self.options['send_icon'],
                tooltip=res.string('BUTTON_SEND_TOOLTIP'))

        # Send the LayoutCallback for the end of the menuline
        # group and close it.
        self.LayoutCallback(self.MENULINE_END)
        self.GroupEnd()

        # Open the main group and add the multiline text box
        # with respective LayoutCallbacks.
        self.GroupBegin(res.GROUP_MAIN, HV_SCALEFIT, 1, 0)
        self.LayoutCallback(self.MAINGROUP_START)

        style = c4d.DR_MULTILINE_MONOSPACED | c4d.DR_MULTILINE_SYNTAXCOLOR | \
                c4d.DR_MULTILINE_PYTHON | c4d.DR_MULTILINE_HIGHLIGHTLINE
        if self.options['status_bar']:
            style |= c4d.DR_MULTILINE_STATUSBAR
        if self.options['highlight_line']:
            style |= c4d.DR_MULTILINE_HIGHLIGHTLINE
        self.AddMultiLineEditText(res.TEXT_SCRIPT, HV_SCALEFIT, style=style)

        # Close the group.
        self.LayoutCallback(self.MAINGROUP_END)
        self.GroupEnd()

        # Create the Traceback group.
        self.GroupBegin(res.GROUP_TRACEBACK, c4d.BFH_SCALEFIT, 1, 0)
        self.GroupEnd()
        self.HideTraceback()

        self.__Update()
        return True

    def InitValues(self):
        self.SetTimer(int(self.options['undo_interval'] * 1000) / 2)
        return True

    def Command(self, id_, msg):
        if id_ == res.BUTTON_SEND and self.__script:
            code = self.GetString(res.TEXT_SCRIPT)
            self.AddUndo(code)
            self.ClearTraceback()
            self.__script.code_submit(self, code)
            self.__Update()
        elif id_ == res.BUTTON_CLOSE_TRACEBACK:
            self.HideTraceback()
        elif id_ == res.BUTTON_UNDO and self.__script:
            undos = self.__script.undos
            if undos.revert():
                self.SetString(res.TEXT_SCRIPT, undos.data)
            self.__Update()
        elif id_ == res.BUTTON_REDO and self.__script:
            undos = self.__script.undos
            if undos.forward():
                self.SetString(res.TEXT_SCRIPT, undos.data)
            self.__Update()
        elif id_ == res.MENU_FILE_OPEN:
            filename = c4d.storage.LoadDialog()
            if filename and os.path.isfile(filename):
                self.AddUndo()
                with open(filename) as fp:
                    code = fp.read()
                self.SetString(res.TEXT_SCRIPT, code)
        elif id_ == res.MENU_FILE_SAVETO:
            filename = c4d.storage.SaveDialog()
            if filename:
                with open(filename, 'w') as fp:
                    fp.write(self.GetString(res.TEXT_SCRIPT))
        elif id_ == res.MENU_VIEW_TRACEBACK:
            self.ToggleTraceback()
        elif id_ == res.MENU_HELP_ABOUT:
            AboutDialog.Display()
        return True

class AboutDialog(c4d.gui.GeDialog):
    r""" Displays the about dialog for the c4dprototyping plugin. """

    PLUGIN_ID = 1031953

    @staticmethod
    def Display():
        r""" Displays the about dialog. """

        if not hasattr(AboutDialog, '_instance'):
            AboutDialog._instance = AboutDialog()
        AboutDialog._instance.Open(
                    c4d.DLG_TYPE_ASYNC_POPUPEDIT, AboutDialog.PLUGIN_ID,
                    xpos=-2, ypos=-2)

    def CreateLayout(self):
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 0)
        self.GroupBorderSpace(4, 4, 4, 4)
        self.GroupBorderNoTitle(c4d.BORDER_ROUND)
        self.AddStaticText(0, 0, name=res.string('ABOUT_LINE1'))
        self.AddStaticText(0, 0, name=res.string('ABOUT_LINE2'))
        self.AddStaticText(0, 0, name=res.string('ABOUT_LINE3'))
        self.GroupEnd()
        return True

    def Message(self, msg, result):
        if msg.GetId() == c4d.BFM_LOSTFOCUS:
            self.Close()
        return super(AboutDialog, self).Message(msg, result)


class TracebackModel(c4d.gui.TreeViewFunctions):
    r""" This is a model for the Cinema 4D TreeViewCustomGui which
    displays an exception traceback. It expects the following data
    as input when calling :meth:`c4d.gui.TreeViewCustomGui.SetRoot`.

    :root: The traceback object
    :userdata: A tuple of ``(exc, dlg)`` while ``dlg`` is a weak
            reference to the dialog.
    """

    # c4d.gui.TreeViewFunctions

    def GetFirst(self, root, ud):
        return root

    def GetNext(self, root, ud, obj):
        if obj:
            return obj.tb_next

    def GetName(self, root, ud, obj):
        if not obj:
            return '<???>'

        code_obj = obj.tb_frame.f_code
        filename = code_obj.co_filename
        name = code_obj.co_name
        line = obj.tb_lineno
        return '%s, line %d in %s' % (filename, line, name)

    def CreateContextMenu(self, root, ud, obj, col, bc):
        bc.FlushAll()

    def MouseDown(self, root, ud, obj, col, info, rightButton):
        # Listen on left-click.
        if info['button'] == 0 and obj:
            # De-reference the weak-ref of the dialog.
            dlg = ud[1]()
            if dlg:
                dlg.SetScriptCursor(obj.tb_lineno, 0)
                return True

        return False

    def Select(self, root, ud, obj, mode):
        pass


class ScriptInterface(object):
    r""" This interface represents a Python script that is being
    coded by the user using the :class:`ScriptEditor`. It manages
    the code and undo steps, status messages and script name.

    .. attribute:: undos

        An :class:`undotree.UndoTree` instance which manages
        the undos of the code. The :meth:`add_undo` method
        is called from the :class:`ScriptEditor` to tell the
        interface to add an undo step.
    """

    def __init__(self, init_code=''):
        super(ScriptInterface, self).__init__()
        self.undos = undotree.UndoTree(init_code, 30, branched=False)

    def add_undo(self, code):
        r""" This method is called with the current code in the
        :class:`ScriptEditor` with the intention to create a new
        undo step. The default implementation simply adds the new
        entry to the :attr:`undos`. """

        self.undos.new(code)

    def code_submit(self, dialog, code):
        r""" Called when the user pressed the "Submit Code" button.
        :meth:`get_status_string` is called after this method. """

        raise NotImplementedError

    def get_name(self):
        r""" Return the name of the interface which will be
        displayed in the dialog title. None can be returned
        to not display a specific name. """

        return None

    def get_status_string(self):
        r""" Called to get the status message of the dialog. It is
        displayed in the menu line of the dialog, next to the send
        button. """

        return None

class DefaultScript(ScriptInterface):
    r""" This is the standard implementation of the
    :class:`ScriptInterface` which executes the code on submission. """

    @staticmethod
    def global_instance():
        r""" Returns the global instance of this class. """

        if not hasattr(DefaultScript, '_instance'):
            DefaultScript._instance = DefaultScript()
        return DefaultScript._instance

    def __init__(self, init_code=''):
        super(DefaultScript, self).__init__(init_code)
        self.last_message = ''

    # ScriptInterface

    def code_submit(self, dialog, code):
        # Create the context in which the script should be
        # executed int.
        doc = c4d.documents.GetActiveDocument()
        scope = {
            '__name__': '__main__',
            'doc': doc,
            'op': doc.GetActiveObject(),
        }

        try:
            exec code in scope
        except Exception as exc:
            self.last_message = str(exc)

            # Print the traceback of the exception (excluding the
            # first level which contains the exec statement from
            # this file.
            tb = sys.exc_info()[2].tb_next
            utils.print_traceback(exc, tb)

            # Move the cursor of the ScriptEditor to the line
            # where the error occured.
            dialog.SetScriptCursor(utils.get_last_traceback().tb_lineno, 0)
            dialog.DisplayTraceback(exc, tb)
        else:
            self.last_message = res.string('IDC_CODE_OK')

    def get_status_string(self):
        return self.last_message or res.string('IDC_CODE_OK')

