#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: Utility functions for the main command module.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

import os
import traceback

from coconut.constants import default_encoding
from coconut.logger import logging

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------

def openfile(filename, opentype="r+"):
    """Returns an open file object."""
    return open(filename, opentype, encoding=default_encoding) # using open from coconut.root

def writefile(openedfile, newcontents):
    """Sets the contents of a file."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(newcontents)

def readfile(openedfile):
    """Reads the contents of a file."""
    openedfile.seek(0)
    return str(openedfile.read())

def fixpath(path):
    """Uniformly formats a path."""
    return os.path.normpath(os.path.realpath(path))

def showpath(path):
    """Formats a path for displaying."""
    if logging.verbose:
        return os.path.abspath(path)
    else:
        return os.path.basename(path)

def rem_encoding(code):
    """Removes encoding declarations from Python code so it can be passed to exec."""
    old_lines = code.splitlines()
    new_lines = []
    for i in range(min(2, len(old_lines))):
        line = old_lines[i]
        if not (line.startswith("#") and "coding" in line):
            new_lines.append(line)
    new_lines += old_lines[2:]
    return "\n".join(new_lines)

def try_eval(code, in_vars):
    """Try to evaluate the given code, otherwise execute it."""
    try:
        return eval(code, in_vars)
    except SyntaxError:
        pass # exit the exception context before executing code
    exec(code, in_vars)
    return None

def escape_color(code):
    """Generates an ANSII color code."""
    return "\033[" + str(code) + "m"

#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------

class Runner(object):
    """Compiled Python executor."""
    def __init__(self, proc=None, exit=None, path=None):
        """Creates the executor."""
        self.exit = exit
        self.vars = {"__name__": "__main__"}
        if path is not None:
            self.vars["__file__"] = fixpath(path)
        if proc is not None:
            self.run(proc.headers("code"))
            self.fixpickle()

    def fixpickle(self):
        """Fixes pickling of Coconut header objects."""
        from coconut import __coconut__
        for var in self.vars:
            if not var.startswith("__") and var in dir(__coconut__):
                self.vars[var] = getattr(__coconut__, var)

    def run(self, code, err=False, run_func=None):
        """Executes Python code."""
        try:
            if run_func is None:
                exec(code, self.vars)
            else:
                return run_func(code, self.vars)
        except (Exception, KeyboardInterrupt):
            if err:
                raise
            else:
                traceback.print_exc()
        except SystemExit:
            if self.exit is None:
                raise
            else:
                self.exit()
        return None
