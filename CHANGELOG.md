# c4ddev Changelog

#### v1.3 (current stream)

- rewrite PyDrawHelper code (cb5aa58)
- fix reloading of c4ddev plugins by reloading the `require` module (7f61b5b)

#### v1.2

- update `require` module to v0.10
- merge PyDrawHelper plugin
- merge [PyShader](https://github.com/nr-plugins/pyshader) plugin

#### v1.1

- add `.pubfile` for [git-publish](https://pypi.python.org/pypi/git-publish)
- add [`localimport`](https://github.com/NiklasRosenstein/py-localimport) v1.4.16 module
- add [`require`](https://github.com/NiklasRosenstein/py-localimport) v0.8 module
- add [`requests`](https://github.com/kennethreitz/requests) v2.10.0 module
- restructure c4ddev plugins to be loaded with `require()`
- restructure `c4ddev` modules to be loaded with `require()`
