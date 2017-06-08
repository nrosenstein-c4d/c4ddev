/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_internal/main.cpp

#include <c4d.h>
#include <lib_py.h>
#include <c4ddev/c4ddev.hpp>
#include <c4ddev/python.hpp>

extern Bool InitPython();
extern Bool RegisterMessageSceneHook();
extern Bool RegisterFileSelectHook();

namespace c4ddev {
  Lib lib;
}


Bool PluginStart() {
  static Int32 const id = c4ddev::LIBRARY_ID;
  static Int32 const version = 0;
  static Int32 const size = sizeof(c4ddev::lib);
  ClearMem(&c4ddev::lib, size);
  if (!InstallLibrary(id, &c4ddev::lib, version, size)) {
    GePrint("C4DDev API Extensions could not be installed.");
    return false;
  }

  if (!RegisterFileSelectHook()) return false;
  if (!RegisterMessageSceneHook()) return false;
  GePrint("C4DDev API EXtensions installed.");
  GePrint("Copyright (c) 2015  Niklas Rosenstein");
  return true;
}


void PluginEnd() {
}


Bool PluginMessage(Int32 msg, void* p_data) {
  switch (msg) {
    case C4DPL_PYINITTYPES: {
      c4ddev::PyTypesInit();
      InitPython();
      break;
    }
  }
  return true;
}
