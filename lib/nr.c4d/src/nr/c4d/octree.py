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
''' Experimental octree implementation in Python. '''


import abc
import c4d
import weakref
from .aabb import AABB


def vector_variants(v):
  ''' Yields all variants of the :class:`c4d.Vector` *v*, that is,
  all possible combinations of positive and negative sign for all
  three components. '''

  V = c4d.Vector
  yield V(+v.x, +v.y, +v.z)
  yield V(+v.x, +v.y, -v.z)
  yield V(+v.x, -v.y, +v.z)
  yield V(+v.x, -v.y, -v.z)

  yield V(-v.x, +v.y, +v.z)
  yield V(-v.x, +v.y, -v.z)
  yield V(-v.x, -v.y, +v.z)
  yield V(-v.x, -v.y, -v.z)


def box_box_intersect(m1, s1, m2, s2):
  ''' Checks if the AABB (axis-aligned bounding-box) defined by *m1*
  and *s1* intersects with the AABB of *m2* and *s2*. The position
  must be the middle point of the box, the size defined the radius of
  the box from its middle point. '''

  m1p = m1 + s1
  m2n = m2 - s2
  if m1p.x < m2n.x:
    return False
  if m1p.y < m2n.y:
    return False
  if m1p.z < m2n.z:
    return False

  m1n = m1 - s1
  m2p = m2 + s2
  if m2p.x < m1n.x:
    return False
  if m2p.y < m1n.y:
    return False
  if m2p.z < m1n.z:
    return False

  return True


def box_box_contains(m1, s1, m2, s2):
  ''' Returns True if the box spanned by *m1* and *s1* contains the
  box spanned by *m2* and *s2* completely. '''

  m1p = m1 + s1
  m2p = m2 + s2
  if m2p.x > m1p.x:
    return False
  if m2p.y > m1p.y:
    return False
  if m2p.z > m1p.z:
    return False

  m1n = m1 - s1
  m2n = m2 - s2
  if m2n.x < m1n.x:
    return False
  if m2n.y < m1n.y:
    return False
  if m2n.z < m1n.z:
    return False

  return True


def box_point_contains(p, m, s):
  ''' Checks if the point *v* is located inside the box defined
  by *m* and *s*. Returns True if it is, False if not. '''

  mp = m + s
  if mp.x < v.x:
    return False
  if mp.y < v.y:
    return False
  if mp.z < v.z:
    return False

  mn = m - s
  if v.x < mn.x:
    return False
  if v.y < mn.y:
    return False
  if v.z < mn.z:
    return False

  return True


class OcItem(object):

  def __init__(self, data, position, size):
    super(OcItem, self).__init__()
    self.data = data
    self.position = position
    self.size = size
    self.containers = []

  def __call__(self):
    return self.data

  def leaf_containers(self):
    ''' Iterator for all containers that are leaf nodes. '''

    for node in self.containers:
      node = node()
      if node.is_leaf:
        yield node

  def neighbours(self):
    ''' Iterates over all items that are contained in the same
    leaf containers of this node. '''

    for node in self.leaf_containers():
      for item in node.data:
        if item is not self:
          yield item


class OcInterface(object):
  ''' Interface for reading size and position of data in the Octree. '''

  @abc.abstractmethod
  def get_metrics(self, item):
    pass


class OcObjectImpl(OcInterface):

  def __init__(self, translation=None):
    super(OcObjectImpl, self).__init__()
    self.translation = c4d.Matrix(translation) if translation else c4d.Matrix()

  def get_metrics(self, obj):
    mat = self.translation * obj.GetMg()
    rad = obj.GetRad()
    bb = AABB()

    for v in vector_variants(rad):
      bb.add(v * mat)
    return bb.midp, bb.size


class OcNode(object):
  ''' Represents a node in an Octree.

  .. attribute:: tree

    A weak reference to the root node of the tree.

  .. attribute:: parent

    A weak-reference to the parent node.

  .. attribute:: position

    The position of the node in 3D space.

  .. attribute:: size

    The size of the node in all-positive direction.

  .. attribute:: data

    A list of :class:`OcItem` instances.

  .. attribute:: children

    A list of children. None if the OcNode is a leaf node.
  '''

  def __init__(self, tree, parent, position, size, depth):
    super(OcNode, self).__init__()
    self.tree = weakref.ref(tree)
    self.parent = weakref.ref(parent) if parent is not None else None
    self.position = c4d.Vector(position)
    self.size = c4d.Vector(size)
    self.data = []
    self.depth = depth
    self.children = None

  @property
  def is_leaf(self):
    return not self.children

  def append(self, obj):
    ''' Appends *obj* to this OcNode and eventually to its child
    nodes. This might not work if the node can not contain the
    *obj*. This method must be called at the root node of the tree.

    :param obj: The obj to add.
    :raise RuntimeError: If this method is not called on
      the root node of the tree.
    :return: True if the obj was added, False if not. '''

    if self.parent:
      raise RuntimeError('must be called in the root node')

    item = OcItem(obj, *self.tree().impl.get_metrics(obj))
    return self.append_item(item)

  def append_item(self, item):
    ''' Appends *item* to this OcNode and eventually to its child
    nodes. This might not work if the node can not contain the
    *item* or if the node is completely contained inside the

    :param item: The item to add.
    :return: True if the item was added, False if not. '''

    # If the box of the item does not intersect with the box
    # of this node, it won't be added to this node.
    if not box_box_intersect(
        self.position, self.size, item.position, item.size):
      return False

    # Also, if the node is completely contained in the box of
    # the item, it won't be added either. It must be handled
    # by a parent node instead.
    if box_box_contains(
        item.position, item.size, self.position, self.size):
      return False

    # Subdivide the node if it isn't already.
    do_subdivide = self.is_leaf
    do_subdivide &= len(self.data) >= self.tree().max_capacity
    do_subdivide &= self.depth < self.tree().max_depth
    if do_subdivide:
      self.subdivide()

    # Add the item to the entries.
    self.data.append(item)
    item.containers.append(weakref.ref(self))

    # Forward to the child nodes.
    if self.children:
      for child in self.children:
        child.append_item(item)

    return True

  def subdivide(self):
    ''' Subdivides the OcNode into 8 equally sized child nodes.
    This is done automatically when the maximum capacity of a
    node is reached by appending to it. '''

    if self.children:
      raise RuntimeError('node already subdivided')

    V = c4d.Vector
    tree = self.tree()
    pos = self.position
    halfsize = self.size ^ c4d.Vector(0.5)

    self.children = []
    for variant in vector_variants(halfsize):
      child = OcNode(tree, self, pos + variant, halfsize, self.depth + 1)
      for item in self.data:
        child.append_item(item)
      self.children.append(child)


class OcTree(OcNode):
  ''' Represents the full Octree. Note that elements that are large
  enough to fully contain the root node can not be added to it. '''

  def __init__(self, max_capacity, max_depth, position, size, impl):
    super(OcTree, self).__init__(self, None, position, size, 0)
    self.impl = impl
    self.max_capacity = int(max_capacity)
    self.max_depth = int(max_depth)
    assert self.max_capacity > 1
