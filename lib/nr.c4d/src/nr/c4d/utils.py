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
''' Common utility functions related to the Cinema 4D API. '''

import c4d
import warnings

try:
  from nr.types.map import HashDict as _HashDict, OrderedDict
except ImportError as exc:
  class _HashDict:
    exc = exc
    def __init__(self):
      raise self.exc
  class OrderedDict:
    exc = exc
    def __init__(self):
      raise self.exc


def serial_info():
  '''
  Retrieve the serial information for the current instance of
  Cinema 4D.

  return (tuple of (dict, bool)):
    The serial info dictionary and a boolean that indicates if this is a
    multi license.
  '''

  is_multi = True
  sinfo = c4d.GeGetSerialInfo(c4d.SERIALINFO_MULTILICENSE)
  if not sinfo['nr']:
    is_multi = False
    sinfo = c4d.GeGetSerialInfo(c4d.SERIALINFO_CINEMA4D)
  return sinfo, is_multi


def flush_console():
  ''' Flush the Cinema 4D scripting console. '''

  c4d.CallCommand(13957)


def update_viewport():
  '''
  Shortcut for using #c4d.DrawViews() to update the Cinema 4D viewport. Check
  the source code for the flags that are passed to the function.
  '''

  return c4d.DrawViews(
    c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW | c4d.DRAWFLAGS_NO_THREAD |
    c4d.DRAWFLAGS_NO_REDUCTION | c4d.DRAWFLAGS_STATICBREAK)


def walk_hierarchy(node, yield_depth=False, _depth=0):
  '''
  Iterator for walking over the hierarchy of a :class:`c4d.BaseList2D`
  node. *node* can also be a list, in which case all items of the list are
  walked. If *yield_depth* is True, a tuple with the second item being
  the index of the depth is yielded instead of only the nodes.

  ```python
  for obj in walk_hierarchy(doc.GetObjects()):
    print(obj.GetName())
  ```

  node (c4d.BaseList2D, list of c4d.BaseList2D):
  yield_depth (bool):
    #True if you want the generator to yield `(node, depth)` tuples,
    otherwise it will just yield the `node`.
  return (generator):
    A generator yielding the nodes of the hierarchy, or tuples of such.
  '''

  if isinstance(node, c4d.C4DAtom):
    if yield_depth:
      yield node, _depth
    else:
      yield node
    for child in node.GetChildren():
      for __ in walk(child, yield_depth, _depth + 1):
        yield __
  else:
    for node in node:
      for __ in walk(node, yield_depth, _depth + 1):
        yield __


def walk_timeline(doc, start, end, update=True):
  '''
  Iterate over each frame in the document from *start* to *end* and yield the
  current frame number while redrawing the viewport if *update* is True. The
  document time will be reset to the original time at the end of the iteration.

  ```python
  for frame in iter_timeline(doc, 0, 100):
    pass  # process current frame here
  ```

  doc (c4d.BaseDocument):
  start (c4d.BaseTime, int): The start time, either as time or frame number.
  end (c4d.BaseTime, int): The end time, either as time or frame number.
  update (bool):
    If #True, the viewport is updated with #update_viewport() and
    #c4d.GeSyncMessage before the current frame number is passed to the
    caller. This is usually desired.
  '''

  fps = doc.GetFps()
  time = doc.GetTime()

  if isinstance(start, c4d.BaseTime):
    start = start.GetFrame(fps)
  if isinstance(end, c4d.BaseTime):
    end = end.GetFrame(fps)

  for frame in xrange(start, end + 1):
    doc.SetTime(c4d.BaseTime(frame, fps))
    if update:
      update_viewport()
      c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)
    yield frame

  doc.SetTime(time)
  if update:
    update_viewport()
    c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)


def walk_container(bc):
  '''
  Walk over all entries in the #c4d.BaseContainer. Usually, you would do this
  with #c4d.BaseContainer.__iter__(), but it poses two issues:

  1. If a subcontainer is yielded, it is actually a copy of that container
  2. If a datatype in the container can not be represented in Python, it
     will raise an :class:`AttributeError`

  This function uses #c4d.BaseContainer.GetIndexId() to iterate over all
  entries and #c4d.BaseContainer.GetIndexData() to read the value.

  Requires R16+
  '''


  index = 0
  ident = bc.GetIndexId(index)
  while ident != c4d.NOTOK:
    try:
      yield ident, bc.GetIndexData(index)
    except AttributeError:
      pass
    index += 1
    ident = bc.GetIndexId(index)


def walk_shaders(node):
  '''
  Walk over the shader-list of a #c4d.BaseList2D node. It is safe to remove
  shaders during iteration.
  '''

  shader = node.GetFirstShader()
  while shader:
    next_ = shader.GetNext()
    yield shader
    shader = next_


def remove_document(doc, new_active_doc=None):
  '''
  The Cinema 4D API only provides a #c4d.documents.KillDocument() function
  that not only removes the specified #c4d.BaseDocument from the document
  list, but really *kills* it, ie. it can not be used anymore aftert the
  function is called.

  This function *only* removes the document from the Cinema 4D document list
  so that it is still valid and can be accessed from Python.

  doc (c4d.BaseDocument): The document to remove.
  new_active_doc (c4d.BaseDocument):
    If specified, this will become the new active Cinema 4D document.
    Otherwise, the next document of *doc* will be used (C4D default behaviour)
    or a new empty document is created if none exists.
  '''

  if type(doc) is not c4d.documents.BaseDocument:
    raise TypeError("doc must be a BaseDocument object")
  if new_active_doc is not None and \
      type(new_active_doc) is not c4d.documents.BaseDocument:
    raise TypeError("new_active_doc must be a BaseDocument object")

  successor = new_active_doc or doc.GetPred() or doc.GetNext()
  doc.Remove()

  # Note: The document will be removed before eventually inserting
  # a new document because if *doc* is the active document and is
  # empty, InsertBaseDocument will actually kill it before inserting
  # the new document.

  if not successor:
    successor = c4d.documents.BaseDocument()
    c4d.documents.InsertBaseDocument(successor)

  c4d.documents.SetActiveDocument(successor)


class TemporaryDocument(object):
  '''
  The #TemporaryDocument class provides, as the name implies, a temporary
  #c4d.documents.BaseDocument that can be used to perform operations in an
  isolated environment such as calling modeling commands or #c4d.CallCommand().

  When the TemporaryDocument is created, it is not immediately activated. To
  do so, one must call the #attach() method or use it as a context-manager.
  When the document is no longer needed, the context-manager will close the
  document and remove it from the Cinema 4D document list or #detach() must be
  called manually. The *TemporaryDocument* can be re-used after it has been
  closed.

  Use the #get() method to obtain the wrapped *BaseDocument* or catch the
  return value of the context-manager.

  > **Note**: If #detach() was not called after #attach() and the
  > #TemporaryDocument object is being deleted via the garbage collector, a
  > #RuntimeWarning will be issued but the document will not be detached.

  **Important**: You must not remove the internal document through any means
  but the #detach() method.
  '''

  __slots__ = ('_bdoc', '_odoc')

  def __init__(self):
    super(TemporaryDocument, self).__init__()
    self._bdoc = c4d.documents.BaseDocument()
    self._odoc = None

  def __del__(self):
    if self._odoc is not None:
      warnings.warn(
        "TemporaryDocument not detached before being "
        "garbage collected", RuntimeWarning)

  def __enter__(self):
    ''' Attaches the real temporary document and returns it. '''

    self.attach()
    return self.get()

  def __exit__(self, *args):
    self.detach()

  def attach(self):
    '''
    Attaches the temporary document to the Cinema 4D document list. It will
    also be promoted to be the active document. A call to #detach() must be
    paired with #attach().

    The document that is active before this method is called will
    be saved and promoted back to being the active document with
    calling #detach().

    Returns *self* for method-chaining.
    '''

    if self._odoc is not None:
      raise RuntimeErrorn("attach() has already been called")

    self._odoc = c4d.documents.GetActiveDocument()
    c4d.documents.InsertBaseDocument(self._bdoc)
    c4d.documents.SetActiveDocument(self._bdoc)
    return self

  def detach(self, do_recall=True):
    '''
    Detaches the temporary document from the Cinema 4D document list and
    promotes the previous active document back to its original status unless
    *do_recall* is False.

    Returns *self* for method-chaining.
    '''

    if self._odoc is None:
      raise RuntimeError("attach() has not been called before")

    remove_document(self._bdoc, self._odoc() if do_recall else None)
    self._odoc = None
    return self

  def get(self):
    ''' Returns the internal #c4d.BaseDocument object. '''

    return self._bdoc

  def is_attached(self):
    '''
    Returns #True if this #TemporaryDocument is attached, i.e. it is inside
    the Cinema 4D document list, #False if it's not.
    '''

    attached = self._odoc is not None
    return attached


class UndoHandler(object):
  '''
  The #UndoHandler is a useful class to temporarily apply changes to
  components of Cinema 4D objects, tags, materials, nodes, documents etc. and
  revert them at a specific point.

  Internally, the #UndoHandler* simply stores a list of callables that are
  called upon #revert(). All methods that store the original state of a node
  simply append a callable to it. Custom callables can be added with
  #custom().
  '''

  __slots__ = ('_flist',)

  def __init__(self):
    super(UndoHandler, self).__init__()
    self._flist = []

  def __enter__(self):
    return self

  def __exit__(self, *args):
    self.revert()

  def revert(self):
    '''
    Reverts back to the original states that have been kept track
    of with this #UndoHandler and flushes these states.
    '''

    flist, self._flist = self._flist, []
    [f() for f in reversed(flist)]

  def custom(self, target):
    '''
    Adds a custom callable object that is invoked when :meth:`revert`
    is called. It must accept no arguments.
    '''

    if not callable(target):
      raise TypeError("<target> must be callable", type(target))
    self._flist.append(target)

  def matrix(self, op):
    ''' Restores ops current matrix upon #revert(). '''

    ml = op.GetMl()
    def revert_matrix():
      op.SetMl(ml)
    self._flist.append(revert_matrix)

  def location(self, node):
    '''
    Tracks the hierarchical location of *node* and restores it upon #revert().
    This method only supports materials, tags and objects. This will also
    remove nodes that were not inserted any where before.
    '''

    pred_node = node.GetPred()
    next_node = node.GetNext()
    parent = node.GetUp()
    tag_host = node.GetObject() if isinstance(node, c4d.BaseTag) else None
    doc = node.GetDocument()

    if not any([pred_node, next_node, parent, tag_host]) and doc:
      supported_classes = (c4d.BaseMaterial, c4d.BaseObject)
      if not isinstance(node, supported_classes):
        raise TypeError(
          "only materials and objects are supported when "
          "located at their root", type(node))

    def revert_hierarchy():
      node.Remove()
      if pred_node and pred_node.GetUp() == parent:
        node.InsertAfter(pred_node)
      elif next_node and next_node.GetUp() == parent:
        node.InsertBefore(next_node)
      elif parent:
        node.InsertUnder(parent)
      elif tag_host:
        tag_host.InsertTag(node)
      elif doc:
        if isinstance(node, c4d.BaseMaterial):
          doc.InsertMaterial(node)
        elif isinstance(node, c4d.BaseObject):
          doc.InsertObject(node)
        else:
          raise RuntimeError("unexpected type of <node>", type(node))

    self._flist.append(revert_hierarchy)

  def container(self, node):
    '''
    Grabs a copy of the nodes #c4d.BaseContainer and restores it upon
    #revert().
    '''

    data = node.GetData()
    def revert_container():
      node.SetData(data)
    self._flist.append(revert_container)

  def whole_node(self, node):
    '''
    Gets a complete copy of *node* and restores its complete state upon
    #revert(). This is like using #c4d.UNDOTYPE_CHANGE with
    #c4d.BaseDocument.AddUndo() except that it does not include the
    hierarchical location. For that, you can use the #location().
    '''

    flags = c4d.COPYFLAGS_NO_HIERARCHY | c4d.COPYFLAGS_NO_BRANCHES
    clone = node.GetClone(flags)
    def revert_node():
      clone.CopyTo(node, c4d.COPYFLAGS_0)
    self._flist.append(revert_node)


def duplicate_object(obj, n=None):
  '''
  Duplicate *obj* and return it. If *n* is not None, it must be a number. If a
  number is specified, this function creates *n* duplicates instead and
  returns a list of the duplicates.

  This function uses the Cinema 4D "Duplicate" tool to create the copies of
  *obj*. In many cases, this is more desirable than using #c4d.C4DAtom.GetClone()
  since the #c4d.AliasTrans class is only available since R17.

  obj (c4d.BaseObject): The object to clone.
  n (None, int): The number of clones.
  return (c4d.BaseObject, list of c4d.BaseObject):
    A list of the cloned objects or a single object if *n* was None.
  raise RuntimeError:
    If *obj* is not inserted in a #c4d.BaseDocument or if the objects could
    not be cloned.
  '''

  doc = obj.GetDocument()
  if not doc:
    raise RuntimeError("obj must be in a c4d.BaseDocument")

  bc = c4d.BaseContainer()
  bc[c4d.MDATA_DUPLICATE_COPIES] = 1 if n is None else n
  bc[c4d.MDATA_DUPLICATE_INSTANCES] = c4d.MDATA_DUPLICATE_INSTANCES_OFF
  bc[c4d.MDATA_ARRANGE_MODE] = c4d.MDATA_ARRANGE_MODE_SELECTMODE
  result = c4d.utils.SendModelingCommand(
    c4d.ID_MODELING_DUPLICATE_TOOL, [obj], bc=bc, doc=doc)
  if not result:
    raise RuntimeError("could not duplicate object")

  name = obj.GetName()
  root = obj.GetNext()
  assert root.CheckType(c4d.Onull)

  clones = []
  for child in root.GetChildren():
    child.SetName(name)
    child.Remove()
    clones.append(child)
  root.Remove()
  return clones


def move_axis(obj, new_axis):
  '''
  Simulate the "Axis Move" mode in Cinema 4D. This function moves the axis of
  a #c4d.BaseObject to the specified *new_axis* in *local space*. Child objects
  will remain at their original position relative to *global space*. If *obj*
  is a #c4d.PointObject, same applies for the object's points.

  ```python
  import c4d
  from nr.c4d.utils import move_axis

  # Rotate the axis of an object by 45 Degrees around the X axis.
  doc.AddUndo(c4d.UNDOTYPE_HIERARCHY_PSR, op)
  mat = op.GetMl() * c4d.utils.MatrixRotX(c4d.utils.Rad(45))
  move_axis(op, mat)
  ```

  obj (c4d.BaseObject):
  new_axis (c4d.Matrix):
  '''

  mat = ~new_axis * obj.GetMl()
  if obj.CheckType(c4d.Opoint):
    points = [p * mat for p in obj.GetAllPoints()]
    obj.SetAllPoints(points)
    obj.Message(c4d.MSG_UPDATE)

  for child in obj.GetChildren():
    child.SetMl(mat * child.GetMl())
  obj.SetMl(new_axis)


class PolygonObjectInfo(object):
  '''
  This class stores the points and polygons of a #c4d.PolygonObject and
  computes the normals and polygon middle points.

  op: The #c4d.PolygonObject to initialize the object for.
  points: True if the object points should be stored.
  polygons: True if the object polygons should be stored.
  normals: True if the object normals should be computed.
  midpoints: True if the polygon midpoints should be computed.
  vertex_normals: True if the vertex normals should be computed
    (implies the *normals* parameter).

  # Members
  points:
  polygons:
  normals:
  vertex_normals:
  midpoints:
  pointcount:
  polycount:
  '''

  def __init__(self, op, points=False, polygons=False, normals=False,
      midpoints=False, vertex_normals=False):
    super(PolygonObjectInfo, self).__init__()

    self.points = None
    self.polygons = None
    self.normals = None
    self.vertex_normals = None
    self.midpoints = None

    self.pointcount = op.GetPointCount()
    self.polycount = op.GetPolygonCount()


    if points or normals or vertex_normals or midpoints:
      self.points = op.GetAllPoints()

    if polygons or normals or vertex_normals or midpoints:
      self.polygons = op.GetAllPolygons()

    if normals or vertex_normals:
      self.normals = [None] * self.polycount
    if vertex_normals:
      self.vertex_normals = [
        [c4d.Vector(), 0] for __ in xrange(self.pointcount)]

    if midpoints:
      self.midpoints = [None] * self.polycount

    if normals or vertex_normals or midpoints:
      m3 = 1.0 / 3.0
      m4 = 1.0 / 4.0
      for i, p in enumerate(self.polygons):
        a, b, c, d = self.points[p.a], self.points[p.b], self.points[p.c], self.points[p.d]

        if normals or vertex_normals:
          n = (a - b).Cross(a - d)
          n.Normalize()
          self.normals[i] = n

        if midpoints:
          m = a + b + c
          if p.c == p.d:
            m *= m3
          else:
            m += d
            m *= m4
          self.midpoints[i] = m

    if vertex_normals:
      def _add(index, n):
        data = self.vertex_normals[index]
        data[0] += n
        data[1] += index
      for n, p in itertools.izip(self.normals, self.polygons):
        _add(p.a, n)
        _add(p.b, n)
        _add(p.c, n)
        if p.c != p.d:
          _add(p.d, n)
      self.vertex_normals[:] = (x.GetNormalized() for x in self.vertex_normals)

    if not points:
      self.points = None
    if not polygons:
      self.polygons = None


def assoc_mats_with_objects(doc):
  '''
  This function goes through the complete object hierarchy of the passed
  #c4d.BaseDocument and all materials with the objects that carry a texture-tag
  with that material. The returnvalue is an #OrderedDict instance. The keys of
  the dictionary-like object are the materials in the document, their
  associated values are lists of #c4d.BaseObject. Note that an object *can*
  occure twice in the same list when the object has two tags with the same
  material on it.

  doc (c4d.BaseDocument):
  return (OrderedDict):
  '''

  data = OrderedDict()

  def callback(op):
    for tag in op.GetTags():
      if tag.CheckType(c4d.Ttexture):
        mat = tag[c4d.TEXTURETAG_MATERIAL]
        if not mat: continue
        data.setdefault(mat, []).append(op)

    for child in op.GetChildren():
      callback(child)

  for obj in doc.GetObjects():
    callback(obj)

  return data


def load_bitmap(filename):
  '''
  Loads a #c4d.bitmaps.BaseBitmap from the specified *filename* and returns it
  or None if the file could not be loaded.

  filename (str): The file to load the image from.
  return (c4d.BaseBitmap, None):
  '''

  bmp = c4d.bitmaps.BaseBitmap()
  if bmp.InitWith(filename)[0] != c4d.IMAGERESULT_OK:
    return None
  return bmp


def find_root(node):
  '''
  Finds the top-most object of the hierarchy of *node* and returns it. Note
  that this could very well be the *node* passed to this function.

  node (c4d.BaseList2D):
  return (c4d.BaseList2D):
  '''

  parent = node.GetUp()
  while parent:
    node = parent
    parent = node.GetUp()
  return node


def candidates(value, obj, callback=lambda vref, vcmp, kcmp: vref == vcmp):
  '''
  Searches for *value* in *obj* and returns a list of all keys where the
  callback returns True, being passed *value* as first argument, the value to
  compare it with as the second argument and the name of the attribute as the third.

  return (list of str):
  '''

  results = []
  for k, v in vars(obj).iteritems():
    if callback(value, v, k):
      results.append(k)

  return results


def find_menu_resource(*path):
  bc = c4d.gui.GetMenuResource(path[0])
  for menu in path[1:]:
    found = False
    index = 0
    while True:
      key = bc.GetIndexId(index)
      if key == c4d.NOTOK: break
      if key == c4d.MENURESOURCE_SUBMENU:
        subbc = bc.GetIndexData(index)
        if subbc[c4d.MENURESOURCE_SUBTITLE] == menu:
          found = True
          bc = subbc
          break
      index += 1
    if not found:
      return None
  return bc


def bc_insert(bc, id, data, index):
  newbc = c4d.BaseContainer()
  for i, (k, v) in enumerate(bc):
    if i == index:
      newbc.InsData(id, data)
    newbc.InsData(k, v)
  newbc.CopyTo(bc, 0)
  return bc

# A dictionary with support for some normally unhashable C4D types.
class HashDict(_HashDict):
  SPECIALIZATIONS = {}
  @classmethod
  def specialize(cls, type):
    def decorator(func):
      cls.SPECIALIZATIONS[type] = func
      return func
    return decorator
  def key_hash(self, key):
    return self.SPECIALIZATIONS.get(type(key), hash)(key)

@HashDict.specialize(c4d.DescID)
def hash_descid(x):
  levels = (x[i] for i in xrange(x.GetDepth()))
  return hash(tuple(l.id for l in levels))
