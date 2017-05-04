/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file nr/apex/lib.h
/// \brief Contains the APEX Cinema 4D Library.

#ifndef NR_APEX_LIB_H__
#define NR_APEX_LIB_H__

#include <c4d.h>

namespace nr {
namespace apex {

  enum
  {
    LIBRARY_ID = 1035747,
  };

  struct Lib : public C4DLibrary {
    // file_select_hook.h
    Bool (*FSH_Put)(Filename const&);
    Bool (*FSH_Pop)(Filename&);
    Int32 (*FSH_Size)();
  };

  #ifdef NR_APEX_INTERNAL
    extern Lib lib;
  #endif

  static inline Lib* LibGet(Int32 offset)
  {
    #ifdef NR_APEX_INTERNAL
      return &lib;
    #else
      static C4DLibrary* cache = nullptr;
      return (Lib*) CheckLib(LIBRARY_ID, offset, &cache);
    #endif
  }

} // namespace apex
} // namespace nr

#ifdef NR_APEX_LIB_DEFINE_LIBCALL
  #define LIBCALLR(func, def) \
    Lib* lib = nr::apex::LibGet(LIBOFFSET(Lib, func)); \
    if (!lib || !lib->func) return def; \
    return lib->func

  #define LIBCALL(func) \
    Lib* lib = nr::apex::LibGet(LIBOFFSET(Lib, func)); \
    if (!lib || !lib->func) return; \
    lib->func
#endif

#endif // NR_APEX_LIB_H__
