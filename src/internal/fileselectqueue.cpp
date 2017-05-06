/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src/internal/fileselectqueue.cpp

#include <c4d.h>
#include <c4ddev/c4ddev.hpp>
#include <c4ddev/macros.hpp>
#include <c4ddev/fileselectqueue.hpp>

/// Global FIFO list that contains the filenames that will be returned
/// instead of a dialog being opened for Filename::FileSelect().
static maxon::BaseList<Filename> _fns;

Bool __Put(Filename const& fn) {
  return _fns.Append(fn) != nullptr;
}

Bool __Pop(Filename& fn) {
  if (_fns.GetCount() > 0) {
    fn = _fns[0];
    _fns.Erase(0);
    return true;
  }
  return false;
}

Int32 __Size() {
  return _fns.GetCount();
}

/// FileSelect Hook

class iFilename {
public:
  Bool FileSelect(FILESELECTTYPE, FILESELECT, String const&, String const&);
  static decltype(&Filename::FileSelect) FileSelect_Original;
};

C4DDEV_DECLMEMBER(iFilename::FileSelect_Original);


Bool iFilename::FileSelect(
  FILESELECTTYPE type, FILESELECT flags, String const& title,
  String const& force_suffix)
{
  Filename* fn = reinterpret_cast<Filename*>(this);
  if (_fns.GetCount() > 0) {
    __Pop(*fn);
    return true;
  }
  if (FileSelect_Original)
    return (fn->*FileSelect_Original)(type, flags, title, force_suffix);
  return false;
}


Bool RegisterFileSelectHook() {
  auto& lib = c4ddev::lib;
  lib.FSH_Put = &__Put;
  lib.FSH_Pop = &__Pop;
  lib.FSH_Size = &__Size;

  // Hook the new FileSelect method in there.
  C4DDEV_HOOKFUNCTION(C4DOS.Fn->FileSelect, iFilename::FileSelect, iFilename::FileSelect_Original);
  return true;
}
