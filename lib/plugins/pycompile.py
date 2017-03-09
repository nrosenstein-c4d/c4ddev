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

import c4d
import compileall
utils = require('../utils')


class CompileDirectoryCommand(c4d.plugins.CommandData):

    PLUGIN_ID = 1033714
    PLUGIN_NAME = "Compile Directory"
    PLUGIN_HELP = "Compiles all Python source files in the selected " \
                  "directory to *.pyc files."

    def Execute(self, doc):
        flags = c4d.FILESELECT_DIRECTORY
        title = 'Select a Directory to compile'
        dirname = c4d.storage.LoadDialog(title=title, flags=flags)
        if not dirname:
            return True

        compileall.compile_dir(dirname, force=1)
        return True


utils.register_command(CompileDirectoryCommand)
