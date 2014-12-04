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

import os
import sys
import c4d


# It is the intention of this plugin to give others access to
# the modules in the lib/ folder. Usually, plugins should not
# want this and make sure that the modules are inaccessible and
# that sys.path is re-set after the import.
libpath = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.append(libpath)
import devtools.plugins


def main():
    devtools.plugins.register_all()


def PluginMessage(msg_type, data):
    if msg_type == c4d.C4DPL_RELOADPYTHONPLUGINS:
        try:
            sys.path.remove(libpath)
        except ValueError:
            pass
        devtools.utils.reload_package(devtools)
    return True


if __name__ == "__main__":
    main()
