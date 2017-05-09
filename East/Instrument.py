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
import tokenize

"""
Python script instrumentor for condition, decision and basic block coverage.

Specifically designed for unit testing, East.Instrument should be run as a
command-line application:

$> python3 -m East.Instrument module1[, module2...]

Each file passed to the command will be
A) Instrumented at the AST level
B) The instrumented AST compiled into bytecode
C) A *.edat, containing the instrumented locations/types, is created

Each instrumented file can be used simply by importing the module into the
test driver as the __pycache__ is automatically used by python3.

When the compiled module is executed, a *.ecov will automatically be created
if needed, appended to if it exists, to record the coverage actually obtained
by the run.

The East.Report module is necessary to convert the *.edat and *.ecov into an
appropriate report.

  The following are parsed as blocks at the first instruction inside the block:
    if, elif, while, for, try, except, final, else

  The following are parsed as decisions at the point of the test:
    if, while

  The following are parsed as conditions:
    and, or, not, is, in
    Equality operators (<, <=, >, >=, !=, ==)

Caveats:
  No attempt is made to insert Else clauses for constructs that support them
  but do not implement them. As such, a buried hard return out of a function
  does not identify blocks following it. Only the status of the decision can
  be used to determine that coverage is missing.

  For example:

  Line   #000001|def example():
  Line + #000002|  call1()
  Line   #000003|  if call2()
  000003.004|T/*|    call2
  Line + #000004|    return
  Line   #000005|  call3()

  In the above, F coverage of the decision is missing, as such, call3() is
  never executed as a side-effect of the return. A good refactor in this case
  would be something like this:

  Line   #000001|def example():
  Line + #000002|  call1()
  Line   #000003|  if not call2()
  000003.006|*/F|
  000003.004|T/*|         call2
  Line * #000004|    call3()

  This is a clearer implementation of the intention of the example() function,
  to execute call3() only if call2() is False.
"""
# ======================================================================
class TokenList:
  """
  Inner class.

  Used to fetch token names.
  """
  def __init__(self, filename):
    self.filename = filename
    self.tokens = None
    self.token_locations = list()
    with open(self.filename, "rb") as FIN:
      self.tokens = list(tokenize.tokenize(FIN.readline))
    if self.tokens:
      old_tokens = self.tokens
      self.tokens = dict()
      for token in old_tokens:
        # this will forcibly overwrite dedents which aren't cared about anyway
        loc = ("%d.%d" % token.start)
        if loc not in self.token_locations:
          self.token_locations.append(loc)
        self.tokens[loc] = token
  # --------------------------------------------------------------------
  def get_true_location(self, keyword, location):
    ret_val = location
    if self.tokens and location in self.token_locations:
      labels = ["if", "elif"]
      if keyword == "while":
        labels = ["while"]
      index = self.token_locations.index(location)
      while index >= 0:
        token = self.tokens[self.token_locations[index]]
        if token.string in labels:
          ret_val = self.token_locations[index]
          break
        index -= 1
    return ret_val
# ======================================================================
class Instrument(ast.NodeTransformer):
  """
  Perform instrumentation on the specified source file.

  If called programatically, the optional parameter of 'run', when set True,
  will execute the instrumented AST (which itself will not be saved).
  """
  def __init__(self, filename, run=False):
    # file info...
    self.filename = os.path.abspath(filename)
    self.basename = os.path.basename(filename)
    self.contents = ""
    # state info...
    self.block_count = 0
    self.block_locations = list()
    self.decision_count = 0
    self.decision_locations = list()
    self.condition_count = 0
    self.condition_locations = list()
    # ...everything else
    self.tokens = TokenList(self.filename)
    with open(self.filename, "r") as FIN:
      for line in FIN:
        self.contents += line
    if self.contents:
      with open(self.filename + ".edat", "w") as self.edat:
        import __main__
        print(self.filename, file=self.edat)
        translation_unit = self.visit(ast.parse(self.contents,filename=self.filename))

        ast_object = compile(translation_unit, filename=self.basename, mode="exec")
        if run:
          exec(ast_object, __main__.__dict__, __main__.__dict__)
        else:
          # setup to manually write the __pycache__ folder for the instrumented
          # source files. This way, the test author only has to import the
          # instrumented files into the test driver to get the modified
          # AST/coverage to work.
          import builtins
          import py_compile
          def my_compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1):
            return ast_object
          builtin_compile = builtins.compile
          builtins.compile = my_compile
          py_compile.compile(self.filename)
          builtins.compile = builtin_compile
  # --------------------------------------------------------------------
  def _add_statement(self, node_body):
    cov_line = None
    location = "%d.%d" % (node_body[0].lineno, node_body[0].col_offset)
    if location not in self.block_locations:
      self.block_locations.append(location)
      label = "BL" + str(self.block_count)
      print("%s:%s:BLOCK" %
            (label, location), file=self.edat)
      self.block_count += 1
      cov_line = ast.parse("east_coverage.statement(\"%s\")" % label).body[0]
      ast.copy_location(cov_line, node_body[0])
      node_body.insert(0, cov_line)
  # --------------------------------------------------------------------
  def _add_decision(self, keyword, old_test):
    dec_line = old_test
    location = "%d.%d" % (old_test.lineno, old_test.col_offset)
    if location not in self.decision_locations:
      self.decision_locations.append(location)
      label = "BR" + str(self.decision_count)
      # have to fix the location in order to accurately report the keyword,
      # rather than the test
      fixed_location = self.tokens.get_true_location(keyword, location)
      print("%s:%s:%s" %
            (label, fixed_location, self.tokens.tokens[fixed_location].string), file=self.edat)
      self.decision_count += 1
      dec_line = ast.Call()
      dec_line.func = ast.Attribute(attr="decision", ctx=ast.Load(),
        value=ast.Name("east_coverage", ast.Load()))
      dec_line.args = [ast.Str(label), old_test]
      dec_line.keywords = []
      dec_line.ctx = ast.Load()
      ast.copy_location(dec_line, old_test)
      ast.fix_missing_locations(dec_line)
    return dec_line
  # --------------------------------------------------------------------
  def _add_condition(self, text, cond_node):
    cd_line = cond_node
    location = "%d.%d" % (cond_node.lineno, cond_node.col_offset)
    if location not in self.condition_locations:
      self.condition_locations.append(location)
      label = "CD" + str(self.condition_count)
      print("%s:%s:%s" %
            (label, location, text), file=self.edat)
      self.condition_count += 1
      cd_line = ast.Call()
      cd_line.func = ast.Attribute(attr="condition", ctx=ast.Load(),
        value=ast.Name("east_coverage", ast.Load()))
      cd_line.args = [ast.Str(label), cond_node]
      cd_line.keywords = []
      cd_line.ctx = ast.Load()
      ast.copy_location(cd_line, cond_node)
      ast.fix_missing_locations(cd_line)
    return cd_line
  # --------------------------------------------------------------------
  def visit_Module(self, module_node):
    imports = list()
    statements = list()
    for anode in module_node.body:
      anode = self.visit(anode)
      if( not statements and
          ( isinstance(anode, ast.Import) or
            isinstance(anode, ast.ImportFrom))):
        imports.append(anode)
      else:
        statements.append(anode)

    # setup and insert the East import
    east_import = ast.parse("import East").body[0]
    east_import.col_offset = 1
    east_import.lineo = 1
    if imports:
      east_import.lineno = imports[-1].lineno+1

    # setup and insert coverage tool
    east_coverage = ast.parse("east_coverage = East.Coverage(\"%s\")" % (self.basename+".ecov")).body[0]
    east_coverage.col_offset = 1
    if statements:
      east_coverage.lineno = east_import.lineno+1

    body = imports + [east_import, east_coverage] + statements
    return ast.Module(body=body)
  # --------------------------------------------------------------------
  def visit_If(self, if_node):
    # Add Coverage.statement for BODY and ELSE
    # Add Coverage.decision for TEST
    self.generic_visit(if_node)
    if if_node.body:
      self._add_statement(if_node.body)
    if if_node.orelse:
      # prevent elif from being duplicated
      if not isinstance(if_node.orelse[0], ast.If):
        self._add_statement(if_node.orelse)
    if_node.test = self._add_decision("if", if_node.test)
    return if_node
  # --------------------------------------------------------------------
  def visit_IfExp(self, exp_node):
    # Add Coverage.decision for TEST
    self.generic_visit(exp_node)
    exp_node.test = self._add_decision("if", exp_node.test)
    return exp_node
  # --------------------------------------------------------------------
  def visit_While(self, while_node):
    # Add Coverage.statement for BODY and ELSE
    # Add Coverage.decision for TEST
    self.generic_visit(while_node)
    if while_node.body:
      self._add_statement(while_node.body)
    if while_node.orelse:
      self._add_statement(while_node.orelse)
    while_node.test = self._add_decision("while", while_node.test)
    return while_node
  # --------------------------------------------------------------------
  def visit_For(self, for_node):
    # Add Coverage.statement for BODY and ELSE
    self.generic_visit(for_node)
    if for_node.body:
      self._add_statement(for_node.body)
    if for_node.orelse:
      self._add_statement(for_node.orelse)
    return for_node
  # --------------------------------------------------------------------
  def visit_FunctionDef(self, func_node):
    # Add Coverage.statement for BODY
    self.generic_visit(func_node)
    if func_node.body:
      self._add_statement(func_node.body)
    return func_node
  # --------------------------------------------------------------------
  def visit_Try(self, try_node):
    # Add Coverage.statement for BODY, ELSE and FINAL
    self.generic_visit(try_node)
    if try_node.body:
      self._add_statement(try_node.body)
    if try_node.orelse:
      self._add_statement(try_node.orelse)
    if try_node.finalbody:
      self._add_statement(try_node.finalbody)
    if try_node.handlers:
      for handler in try_node.handlers:
        self._add_statement(handler.body)
    return try_node
  # --------------------------------------------------------------------
  def visit_UnaryOp(self, unary_node):
    self.generic_visit(unary_node)
    if isinstance(unary_node.op, ast.Not):
      unary_node = self._add_condition("not", unary_node)
    return unary_node
  # --------------------------------------------------------------------
  def visit_Compare(self, comp_node):
    self.generic_visit(comp_node)
    if len(comp_node.ops) == 1:
      location = ("%d.%d" % (comp_node.lineno, comp_node.col_offset))
      text = self.tokens.tokens[location].string + "..."
      comp_node = self._add_condition(text, comp_node)
    else:
      # construct the AND gate and forward to visit_BoolOp
      # The chain
      #   aa < bb < cc
      # gets decomposed as
      #   aa < bb and bb < cc
      decomposed = ast.BoolOp(op=ast.And(), values=list())
      operands = list(comp_node.comparators)
      operands.insert(0, comp_node.left)
      index = 0
      for op in comp_node.ops:
        a_comp = ast.Compare()
        a_comp.left = operands[index]
        a_comp.ops = [op]
        a_comp.comparators = [operands[index+1]]
        ast.copy_location(a_comp, operands[index])
        ast.fix_missing_locations(a_comp)
        decomposed.values.append(a_comp)
        index += 1
      ast.copy_location(decomposed, comp_node)
      # redundant but just in case...
      ast.fix_missing_locations(decomposed)
      comp_node = self.visit_BoolOp(decomposed)
    return comp_node
  # --------------------------------------------------------------------
  def visit_BoolOp(self, bool_node):
    self.generic_visit(bool_node)
    index = 0
    count = len(bool_node.values)
    while index < count:
      a_node = bool_node.values[index]
      location = ("%d.%d" % (a_node.lineno, a_node.col_offset))
      text = self.tokens.tokens[location].string
      bool_node.values[index] = self._add_condition(text, a_node)
      index += 1
    return bool_node
# ======================================================================
if __name__ == "__main__":
  if len(sys.argv) > 1:
    args = sys.argv[1:]
    for arg in args:
      Instrument(arg, False)
