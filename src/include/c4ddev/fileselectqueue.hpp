/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file c4ddev/fileselectqueue.hpp
/// \brief Provides an interface for the #Filename::FileSelect()
///   hook that prevents the file selection dialog from popping
///   up for the next time the method is called.

#pragma once
#include <c4d.h>
#include "c4ddev.hpp"

namespace c4ddev {
namespace FileSelectQueue {

  /// Put a #Filename on the queue that will be returned on the
  /// next call to #Filename::FileSelect() instead of the file
  /// selection dialog popping up. Returns true on success, false
  /// on failure.
  inline Bool Put(Filename const& fn) {
    C4DDEV_LIBCALLR(FSH_Put, false)(fn);
  }

  /// Pop the next #Filename from the queue. Returns true on success,
  /// false if it could not be popped (eg. if the queue is empty).
  inline Bool Pop(Filename& fn) {
    C4DDEV_LIBCALLR(FSH_Pop, false)(fn);
  }

  /// Returns the number of elements in the queue that are waiting
  /// to be popped by using the Pop() function or #Filename::FileSelect().
  inline Int32 Size() {
    C4DDEV_LIBCALLR(FSH_Size, 0)();
  }

} // FileSelectQueue
} // namespace c4ddev
