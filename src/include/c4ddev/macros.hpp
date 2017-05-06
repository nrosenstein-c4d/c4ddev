/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file c4ddev/macros.hpp
/// \brief Defines macros used in the C4DDev plugin.

#pragma once

/// Shorthand to declare a member of a namespace or class in a
/// translation unit instead of writing the full type specifier
/// all over again.
#define C4DDEV_DECLMEMBER(name) decltype(name) name

/// Macro to hook a function into the C4DOS library. The new function
/// will automatically be force casted into the required type, so be
/// careful!
#define C4DDEV_HOOKFUNCTION(dest, newFunc, oldFunc) \
  do { \
    oldFunc = dest; \
    dest = reinterpret_cast<decltype(dest)>(&newFunc); \
  } while(0)
