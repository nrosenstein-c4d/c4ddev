#ifndef WINDOWS_INCLUDE_H__
#define WINDOWS_INCLUDE_H__

// Rename Windows LONG/ULONG type as it collides with CINEMA 4D API's new definition
#pragma push_macro("LONG")
#pragma push_macro("ULONG")
#define LONG	WinLONG
#define ULONG	WinULONG

// Prevent include of Windows dialog definitions that will collide with CINEMA 4D API's types
#define	WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <winsock2.h>
#include <ws2ipdef.h>

#pragma pop_macro("LONG")
#pragma pop_macro("ULONG")

#endif // WINDOWS_INCLUDE_H__
