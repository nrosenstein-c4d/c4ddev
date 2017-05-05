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
''' This module provides the `TreeNode` class which can be used to
build custom hierarchical datastructures. '''


class TreeNode(object):
  ''' This class implements a tree datastructure very similar to
  the :class:`c4d.BaseList2D` class. It is most commonly used to
  represent a tree in a :class:`c4d.gui.TreeViewGui`. '''

  def __init__(self):
    super(TreeNode, self).__init__()
    self.__parent = None
    self.__next = None
    self.__pred = None
    self.__down = None
    self.__down_last = None

  def __assert_dangling(self, param):
    if not self.is_dangling():
      message = '<{0}> is already in a hierarchy'.format(param)
      raise RuntimeError(message, self)

  def is_dangling(self):
    ''' Returns True if the node is a dangling node, meaning it
    is not inserted in a hierarchy. A dangling node has no parent
    or neighbouring nodes. '''

    return not (self.__parent or self.__next or self.__pred)

  def get_root(self):
    root = self
    while root.__parent:
      root = root.__parent
    return root

  def get_parent(self):
    return self.__parent

  def get_next(self):
    return self.__next

  def get_pred(self):
    return self.__pred

  def get_down(self):
    return self.__down

  def get_down_last(self):
    return self.__down_last

  def get_children(self):
    children = []
    child = self.__down
    while child:
      children.append(child)
      child = child.__next
    return children

  def remove(self):
    ''' Removes the node from the parent and neighbouring nodes.
    Does not detach child nodes. '''

    if self.__parent:
      if self is self.__parent.__down:
        self.__parent.__down = self.__next
      if self is self.__parent.__down_last:
        self.__parent.__down_last = self.__pred
    if self.__next:
      self.__next.__pred = self.__pred
    if self.__pred:
      self.__pred.__next = self.__next
    self.__parent = None
    self.__next = None
    self.__pred = None

  def insert_after(self, node):
    ''' Inserts *self* after *node*. *self* must be free (not in a
    hierarchy) and *node* must have a parent node, otherwise a
    `RuntimeError` is raised. '''

    if not isinstance(node, TreeNode):
      raise TypeError('<node> must be TreeNode instance', type(node))
    self.__assert_dangling('self')
    if not node.__parent:
      raise RuntimeError('<node> must have a parent node', node)

    self.__parent = node.__parent
    if node.__next:
      node.__next.__pred = self
    else:
      assert self.__parent.__down_last is node
      self.__parent.__down_last = self
    node.__next = self
    self.__pred = node

  def insert_before(self, node):
    ''' Inserts *self* before *node*. *self* must be free (not in a
    hierarchy) and *node* must have a parent node, otherwise a
    `RuntimeError` is raised. '''

    if not isinstance(node, TreeNode):
      raise TypeError('<node> must be TreeNode instance', type(node))
    self.__assert_dangling('self')
    if not node.__parent:
      raise RuntimeError('<node> must have a parent node', node)

    self.__parent = node.__parent
    if node.__pred:
      node.__pred.__next = self
    else:
      assert node is self.__parent.__down
      self.__parent.__down = self
    node.__pred = self
    self.__next = node

  def append(self, node, index=None):
    ''' Appends *node* at the specified *index*. If *index* is None,
    *node* will be inserted at the end of the children list. The
    *index* can not be a negative value as it would need to count
    the number of childrens first. '''

    if not isinstance(node, TreeNode):
      raise TypeError('<node> must be TreeNode instance', type(node))
    if index is not None and not isinstance(index, int):
      raise TypeError('<index> must be None or int', type(index))
    if index is not None and index < 0:
      raise ValueError('<index> must be None or positive int', index)

    # Make sure the node is not already in a hierarchy.
    node.__assert_dangling('node')

    # Even if the node that is to be inserted is free, it could
    # still be the root of the hierarchy which would be free.
    if node is self.root:
      raise RuntimeError('can not insert <root> node into its hierarchy', node)

    assert bool(self.__down) == bool(self.__down_last), \
      "TreeNode.down and TreeNode.down_last out of balance (" + self.name + ")"

    if not self.__down:
      self.__down = node
      self.__down_last = node
      node.__parent = self
    else:
      if index is not None:
        dest = self.__down
        child_index = 0
        while dest and child_index < index:
          dest = dest.__next
          child_index += 1
      else:
        dest = None

      if dest:
        node.insert_before(dest)
      else:
        node.insert_after(self.__down_last)

  def iter_children(self, filter_func=None, recursive=False):
    ''' Iterator for the children of this node. It is safe to call
    :meth:`remove` on yielded nodes. Optionally, the children can
    be filtered with the specified *filter_func*. '''

    if filter_func and not callable(filter_func):
      raise TypeError('filter_func must be callable')

    child = self.down
    while child:
      next = child.next
      if not filter_func or filter_func(child):
        yield child
      if recursive:
        for sub in child.iter_children(filter_func, recursive):
          yield sub
      child = next

  root = property(get_root)
  parent = property(get_parent)
  next = property(get_next)
  pred = property(get_pred)
  down = property(get_down)
  down_last = property(get_down_last)
  children = property(get_children)


exports = TreeNode
