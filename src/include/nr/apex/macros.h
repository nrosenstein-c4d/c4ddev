/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file nr/apex/macros.h
/// \brief Defines macros used in the Apex plugin.

#ifndef NR_APEX_MACROS_H__
#define NR_APEX_MACROS_H__

/// Shorthand to declare a member of a namespace or class in a
/// translation unit instead of writing the full type specifier
/// all over again.
#define NR_APEX_DECLMEMBER(name) decltype(name) name

/// Macro to hook a function into the C4DOS library. The new function
/// will automatically be force casted into the required type, so be
/// careful!
#define NR_APEX_HOOKFUNCTION(dest, newFunc, oldFunc) \
  do { \
    oldFunc = dest; \
    dest = reinterpret_cast<decltype(dest)>(&newFunc); \
  } while(0)

#endif // NR_APEX_MACROS_H__
