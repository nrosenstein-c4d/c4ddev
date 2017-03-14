# Copyright (c) 2014  Niklas Rosenstein
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

class UndoTree(object):
    r""" This class implements a branched undo-system. """

    def __init__(self, init_data, max_steps, branched=True):
        super(UndoTree, self).__init__()
        self.__age = 0
        self.__root = Root()
        self.__focus = self.__root
        self.__max_steps = max_steps
        self.__branched = branched
        self.__reverted_nodes = []
        self.new(init_data)

    def new(self, data):
        r""" Creates a new undo-step with the specified *data* if
        it doesn't equal the data of the focused undo-step. Cuts
        the number of undo-step by :attr:`max_steps` afterwards.

        The created undo-step owns the new focus. """

        if data != self.__focus.data:
            self.__age += 1
            self.__focus = self.__focus.split(self.__age, data, self.__branched)
            self.__clean()
            self.break_forward()

    def revert(self):
        r""" Reverts to the previous step, returns True if
        successful, False if not. """

        if self.__focus.parent:
            self.__reverted_nodes.append(self.__focus)
            self.focus = self.__focus.parent
            return True
        return False

    def forward(self):
        r""" Forwards to the next undo-step. Returns True on success,
        False if the focus node is the current one. The UndoTree keeps
        a list of previously revertedundos to continue on the branch
        as before. """

        if self.__reverted_nodes:
            self.__focus = self.__reverted_nodes.pop()
            return True
        return False

    def can_revert(self):
        return bool(self.__focus.parent)

    def can_forward(self):
        return bool(self.__reverted_nodes)

    def break_forward(self):
        r""" Call this method when data is being changed but no
        undo step has yet been added. This will break the forward
        capability. """

        self.__reverted_nodes = []

    def __clean(self):
        min_index = self.__age - self.__max_steps
        self.__root.clean(min_index)

    @property
    def max_steps(self):
        r""" The maximum number of allowed undo steps. Every time a new
        undo is added to the tree, the number of nodes will be cut
        to not exceed this number. """

        return self.__max_steps

    @max_steps.setter
    def max_steps(self, value):
        self.__max_steps = int(value)
        self.__root.clean(self.__age - self.__max_steps)

    @property
    def focus(self):
        r""" Returns the the focused undo-step :class:`Node`. """

        return self.__focus

    @focus.setter
    def focus(self, node):
        r""" Sets the focus on the supplied :class:`Node`. """

        if type(node) != Node:
            name = node.__class__.__name__
            raise TypeError('expected Node object, got %s' % name)
        self.__focus = node

    @property
    def root(self):
        r""" Returns the root node. """

        return self.__root

    @property
    def data(self):
        r""" Returns the data of the current undo-step. """

        return self.__focus.data

class Node(object):
    r""" An undo-step node. Each node has a number assigned, which
    represents the index of the undo-step, and the actual data which
    is associated to the step. """

    def __init__(self, index, data, parent=None):
        super(Node, self).__init__()
        self.index = index
        self.data = data
        self.parent = parent
        self.children = []

    def __repr__(self):
        return '<Node:%d with %r>' % (self.index, self.data)

    def split(self, new_index, data, branched):
        r""" Creates a new undo-step from this Node with the new
        *data* if and index. Returns the created node. """

        assert new_index > self.index

        new = Node(new_index, data, self)
        if branched:
            self.children.append(new)
        else:
            self.children = [new]
        return new

    def clean(self, min_index):
        r""" Strips all nodes from the tree that have an index lower
        than the supplied *min_index*. This method returns a list of
        the nodes that take the new place of the current :class:`Node`.
        If the node is not being stripped from the tree, a list which
        contains only *self* is returned. """

        if self.index < min_index:
            result = []
            for child in self.children:
                result.extend(child.clean(min_index))
        else:
            result = [self]

        return result

class Root(Node):
    r""" This class represents the root node. All it does is not
    contain any data and specialize the :meth:`clean` method. """

    def __init__(self):
        super(Root, self).__init__(0, None, None)

    def clean(self, min_index):
        result = []
        for child in self.children:
            result.extend(child.clean(min_index))

        self.children = result
        for child in self.children:
            child.parent = None

