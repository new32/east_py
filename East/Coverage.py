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
import atexit
"""
This class should not be used directly as it is intended to be inserted
within the modified AST.
"""
# ==
class Coverage:
  def __init__(self, ecov, use_console=False):
    self.ecov_file = ecov
    self.ecov = sys.stdout
    if not use_console:
      self.ecov = open(self.ecov_file, "a")
    atexit.register(self._shutdown)
  # --
  def _shutdown(self):
    if self.ecov and self.ecov != sys.stdout:
      self.ecov.close()
  # --
  def _check(self, label, value):
    # forward Coverage.condition and Coverage.decision
    # here since, for now, the behavior is the same
    if self.ecov == sys.stdout:
      label = "%s:%s" % (self.ecov_file, label)
    print(label + ":%d" % (1 if value else 0), file=self.ecov)
    return value
  # --
  def condition(self, label, value):
    # prints the CD# entries
    return self._check(label, value)
  # --
  def decision(self, label, value):
    # prints the BR# entries
    return self._check(label, value)
  # --
  def block(self, label):
    self._check(label, 1)
