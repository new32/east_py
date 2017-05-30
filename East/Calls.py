#!/usr/bin/env python3

# Copyright (c) 2017, Arthur Gardiner
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import ast
import os
import sys
import re
# ======================================================================
class _Id:
  def __init__(self, name="", line=0, col=0, use_type=None):
    self.name = name
    self.line = line
    self.col = col
    self.use_type = use_type
  # --------------------------------------------------------------------
  def __repr__(self):
    my_str = "%s (" % (self.name)
    if self.use_type == _Node.CLASS:
      my_str += "C:"
    elif self.use_type == _Node.FUNCTION:
      my_str += "F:"
    elif self.use_type == _Node.CALL:
      my_str += "E:"
    else:
      my_str += "U:"
    my_str += "%d,%d)" % (self.line, self.col)
    return my_str
  # --------------------------------------------------------------------
  def __eq__(self, other):
    return (  (self.name == other.name) and
              (self.line == other.line) and
              (self.col == other.col)   )
# ======================================================================
class _Node:
  CLASS = "class"
  FUNCTION = "func"
  CALL = "call"
  def __init__(self, name, line=0, col=0, use_type=CLASS):
    self.name = _Id(name, line, col, use_type)
    self.use_type = self.name.use_type
    # append either _Id or _Node
    self.children = list()
  # --------------------------------------------------------------------
  def _print(self, child, depth):
    my_str = "\n"
    my_str += ("| "*depth)
    my_str += str(child.name)
    for achild in child.children:
      my_str += self._print(achild,depth+1)
    return my_str
  # --------------------------------------------------------------------
  def __repr__(self):
    my_str = str(self.name)
    for child in self.children:
      my_str += self._print(child,1)
    return my_str
  # --------------------------------------------------------------------
  def __eq__(self, other):
    return self.name == other.name
# ======================================================================
class Calls(ast.NodeVisitor):
  """
  Script analyzer for extracting all classes and functions.

  The script's AST is walked, extracting all classes and functions defined
  with the script body (including nested members). Output is sent directly
  to standard out.

  filename - Script to analyze. Required
  enable_calls - Enables processing of executed calls ('__call__' entities).
                 Defaults to False.

  Example Output:
    Calls.py:
    _Id (C:22,0)
    | __init__ (F:23,2)
    | __repr__ (F:29,2)
    | __eq__ (F:42,2)
    _Node (C:47,0)
    | __init__ (F:51,2)
    | _print (F:57,2)
    | __repr__ (F:65,2)
    | __eq__ (F:71,2)
    Calls (C:74,0)
    | __init__ (F:86,2)
    | walk_node (F:107,2)
    | visit_ClassDef (F:137,2)
    | visit_FunctionDef (F:141,2)
    | visit_Call (F:145,2)
    _get_full_name (F:150,0)

  Example Output with Calls Enabled:
    Calls.py:
    _Id (C:22,0)
    | __init__ (F:23,2)
    | __repr__ (F:29,2)
    | __eq__ (F:42,2)
    _Node (C:47,0)
    | __init__ (F:51,2)
    | | _Id (E:52,16)
    | | list (E:55,20)
    | _print (F:57,2)
    | | str (E:60,14)
    | | self._print (E:62,16)
    | __repr__ (F:65,2)
    | | str (E:66,13)
    | | self._print (E:68,16)
    | __eq__ (F:71,2)
    Calls (C:74,0)
    | __init__ (F:107,2)
    | | os.path.abspath (E:111,20)
    | | os.path.basename (E:112,20)
    | | list (E:114,16)
    | | list (E:115,19)
    | | list (E:116,21)
    | | list (E:117,17)
    | | open (E:118,9)
    | | ast.parse (E:122,25)
    | | self.visit (E:123,6)
    | | print (E:124,6)
    | | print (E:126,8)
    | walk_node (F:128,2)
    | | hasattr (E:129,7)
    | | _Node (E:134,15)
    | | ast.walk (E:136,17)
    | | _get_full_name (E:133,13)
    | | isinstance (E:141,11)
    | | self.walk_node (E:142,23)
    | | isinstance (E:146,13)
    | | the_node.children.append (E:144,12)
    | | self.classes.append (E:145,12)
    | | self.walk_node (E:147,23)
    | | the_node.children.append (E:149,12)
    | | self.functions.append (E:150,12)
    | | isinstance (E:151,13)
    | | self.walk_node (E:152,23)
    | | the_node.children.append (E:154,12)
    | | self.calls.append (E:155,12)
    | visit_ClassDef (F:158,2)
    | | self.data.append (E:160,4)
    | | | self.walk_node (E:160,21)
    | visit_FunctionDef (F:162,2)
    | | self.data.append (E:164,4)
    | | | self.walk_node (E:164,21)
    | visit_Call (F:166,2)
    | | self.data.append (E:169,6)
    | | | self.walk_node (E:169,23)
    _get_full_name (F:171,0)
    | list (E:172,13)
    | ast.walk (E:173,15)
    | elements.reverse (E:178,2)
    | isinstance (E:174,7)
    | elements.append (E:175,6)
    | isinstance (E:176,9)
    | elements.append (E:177,6)
    len (E:190,5)
    Calls (E:192,6)
  """
  def __init__(self, filename, enable_calls=False):
    self._enable_calls = enable_calls
    self._global = "<<global>>"
    # file info...
    self.filename = os.path.abspath(filename)
    self.basename = os.path.basename(filename)
    self.contents = ""
    self.data = list()
    self.classes = list()
    self.functions = list()
    self.calls = list()
    with open(self.filename, "r") as FIN:
      for line in FIN:
        self.contents += line
    if self.contents:
      translation_unit = ast.parse(self.contents,filename=self.filename)
      self.visit(translation_unit)
      print(filename + ":")
      for item in self.data:
        print(item)
  # --------------------------------------------------------------------
  def walk_node(self, node, use_type):
    if hasattr(node, "name"):
      name = node.name
    else:
      # only necessary if the call data is enabled
      name = _get_full_name(node)
    the_node = _Node(name, node.lineno, node.col_offset, use_type)
    skip = True
    for anode in ast.walk(node):
      if skip:
        # skip the first node since it's the entry node
        skip = False
      else:
        if isinstance(anode, ast.ClassDef):
          child_node = self.walk_node(anode, _Node.CLASS)
          if child_node not in self.classes:
            the_node.children.append(child_node)
            self.classes.append(child_node)
        elif isinstance(anode, ast.FunctionDef):
          child_node = self.walk_node(anode, _Node.FUNCTION)
          if child_node not in self.functions:
            the_node.children.append(child_node)
            self.functions.append(child_node)
        elif isinstance(anode, ast.Call) and self._enable_calls:
          child_node = self.walk_node(anode, _Node.CALL)
          if child_node not in self.calls:
            the_node.children.append(child_node)
            self.calls.append(child_node)
    return the_node
  # --------------------------------------------------------------------
  def visit_ClassDef(self, node):
    # parse toplevel class definitions
    self.data.append(self.walk_node(node, _Node.CLASS))
  # --------------------------------------------------------------------
  def visit_FunctionDef(self, node):
    # parse toplevel function definitions
    self.data.append(self.walk_node(node, _Node.FUNCTION))
  # --------------------------------------------------------------------
  def visit_Call(self, node):
    if self._enable_calls:
      # parse toplevel calls
      self.data.append(self.walk_node(node, _Node.CALL))
# ======================================================================
def _get_full_name(node):
  elements = list()
  for anode in ast.walk(node.func):
    if isinstance(anode, ast.Name):
      elements.append(anode.id)
    elif isinstance(anode, ast.Attribute):
      elements.append(anode.attr)
  elements.reverse()
  first = True
  full_name = ""
  for elem in elements:
    if not first:
      full_name += "."
    else:
      first = False
    full_name += elem
  return full_name
# ======================================================================
if __name__ == "__main__":
  if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
      Calls(arg, True)
