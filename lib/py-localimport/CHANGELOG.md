#### 1.7.3

- `.pth` files are now evaluated when the `localimport()` constructor is
  called. Import statements in these files will still only be evaluated
  inside the context manager.

#### 1.7.2

- `localimport.discover()` now uses `pkgutil.iter_modules()` rather than
  `pkgutil.walk_packages()`: We only need to know the top-level package/module
  names and `walk_packages()` will cause actual packages to be imported in
  order to find submodules.

#### 1.7.1

- Fix `localimport.autodisable()` for Python 2 (where
  `pkgutil.walk_packages()` yields tuples instead of namedtuples).

#### 1.7.0

- Add `localimport(do_autodisable)` parameter which defaults to `True` *(Note:
  different semantics apply)*
- Add `localimport.discover()`
- Add `localimport.autodisable()`

#### 1.6.1

- Update setup.py to adjust README.rst for PyPI

#### v1.6.0

- fix #19 -- read `README.rst` as UTF-8 in setup.py
- fix issue when the current working directory is used as one of the
  localimport paths
- move non-member functions to global scope, out of the localimport class
- add `__author__` and __version__` to global scope

#### v1.5.2

- fix #17 where `sys.modules` changed size during iteration in
  `localimport.__enter__()` (Python 3)

#### v1.5.1

- add Python 3 compatibility

#### v1.5

- add `setup.py`
- add `make_min` and `make_b64` commands to `setup.py`
- fix possible error when `localimport(parent_dir)` parameter is
  not specified and the `__file__` of the Python module that uses
  localimport is in the current working directory

#### v1.4.16
- fix possible `KeyError` when restoring namespace module paths
- renamed `_localimport` class to `localimport`
- `localimport(parent_dir)` parameter is now determined dynamically
  using `sys._getframe()`
- support for [py-require][require]

#### v1.4.14
- Mockup `pkg_resources.declare_namespace()`, making it call
  `pkgutil.extend_path()` afterwards to ensure we find all available
  namespace paths

#### v1.4.13
- fixed possible KeyError and AttributeError when using
  the `_localimport.disable()` method

#### v1.4.12
- Removed auto discovering of modules importable from the local site
- Add `_localimport.disable()` method

#### v1.4.11
- Fixed a bug where re-using the `_localimport` context added local modules
  back to `sys.modules` but removed them immediately (#15)

#### v1.4.10
- Fix #13, `_extend_path()` now keeps order of the paths
- Updat class docstrings
- Add `do_eggs` and `do_pth` parameters to the constructor
- Fix #12, add `_discover()` method and automatic disabling of modules  that could conflict with modules from the `_localimport` site

#### v1.4.9

- Fix #11, remove `None`-entries of namespace packages in `sys.modules`
- `_localimport._extend_path()` is is now less tolerant about extending
  the namespace path and only does so when a `__init__.{py,pyc,pyo}` file
  exists in the parsed directory

#### v1.4.8

* Now checks any path for being a zipfile rather than just .egg files
