# Copyright (C) 2016  Niklas Rosenstein
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

cxc = load('craftr.lang.cxx').cxc
dirs = __module__.dirs

# Gather a list of the C4D include directories.
include = [
  dirs.source,
  dirs.source + '/c4d_customgui',
  dirs.source + '/c4d_gv',
  dirs.source + '/c4d_libs',
  dirs.source + '/c4d_misc',
  dirs.source + '/c4d_misc/datastructures',
  dirs.source + '/c4d_misc/memory',
  dirs.source + '/c4d_misc/utilities',
  dirs.source + '/c4d_preview',
  dirs.source + '/c4d_scaling',
  dirs.resource + '/res/description'
]
if options.release <= 15:
  include += glob(['modules/*/res/description'], parent = dirs.resource)
  include += glob(['modules/*/res/description'], parent = dirs.c4d)
  include += glob(['modules/*/*/res/description'], parent = dirs.c4d)
else:
  include += glob(['modules/*/description'], parent = dirs.resource)
include = map(path.norm, include)

def get_windows_framework():
  debug = options.debug
  arch = 'x64' if '64' in cxc.target_arch else 'x86'

  defines = ['__PC']
  if options.release >= 15:
    defines += ['MAXON_API', 'MAXON_TARGET_WINDOWS']
    defines += ['MAXON_TARGET_DEBUG'] if debug else ['MAXON_TARGET_RELEASE']
    if arch == 'x64':
      defines += ['MAXON_TARGET_64BIT']
  else:
    defines += ['_DEBUG', 'DEBUG'] if debug else ['NDEBUG']
    if arch == 'x64':
      defines += ['__C4D_64BIT', 'WIN64', '_WIN64']
    else:
      defines += ['WIN32', '_WIN32']

  if debug:
    flags = []
  else:
    # These are not set by the MSVC interface.
    flags = ['/Oy-', '/Oi', '/Ob2', '/Ot', '/GF']

  if cxc.name == 'msvc' and cxc.version >= '19.00.24':
    # Cinema 4D does not properly detect Visual Studio 2015 Update 3 and
    # adds `#define decltype typeof` in compilerdetection.h.
    defines += ['_HAS_DECLTYPE']

  def prepare_link(linker, builder):
    suffix = '.cdl64' if arch == 'x64' else '.cdl'
    builder.setdefault('dll_suffix', suffix)

  return Framework('maxon.c4d',
    debug = debug,
    include = include,
    defines = defines,
    exceptions = False,
    warn = 'all',
    msvc_disable_warnings = (
      '4062 4100 4127 4131 4201 4210 4242 4244 4245 4305 4310 4324 4355 '
      '4365 4389 4505 4512 4611 4706 4718 4740 4748 4996 4595 4458').split(),
    msvc_warnings_as_errors = ['4264'],
    msvc_compile_additional_flags = (
      '/vmg /vms /w44263 /FC /errorReport:prompt /fp:precise /Zc:wchar_t- '
      '/Gd /TP /WX- /MP /Gm- /Gs /Gy-').split() + flags,
    clangcl_compile_additional_flags = (
      '-Wno-unused-parameter -Wno-macro-redefined -Wno-microsoft-enum-value '
      '-Wno-unused-private-field'.split()
    ),
    llvm_compile_additional_flags = (
      '-fms-memptr-rep=virtual -fms-memptr-rep=single'.split()  # /vmg /vms
    ),
    cxc_link_prepare_callbacks = [prepare_link]
  )


def get_mac_or_linux_framework():
  debug = options.debug
  stdlib = 'stdc++' if options.release <= 15 else 'c++'

  defines = []
  if platform.name == 'mac':
    defines += ['C4D_COCOA', '__MAC']
    if options.release >= 15:
      defines += ['MAXON_TARGET_OSX']
  elif platform.name == 'linux':
    defines += ['__LINUX']
    if options.release >= 15:
      defines += ['MAXON_TARGET_LINUX']
  else:
    assert False

  if options.release >= 15:
    defines += ['MAXON_API']
    defines += ['MAXON_TARGET_DEBUG'] if debug else ['MAXON_TARGET_RELEASE']
    defines += ['MAXON_TARGET_64BIT']
  else:
    defines += ['_DEBUG', 'DEBUG'] if debug else ['NDEBUG']
    defines += ['__C4D_64BIT']

  if options.release <= 15:
    flags = shell.split('''
      -fmessage-length=0 -Wno-trigraphs -Wno-missing-field-initializers
      -Wno-non-virtual-dtor -Woverloaded-virtual -Wmissing-braces -Wparentheses
      -Wno-switch -Wunused-function -Wunused-label -Wno-unused-parameter
      -Wunused-variable -Wunused-value -Wno-empty-body -Wno-uninitialized
      -Wunknown-pragmas -Wno-shadow -Wno-conversion -fstrict-aliasing
      -Wdeprecated-declarations -Wno-invalid-offsetof -msse3 -fvisibility=hidden
      -fvisibility-inlines-hidden -Wno-sign-conversion -fno-math-errno''')
    if platform.name == 'mac':
      flags += shell.split('''
        -mmacosx-version-min=10.6 -Wno-int-conversion -Wno-logical-op-parentheses
        -Wno-shorten-64-to-32 -Wno-enum-conversion -Wno-bool-conversion
        -Wno-constant-conversion''')
  else:
    flags = shell.split('''
      -fmessage-length=0 -Wno-trigraphs -Wmissing-field-initializers
      -Wno-non-virtual-dtor -Woverloaded-virtual -Wmissing-braces -Wparentheses
      -Wno-switch -Wunused-function -Wunused-label -Wno-unused-parameter
      -Wunused-variable -Wunused-value -Wempty-body -Wuninitialized
      -Wunknown-pragmas -Wshadow -Wno-conversion -Wsign-compare -fstrict-aliasing
      -Wdeprecated-declarations -Wno-invalid-offsetof -msse3 -fvisibility=hidden
      -fvisibility-inlines-hidden -Wno-sign-conversion -fno-math-errno''')
    if platform.name == 'mac':
      flags += shell.split('''
        -mmacosx-version-min=10.7 -Wconstant-conversion -Wbool-conversion
        -Wenum-conversion -Wshorten-64-to-32 -Wint-conversion''')

  if platform.name == 'mac':
    flags += shell.split('''
      -fdiagnostics-show-note-include-stack -fmacro-backtrace-limit=0
      -fpascal-strings -fasm-blocks -Wno-c++11-extensions -Wno-newline-eof
      -Wno-four-char-constants -Wno-exit-time-destructors
      -Wno-missing-prototypes''')
    # These flags are not usually set in the C4D SDK.
    flags += ['-Wno-unused-private-field']
  elif platform.name == 'linux':
    flags += shell.split('''
      -Wno-multichar -Wno-strict-aliasing -Wno-shadow -Wno-conversion-null''')

  forced_include = []
  if platform.name == 'mac' and options.release <= 15:
    if debug:
      forced_include = [path.join(dirs.source, 'ge_mac_debug_flags.h')]
    else:
      forced_include = [path.join(dirs.source, 'ge_mac_flags.h')]
    for f in ['__C4D_64BIT', '__MAC']:  # already in flags header
      try: defines.remove(f)
      except ValueError: pass

  def prepare_compile(compiler, builder):
    builder.setdefault('cpp_stdlib', stdlib)
    builder.setdefault('std', 'c++11')
    builder.add_local_framework('maxon.c4d_sdk.mac.compile',
      additional_flags = flags
    )

  return Framework('maxon.c4d_sdk',
    debug = debug,
    defines = defines,
    include = include,
    exceptions = False,
    forced_include = forced_include,
    pic = True,
    cxc_compile_prepare_callbacks = [prepare_compile]
  )


def get_frameworks():
  if platform.name == 'win':
    c4d_sdk = get_windows_framework()
  elif platform.name in ('mac', 'linux'):
    c4d_sdk = get_mac_or_linux_framework()
  else:
    assert False
  c4d_legacy_sdk = Framework('maxon.c4d_legacy_sdk',
    frameworks = [c4d_sdk],
    defines = ['__LEGACY_API']
  )
  c4d_sdk['include'] += [local('include')]
  return c4d_sdk, c4d_legacy_sdk
