# package: East
A suite of unit testing tools and classes for test development.

## License (ISC)
```
Copyright (c) 2017, Arthur Gardiner

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
```

## Source Code
[East GitHub Repo](https://github.com/new32/east_py)

## Installation
East only requires a standard Python3(.5+) installation and is not tied to any
particular location. As such, installation can be done using either the
`setup.py` script to install into a global location or the 'East'
folder can be copied into  `$HOME/.local/lib/python3.5/site-packages` for local
(per user) installation.

## Usage

### East.Test
Subclasses of this library are used to actually setup and run unittests. Test
suites are simply methods of the subclass. To execute, add the test suites using
the `add(suite)` and then call the subclass's `run()` method.

#### Results
By default, the script name is used, appending "_rpt.txt". The test author can
always specify a different file. The format is documented by `East/Test.py`.

### East.Instrument
This program instruments a named library, adding condition, decision and basic
block coverage, compiling the the modified AST into bytecode. To use the
instrumented AST, simply import the library like normal into the test driver.

#### Results
The initial instrumentation creates .edat in the current directory,
which contains the listing of instrumented items. When executing the
instrumented file, .ecov stores all the coverage obtained by the run.
As the file is appended to, coverage can be captured in subsequent runs.

### East.Report
Merges the .edat and .ecov files into either a single report. The format is
documented by `East/Report.py`.

#### Results
Either a text report, script.py_cov.txt, or the HTML equivalent.

## Example
A complete example of using and running the tools is provided in the 'Examples/'
directory of the github distribution
