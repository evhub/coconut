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

from coconut.const import default_encoding, color_codes, end_color_code
from coconut.compiler.exceptions import printerr

import os

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------


def openfile(filename, opentype="r+"):
    """Returns an open file object."""
    return open(filename, opentype, encoding=default_encoding) # using open from .root

def writefile(openedfile, newcontents):
    """Sets the contents of a file."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(newcontents)

def readfile(openedfile):
    """Reads the contents of a file."""
    openedfile.seek(0)
    return str(openedfile.read())

def showpath(path):
    """Formats a path for displaying."""
    return os.path.basename(path)

def fixpath(path):
    """Uniformly formats a path."""
    return os.path.normpath(os.path.realpath(path))

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

class Console(object):
    """Manages printing and reading data to the console."""
    color_code = None
    on = True

    def __init__(self, main_sig="", debug_sig=""):
        """Creates the console."""
        self.main_sig, self.debug_sig = main_sig, debug_sig

    def set_color(self, color=None):
        """Set output color."""
        if color:
            color = color.replace("_", "")
            if color in color_codes:
                self.color_code = color_codes[color]
            else:
                try:
                    color = int(color)
                except ValueError:
                    raise CoconutException('unrecognized color "'+color+'" (enter a valid color name or code)')
                else:
                    if 0 < color <= 256:
                        self.color_code = color
                    else:
                        raise CoconutException('color code '+str(color)+' out of range (must obey 0 < color code <= 256)')
        else:
            self.color_code = None

    def add_color(self, inputstring):
        """Adds the specified color to the string."""
        if self.color_code is None:
            return inputstring
        else:
            return escape_color(self.color_code) + inputstring + escape_color(end_color_code)

    def display(self, messages, sig="", debug=False):
        """Prints messages."""
        if self.on:
            message = " ".join(str(msg) for msg in messages)
            for line in message.splitlines():
                msg = self.add_color(sig + line)
                if debug is True:
                    printerr(msg)
                else:
                    print(msg)

    def print(self, *messages):
        """Prints messages with color."""
        self.display(messages)

    def printerr(self, *messages):
        """Prints error messages with color and debug signature."""
        self.display(messages, self.debug_sig, True)

    def show(self, *messages):
        """Prints messages with color and main signature."""
        self.display(messages, self.main_sig)