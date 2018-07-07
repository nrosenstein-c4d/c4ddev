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
'''
This module implements a function for checking the alignment of the
normals of a polygon-object.
'''

import c4d
import math
from .utils import PolygonObjectInfo


def test_object_normals(op, info=None, logger=None):
  ''' Tests the normals of the :class:`c4d.PolygonObject` *op* if they're
  pointing to the in or outside of the object. Returns a list of boolean
  variables where each index defines wether the associated polygon's
  normal is pointing into the right direction or not.

  The algorithm works best on completely closed shapes with one
  segment only. The PolygonObject should also be valid, therefore not
  more than two polygons per edge, etc. The results might be incorrect
  with an invalid mesh structure.

  :param op: The :class:`c4d.PolygonObject` instance to test.
  :param info: A :class:`~nr.c4d.utils.PolygonObjectInfo` instance for
    the passed object, or None to generate on demand. If an info object
    is passed, it must support the following data: ``polygons``,
    ``normals`` and ``midpoints``.
  :param logger: An object implementing the logger interface. This
    is optional and only use for debug purposes.
  :return: A :class:`list` of :class:`bool` values and the *info*
    object that was passed or has been generated. '''

  if not info:
    info = PolygonObjectInfo(op, polygons=True, normals=True, midpoints=True)
  if info.polycount <= 0:
    return ([], None)

  collider = c4d.utils.GeRayCollider()
  if not collider.Init(op):
    raise RuntimeError('GeRayCollider could not be initialized.')

  mg = op.GetMg()
  mp = op.GetMp()
  size = op.GetRad()

  # Define three camera position for the object. We could simply use
  # one if there wouldn't be the special case where a polygon's normal
  # is exactly in an angle of 90°, where we can not define wether the
  # normal is correctly aligned or not.

  maxp = mp + size + c4d.Vector(size.GetLength() * 2)
  cam1 = c4d.Vector(maxp.x, 0, 0)
  cam2 = c4d.Vector(0, maxp.y, 0)
  cam3 = c4d.Vector(0, 0, maxp.z)

  # Check each polygon from each camera position for the angle between
  # them. If one of the angles is greater than 90°, the face is pointing
  # into the wrong direction.

  result = []
  iterator = enumerate(zip(info.normals, info.midpoints))
  for index, (normal, midpoint) in iterator:
    normal_aligned = False

    for cam in [cam1, cam2, cam3]:

      # Compute the direction vector from the cam to the midpoint
      # of the polygon and the ray length to garuantee a hit with
      # the polygon.
      direction = (midpoint - cam)
      length = direction.GetLengthSquared()
      direction.Normalize()

      # Compute the intersections point from the cam to the midpoint
      # of the polygon.
      collider.Intersect(cam, direction, length)
      intersections = {}
      for i in xrange(collider.GetIntersectionCount()):
        isect = collider.GetIntersection(i)

        # The GeRayCollider class may yield doubled intersections,
        # we filter them out this way.
        if isect['face_id'] not in intersections:
          intersections[isect['face_id']] = isect

      # Sort the intersections by distance to the cam.
      intersections = sorted(
          intersections.values(),
          key=lambda x: x['distance'])

      # Find the intersection with the current polygon and how
      # many polygons have been intersected before this polygon
      # was intersection.
      isect_index = -1
      isect = None
      for i, isect in enumerate(intersections):
        if isect['face_id'] == index:
          isect_index = i
          break

      # We actually *have* to find an intersection, it would be
      # a strange error if we wouldn't have found one.
      if isect_index < 0:
        if logger:
          message = "No intersection with face %d from cam %s"
          logger.warning(message % (index, cam))
        continue

      angle = c4d.utils.VectorAngle(normal, direction * -1)

      # If there has been one intersection with another face before
      # the intersection with the current polygon, the polygon is
      # assumed to be intended to face away from the camera. Same for
      # all other odd numbers of intersection that have occured
      # before the intersection with the current face.
      if isect_index % 2:
        angle = (math.pi / 2) - angle

      if not xor(isect['backface'], isect_index % 2):
        normal_aligned = True

    result.append(normal_aligned)

  return result, info


def align_object_normals(op, info=None, logger=None, normal_info=None):
  ''' Align the normals of the :class:`c4d.PolygonObject` *op* to point to
  the outside of the object. The same algorithmic restrictions as for
  :func:`test_object_normals` apply. The parameters are also the same.
  You can pass an already computed result of :func:`test_object_normals`
  for *normal_info*. '''

  if normal_info is None:
    normal_info, info = test_object_normals(op, info, logger)

  for i, state in enumerate(normal_info):
    if not state:
      p = info.polygons[i]
      if p.c == p.d:
        p.a, p.b, p.c = p.c, p.b, p.a
        p.d = p.c
      else:
        p.a, p.b, p.c, p.d = p.d, p.c, p.b, p.a

      op.SetPolygon(i, p)

  op.Message(c4d.MSG_CHANGE)
