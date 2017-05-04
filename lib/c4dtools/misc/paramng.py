# -*- coding: utf8; -*-
#
# Copyright (C) 2015 Niklas Rosenstein
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
''' This module implements helper classes for easy management of GUI
parameters by using a declared set of parameters and converting them
to a Python management system.

Example:

.. code-block:: python

  import c4d
  from nr.c4d.misc import paramng

  class res:
    CHK_ON = 100001
    EDT_INDEX = 100002
    EDT_NAME = 100003

  class MyDialog(c4d.gui.GeDialog):

    def __init__(self):
      super(MyDialog, self).__init__()

      # Create the DataManager instance associated with our dialog.
      # The dialog will be stored as a weak reference.
      self.params = paramng.DataManager(self)

      # Create the parameter declaration factory which will certainly
      # help us to declare the parameters to the DataManager.
      f = paramng.Factory(self.params)

      # Declare the parameters.
      f.b('on', res.CHK_ON, default=True)
      f.i('index', res.EDT_INDEX, min=0, max=100)
      f.s('name', res.EDT_NAME, default='Peter')

    def CreateLayout(self):
      return self.LoadDialogResource(res.DLG_MYDIALOG)

    def InitValues(self):
      # Initialize the declared parameters with either the globally
      # saved date, or, if no data was stored globally, the default
      # values.
      bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)
      if bc:
        paramng.from_base_container(self.params, bc)
      else:
        self.params.restore_defaults()

      # Trigger the Command() message for the CHK_ON widget.
      # Note: If you want to simulate a real Command() message, use
      # the Message() method and BFM_ACTION.
      msg = c4d.BaseContainer()
      self.Command(res.CHK_ON, msg)

      return True

    def DestroyWindow(self):
      # Store our dialog configuration.
      bc = paramng.to_base_container(self.params)
      c4d.plugins.SetWorldPluginData(self.params, bc, add=True)

      super(MyDialog, self).DestroyWindow()

    def Command(self, wid, msg):
      if wid == res.CHK_ON:
        on = self.params.get('on')
        self.Enable(res.EDT_INDEX, on)

      return True
'''

import abc
import c4d
import weakref

from c4d import BaseContainer
from c4d.gui import GeDialog


class DataManager(object):
  ''' This class allows for easy getting and setting of dialog parameters.
  The first step is to declare all available parameters to this class using
  :meth:`declare` or :meth:`__lshift__`. After that, you can easily retrieve
  parameters using the :meth:`get` method. '''

  def __init__(self, reference=None):
    super(DataManager, self).__init__()
    self.declarations = {}
    if reference:
      reference = weakref.ref(reference)
    self.reference = reference

  def __iter__(self):
    ''' Iterate over all declarated parameters in the DataManager. '''

    return self.declarations.iteritems()

  def __lshift__(self, name__parameter):
    ''' Just like :meth:`declare`, but returns *self*. '''

    name, parameter = name__parameter
    self.declare(name, parameter)
    return self

  def __getitem__(self, name):
    ''' Get a declared :class:`AbstractParameter` instance. '''

    return self.declarations[name]

  def _get_reference(self, reference):
    if not reference:
      if self.reference:
        reference = self.reference()
        if not reference:
          raise RuntimeError('Lost weak-reference.')
      else:
        raise RuntimeError('No reference specified.')
    return reference

  def declare(self, name, parameter):
    ''' Declare a parameter to the DataManager. Raises an AssertionError
    if a parameter with the specified *name* is already defined or
    *parameter* is not a :class:`AbstractParameter` instance. '''

    assert name not in self.declarations
    assert isinstance(parameter, AbstractParameter)
    self.declarations[name] = parameter

  def get(self, name, reference=None):
    ''' Retrieve the value of a parameter by name. If :attr:`reference`
    is not specified, *reference* must be given. A RuntimeError is raised
    otherwise. '''

    reference = self._get_reference(reference)
    return self.declarations[name].get(reference)

  def set(self, name, value, reference=None):
    ''' Set a value to a parameter by name. If :attr:`reference` is not
    specified, *reference*  must be given. A RuntimeError is raised
    otherwise. '''

    reference = self._get_reference(reference)
    self.declarations[name].set(reference, value)

  def get_all(self, *names, **refkwargs):
    ''' Get a generator of all values of the parameters specified by
    *\*names*. '''

    reference = refkwargs.pop('reference', None)
    for key in refkwargs:
      raise TypeError('Unexpected keyword argument %s.' % key)

    for name in names:
      yield self.get(name, reference)

  def set_all(self, *names, **refkwargs):
    ''' Set parameters specified in *\*names*. An item of *\*names* can
    be either a list or tuple of two items, or a string followed by any
    other value. '''

    reference = refkwargs.pop('reference', None)
    for key in refkwargs:
      raise TypeError('Unexpected keyword argument %s.' % key)

    it = iter(names)
    while True:
      try:
        value = next(it)
      except StopIteration:
        break

      if isinstance(value, (list, tuple)):
        name, value = value
      else:
        name = value
        value = next(it)

      self.set(name, value, reference)

  def default(self, name, reference=None):
    ''' Get the default value of a parameter by name. Raises a
    RuntimeError if *reference* is not given and the :attr:`reference`
    attribute is not specified either. '''

    reference = self._get_reference(reference)
    return self.declarations[name].get_default()

  def set_default(self, name, reference=None):
    ''' Set the default value of the parameter specified via *name*. '''

    reference = self._get_reference(reference)
    self.declarations[name].set_default(reference)

  def restore_defaults(self, reference=None):
    ''' Restore the default values of all declared parameters. '''

    reference = self._get_reference(reference)
    for name, parameter in self:
      parameter.set_default(reference)

  def dict(self, reference=None):
    ''' Gather a Python dictionary filled with all the parameters from
    the specified *reference*. If *reference* is omitted and
    :attr:`reference` is not specified either, a RuntimeError is raised. '''

    reference = self._get_reference(reference)
    result = {}
    for name, parameter in self:
      result[name] = parameter.get(reference)

    return result


class AbstractParameter(object):
  ''' Base class for parameter declarations for the :class:`DataManager`
  class. It implements the retrieval and overriding of values. '''

  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def get(self, reference):
    pass

  @abc.abstractmethod
  def set(self, reference, value):
    pass

  @abc.abstractmethod
  def get_default(self):
    pass

  @abc.abstractmethod
  def set_default(self, reference):
    pass


class BaseFactory(object):
  ''' The BaseFactory class for doing simple parameter declaration for a
  :class:`DataManager` instance. '''

  def __init__(self, manager):
    super(BaseFactory, self).__init__()
    self.manager = manager
    self.synonyms = {}

  def __getattr__(self, type_name):
    ''' Returns a callable object which will accept a name parameter
    (representing the name passed to :meth:`DataManager.declare`) and
    any additional arguments which will be passed to the parameter class
    constructor specified by *type_name*. '''

    def func(__name, *args, **kwargs):
      return self.declare(type_name, __name, *args, **kwargs)

    return func

  def add_synonym(self, type_name, class_):
    ''' Add a :class:`AbstractParameter` class synonym to the BaseFactory
    which can be addressed by using the :meth:`__call__` or :meth:`declare`
    method. Raises ValueError if the synonym *type_name* is already taken. '''

    if type_name in self.synonyms:
      raise ValueError('Synonym "%s" already taken.' % type_name)

    self.synonyms[type_name] = class_

  def declare(self, __type_name, __name, *args, **kwargs):
    ''' Declare a new parameter to the wrapped :class:`DataManager`
    instance by using one of the defined synonyms (see :meth:`add_synonym`).
    '''

    param = self.synonyms[__type_name](*args, **kwargs)
    self.manager.declare(__name, param)
    return param

  __call__ = declare


# Available since R15.
if c4d.GetC4DVersion() < 15000:
  c4d.FORMAT_FLOAT = 1718773089
  c4d.FORMAT_INT = 1718382183


class C4DAbstractParameter(AbstractParameter):
  ''' Base-class for Cinema 4D Dialog Widget declarations. '''

  def __init__(self, param):
    super(C4DAbstractParameter, self).__init__()
    self.param = param

  @abc.abstractmethod
  def bc_get(self, container):
    pass

  @abc.abstractmethod
  def bc_set(self, container, value):
    pass


class C4DParameter(C4DAbstractParameter):

  typename = None

  def __init__(self, param, default=None, **set_kwargs):
    super(C4DParameter, self).__init__(param)
    self.default = default
    self.set_kwargs = set_kwargs

  def bc_get(self, container):
    method = getattr(container, 'Get%s' % self.typename)
    return method(self.param)

  def bc_set(self, container, value):
    method = getattr(container, 'Set%s' % self.typename)
    method(self.param, value)

  def filter_set_kwargs(self, kwargs):
    return kwargs

  # AbstractParameter

  def get(self, reference):
    method = getattr(reference, 'Get%s' % self.typename)
    return method(self.param)

  def set(self, reference, value):
    kwargs = self.filter_set_kwargs(self.set_kwargs.copy())
    method = getattr(reference, 'Set%s' % self.typename)
    method(self.param, value, **kwargs)

  def get_default(self):
    return self.default

  def set_default(self, reference):
    if self.default is not None:
      self.set(reference, self.default)


class C4DLongParameter(C4DParameter):

  typename = 'Long'

  def __init__(self, param, default=0, min=None, max=None, step=1,
         min2=None, max2=None, tristate=False):
    super(C4DLongParameter, self).__init__(
        param, default, min=min, max=max, step=step, min2=min2,
        max2=max2, tristate=tristate)

  # C4DAbstractParameter

  def filter_set_kwargs(self, kwargs):
    for key in ('min', 'max', 'min2', 'max2'):
      if kwargs[key] is None:
        kwargs.pop(key)
    return kwargs


class C4DRealParameter(C4DLongParameter):

  typename = 'Real'

  def __init__(self, param, default=0.0, min=None, max=None, step=1.0,
         format=c4d.FORMAT_FLOAT, min2=None, max2=None,
         quadscale=False, tristate=False):
    super(C4DRealParameter, self).__init__(
        param, default, min, max, step, min2, max2, tristate)
    self.set_kwargs.update({'format': format, 'quadscale': quadscale})


class C4DStringParameter(C4DParameter):

  typename = 'String'

  def __init__(self, param, default='', tristate=False, flags=0):
    super(C4DStringParameter, self).__init__(
        param, default, tristate=tristate, flags=flags)


class C4DBoolParameter(C4DParameter):

  typename = 'Bool'

  def __init__(self, param, default=False):
    super(C4DBoolParameter, self).__init__(param, default)


class C4DFilenameParameter(C4DParameter):

  typename = 'Filename'

  def __init__(self, param, default=''):
    super(C4DFilenameParameter, self).__init__(param, default)


class C4DVectorParameter(C4DAbstractParameter):

  @classmethod
  def from_params(self, idx, idy, idz, default=0, min=None, max=None,
          step=1.0, format=c4d.FORMAT_FLOAT, min2=None, max2=None,
          quadscale=False, tristate=False):
    ''' Creates a new C4DVectorParameter instance from *idx*, *idy*
    and *idz* being dialog symbols and *\*args* and *\*\*kwargs* being
    passed to each :class:`C4DRealParameter` instance created for the
    :class:`C4DVectorParameter` instance which is returned from this
    method. '''

    def triple(x, name):
      if isinstance(x, c4d.Vector):
        return (x.x, x.y, x.z)
      elif isinstance(x, (list, tuple)):
        assert len(x) == 3, '%s must have length 3 when being ' \
            'list or tuple.' % name
        return x
      else:
        return (x,) * 3

    default = triple(default, 'default')
    min = triple(min, 'min')
    max = triple(max, 'max')
    min2 = triple(min2, 'min2')
    max2 = triple(max2, 'max2')
    step = triple(step, 'step')
    format = triple(format, 'format')
    quadscale = triple(quadscale, 'quadscale')
    tristate = triple(tristate, 'tristate')

    params = []
    for i, wid in enumerate((idx, idy, idz)):
      p = C4DRealParameter(wid, default[i], min=min[i], max=max[i],
          step=step[i], format=format[i], min2=min2[i],
          max2=max2[i], quadscale=quadscale[i],
          tristate=tristate[i])
      params.append(p)

    return C4DVectorParameter(*params)

  def __init__(self, px, py, pz):
    super(C4DVectorParameter, self).__init__(px.param)
    self.px = px
    self.py = py
    self.pz = pz

  # C4DAbstractParameter

  def bc_get(self, container):
    return container.GetVector(self.param)

  def bc_set(self, container, value):
    container.SetVector(self.param, value)

  # AbstractParameter

  def get(self, reference):
    v = map(lambda x: x.get(reference), (self.px, self.py, self.pz))
    return c4d.Vector(*v)

  def set(self, reference, value):
    self.px.set(reference, value.x)
    self.py.set(reference, value.y)
    self.pz.set(reference, value.z)

  def get_default(self):
    dx, dy, dz = (self.px.get_default(), self.py.get_default(),
        self.pz.get_default())
    if all(map(lambda x: x is None, (dx, dy, dz))):
      return None

    if dx is None: dx = 0.0
    if dy is None: dy = 0.0
    if dz is None: dz = 0.0
    return c4d.Vector(dx, dy, dz)

  def set_default(self, reference):
    default = self.get_default()
    if default:
      self.set(reference, default)


def to_base_container(manager, reference=None):
  ''' Convert the values declared in the :class:`DataManager` of
  *manager* to a :class:`c4d.BaseContainer` via the specified *reference*
  or the reference specified in the manager. '''

  reference = manager._get_reference(reference)
  container = BaseContainer()
  for name, param in manager:
    if not isinstance(param, C4DAbstractParameter):
      continue

    value = param.get(reference)
    param.bc_set(container, value)

  return container


def from_base_container(manager, container, reference=None):
  ''' The reverse to :func:`c4d_to_container`. '''

  reference = manager._get_reference(reference)
  parammap = {}
  for name, param in manager:
    if not isinstance(param, C4DAbstractParameter):
      continue

    parammap[param.param] = param

  for key, value in container:
    param = parammap.get(key)
    if not param:
      continue

    value = param.bc_get(container)
    param.set(reference, value)


class Factory(BaseFactory):
  ''' Create a new :class:`BaseFactory` instance with all standard
  parameter shortcuts assigned.

  === ========
  l/i LONG
  r   Real
  s   String
  b   Boool
  f   Filename
  v   Vector
  === ========
  '''

  def __init__(self, manager):
    super(Factory, self).__init__(manager)

    self.add_synonym('l', C4DLongParameter)
    self.add_synonym('i', C4DLongParameter)
    self.add_synonym('r', C4DRealParameter)
    self.add_synonym('s', C4DStringParameter)
    self.add_synonym('b', C4DBoolParameter)
    self.add_synonym('f', C4DFilenameParameter)
    self.add_synonym('v', C4DVectorParameter.from_params)
