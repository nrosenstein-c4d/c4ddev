/// Copyright (C) 2017 Niklas Rosenstein
/// All rights reserved.

#pragma once
#include <c4d.h>

namespace c4ddev {

  // Thanks to https://helloacm.com/cc-function-to-compute-the-bilinear-interpolation/
  inline Float BilinearInterpolation(
    Float q11, Float q12, Float q21, Float q22,
    Float x1, Float x2, Float y1, Float y2, Float x, Float y)
  {
      Float x2x1, y2y1, x2x, y2y, yy1, xx1;
      x2x1 = x2 - x1;
      y2y1 = y2 - y1;
      x2x = x2 - x;
      y2y = y2 - y;
      yy1 = y - y1;
      xx1 = x - x1;
      return 1.0 / (x2x1 * y2y1) * (
          q11 * x2x * y2y +
          q21 * xx1 * y2y +
          q12 * x2x * yy1 +
          q22 * xx1 * yy1
      );
  }

} // namespace c4ddev
