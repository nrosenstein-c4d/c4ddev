This directory contains additional headers that are available for convenience
when compiling a Cinema 4D plugin project with Craftr. Available headers are:

__`craftr/c4d_legacy.h`__

This header is automatically included when compiling for Cinema 4D R17 or
newer when the `legacy_sdk` is used. It takes on the job of the previously
available `__LEGACY_API` define which would include the Cinema 4D `legacy.h`
header which is only available in R15 and R16.

__`craftr/c4d_python.h`__

This is a convenience header that includes `Python.h` after disabling the
`DEBUG` macro temporarily. Since Cinema 4D does not deliver debug binaries
of the embedded Python version, the header must be included without the
`DEBUG` macro set.

__`craftr/compilerdetection.h`__

The R16 SDK uses `#define override` on Windows which is actually invalid
and Visual Studio 2015 (aka. 14.0) complains about this. This directory
contains file(s) that can be replaced in the R16 SDK to fix this issue, or
alternatively a forced-include could be used which would disable the inclusion
of the original `compilerdetection.h`.
