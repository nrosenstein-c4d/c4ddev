
# Automatically generated with c4ddev v0.1.6.

import os
import sys
import c4d

_frame = sys._getframe(1)
while _frame and not '__res__' in _frame.f_globals:
  _frame = _frame.f_back

project_path = os.path.dirname(_frame.f_globals['__file__'])
project_path = os.path.normpath(os.path.join(project_path, ''))
resource = __res__ = _frame.f_globals['__res__']

def string(name, *subst, **kwargs):
  disable = kwargs.pop('disable', False)
  checked = kwargs.pop('checked', False)
  if kwargs:
    raise TypeError('unexpected keyword arguments: ' + ','.join(kwargs))

  if isinstance(name, str):
    name = globals()[name]
  elif not isinstance(name, (int, long)):
    raise TypeError('name must be str, int or long')

  result = resource.LoadString(name)
  for item in subst:
    result = result.replace('#', str(item), 1)

  if disable:
    result += '&d&'
  if checked:
    result += '&c&'
  return result

def tup(name, *subst, **kwargs):
  if isinstance(name, str):
    name = globals()[name]
  return (name, string(name, *subst))

def path(*parts):
  path = os.path.join(*parts)
  if not os.path.isabs(path):
    path = os.path.join(project_path, path)
  return path

def bitmap(*parts):
  bitmap = c4d.bitmaps.BaseBitmap()
  result, ismovie = bitmap.InitWith(file(*parts))
  if result != c4d.IMAGERESULT_OK:
    return None
  return bitmap

file = path  # backwards compatibility

ABOUT_LINE1 = 10021
ABOUT_LINE2 = 10022
ABOUT_LINE3 = 10023
BTN_COMMIT = 10002
BUTTON_CLOSE_TRACEBACK = 10013
BUTTON_REDO = 10007
BUTTON_SEND = 10008
BUTTON_SEND_TOOLTIP = 10009
BUTTON_UNDO = 10006
DRAWHELPER_EDITOR = 10001
EDT_SOURCE = 10003
GROUP_MAIN = 10004
GROUP_TRACEBACK = 10011
IDC_CODE_OK = 10026
IDC_EDITOR_ASKCLOSE = 10032
IDC_NO_TRACEBACK = 10027
IDC_SCRIPT_EDITOR = 10024
IDC_SCRIPT_EDITOR_HELP = 10025
IDS_EDITOR = 10028
IDS_EDITOR_CODE = 10031
IDS_EDITOR_HELP = 10029
IDS_EDITOR_TABS = 10030
MENU_FILE = 10014
MENU_FILE_OPEN = 10015
MENU_FILE_SAVETO = 10016
MENU_HELP = 10019
MENU_HELP_ABOUT = 10020
MENU_VIEW = 10017
MENU_VIEW_TRACEBACK = 10018
STATIC_STATUS = 10005
TEXT_SCRIPT = 10010
TREE_TRACEBACK = 10012
NR_PYOBJECT_OPENEDITOR = 1002
NR_PYOBJECT_SOURCE = 1001
NR_PYSHADER_CODE = 2000
NR_PYSHADER_INFO = 2001
NR_PYSHADER_OPENEDITOR = 2002
nr_pyshader = 1036204
