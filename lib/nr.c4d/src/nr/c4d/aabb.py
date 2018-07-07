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
This module provides the #AABB class to compute the axis aligned bounding box
of an object or a set of objects.
'''

import c4d
from c4d import Vector
from .math import vmin, vmax


class AABB(object):
  ''' This class is used to compute the axis aligned bounding box of
  an object, a set of objects or a set of points.

  .. code-block:: python

    from nr.c4d.misc import aabb
    box = aabb.AABB()
    box.add(point)
    box.add_object(op, recursive=True)
    print(box.midpoint)
    print(box.size)

  :param translation:

    A :class:`c4d.Matrix` that is applied to all points that are
    added to the *AABB* with :meth:`add`.

  .. attribute:: minv

    The minimum Vector. Initialized with None.

  .. attribute:: maxv

    The maximum Vector. Initialized with None.

  .. attribute:: init

    True if the *AABB* object has been initialized with at least one
    point, False if not.

  .. attribute:: translation

    The translation :class:`~c4d.Matrix` that is applied to all objects
    added to the box with :meth:`add`.
  '''

  def __init__(self, translation=None):
    super(AABB, self).__init__()
    if translation is None:
      translation = c4d.Matrix()

    self.minv = None
    self.maxv = None
    self.init = False
    self.translation = translation

  def add(self, point):
    ''' Add the specified *point* to the *AABB*. The point is multiplied
    by the internal :attr:`translation` matrix. '''

    point = point * self.translation
    if not self.init:
      self.minv = c4d.Vector(point)
      self.maxv = c4d.Vector(point)
      self.init = True
    else:
      self.minv = vmin(self.minv, point)
      self.maxv = vmax(self.maxv, point)

  def add_object(self, obj, recursive=False, slow=False):
    ''' Add corner points of *obj* to the *AABB*.

    :param obj: A :class:`c4d.BaseObject`
    :param recursive: If True, child objects will be added as well.
    :param slow: If True, :class:`c4d.PointObject` objects that are
      encountered are computed *slowly* by taking each point separately.
      This should usually not be necessary as the bounding box of the
      object is computed when :data:`c4d.MSG_UPDATE` is sent.
    '''

    mg = obj.GetMg()

    if slow and isinstance(obj, c4d.PointObject):
      for p in obj.GetAllPoints():
        self.add(p * mg)
    else:
      mp = obj.GetMp()
      bb = obj.GetRad()

      V = c4d.Vector

      self.add(V(mp.x + bb.x, mp.y + bb.y, mp.z + bb.z) * mg)
      self.add(V(mp.x - bb.x, mp.y + bb.y, mp.z + bb.z) * mg)
      self.add(V(mp.x + bb.x, mp.y + bb.y, mp.z - bb.z) * mg)
      self.add(V(mp.x - bb.x, mp.y + bb.y, mp.z - bb.z) * mg)

      self.add(V(mp.x + bb.x, mp.y - bb.y, mp.z + bb.z) * mg)
      self.add(V(mp.x - bb.x, mp.y - bb.y, mp.z + bb.z) * mg)
      self.add(V(mp.x + bb.x, mp.y - bb.y, mp.z - bb.z) * mg)
      self.add(V(mp.x - bb.x, mp.y - bb.y, mp.z - bb.z) * mg)

    if recursive:
      for child in obj.GetChildren():
        self.add_object(child, True)

  @property
  def midpoint(self):
    ''' The mid point of the bounding box. '''
    return (self.minv + self.maxv) * 0.5

  @property
  def size(self):
    ''' The size of the bounding box, from the middle to one of the corners. '''
    return (self.maxv - self.minv) * 0.5
