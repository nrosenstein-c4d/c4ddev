# -*- coding: utf8; -*-
#
# Copyright (C) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import c4d


def closest_point_on_line(a, b, p):
  ''' Returns the closest point to *p* which is on the line through the
  points *a* and *b*. :class:`ZeroDivisionError` is raised if *a* and
  *b* are the same. '''

  ap = a - p
  ab = b - a
  ab2 = ab.x ** 2 + ab.y ** 2 + ab.z ** 2
  ab_ap = (ap.x * ab.x) + (ap.y * ab.y) + (ap.z * ab.z)
  t = ab_ap / ab2
  return a - ab * t


def line_line_intersection(p1, d1, p2, d2, precision=1.0e-7):
  ''' Calculates the intersection point of the two lines defined
  by *p1*, *d1* and *p2*, *d2*.

  :param p1: A point on the first line.
  :param d1: The direction of the first line.
  :param p2: A point on the second line.
  :param d2: The direction of the second line.
  :param precision: The accepted deviation between the components
    of the linear factors.
  :return: A :class:`c4d.Vector` if the lines intersect, None otherwise. '''

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
    ''' Combines the lowest components of the two vectors *a* and *b*
    into a new vector.

    :param a: The first vector.
    :param b: The second vector.
    :param copy: If True, a copy of *a* will be created and returned
      from this function. Otherwise, *a* will be used and returned
      directly.
    '''

    if copy:
      c = c4d.Vector(a)
    else:
      c = a
    if b.x < a.x: c.x = b.x
    if b.y < a.y: c.y = b.y
    if b.z < a.z: c.z = b.z
    return c


def vmax(a, b, copy=True):
    ''' Combines the highest components of the two vectors *a* and *b*
    into a new vector.

    :param a: The first vector.
    :param b: The second vector.
    :param copy: If True, a copy of *a* will be created and returned
      from this function. Otherwise, *a* will be used and returned
      directly.
    '''

    if copy:
      c = c4d.Vector(a)
    else:
      c = a
    if b.x > a.x: c.x = b.x
    if b.y > a.y: c.y = b.y
    if b.z > a.z: c.z = b.z
    return c
