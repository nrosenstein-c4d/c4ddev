/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_public/file_select_hook.cpp

#define NR_APEX_LIB_DEFINE_LIBCALL
#include <nr/apex/lib.h>
#include <nr/apex/file_select_hook.h>

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Bool nr::apex::file_select_hook::Put(Filename const& fn)
{
  LIBCALLR(FSH_Put, false)(fn);
}

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Bool nr::apex::file_select_hook::Pop(Filename& fn)
{
  LIBCALLR(FSH_Pop, false)(fn);
}

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Int32 nr::apex::file_select_hook::Size()
{
  LIBCALLR(FSH_Size, 0)();
}
