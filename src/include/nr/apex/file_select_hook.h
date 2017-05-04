/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file nr/apex/file_select_hook.h
/// \brief Declares the interface for the Filename::FileSelect()
///   hook that prevents the file selection dialog from popping
///   up for the next time the method is called.

#ifndef NR_APEX_FILESELECTHOOK_H__
#define NR_APEX_FILESELECTHOOK_H__

#include <c4d.h>

namespace nr {
namespace apex {
namespace file_select_hook {

  /// Put a Filename on the queue that will be returned on the
  /// next call to Filename::FileSelect() instead of the file
  /// selection dialog popping up. Returns true on success, false
  /// on failure.
  Bool Put(Filename const&);

  /// Pop the next Filename from the queue. Returns true on success,
  /// false if it could not be popped (eg. if the queue is empty).
  Bool Pop(Filename&);

  /// Returns the number of elements in the queue that are waiting
  /// to be popped by using the Pop() function or Filename::FileSelect().
  Int32 Size();

} // namespace file_select_hook
} // namespace apex
} // namespace nr

#endif // NR_APEX_FILESELECTHOOK_H__
