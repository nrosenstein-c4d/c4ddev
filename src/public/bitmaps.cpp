/// Copyright (C) 2017 Niklas Rosenstein
/// All rights reserved.

#include <c4ddev/bitmaps.hpp>
#include <c4ddev/math.hpp>

void c4ddev::BlitBitmap(
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
  BLIT_MODE mode
){
  // FIXME: Boundchecks
  if (!dst || !src) return;
  UInt16 r[5], g[5], b[5], a[5];
  #pragma omp parallel for private(r, g, b, a)
  for (Int32 y1 = 0; y1 < dh; ++y1) {
    for (Int32 x1 = 0; x1 < dw; ++x1) {
      // Map the coordinates onto the source bitmap.
      Float y = (y1 / Float(dh)) * sh + sx;
      Float x = (x1 / Float(dw)) * sw + sy;
      Int32 iy = Floor(y);
      Int32 ix = Floor(x);
      src->GetPixel(ix+0, iy+1, r+0, g+0, b+0);
      src->GetPixel(ix+0, iy+0, r+1, g+1, b+1);
      src->GetPixel(ix+1, iy+0, r+2, g+2, b+2);
      src->GetPixel(ix+1, iy+1, r+3, g+3, b+3);

      if (mode == 1) {
        // FIXME: Black tear-line appearing in upscaled image.
        r[4] = BilinearInterpolation(r[0], r[1], r[2], r[3], ix, iy, ix+1, iy+1, x, y);
        g[4] = BilinearInterpolation(g[0], g[1], g[2], g[3], ix, iy, ix+1, iy+1, x, y);
        b[4] = BilinearInterpolation(b[0], b[1], b[2], b[3], ix, iy, ix+1, iy+1, x, y);
        a[4] = BilinearInterpolation(a[0], a[1], a[2], a[3], ix, iy, ix+1, iy+1, x, y);
      }
      else if (mode == 2) {
        // FIXME: Implement Bicubic interpolation.
        //r[4] = BicubicInterpolation(r[0], r[1], r[2], r[3], ix, iy, ix+1, iy+1, x, y);
        //g[4] = BicubicInterpolation(g[0], g[1], g[2], g[3], ix, iy, ix+1, iy+1, x, y);
        //b[4] = BicubicInterpolation(b[0], b[1], b[2], b[3], ix, iy, ix+1, iy+1, x, y);
        //a[4] = BicubicInterpolation(a[0], a[1], a[2], a[3], ix, iy, ix+1, iy+1, x, y);
      }
      else {
        // FIXME: Proper nearest neighbour interpolation.
        r[4] = r[0];
        g[4] = g[0];
        b[4] = b[0];
        a[4] = a[0];
      }
      dst->SetPixel(dx+x1, dy+y1, r[4], g[4], b[4]);
    }
  }
}
