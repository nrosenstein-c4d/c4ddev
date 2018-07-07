# The MIT License (MIT)
#
# Copyright (c) 2018 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import c4d
import collections
from c4d import Vector


def closest_point_on_line(a, b, p):
  """
  Returns the closest point to *p* which is on the line through the points
  *a* and *b*. #ZeroDivisionError is raised if *a* and *b* are the same.
  """

  ap = a - p
  ab = b - a
  ab2 = ab.x ** 2 + ab.y ** 2 + ab.z ** 2
  ab_ap = (ap.x * ab.x) + (ap.y * ab.y) + (ap.z * ab.z)
  t = ab_ap / ab2
  return a - ab * t


def line_line_intersection(p1, d1, p2, d2, precision=1.0e-7):
  """
  Calculates the intersection point of the two lines defined by *p1*, *d1*
  and *p2*, *d2*.

  # Parameters
  p1 (c4d.Vector): A point on the first line.
  d1 (c4d.Vector): The direction of the first line.
  p2 (c4d.Vector): A point on the second line.
  d2 (c4d.Vector): The direction of the second line.
  precision (float):
    The accepted deviation between the components of the linear factors.
  return (c4d.Vector, None):
    The intersection point if the lines intersect, otherwise #None.
  """

  # xxx: Where did I find this algorithm??

  a = d1.Cross(d2)
  b = (p2 - p1).Cross(d2)
  c = c4d.Vector(b.x / a.x, b.y / a.y, b.z / a.z)

  # Now check if the resulting deviation can be accepted.
  ref = c.x
  val = ref
  for v in (c.y, c.z):
    if abs(v - ref) > precision:
      return None
    val += v

  return p1 + d1 * val / 3.0


def vmin(a, b, copy=True):
  """
  Combines the lowest components of the two vectors *a* and *b* into a
  new vector.
  """

  if copy:
    c = c4d.Vector(a)
  else:
    c = a
  if b.x < a.x: c.x = b.x
  if b.y < a.y: c.y = b.y
  if b.z < a.z: c.z = b.z
  return c


def vmax(a, b, copy=True):
  """
  Combines the highest components of the two vectors *a* and *b* into a
  new vector.
  """

  if copy:
    c = c4d.Vector(a)
  else:
    c = a
  if b.x > a.x: c.x = b.x
  if b.y > a.y: c.y = b.y
  if b.z > a.z: c.z = b.z
  return c


def vbbmid(vectors):
  """
  Returns the mid-point of the bounding box spanned by the list of vectors.
  This is different to the arithmetic middle of the points.
  """

  if not isinstance(vectors, collections.Sequence):
    raise ValueError('vectors must be a Sequence')
  vectors = tuple(vectors)
  if not vectors:
    raise ValueError('An empty sequence is not accepted.')

  min = Vector(vectors[0])
  max = Vector(min)
  for v in vectors:
    vmin(min, v)
    vmax(max, v)

  return (min + max) * 0.5
