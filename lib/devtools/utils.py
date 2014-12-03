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

import sys
import c4d
import weakref


def register_command(cmd):
    ''' Utility function to register a Cinema 4D CommandData plugin.
    This function will read from several attributes of *cmd* to find
    the information required for registration.

    ================ ==================================
    Name             Default
    ================ ==================================
    ``PLUGIN_ID``    -
    ``PLUGIN_NAME``  -
    ``PLUGIN_ICON``  ``None``
    ``PLUGIN_HELP``  ``''``
    ``PLUGIN_INFO``  ``c4d.PLUGINFLAG_COMMAND_HOTKEY``
    ================ ==================================

    The CommandData subclass that is being registered will be assigned
    an attribute called ``registered_instance`` which contains a weak
    reference to the instance that has been registered. If registration
    fails, the attribute will be set to None.

    :param cmd: A :class:`c4d.plugins.CommandData` subclass or
        instance. If the type itself is passed, an instance of the
        type will be created.
    :return: The result of :func:`c4d.plugins.RegisterCommandPlugin`
    '''

    # If the type itself is passed, create an instance of it
    # which is to be registered.
    if isinstance(cmd, type):
        cmd = cmd()

    # Read the information for registration.
    info = getattr(cmd, 'PLUGIN_INFO', c4d.PLUGINFLAG_COMMAND_HOTKEY)
    helpstr = getattr(cmd, 'PLUGIN_HELP', '')
    icon = getattr(cmd, 'PLUGIN_ICON', None)

    # If the icon is a string, we load it as a bitmap.
    if isinstance(icon, str):
        path = icon
        icon = c4d.bitmaps.BaseBitmap()
        if icon.InitWith(path)[0] != c4d.IMAGERESULT_OK:
            icon = None

    # Register the command and update the registered_instance
    # attribute of the commands type.
    sucess = False
    try:
        success = c4d.plugins.RegisterCommandPlugin(
            cmd.PLUGIN_ID, cmd.PLUGIN_NAME, info, icon, helpstr, cmd)
    finally:
        if success:
            type(cmd).registered_instance = weakref.ref(cmd)
        else:
            type(cmd).registered_instance = None

    return success


def reload_package(package):
    ''' Recursively reloads *package* which must be a Python module
    object. Note that reloading modules can always lead to issues if
    things are still reference, because, for instance, class identities
    will change. '''

    name = package.__name__
    for module in sorted(sys.modules.keys(), key=lambda x: -len(x)):
        if module == name or module.startswith(name + '.'):
            modobj = sys.modules[module]
            if modobj is not None:
                reload(sys.modules[module])
