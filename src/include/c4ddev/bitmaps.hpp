/// Copyright (C) 2017 Niklas Rosenstein
/// All rights reserved.

#pragma once
#include <c4d.h>
#include "math.hpp"

namespace c4ddev {

  enum BLIT_MODE {
    BLIT_NN,
    BLIT_BILINEAR,
    BLIT_BICUBIC
  };

  //
  // Render one bitmap onto another using one of three interpolation modes as
  // specified by the #BLIT_MODE enumeration
  // The #FuncRead function must have the following signature:
  //     bool (Int32 x, Int32 y, Float col[4])
  // The #FuncWrite function must have the following signature:
  //     bool (Int32 x, Int32 y, Float const col[4])
  //
  template <typename FuncWrite, typename FuncRead>
  void BlitBitmap(
    FuncWrite&& write,
    FuncRead&& read,
    Int32 dx,
    Int32 dy,
    Int32 dw,
    Int32 dh,
    Int32 sx,
    Int32 sy,
    Int32 sw,
    Int32 sh,
    BLIT_MODE mode=BLIT_NN
  ){
    // 5 colors with each 4 components.
    Float c[5][4];
    #pragma omp parallel for private(c)
    for (Int32 y1 = 0; y1 < dh; ++y1) {
      for (Int32 x1 = 0; x1 < dw; ++x1) {
        // Map the coordinates onto the source bitmap.
        Float y = (y1 / Float(dh)) * sh + sx;
        Float x = (x1 / Float(dw)) * sw + sy;
        Int32 iy = Floor(y);
        Int32 ix = Floor(x);
        Bool valid = read(ix+0, iy+1, c[0]) && read(ix+0, iy+0, c[1]) && read(ix+1, iy+0, c[2]) && read(ix+1, iy+1, c[3]);
        if (!valid) continue;

        if (mode == 1) {
          // FIXME: Black tear-line appearing in upscaled image.
          c[4][0] = BilinearInterpolation(c[0][0], c[0][1], c[0][2], c[0][3], ix, iy, ix+1, iy+1, x, y);
          c[4][1] = BilinearInterpolation(c[1][0], c[1][1], c[1][2], c[1][3], ix, iy, ix+1, iy+1, x, y);
          c[4][2] = BilinearInterpolation(c[2][0], c[2][1], c[2][2], c[2][3], ix, iy, ix+1, iy+1, x, y);
          c[4][3] = BilinearInterpolation(c[3][0], c[3][1], c[3][2], c[3][3], ix, iy, ix+1, iy+1, x, y);
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
          memcpy(c[4], c[0], sizeof(c[0]));
        }
        write(dx+x1, dy+y1, c[4]);
      }
    }

  }

  inline void BlitBitmap(
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
  ){
    // FIXME: Alpha.
    Int32 dbw = dst->GetBw();
    Int32 dbh = dst->GetBh();
    Int32 sbw = src->GetBw();
    Int32 sbh = src->GetBh();
    return BlitBitmap(
      [dst, dbw, dbh](Int32 x, Int32 y, Float const col[4]) {
        if (x < 0 || y < 0 || x >= dbw || y >= dbh) return false;
        dst->SetPixel(x, y, col[0], col[1], col[2]);
        return true;
      },
      [src, sbw, sbh](Int32 x, Int32 y, Float col[4]) {
        if (x < 0 || y < 0 || x >= sbw || y >= sbh) return false;
        UInt16 r, g, b, a = 255;
        src->GetPixel(x, y, &r, &g, &b);
        col[0] = r;
        col[1] = g;
        col[2] = b;
        col[3] = a;
        return true;
      },
      dx, dy, dw, dh, sx, sy, sw, sh, mode
    );
  }

  inline void BlitBitmap(
    GeClipMap* dst,
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
  ){
    // FIXME: Alpha.
    Int32 dbw = dst->GetBw();
    Int32 dbh = dst->GetBh();
    Int32 sbw = src->GetBw();
    Int32 sbh = src->GetBh();
    return BlitBitmap(
      [dst, dbw, dbh](Int32 x, Int32 y, Float const col[4]) {
        if (x < 0 || y < 0 || x >= dbw || y >= dbh) return false;
        dst->SetPixelRGBA(x, y, col[0], col[1], col[2], col[3]);
        return true;
      },
      [src, sbw, sbh](Int32 x, Int32 y, Float col[4]) {
        if (x < 0 || y < 0 || x >= sbw || y >= sbh) return false;
        UInt16 r, g, b, a = 255;
        src->GetPixel(x, y, &r, &g, &b);
        col[0] = r;
        col[1] = g;
        col[2] = b;
        col[3] = a;
        return true;
      },
      dx, dy, dw, dh, sx, sy, sw, sh, mode
    );
  }

} // namespace c4ddev
