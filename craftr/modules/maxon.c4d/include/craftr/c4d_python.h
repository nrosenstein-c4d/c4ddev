/// Cinema 4D does not come with a debug binary distribution of Python,
/// so we make sure that Python does not assume debug mode.
#pragma push_macro("_DEBUG")
#ifdef _DEBUG
  #undef _DEBUG
#endif
#include <Python.h>
#pragma pop_macro("_DEBUG")
