/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_internal/file_select_hook.cpp
/// \brief Implements the Hook to override a FileSelect call. Items
///   can be added via FileSelectPut() and removed with FileSelectPop().
///   The internal structure operates the FIFO principle.

#include <c4d.h>
#include <nr/apex/macros.h>
#include <nr/apex/lib.h>
#include <nr/apex/file_select_hook.h>

/// Global FIFO list that contains the filenames that will be returned
/// instead of a dialog being opened for Filename::FileSelect().
static maxon::BaseList<Filename> _fns;

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Bool FileSelect_Put(Filename const& fn)
{
  return _fns.Append(fn) != nullptr;
}

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Bool FileSelect_Pop(Filename& fn)
{
  if (_fns.GetCount() > 0) {
    fn = _fns[0];
    _fns.Erase(0);
    return true;
  }
  return false;
}

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Int32 FileSelect_Size()
{
  return _fns.GetCount();
}

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
class iFilename {
public:
  Bool FileSelect(FILESELECTTYPE, FILESELECT, String const&, String const&);
  static decltype(&Filename::FileSelect) FileSelect_Original;
};

NR_APEX_DECLMEMBER(iFilename::FileSelect_Original);

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Bool iFilename::FileSelect(
  FILESELECTTYPE type, FILESELECT flags, String const& title,
  String const& force_suffix)
{
  Filename* fn = reinterpret_cast<Filename*>(this);
  if (_fns.GetCount() > 0) {
    FileSelect_Pop(*fn);
    return true;
  }
  if (FileSelect_Original)
    return (fn->*FileSelect_Original)(type, flags, title, force_suffix);
  return false;
}

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Bool RegisterFileSelectHook()
{
  auto& lib = nr::apex::lib;
  lib.FSH_Put = &FileSelect_Put;
  lib.FSH_Pop = &FileSelect_Pop;
  lib.FSH_Size = &FileSelect_Size;

  // Hook the new FileSelect method in there.
  NR_APEX_HOOKFUNCTION(C4DOS.Fn->FileSelect, iFilename::FileSelect, iFilename::FileSelect_Original);
  return true;
}
