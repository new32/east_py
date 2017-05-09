#!/usr/bin/env python3

# If you want to leave this as portable, don't bother with setup and simply
# copy the East folder to $HOME/.local/lib/python3.{rev}/site-packages
# where {rev} is your installed version

from distutils.core import setup

setup(
  name = "East",
  packages = ['East'],
  version = "20170500",
  author = "Arthur Gardiner",
  author_email = "newbie32@gmail.com",
  url = "https://github.com/new32/east_py",
  description = "East Unit Testing Tools",
  long_description = """
  East unit testing tools contains the following programs:
    East.Instrument - Instrument the AST for condition and decision coverage
                      and compile the modified AST
    East.Report - Convert the *.ecov and *.edat into a single report
  and the following test tool:
    East.Test - Subclass to create test drivers
""",
  keywords = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Environment :: Console",
    "License :: OSI Approved :: ISC License (ISCL)",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Software Development :: Testing",
  ]
)
