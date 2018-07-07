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
Helpers to work with Cinema 4D XPresso Nodes (mostly GUI related).
"""

import c4d
from c4d.modules import graphview as gv
from .math import vbbmid


class GraphNode(object):
  ''' This class is a thin wrapper for the `c4d.modules.graphview.GvNode`
  class providing an easy interface for accessing and modifieng the
  visual appeareance of an XPresso node in the XPresso editor.

  Currently, only accessing the position and size is supported.
  '''

  POS_X = 100
  POS_Y = 101
  VIEWPOS_X = 102
  VIEWPOS_Y = 103
  SIZE_X = 108
  SIZE_Y = 109
  FULLSCREENSIZE_X = 110
  FULLSCREENSIZE_Y = 111

  ZOOM = 104
  VIEW = 105

  VIEW_MINIMIZED = 0
  VIEW_STANDART = 1
  VIEW_EXTENDED = 2
  VIEW_FULLSCREEN = 3

  def __init__(self, node):
    super(GraphNode, self).__init__()
    self.node = node

    container = node.GetDataInstance()
    container = self.get_graphcontainer(container)
    self.graphdata = container

  def get_graphcontainer(self, container):
    ''' This method returns the container containing the graphdata for
    the node in the XPresso grap based on the ``GvNode`` s container.
    '''

    data = container.GetContainerInstance(1001)
    data = data.GetContainerInstance(1000)
    return data

  def get_sizeids(self):
    if self.view == self.VIEW_EXTENDED:
      id_x = self.FULLSCREENSIZE_X
      id_y = self.FULLSCREENSIZE_Y
    else:
      id_x = self.SIZE_X
      id_y = self.SIZE_Y
    return (id_x, id_y)

  @property
  def position(self):
    ''' Returns the visual position of the node as c4d.Vector. '''

    data = self.graphdata
    x = data.GetReal(self.POS_X)
    y = data.GetReal(self.POS_Y)
    return c4d.Vector(x, y, 0)

  @position.setter
  def position(self, value):
    data = self.graphdata
    data.SetReal(self.POS_X, value.x)
    data.SetReal(self.POS_Y, value.y)

  @property
  def view_position(self):
    ''' Returns the position of the "camera" that is "looking" onto the
    nodes as c4d.Vector.
    '''

    data = self.graphdata
    x = data.GetReal(self.VIEWPOS_X)
    y = data.GetReal(self.VIEWPOS_Y)
    return c4d.Vector(x, y, 0)

  @view_position.setter
  def view_position(self, value):
    data = self.graphdata
    data.SetReal(self.VIEWPOS_X, value.x)
    data.SetReal(self.VIEWPOS_Y, value.y)

  @property
  def size(self):
    ''' Returns the visual size of the node as c4d.Vector. The container
    IDs differ for extended and standart view mode. The size is
    read/set according the to view mode the node is currently
    assigned to.
    '''

    data = self.graphdata
    id_x, id_y = self.get_sizeids()
    x = data.GetReal(id_x)
    y = data.GetReal(id_y)
    return c4d.Vector(x, y, 0)

  @size.setter
  def size(self, value):
    data = self.graphdata
    id_x, id_y = self.get_sizeids()
    data.SetReal(id_x, value.x)
    data.SetReal(id_y, value.y)

  @property
  def zoom(self):
    ''' Returns the zoom of the XPresso nodes graphview. This value is
    only has effect for XGroups. The zoom is a floating-point value,
    100% represented as 1.0.
    '''

    return self.graphdata.GetReal(self.ZOOM)

  @zoom.setter
  def zoom(self, value):
    self.graphdata.SetReal(self.ZOOM, value)

  @property
  def view(self):
    ''' Returns the type of view of the node. Either VIEW_MINIMIZED,
    VIEW_STANDART, VIEW_EXTENDED or VIEW_FULLSCREEN.

    Note: Still not sure how the locking is specified in the container,
        it is however defined in the View section in the GUI.
    '''

    return self.graphdata.GetLong(self.VIEW)

  @view.setter
  def view(self, value):
    self.graphdata.SetLong(self.VIEW, value)


def find_selected_nodes(root):
  ''' Finds the group of selected nodes in the XPresso Manager and returns
  a list of GvNode objects.
  '''

  children = root.GetChildren()
  selected = []
  for child in children:
    if child.GetBit(c4d.BIT_ACTIVE):
      selected.append(child)
  if not selected:
    for child in children:
      selected = find_selected_nodes(child)
      if selected:
        return selected
  return selected


def find_nodes_mid(nodes):
  ''' Finds the mid-point of the passed list of
  `c4dtools.misc.graphnode.GraphNode` instances.
  '''

  if not nodes:
    return c4d.Vector(0)

  vectors = [n.position for n in nodes]
  return vbbmid(vectors)
