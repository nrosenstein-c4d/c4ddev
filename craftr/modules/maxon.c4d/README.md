# Maxon Cinema 4D SDK (`NiklasRosenstein.maxon.c4d`)

[![Build Status](https://travis-ci.org/craftr-build/NiklasRosenstein.maxon.c4d.svg?branch=master)](https://travis-ci.org/craftr-build/NiklasRosenstein.maxon.c4d)
[![Build status](https://ci.appveyor.com/api/projects/status/sls9x3ic6nc1gosw/branch/master?svg=true)](https://ci.appveyor.com/project/NiklasRosenstein/niklasrosenstein-maxon-c4d/branch/master)

-- Compile the Cinema 4D SDK and plugins with [Craftr].

[Craftr]: https://github.com/craftr-build/craftr

__Features__:

- Provides `__LEGACY_API` functionality for R17+ (just use `c4d.legacy_sdk`
  instead of `c4d.sdk`).
- Provides a header `craftr/c4d_python.h` that conveniently includes `Python.h`
  which is not straight forward.
- Supports compilation with MSVC, Clang-CL and Clang (Mac OS only).
- Automatically download the Cinema 4D SDK source when compiling outside
  of a Cinema 4D installation environment.
- Support for GCC on Linux (experimental)

__Configuration__:

- `.debug` &ndash; Inheritable option. Specifies whether the Cinema 4D SDK
  is built in debug mode and with debug symbols. Note that this enables some
  C4D SDK specific debug features, but the C++ toolkit's the `debug` option
  should be enabled as well. Thus, it is always a good idea to set the `debug`
  option globally.
- `.rtti` &ndash; By default the Cinema 4D SDK compiles with RTTI, thus the
  default value for this option is `false`. Note that this option will be
  set globally if no explicit global value is present in the Craftrfile.
- `.directory` &ndash; The directory of the Cinema 4D installation. If this
  option is not set, it will be automatically determined from the path of this
  Craftr package (TODO: Use the path of the MAIN Craftr package instead).
- `.release` &ndash; The Cinema 4D release to compile for. If not specified,
  the script will attempt to automatically determine the number of the
  `.directory` or `.version` options.
- `.version` &ndash; If specified, instead of using the `.directory` option,
  the Cinema 4D SDK will be downloaded from the URL specified with the `.url`
  option. Check https://public.niklasrosenstein.com/cinema4dsdk/ for available
  versions if you keep the `.url` default value.
- `.url` &ndash; The URL to download the Cinema 4D SDK source from. The default
  value for this option is `https://public.niklasrosenstein.com/cinema4dsdk/c4dsdk-${VERSION}.tar.gz`.

__Version Matrix__:

| Version       | Windows            | OSX               |
| ------------- | ------------------ | ----------------- |
| Cinema 4D R18 | Visual Studio 2013 | Apple XCode 7     |
| Cinema 4D R17 | Visual Studio 2013 | Apple XCode 6     |
| Cinema 4D R16 | Visual Studio 2012 | Apple XCode 5.0.2 |
| Cinema 4D R15 | Visual Studio 2012 | Apple XCode 4.6.3 |
| Cinema 4D R14 | Visual Studio 2010 | Apple XCode 4.3.2 |
| Cinema 4D R13 | Visual Studio 2005 | Apple XCode 3.2.6 |

> <sub>source: https://developers.maxon.net/?page_id=1108</sub>

__Example__:

```python
cxx = load('craftr.lang.cxx')
c4d = load('NiklasRosenstein.maxon.c4d')

plugin = cxx.shared_library(
  output = local('myplugin'),
  inputs = cxx.compile_cpp(
    sources = glob('src/**/*.cpp'),
    frameworks = [c4d.sdk]
  )
)
```

__Known Issues__:

- Building R15.064, R16.021, R16.050 with **Visual Studio 2015** <sub>v140</sub> fails

## FAQ

__Why `NiklasRosenstein.maxon.c4d`?__

Craftr requires packages to be namespaced.

__Will MinGW be supported anytime soon?__

It is planned for the future.
