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

if options.release >= 17:
  version = '2.7'
elif options.release >= 12:
  version = '2.6'
else:
  version = None


def get_framework():
  join = path.join
  if options.release >= 16:
    resource = join(__module__.dirs.resource, 'modules', 'python')
  else:
    resource = join(__module__.dirs.resource, 'modules', 'python', 'res')

  if platform.name == 'win':
    arch = '86' if cxc.target_arch == 'x86' else '64'
    fw_path = join(resource, 'Python.win' + arch + '.framework')
    lib = 'python' + version.replace('.', '')
    lib_path = join(fw_path, 'libs', 'python' + version.replace('.', ''))

    lib_full_path = join(lib_path, lib + '.lib')
    if not path.isdir(lib_full_path):
      lib_full_path = path.dirname(lib_full_path)

    # There are multiple paths where the include directory could be.
    include = join(fw_path, 'include', 'python' + version.replace('.', ''))
    if not path.isdir(include):
      include = path.join(path.dirname(include), 'python' + version)
    if not path.isdir(include):
      include = path.dirname(include)

    return Framework('maxon.c4d_python',
      include = [include, local('fix/python_api')],
      libpath = [lib_path],
    )
  elif platform.name == 'mac':
    fw_path = join(resource, 'Python.osx.framework')
    lib = 'Python.osx'
    lib_path = fw_path
    lib_full_path = join(lib_path, lib)
    include = join(fw_path, 'include', 'python' + version)

    return Framework('maxon.c4d_python',
      include = [include, local('fix/python_api')],
      external_libs = [lib_full_path],
    )
  elif platform.name == 'linux':
    return None
  else:
    assert False
