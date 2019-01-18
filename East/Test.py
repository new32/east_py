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

import sys
import re
import math
import os
import datetime
import enum
import atexit

# ==
class StopException(Exception):
  """ Inner class to represent Stops of execution. """
  def __init__(self, message):
    self.message = message
# ==
class Test:
  EQ = 0
  NE = 1
  GT = 2
  GTE = 3
  LT = 4
  LTE = 5
  def __init__(self, report="", use_console=False):
    self.report = report
    self.use_console = use_console
    self.testcase = 0
    self.passes = 0
    self.fails = 0
    self.case_count = 0
    self.iteration_count = 0
    self.fout = sys.stdout
    self.failed_suites = list()
    self.labels = {
      Test.EQ:"==", Test.NE:"!=",
      Test.GT:">", Test.GTE:">=",
      Test.LT:"<", Test.LTE:"<="
    }
    self._default_tolerance = 1.0e-5
    self._done = False

    if not use_console:
      if not self.report or self.report == "":
        self.report = re.sub("\.", "_", sys.argv[0])+".rpt"
      try:
        self.fout = open(self.report, "w")
      except:
        print("E: Unable to open '%s'...using stdout" % self.report, file=sys.stderr)
        self.fout = sys.stdout
    atexit.register(self._end)
# --
  def __enter__(self):
    return self
# --
  def __exit__(self, exc_type, exc_value, traceback):
    self._end()
# --
  def _timestamp(self):
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# --
  def _print(self, text):
    print(text, file=self.fout)
# --
  def _end(self):
    if not self._done:
      self._done = True
      self.separator()
      if self.failed_suites:
        self.doc("The following suites contain failures:")
        for afail in self.failed_suites:
          self.doc("  " + afail)
      self.doc("Executed: " + os.path.basename(sys.argv[0]))
      self.doc("Report generated on " + self._timestamp())
      if self.fout != sys.stdout:
        self.fout.close()
# --
  def separator(self):
    print("# --", file=self.fout)
# --
  def blank(self):
    print("", file=self.fout)
# --
  def run(self, func, count=1):
    self.testcase += 1
    self.passes = 0
    self.fails = 0
    self.case_count = 0
    self.iteration_count = 0

    full_name = func.__qualname__

    tc_num = "%03d" % self.testcase

    self.doc("== Test " + tc_num + " : " + full_name)

    exception_hit = False

    while self.iteration_count < count:
      try:
        func()
        self.iteration_count += 1
      except StopException:
        self.doc("  'Stop' encountered")
        break
      except Exception as BE:
        message = BE.__class__.__name__ + ": " + str(BE)
        self.doc("Exception on iteration %d - %s" % (self.iteration_count, message))
        exception_hit = True
        break

    self.doc("-- Summary")
    self._print("Date " + self._timestamp())
    self._print("Plan 1..%d" % self.case_count)
    self._print("Pass %d/%d" % (self.passes, self.case_count))
    self._print("Fail %d/%d" % (self.fails, self.case_count))
    status = "Not Ok" if self.fails or exception_hit else "Ok"
    self._print("Test %s (%s) %s" % (tc_num, full_name, status))
    self._print("\n")
    if status == "Not Ok":
      self.failed_suites.append(tc_num)
# --
  def header(self, type, text):
    if self.iteration_count == 0 and type and text:
      self.doc(type+":")
      lines = text.split("\n")
      for aline in lines:
        self.doc("  " + aline.strip())
# --
  def doc(self, text):
    if text:
      lines = text.split("\n")
      for aline in lines:
        self._print("# " + aline)
# --
  def check_eval(self, actual, skip=False, die=False, desc=""):
    self.check(actual=actual, expected=True, skip=skip, die=die, desc="")
# --
  def check(self, actual=0, expected=0, eval=None, compare=EQ, skip=False, die=False, tolerance=0, desc=""):
    self.case_count += 1
    text = ""

    if eval != None:
      actual = eval
      expected = True
      if compare != Test.EQ:
        compare = Test.NE

    if not skip:
      result = False
      if tolerance > 0:
        # floating point comparison
        tt = abs(expected * (tolerance/100))
        # protect tolerance to ensure it's not 0
        tt = tt if tt != 0 and tt > self._default_tolerance else self._default_tolerance
        diff = abs(actual - expected)
        if compare == Test.EQ:
          result = diff <= tt
        elif compare == Test.NE:
          result = diff > tt
        elif compare == Test.GT or compare == Test.GTE:
          result = actual > expected
          if compare == Test.GTE and not result:
            result = diff <= tt
        elif compare == Test.LT or compare == Test.LTE:
          result = actual < expected
          if compare == Test.LTE and not result:
            result = diff <= tt
      else:
        if compare == Test.EQ:
          result = actual == expected
        elif compare == Test.NE:
          result = actual != expected
        elif compare == Test.GT or compare == Test.GTE:
          result = actual > expected
          if compare == Test.GTE and not result:
            result = actual == expected
        elif compare == Test.LT or compare == Test.LTE:
          result = actual < expected
          if compare == Test.LTE and not result:
            result = actual == expected
      if result:
        if die:
          text = "Stop"
          self.fails += 1
        else:
          text = "Pass"
          self.passes += 1
      else:
        if die:
          text = "Pass"
          self.passes += 1
        else:
          text = "Fail"
          self.fails += 1
    else:
      self.passes += 1
      text = "Skip"
    message = "%s %s %s" % (
      str(actual), self.labels[compare], str(expected))
    if die:
      message = "Not (" + message + ")"
    label = "Case %03d : %s : %s " % (self.case_count, text, message)
    if desc:
      label += " : " + desc
    self._print(label)
    if text == "Stop":
      raise StopException("Stop")
# --
  def suspend(self, text):
    self.doc("SUSPENDED:\n" + text.strip())
    raise StopException("Suspended")
# --
  def function(self, text="N/A"):
    self.header("Function Under Test", text.strip())
# --
  def requirements(self, text="N/A"):
    self.header("Requirements", text.strip())
# --
  def support(self, text="N/A"):
    self.header("Support Functions", text.strip())
# --
  def files(self, text="N/A"):
    self.header("Support Files", text.strip())
# --
  def stubs(self, text="N/A"):
    self.header("Stubs", text.strip())
# --
  def description(self, text="N/A"):
    self.header("Description", text.strip())
# ==
if __name__ == "__main__":
  print("Demo")
  with Test(use_console=True) as tester:
    tester.check(eval=(0 < 1))
    tester.check(eval=(0 > 1))
    tester.check(eval=False)
    tester.check(eval=True)
    tester.check(actual=3, expected=3, eval=(1 > 2))
