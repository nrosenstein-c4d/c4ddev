
import c4d, pkgutil
from c4ddev.utils import find_menu_resource

menu_bc = c4d.BaseContainer()
menu_bc[c4d.MENURESOURCE_SUBTITLE] = 'C4DDev'

def add_command(plugin_id):
  menu_bc.InsData(c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_' + str(plugin_id))

def add_separator():
  menu_bc.InsData(c4d.MENURESOURCE_SEPERATOR, True)


from c4ddev.ide import ScriptEditor

add_command(1038999)  # ide.py: Open Editor Window
add_command(ScriptEditor.GLOBAL_PLUGIN_ID)  # Old Editor
add_separator()
add_command(1027193)  # pyobject.py: PyObject
add_command(1036204)  # pyshader.py: PyShader
add_separator()
add_command(1039246)  # scripting_server.py: Server Toggle
add_command(1033712)  # uescape_tool.py: Unicode Escape Tool


def PluginMessage(msg_id, data):
  if msg_id == c4d.C4DPL_BUILDMENU:
    bc = find_menu_resource('M_EDITOR', 'IDS_SCRIPTING_MAIN')
    bc.InsData(c4d.MENURESOURCE_SEPERATOR, True)
    bc.InsData(c4d.MENURESOURCE_SUBMENU, menu_bc)
    return True
  return False
