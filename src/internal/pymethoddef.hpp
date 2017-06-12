
#pragma once

/// A small helper to define a Python method.
#define METHODDEF(prefix, name, argstype) {#name, py_##prefix##name, argstype, prefix##name##_docstring}
