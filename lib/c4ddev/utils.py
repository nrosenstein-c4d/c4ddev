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
import weakref
from . import res


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
    success = False
    try:
        success = c4d.plugins.RegisterCommandPlugin(
            cmd.PLUGIN_ID, cmd.PLUGIN_NAME, info, icon, helpstr, cmd)
    finally:
        if success:
            type(cmd).registered_instance = weakref.ref(cmd)
        else:
            type(cmd).registered_instance = None

    return success


def register_messagedata(data):
    ''' Similar to :func:`register_command`, this function registers
    a :class:`c4d.plugins.MessageData` plugin to Cinema 4D. *data*
    must be an instance or subclass of the MessageData class and
    provide the following attributes:

    ================ ==================================
    Name             Default
    ================ ==================================
    ``PLUGIN_ID``    -
    ``PLUGIN_NAME``  -
    ``PLUGIN_INFO``  ``0``
    ================ ==================================

    The MessageData subclass that is being registered will be assigned
    an attribute called ``registered_instance`` which contains a weak
    reference to the instance that has been registered. If registration
    fails, the attribute will be set to None.
    '''

    if isinstance(data, type):
        data = data()

    info = getattr(data, 'PLUGIN_INFO', 0)

    success = False
    try:
        success = c4d.plugins.RegisterMessagePlugin(
            data.PLUGIN_ID, data.PLUGIN_NAME, info, data)
    finally:
        if success:
            type(data).registered_instance = weakref.ref(data)
        else:
            type(data).registered_instance = None

    return success


def reload_package(package):
    ''' Reloads *package* which must be a Python module object. Note
    that reloading modules can always lead to issues if things are
    still reference, because, for instance, class identities will
    change. '''

    name = package.__name__
    for module in sorted(sys.modules.keys(), key=lambda x: -len(x)):
        if module == name or module.startswith(name + '.'):
            modobj = sys.modules[module]
            if modobj is not None:
                reload(sys.modules[module])


def remove_package(package):
    ''' Removes *package* from :data:`sys.modules` and all its sub
    packages and modules. '''

    name = package.__name__
    for module in sys.modules.keys():
        if module == name or module.startswith(name + '.'):
            del sys.modules[module]


def is_local_module(name, mod, path):
    ''' Determines if the module *mod* with *name* is a module imported
    from the specified *path* or any subpath. *mod* can be None in
    which case the parent-module is checked (determined from *name*). '''

    if mod is None:
        parent = name.rpartition('.')[0]
        if not parent:
            raise ValueError('mod is None and name is root module')
        if parent in sys.modules:
            return is_local_module(parent, sys.modules[parent], path)
        return False

    filename = getattr(mod, '__file__', None)
    if filename:
        try:
            s = os.path.relpath(filename, path)
        except ValueError:
            # Eg. on Windows with different drive letters.
            return False
        else:
            return s == os.curdir or not s.startswith(os.pardir)
    return False


def find_menu_resource(*path):
    bc = c4d.gui.GetMenuResource(path[0])
    for menu in path[1:]:
        found = False
        index = 0
        while True:
            key = bc.GetIndexId(index)
            if key == c4d.NOTOK: break
            if key == c4d.MENURESOURCE_SUBMENU:
                subbc = bc.GetIndexData(index)
                if subbc[c4d.MENURESOURCE_SUBTITLE] == menu:
                    found = True
                    bc = subbc
                    break
            index += 1
        if not found:
            return None
    return bc


class AtomDict(object):
    ''' Dictionary-like object that is just a list of key-value pairs.
    This will allow to use unhashable objects as keys. '''

    def __init__(self):
        super(AtomDict, self).__init__()
        self._items = []

    def __repr__(self):
        middle = ', '.join('%r: %r' % (k, v) for k, v in self._items)
        return 'AtomDict({%s})' % middle

    def __iter__(self):
        for key, __ in self._items:
            yield key

    def __getitem__(self, key):
        for k, v in self._items:
            if k == key:
                return v
        raise KeyError(key)

    def __setitem__(self, key, value):
        for item in self._items:
            if item[0] == key:
                item[1] = value
                return
        self._items.append([key, value])

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def clear(self):
        self._items[:] = []

    def setdefault(self, key, value):
        try:
            return self[key]
        except KeyError:
            self._items.append([key, value])
            return value


    iterkeys = __iter__

    def itervalues(self):
        for __, v in self._items:
            yield v

    def iteritems(self):
        return iter(self._items)

    def keys(self):
        return list(self)

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self._items)
