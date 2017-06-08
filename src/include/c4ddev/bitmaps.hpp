/// Copyright (C) 2017 Niklas Rosenstein
/// All rights reserved.

#pragma once
#include <c4d.h>

namespace c4ddev {

  enum BLIT_MODE {
    BLIT_NN,
    BLIT_BILINEAR,
    BLIT_BICUBIC
  };

  // Render one bitmap onto another using one of three interpolation modes
  // as specified by the #BLIT_MODE enumeration.
  void BlitBitmap(
    BaseBitmap* dst,
    BaseBitmap* src,
    Int32 dx,
    Int32 dy,
    Int32 dw,
    Int32 dh,
    Int32 sx,
    Int32 sy,
    Int32 sw,
    Int32 sh,
    BLIT_MODE mode=BLIT_NN
  );

} // namespace c4ddev
