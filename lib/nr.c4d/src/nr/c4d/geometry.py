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
"""
This module provides common helper methods for working with geometry in
Cinema 4D, such as computing face- and vertex normals.
"""

import c4d


def calculate_face_normals(op=None, points=None, polys=None):
  """
  Builds a list of face normals and polygon midpoints from *op* or the
  specified *points* and *polygons* lists.

  # Parameters
  op (c4d.PolygonObject):
  points (list of c4d.Vector):
  polys (list of c4d.CPolygon):
  return (tuple of (list of c4d.Vector, list of c4d.Vector):
    The first element is the polygon normals, the second is the polygon
    midpoints.
  """

  if points is None:
    points = op.GetAllPoints()
  if polys is None:
    polys = op.GetAllPoints()

  midpoints = []
  normals = []

  for poly in polys:
    a, b, c, d = points[poly.a], points[poly.b], points[poly.c], points[poly.d]
    midp = a + b + c
    if poly.c == poly.d:
      midp *= 1.0 / 3
    else:
      midp = (midp + d) * (1.0 / 4)
    midpoints.append(midp)
    normals.append((b - a).Cross(d - a))

  return (normals, midpoints)


def build_point_connection_list(op, nb, polys=None):
  """
  Builds a list that for each vertex contains a tuple which consists of the
  indices of points connected with that respective point by an edge in the
  mesh.

  ```python
  from nr.c4d.geometry import build_point_connection_list
  from c4d.utils import Neighbor

  def main():
    nb = Neighbor()
    nb.Init(op)
    conn = build_point_connection_list(op, nb)
    print "Points connected with point 1:", conn[1]
  ```

  # Parameters
  o (c4d.PolygonObject):
  nb (c4d.utils.Neighbor): Must be initialized with *op*.
  polys (list of c4d.CPolygon): An optional list of the polygons of *op*.
  return (list of tuple of int):
  """

  result = []
  if polys is None:
    polys = op.GetAllPolygons()
  for pindex in xrange(op.GetPointCount()):
    connections = set()
    for findex in nb.GetPointPolys(pindex):
      poly = polys[findex]
      if poly.a == pindex:
        connections.add(poly.d)
        connections.add(poly.b)
      elif poly.b == pindex:
        connections.add(poly.a)
        connections.add(poly.c)
      elif poly.c == pindex:
        connections.add(poly.b)
        connections.add(poly.d)
      elif poly.d == pindex:
        connections.add(poly.c)
        connections.add(poly.a)
    result.append(tuple(connections))
  return result
