# Copyright (c) 2017  Niklas Rosenstein
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
# THE SOFTWARE

from __future__ import absolute_import
from xml import sax
from xml.dom import minidom
import contextlib
import sys


class ParseError(Exception):
  pass


def support_parse_position(parser):
  """
  Hooks as SAX parser's `set_content_handler()` method to publish a
  `parse_position` member to every node.
  """

  # Thanks to https://stackoverflow.com/a/5133181/791713
  def set_content_handler(dom_handler):
    def startElementNS(name, tagName, attrs):
      orig_start_cb(name, tagName, attrs)
      cur_elem = dom_handler.elementStack[-1]
      cur_elem.parse_position = (
        parser._parser.CurrentLineNumber,
        parser._parser.CurrentColumnNumber
      )

    orig_start_cb = dom_handler.startElementNS
    dom_handler.startElementNS = startElementNS
    orig_set_content_handler(dom_handler)

  orig_set_content_handler = parser.setContentHandler
  parser.setContentHandler = set_content_handler


def load_xml_widgets(string, globals, insert_widget):
  """
  Parses an XML string and converts it to a view hierarchy. The *insert_widget*
  function will be called with arguments *(parent, child)* to insert the child
  widget into the parent widget.
  """

  parser = sax.make_parser()
  support_parse_position(parser)
  doc = minidom.parseString(string, parser)

  def parse(node):
    if node.nodeType != node.ELEMENT_NODE:
      if node.nodeType == node.TEXT_NODE:
        if not node.nodeValue.strip():
          return  # empty text is ok
        raise ParseError(node.parentNode.parse_position, "found non-empty text")
      raise ParseError(node.parse_position, "got node type: {}".format(node.nodeType))
    parts = node.nodeName.split('.')
    if parts[0] not in globals:
      raise ParseError(node.parse_position, 'name "{}" not defined'.format(parts[0]))

    member = globals[parts[0]]
    for part in parts[1:]:
      try:
        member = getattr(member, part)
      except AttributeError as exc:
        raise ParseError(node.parse_position, exc)

    kwargs = {}
    for key, value in node.attributes.items():
      kwargs[key] = value
    try:
      widget = member(**kwargs)
    except TypeError as exc:
      tb = sys.exc_info()[2]
      raise TypeError, TypeError('{}: {}'.format(member.__name__, exc)), tb
    #try:
    #except Exception as exc:
    #  raise ParseError(node.parse_position, '{}(): {}'.format(member.__name__, exc))

    for child_node in node.childNodes:
      child_widget = parse(child_node)
      if child_widget is not None:
        insert_widget(widget, child_widget)

    return widget

  return parse(doc.childNodes[0])
