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
import os
import re
import datetime

"""
Generate TXT or HTML reports from East data files.

East.Report should be run as a command-line application:

$> python3 -m East.Report <options> file1[, file2...]

For conditions and decisions, coverages are printed below the original source
and denote T/F status for each. A missing coverage is replaced with
an asterisk (*).
For blocks, coverages are printed within the margin in the Line area. If
a block is covered, a plus (+) appears. If a block is missed, an asterisk
(*) appears.
In HTML mode, the report sets the foreground color based on the pass or
fail status.
"""

# ==
class CoverageEntry:
  """
  Inner class.

  Defines a covered entry and tracks the number of Trues and Falses
  encountered
  """
  def __init__(self):
    self.coverage = ""
    self.line = 0
    self.column = 0
    self.trues = 0
    self.falses = 0
  # --
  def hasTrue(self):
    return self.trues > 0
  # --
  def hasFalse(self):
    ret_val = self.falses > 0
    if self.coverage == "S":
      ret_val = True
    return ret_val
  # --
  def isFullyCovered(self):
    ret_val = (self.hasTrue() and self.hasFalse())
    if self.coverage == "B":
      ret_val = self.hasTrue()
    return ret_val
  # --
  def to_string(self, start_at_zero):
    my_str  = "%0.6d.%0.3d|" % (self.line,self.column)
    if self.trues > 0:
      my_str += "T"
    else:
      my_str += "*"
    my_str += "/"
    # Blocks can only ever be "Hit" or "Not Hit"
    # so don't attempt to display a False coverage
    if self.coverage != "B":
      if self.falses > 0:
        my_str += "F"
      else:
        my_str += "*"
    else:
      my_str += "X"
    my_str += "|"
    idx = 1
    if start_at_zero:
      idx = 0
    while idx < self.column:
      my_str += " "
      idx += 1
    my_str += "^"
    return my_str
  # --
  def __repr__(self):
    return self.to_string(False)
# ==
class CoverageData:
  """
  Inner class.

  Container for coverage entries. Also organizes entries by line
  for reporting.
  """
  def __init__(self, edat, ecov, source):
    self.edat = edat
    self.ecov = ecov
    self.source = source
    self.decisions = dict()
    self.conditions = dict()
    self.blocks = dict()
    self.entries_by_line = dict()
    self.block_lines = dict()
  # --
  def total_conditions(self):
    return len(self.conditions)
  # --
  def total_decisions(self):
    return len(self.decisions)
  # --
  def total_blocks(self):
    return len(self.blocks)
  # --
  def covered_conditions(self):
    count = 0
    for acondition in self.conditions:
      condition = self.conditions[acondition]
      if condition.isFullyCovered():
        count += 1
    return count
  # --
  def covered_blocks(self):
    count = 0
    for ablock in self.blocks:
      block = self.blocks[ablock]
      if block.isFullyCovered():
        count += 1
    return count
  # --
  def covered_decisions(self):
    count = 0
    for adecision in self.decisions:
      decision = self.decisions[adecision]
      if decision.isFullyCovered():
        count += 1
    return count
  # --
  def append(self, in_string):
    # append a coverage entry from the ECOV to the correct storage
    # pool. Also separates out the basic block and line entry coverage
    (location, coverage) = in_string.split(":", maxsplit=2)
    (line, col) = location.split(".")
    line = int(line)
    col = int(col)

    value = CoverageEntry()
    value.coverage = coverage
    value.line    = line
    value.column  = col
    value.trues   = 0
    value.false   = 0

    if coverage == "C" and location not in self.conditions:
      self.conditions[location] = value
    elif coverage == "D" and location not in self.decisions:
      self.decisions[location] = value
    elif coverage == "B" and location not in self.blocks:
      self.blocks[location] = value
    if not line in self.entries_by_line and coverage != "B":
      self.entries_by_line[line] = list()
    if coverage != "B":
      self.entries_by_line[line].append(value)
    else:
      self.block_lines[line] = location
  # --
  def cover(self, in_string):
    # Increments the coverage count for a given entity
    (location, coverage, value) = in_string.split(":")

    entry = None
    if coverage == "C":
      if location in self.conditions:
        entry = self.conditions[location]
    elif coverage == "D":
      if location in self.decisions:
        entry = self.decisions[location]
    elif coverage == "B":
      if location in self.blocks:
        entry = self.blocks[location]
    if entry:
      if value == "0":
        entry.falses += 1
      else:
        entry.trues += 1
# ==
class Report:
  def __init__(self):
    self.use_html = False
  # --
  def useHTML(self):
    self.use_html = True
  # --
  def check_all(self, cwd="."):
    # grabs each edat within the directory and passes it
    # purely to check_file
    files = os.listdir(cwd)
    for file in files:
      if file.endswith(".edat"):
        self.check_file(os.path.abspath(file))
  # --
  def check_file(self,edat):
    # verify that the edat, ecov and source files exist before attempting
    # to parse anything
    if not edat.endswith(".edat"):
      edat += ".edat"
    if os.path.exists(edat):
      ecov = re.sub("\.edat", ".ecov", edat)
      if os.path.exists(ecov):
        source = None
        # the source data is the first line of the edat so only 1 line is read
        with open(edat, "r") as FIN:
          for line in FIN:
            source = os.path.abspath(line.strip())
            break

        if source:
          if os.path.exists(source):
            self.check(edat, ecov, source)
          else:
            print(source + " does not exist...nothing to do", file=sys.stderr)
        else:
          print("No source entry in " + ecov + "...nothing to do",
            file=sys.stderr)
      else:
        print(ecov + " does not exist...nothing to do", file=sys.stderr)
    else:
      print(edat + " does not exist...nothing to do", file=sys.stderr)
  # --
  def parse_edat(self, edat, coverage_data):
    with open(edat, "r") as FIN:
      for line in FIN:
        if line and not line.startswith("#"):
          line = line.strip()
          if ":" in line:
            coverage_data.append(line)
  # --
  def parse_ecov(self, ecov, coverage_data):
    with open(ecov, "r") as FIN:
      for line in FIN:
        if line and not line.startswith("#"):
          line = line.strip()
          if ":" in line:
            coverage_data.cover(line)
  # --
  def report(self, source, coverage_data):
    is_py_src = source.endswith(".py")
    # print the report based on the edat name/location
    line_number = 0
    missed_list = list()
    ext = "_cov.txt"
    if self.use_html:
      ext = "_cov.html"
    output_name = re.sub("\.edat", ext, coverage_data.edat)
    with open(output_name, "w") as FOUT:
      print("M: Writing " + output_name + "...")
      if self.use_html:
        # print the heading and style info
        print("<html>",file=FOUT)
        print("<head>",file=FOUT)
        print("<title>"+ os.path.basename(coverage_data.edat) + "</title>",file=FOUT)
        print("<style type=\"text/css\">",file=FOUT)
        print("BODY {font-family: Monospace}",file=FOUT)
        print("TABLE.listing {border-style: none}",file=FOUT)
        print("TD.listing {font-family: Monospace}",file=FOUT)
        print("TD.summary {font-family: Monospace}",file=FOUT)
        print(".failed {background-color: LightPink}",file=FOUT)
        print(".passed {color: DarkGreen}",file=FOUT)
        print(".block_miss {background-color: LightPink}",file=FOUT)
        print(".block_hit {color: DarkGreen}", file=FOUT)
        print(".summary_miss {color: DarkRed}",file=FOUT)
        print(".summary_pass {color: DarkGreen}",file=FOUT)
        print("</style>",file=FOUT)
        print("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">",file=FOUT)
        print("</head>",file=FOUT)
        print("<body>",file=FOUT)
        print("<table class=\"listing\"><tr><td class=\"header\"><pre>",file=FOUT)
      # print report header
      print("edat:      " + coverage_data.edat,file=FOUT)
      print("ecov:      " + coverage_data.ecov,file=FOUT)
      print("source:    " + coverage_data.source,file=FOUT)
      print("generated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),file=FOUT)
      print("",file=FOUT)

      if self.use_html:
        print("</pre></td></tr><tr><td class=\"listing\"><pre>",file=FOUT)
      else:
        print("=====",file=FOUT)
      # print listing data
      with open(source, "r") as FIN:
        for line in FIN:
          line_number += 1
          line = line.rstrip()
          line_data = "Line   #%0.6d|%s" % (line_number, line)

          if line_number in coverage_data.block_lines:
            label = coverage_data.block_lines[line_number]
            if coverage_data.blocks[label].isFullyCovered():
              line_data = re.sub("Line\s+","Line + ",line_data)
              if self.use_html:
                line_data = "<span class=\"block_hit\">" + line_data + "</span>"
            else:
              missed_list.append(str(coverage_data.blocks[label]))
              line_data = re.sub("Line\s+","Line * ",line_data)
              if self.use_html:
                line_data = "<span class=\"block_miss\">" + line_data + "</span>"

          print(line_data,file=FOUT)

          if line_number in coverage_data.entries_by_line:
            entries = coverage_data.entries_by_line[line_number]
            entries.sort(key=lambda entry: entry.column)
            for an_entry in entries:
              my_str = an_entry.to_string(is_py_src)
              if self.use_html:
                if "*" in my_str:
                  my_str = "<span class=\"failed\">" + my_str + "</span>"
                else:
                  my_str = "<span class=\"passed\">" + my_str + "</span>"
              print(my_str,file=FOUT)
              if not an_entry.isFullyCovered():
                missed_list.append(an_entry)
      if self.use_html:
        print("</pre></td></tr><tr><td class=\"summary\"><pre>",file=FOUT)
      else:
        print("=====",file=FOUT)
      print("",file=FOUT)
      # print the summary
      decision_data = "%0.5d/%0.5d" % (coverage_data.covered_decisions(), coverage_data.total_decisions())
      condition_data = "%0.5d/%0.5d" % (coverage_data.covered_conditions(), coverage_data.total_conditions())
      block_data = "%0.5d/%0.5d" % (coverage_data.covered_blocks(), coverage_data.total_blocks())

      if self.use_html:
        if coverage_data.covered_decisions() != coverage_data.total_decisions():
          decision_data = "<span class=\"summary_miss\">" + decision_data + "</span>"
        else:
          decision_data = "<span class=\"summary_pass\">" + decision_data + "</span>"
        if coverage_data.covered_conditions() != coverage_data.total_conditions():
          condition_data = "<span class=\"summary_miss\">" + condition_data + "</span>"
        else:
          condition_data = "<span class=\"summary_pass\">" + condition_data + "</span>"
        if coverage_data.covered_blocks() != coverage_data.total_blocks():
          block_data = "<span class=\"summary_miss\">" + block_data + "</span>"
        else:
          block_data = "<span class=\"summary_pass\">" + block_data + "</span>"

      print("Decisions:  " + decision_data,file=FOUT)
      print("Conditions: " + condition_data,file=FOUT)
      print("Blocks:     " + block_data,file=FOUT)
      print("",file=FOUT)
      # print missing entities (if any)
      if len(missed_list) == 0:
        print("All coverage obtained",file=FOUT)
      else:
        for elem in missed_list:
          my_str = str(elem)
          if "*/*" in my_str:
            my_str = "Missing ALL cases |" + my_str
          elif "*/" in my_str:
            my_str = "Missing T case    |" + my_str
          else:
            my_str = "Missing F case    |" + my_str
          my_str = re.sub("\|\s+\^", "", my_str)
          print(my_str,file=FOUT)

      if self.use_html:
        print("</pre></td></tr></table></body></html>",file=FOUT)

  # --
  def check(self, edat, ecov, source=None):
    # Create the coverage data, populate it and dump the report
    # assuming all 3 files have already been validated and exist
    coverage_data = CoverageData(edat,ecov,source)
    self.parse_edat(edat, coverage_data)
    self.parse_ecov(ecov, coverage_data)
    self.report(source, coverage_data)
# ==
if __name__ == "__main__":
  # The following operation modes need to be supported
  # #1) No arguments
  # Ex: ./east_report.py
  #   process all EDAT/ECOV files in the current directory
  # #2) Passed a name
  # Ex: ./east_report.py test
  #   Process only the EDAT and ECOV for the named file, path info taken from
  #   the EDAT
  # #3) Passed EDAT, ECOV, and SOURCE
  # Ex: ./east_report.py ../data/test.edat ../cov/test.ecov src/test/test.cpp
  #   Assume the ECOV is for the EDAT, which contains the info for SOURCE
  # All modes name the report after the EDAT file processed
  #
  # Additional options:
  # --html
  #   Generate reports in HTML
  report = Report()
  if len(sys.argv) > 1:
    args = sys.argv[1:]
    if "-html" in args:
      report.useHTML()
      args.remove("-html")
    if len(args) == 0:
      report.check_all()
    elif len(args) == 1:
      the_file = args[0]
      if os.path.isdir(the_file):
        report.check_all(the_file)
      else:
        report.check_file(
          os.path.abspath(the_file)
        )
    elif len(args) == 3:
      report.check(
        os.path.abspath(args[0]),
        os.path.abspath(args[1]),
        os.path.abspath(args[2])
      )
    else:
      print("Unknown arguments list encountered...exiting", file=sys.stderr)
      print(args)
  else:
    report.check_all()
