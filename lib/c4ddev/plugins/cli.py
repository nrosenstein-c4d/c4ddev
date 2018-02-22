
import c4d, os, sys
import c4ddev

def PluginMessage(msg, data):
  if msg == c4d.C4DPL_COMMANDLINEARGS:
    protect_files = []
    index = 0
    while index < len(sys.argv):
      value = sys.argv[index]
      if value == '-c4ddev-protect-source':
        del sys.argv[index]
        try:
          protect_files.append(sys.argv.pop(index))
        except IndexError:
          print "[c4ddev ERROR]: -c4ddev-protect-source missing argument."
      else:
        index += 1
    if protect_files:
      if not c4ddev.has_cpp_extensions:
        print "[c4ddev ERROR]: C4DDev C++ extensions are not installed, " \
              "can not protect source file(s)."
        return False
      for filename in protect_files:
        filename = os.path.abspath(filename)
        print "[c4ddev INFO]: Calling Source Protector for %s" % repr(filename)
        c4ddev.FileSelectPut(filename)
        c4d.CallCommand(1023699)  # Source Protector
      return True
  return False
