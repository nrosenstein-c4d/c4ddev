/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_internal/main.cpp

#include <c4d.h>
#include <lib_py.h>
#include <nr/apex/lib.h>

extern Bool InitPython();
extern Bool RegisterApexSceneHook();
extern Bool RegisterFileSelectHook();

namespace nr {
namespace apex {
  Lib lib;
}
}

/// ***************************************************************************
/// ***************************************************************************
Bool PluginStart()
{
  // Register the APEX library.
  static Int32 const id = nr::apex::LIBRARY_ID;
  static Int32 const version = 0;
  static Int32 const size = sizeof(nr::apex::lib);
  ClearMem(&nr::apex::lib, size);
  if (!InstallLibrary(id, &nr::apex::lib, version, size)) {
    GePrint("APEX]: Cinema 4D Library could not be installed.");
    return false;
  }

  if (!RegisterFileSelectHook()) return false;
  if (!RegisterApexSceneHook()) return false;
  GePrint("APEX]: Cinema 4D API EXtensions installed.");
  GePrint("Copyright (C) 2015  Niklas Rosenstein");
  return true;
}

/// ***************************************************************************
/// ***************************************************************************
void PluginEnd()
{
}

/// ***************************************************************************
/// ***************************************************************************
Bool PluginMessage(Int32 msg, void* p_data)
{
  switch (msg) {
    case C4DPL_PYINITTYPES: {
      InitPython();
      break;
    }
  }
  return true;
}
