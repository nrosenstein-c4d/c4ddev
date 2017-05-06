/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file c4ddev/c4ddev.hpp
/// \brief Provides the Cinema 4D C4DDev Library.

#pragma once
#include <c4d.h>

namespace c4ddev {

  enum {
    LIBRARY_ID = 1035747,
  };

  struct Lib : public C4DLibrary {
    // file_select_hook.h
    Bool (*FSH_Put)(Filename const&);
    Bool (*FSH_Pop)(Filename&);
    Int32 (*FSH_Size)();
  };

  #ifdef C4DDEV_INTERNAL
    extern Lib lib;
  #endif

  static inline Lib* LibGet(Int32 offset) {
    #ifdef C4DDEV_INTERNAL
      return &lib;
    #else
      static C4DLibrary* cache = nullptr;
      return (Lib*) CheckLib(LIBRARY_ID, offset, &cache);
    #endif
  }

} // namespace c4ddev


#define C4DDEV_LIBCALLR(func, def) \
  auto* _lib = c4ddev::LibGet(LIBOFFSET(c4ddev::Lib, func)); \
  if (!_lib || !_lib->func) return def; \
  return _lib->func

#define C4DDEV_LIBCALL(func) \
  auto* _lib = c4ddev::LibGet(LIBOFFSET(c4ddev::Lib, func)); \
  if (!_lib || !_lib->func) return; \
  _lib->func
