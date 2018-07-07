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

from .utils import UndoHandler, find_root


class Error(Exception):
  '''
  This exception is generally raised if an exception in a modeling
  function occurred. For instance, if the required preconditions for
  the "Current State to Object" command are not met, it will return no
  object in which case this exception is raised.
  '''


class Kernel(object):
  '''
  The *Kernel* class provides all modeling functionality. Some
  modeling functions require a document to operate in, others may
  even require it to be the active Cinema 4D document as it may use
  :func:`c4d.CallCommand` to achieve its goal. Yet, the *Kernel*
  does not necessarily be initialized with a document. You will be
  able to use all functions that do not require it. Some methods are
  even static as they require no specialised context.

  To create a temporary document, you should use the
  :class:`nr.c4d.utils.TemporaryDocument` class.
  '''

  def __init__(self, doc=None):
    super(Kernel, self).__init__()
    self._doc = doc

    if doc is not None and not isinstance(doc, c4d.documents.BaseDocument):
      raise TypeError('<doc> must be BaseDocument', type(doc))

  @staticmethod
  def triangulate(obj):
    '''
    Triangulates the PolygonObject *obj* in place.

    :raise TypeError: If *obj* is not a PolygonObject.
    :raise Error: When an unexpected error occurs.
    '''

    if not isinstance(obj, c4d.PolygonObject):
      raise TypeError("<obj> must be a PolygonObject", type(obj))

    result = c4d.utils.SendModelingCommand(c4d.MCOMMAND_TRIANGULATE, [obj])
    if not result:
      raise Error("Triangulate failed")

  @staticmethod
  def untriangulate(obj, angle_rad=None):
    '''
    Untriangulates the PolygonObject *obj* in place.

    :param obj: The :class:`c4d.PolygonObject` to untriangulate.
    :param angle_rad: The untriangulate angle radius. Defaults to 0.1°.
    :raise TypeError: If *obj* is not a PolygonObject.
    :raise Error: When an unexpected error occurs.
    '''

    if not isinstance(obj, c4d.PolygonObject):
      raise TypeError("<obj> must be a PolygonObject", type(obj))

    if angle_rad is None:
      angle_rad = c4d.utils.Rad(0.1)

    bc = c4d.BaseContainer()
    bc.SetFloat(c4d.MDATA_UNTRIANGULATE_ANGLE_RAD, angle_rad)
    result = c4d.utils.SendModelingCommand(
      c4d.MCOMMAND_UNTRIANGULATE, [obj], doc=None, bc=bc)

    if not result:
      raise Error("Untriangulate failed")

  @staticmethod
  def optimize(obj, tolerance=0.01, points=True, polygons=True,
      unused_points=True):
    '''
    Optimizes the PolygonObject *obj* using the Cinema 4D
    "Optimize" command. The parameters to this method reflect
    the parameters of the Cinema 4D command.

    :raise TypeError: If *obj* is not a PolygonObject.
    :raise Error: When an unexpected error occurs.
    '''

    if not isinstance(obj, c4d.PolygonObject):
      raise TypeError("<obj> must be a PolygonObject", type(obj))

    bc = c4d.BaseContainer()
    bc.SetFloat(c4d.MDATA_OPTIMIZE_TOLERANCE, tolerance)
    bc.SetBool(c4d.MDATA_OPTIMIZE_POINTS, points)
    bc.SetBool(c4d.MDATA_OPTIMIZE_POLYGONS, polygons)
    bc.SetBool(c4d.MDATA_OPTIMIZE_UNUSEDPOINTS, unused_points)
    result = c4d.utils.SendModelingCommand(
      c4d.MCOMMAND_OPTIMIZE, [obj], doc=None, bc=bc)

    if not result:
      raise Error("Optimize failed")

  def _assert_doc(self, method):
    '''
    Private. Raises a :class:`RuntimeError` if the *Kernel* was
    not initialized with a Cinema 4D document. '''

    if self._doc is None:
      raise RuntimeError(
        "Kernel method '{0}' requires a Cinema 4D document but "
        "the Kernel was initialized with None".format(method))
    assert isinstance(self._doc, c4d.documents.BaseDocument)

  def current_state_to_object(self, obj):
    '''
    Executes the Cinema 4D "Current State to Object" on *obj* and
    returns the resulting object. The object will be temporarily
    moved into the document the *Kernel* was initialized with. If
    you want to keep links (eg. texture tag material links), the
    *Kernel* should have been initialized with the objects document.

    .. note:: All parent objects of *obj* will be moved with it as
      it may have influence on the outcome (eg. deformers applied
      on a hierarchy in a Null-Object).

    :requires:
      - The *Kernel* must be initialized with a document.
    :raise RuntimeError: If the *Kernel* was not initialized
      with a document.
    :raise TypeError: If *obj* is not a BaseObject.
    :raise Error: When an unexpected error occurs.
    '''

    self._assert_doc('current_state_to_object')
    if not isinstance(obj, c4d.BaseObject):
      raise TypeError("<obj> must be a BaseObject", type(obj))

    doc = self._doc
    root = find_root(obj)

    with UndoHandler() as undo:
      undo.location(root)
      root.Remove()
      doc.InsertObject(root)
      result = c4d.utils.SendModelingCommand(
        c4d.MCOMMAND_CURRENTSTATETOOBJECT, [obj], doc=doc)

    if not result:
      raise Error("Current State to Object failed")
    return result[0]

  def connect_objects(self, objects):
    '''
    Joins all PolygonObjects and SplineObjects the list *objects*
    into a single object using the Cinema 4D "Connect Objects"
    command.

    This method will move *all* objects to the internal document
    temporarily before joining them into one object.

    :param objects: A list of :class:`c4d.BaseObject`.
    :return: The new connected object.
    :requires:
      - The *Kernel* must be initialized with a document.
    :raise RuntimeError: If the *Kernel* was not initialized
      with a document.
    :raise TypeError:
        - If *objects* is not iterable
        - If an element of *objects* is not a BaseObject
    :raise Error: When an unexpected error occurs.


    .. important:: The returned object axis is located at the world
      center. If you want to mimic the real "Connect Objects" command
      in that it positions the axis at the location of the first
      object in the list, use the :func:`nr.c4d.utils.move_axis`
      function.
    '''

    self._assert_doc('connect_objects')
    if not isinstance(objects, collections.Iterable):
      raise TypeError("<objects> must be iterable", type(objects))

    doc = self._doc
    root = c4d.BaseObject(c4d.Onull)

    with UndoHandler() as undo:
      undo.location(root)
      doc.InsertObject(root)

      # Move all objects under the new root object temporarily.
      for obj in objects:
        if not isinstance(obj, c4d.BaseObject):
          message = "element of <objects> must be BaseObject"
          raise TypeError(message, type(obj))

        undo.location(obj)
        undo.matrix(obj)

        mg = obj.GetMg()
        obj.Remove()
        obj.InsertUnder(root)
        obj.SetMl(mg)

      result = c4d.utils.SendModelingCommand(
        c4d.MCOMMAND_JOIN, root.GetChildren(), doc=doc)

    if not result:
      raise Error("Connect Objects failed")

    result[0].SetMl(c4d.Matrix())
    return result[0]

  def polygon_reduction(self, obj, strength, meshfactor=1000,
      coplanar=True, boundary=True, quality=False):
    '''
    Uses the Cinema 4D "Polygon Reduction" deformer to create a
    copy of *obj* with reduced polygon count. The parameters to
    this function reflect the parameters in the "Polygon Reduction"
    deformer. :meth:`current_state_to_object` is used to obtain
    the deformed state of *obj*.

    :requires:
      - The *Kernel* must be initialized with a document.
    :raise RuntimeError: If the *Kernel* was not initialized with a document.
    :raise TypeError: If *obj* is not a BaseObject.
    :raise Error: When an unexpected error occurs.

    .. important:: In rare cases, the returned object can be a null
      object even though the input object was a polygon object. In that
      case, the null object contains the reduced polygon object as a
      child.
    '''

    self._assert_doc('polygon_reduction')
    if not isinstance(obj, c4d.BaseObject):
      raise TypeError("<obj> must be BaseObject", type(obj))

    root = c4d.BaseObject(c4d.Onull)
    deformer = c4d.BaseObject(c4d.Opolyreduction)
    deformer.InsertUnder(root)
    deformer[c4d.POLYREDUCTIONOBJECT_STRENGTH] = strength
    deformer[c4d.POLYREDUCTIONOBJECT_MESHFACTOR] = meshfactor
    deformer[c4d.POLYREDUCTIONOBJECT_COPLANAR] = coplanar
    deformer[c4d.POLYREDUCTIONOBJECT_BOUNDARY] = boundary
    deformer[c4d.POLYREDUCTIONOBJECT_QUALITY] = quality

    doc = self._doc
    with UndoHandler() as undo:
      undo.location(root)
      undo.location(obj)
      undo.matrix(obj)
      doc.InsertObject(root)
      obj.Remove()
      obj.InsertAfter(deformer)
      root = self.current_state_to_object(root)

    # Root will definetely be a Null-Object, so we need to go
    # down one object at least.
    result = root.GetDown()
    if not result:
      raise Error("Polygon Reduction failed")

    result.Remove()
    return result

  def boole(self, obja, objb, boole_type, high_quality=True,
      single_object=False, hide_new_edges=False, break_cut_edges=False,
      sel_cut_edges=False, optimize_level=0.01):
    '''
    Uses the Cinema 4D "Boole Object" to perform a boolean
    volumetric operation on *obja* and *objb* and returns the
    resulting object hierarchy. The method parameters reflect
    the "Boole Object" parameters.

    :param obja: The first object for the boole operation.
    :param objb: The second object for the boole operation.
    :param boole_type: One of the boole modes:

      - :data:`c4d.BOOLEOBJECT_TYPE_UNION`
      - :data:`c4d.BOOLEOBJECT_TYPE_SUBTRACT`
      - :data:`c4d.BOOLEOBJECT_TYPE_INTERSECT`
      - :data:`c4d.BOOLEOBJECT_TYPE_WITHOUT`
    :param high_quality: See Boole Object documentation.
    :param single_object: See Boole Object documentation.
    :param hide_new_edges: See Boole Object documentation.
    :param break_cut_edges: See Boole Object documentation.
    :param sel_cut_edges: See Boole Object documentation.
    :param optimize_level: See Boole Object documentation.
    :return: The result of the Boole operation converted using
      :meth:`current_state_to_object`.
    :requires:
      - The *Kernel* must be initialized with a document.
    :raise RuntimeError: If the *Kernel* was not initialized
      with a document.
    :raise TypeError: If *obja* or *objb* is not a BaseObject.
    :raise ValueError: If *boole_type* is invalid.
    :raise Error: When an unexpected error occurs.
    '''

    self._assert_doc('boole')

    choices = (
      c4d.BOOLEOBJECT_TYPE_UNION, c4d.BOOLEOBJECT_TYPE_SUBTRACT,
      c4d.BOOLEOBJECT_TYPE_INTERSECT, c4d.BOOLEOBJECT_TYPE_WITHOUT)
    if boole_type not in choices:
      raise ValueError("unexpected value for <boole_type>", boole_type)
    if not isinstance(obja, c4d.BaseObject):
      raise TypeError("<obja> must be BaseObject", type(obja))
    if not isinstance(obja, c4d.BaseObject):
      raise TypeError("<objb> must be BaseObject", type(objb))

    boole = c4d.BaseObject(c4d.Oboole)
    boole[c4d.BOOLEOBJECT_TYPE] = boole_type
    boole[c4d.BOOLEOBJECT_HIGHQUALITY] = high_quality
    boole[c4d.BOOLEOBJECT_SINGLE_OBJECT] = single_object
    boole[c4d.BOOLEOBJECT_HIDE_NEW_EDGES] = hide_new_edges
    boole[c4d.BOOLEOBJECT_BREAK_CUT_EDGES] = break_cut_edges
    boole[c4d.BOOLEOBJECT_SEL_CUT_EDGES] = sel_cut_edges
    boole[c4d.BOOLEOBJECT_OPTIMIZE_LEVEL] = optimize_level

    with UndoHandler() as undo:
      undo.location(boole)
      undo.location(obja)
      undo.location(objb)
      undo.matrix(obja)
      undo.matrix(objb)

      mga, mgb = obja.GetMg(), objb.GetMg()
      obja.Remove(), objb.Remove()
      obja.InsertUnder(boole), objb.InsertUnderLast(boole)
      obja.SetMg(mga), objb.SetMg(mgb)
      self._doc.InsertObject(boole)
      return self.current_state_to_object(boole)
