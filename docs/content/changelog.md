+++
title = "Changelog"
+++

  [Node.py]: https://github.com/nodepy/nodepy

## v0.1.6 (development)

- add `c4ddev pluginid` command
- fix `c4ddev build-loader` command and add `--blob,--no-blob` options
- move `c4ddev.handlemousedrag()` to `c4ddev.HandleMouseDrag()`
- rename `c4ddev.fileselect_~()` to `c4ddev.FileSelect~()`
- rename `c4ddev.cast_node()` to `c4ddev.GeListNodeFromAddress()`
- add `c4ddev.GetUserAreaHandle()`
- add `c4ddev.GetClipMapHandle()`
- add `c4ddev.BlitClipMap()`
- add `c4ddev.am` module

## v0.1.5

- merge https://github.com/NiklasRosenstein/c4d-apex into C4DDev and
  rename everything from `c4d.apex` to `c4ddev`
- merge https://github.com/NiklasRosenstein/py-c4dtools into C4DDev
- merge https://github.com/NiklasRosenstein/c4d-sublime-script into C4DDev
- Rename SublimeScript to Scripting Server
- The Scripting Server must be enabled explicitly from the C4DDev plugin menu

## v0.1.4

- merge https://github.com/NiklasRosenstein/c4d-deprecated-ide into C4DDev
- update docs
- add `c4ddev run` command
- rename `c4ddev pip-get` command to `c4ddev get-pip`
- fix `c4ddev/scripting/localimport` and add `python/` to `PYTHONPATH` inside
  the context

__PyObject__

- renamed from *DrawHelper*
- extended to allow overriding of other `ObjectData` methods

__PyShader__

- changed interface to match the method names in `ShaderData`
- add "Open Editor" button
- Python code is now also evaluated in Material preview

__ResourcePackage__

- add `SetPrefix()` keyword
- allow newlines and skippable tokens before the `ResourcePackage` statement

## v0.1.3

- rewrite PyDrawHelper code (cb5aa58)
- fix reloading of c4ddev plugins by reloading the `require` module (7f61b5b)
- add option to install `c4ddev` command-line interface
- add `c4ddev pypkg` command
- add `c4ddev build-loader` command
- update C4DDev to be based completely on [Node.py]
- removed additional dependencies and convenience libraries like `requests` for now
- add `ResourcePackage(resource_name)` syntax

## v1.2

- update `require` module to v0.10
- merge PyDrawHelper plugin
- merge [PyShader](https://github.com/nr-plugins/pyshader) plugin

## v1.1

- add `.pubfile` for [git-publish](https://pypi.python.org/pypi/git-publish)
- add [`localimport`](https://github.com/NiklasRosenstein/py-localimport) v1.4.16 module
- add [`require`](https://github.com/NiklasRosenstein/py-localimport) v0.8 module
- add [`requests`](https://github.com/kennethreitz/requests) v2.10.0 module
- restructure c4ddev plugins to be loaded with `require()`
- restructure `c4ddev` modules to be loaded with `require()`
