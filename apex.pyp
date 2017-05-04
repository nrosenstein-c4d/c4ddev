# Copyright (C) 2015 Niklas Rosenstein
# All rights reserved.

import c4d.apex
import os
import sys

APEX_VERSION = '1.3.0'
c4d.NR_APEX_ID = 1035360


def PluginMessage(msg, data):
  if msg == c4d.C4DPL_COMMANDLINEARGS:
    protect_files = []
    index = 0
    while index < len(sys.argv):
      value = sys.argv[index]
      if value == '-apex-protect-source':
        del sys.argv[index]
        try:
          protect_files.append(sys.argv.pop(index))
        except IndexError:
          print "[apex / ERROR]: -apex-protect-source missing argument."
      else:
        index += 1
    for filename in protect_files:
      filename = os.path.abspath(filename)
      print "[apex / INFO]: Calling Source Protector for %s" % repr(filename)
      c4d.apex.fileselect_put(filename)
      c4d.CallCommand(1023699)  # Source Protector
  return True
