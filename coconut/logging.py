#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: logger utilities.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

import sys
import os
import traceback
from contextlib import contextmanager

from pyparsing import lineno, col

from coconut.constants import (
    default_encoding,
    color_codes,
    end_color_code,
    info_tabulation,
    main_sig,
    debug_sig,
    taberrfmt,
)
from coconut.exceptions import CoconutException, CoconutWarning, clean

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------

def printerr(*args):
    """Prints to standard error."""
    print(*args, file=sys.stderr)

def format_error(err_type, err_value, err_trace=None):
    """Properly formats the specified error."""
    if err_trace is None:
        err_name, err_msg = "".join(traceback.format_exception_only(err_type, err_value)).strip().split(": ", 1)
        err_name = err_name.split(".")[-1]
        return err_name + ": " + err_msg
    else:
        return "".join(traceback.format_exception(err_type, err_value, err_trace)).strip()

def escape_color(code):
    """Generates an ANSII color code."""
    return "\033[" + str(code) + "m"

def complain(error):
    """Raises an error in DEVELOP, otherwise does nothing."""
    if DEVELOP:
        raise error

#-----------------------------------------------------------------------------------------------------------------------
# logger:
#-----------------------------------------------------------------------------------------------------------------------

class Logger(object):
    """Container object for various logger functions and variables."""
    verbose = False
    quiet = False
    color_code = None
    path = None

    def copy_from(self, other):
        """Copy other onto self."""
        self.verbose, self.quiet, self.color_code, self.path = other.verbose, other.quiet, other.color_code, other.path

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
        """Prints an iterator of messages with color."""
        full_message = " ".join(str(msg) for msg in messages)
        print_lines = []
        for line in full_message.splitlines():
            line = sig + line
            if line:
                line = self.add_color(line)
            print_lines.append(line)
        print_message = "\n".join(print_lines)
        if debug is True:
            printerr(print_message)
        else:
            print(print_message)

    def print(self, *messages):
        """Prints messages with color."""
        self.display(messages)

    def printerr(self, *messages):
        """Prints error messages with color and debug signature."""
        self.display(messages, debug_sig, True)

    def show(self, *messages):
        """Prints messages with color and main signature."""
        if not self.quiet:
            self.display(messages, main_sig)

    def get_error(self):
        """Properly formats the current error."""
        err_type, err_value, err_trace = sys.exc_info()
        if not self.verbose:
            err_trace = None
        return format_error(err_type, err_value, err_trace)

    @contextmanager
    def in_path(self, new_path, old_path=None):
        """Temporarily enters a path."""
        self.path = new_path
        try:
            yield
        finally:
            self.path = old_path

    def warn(self, warning):
        """Displays a warning."""
        try:
            raise warning
        except CoconutWarning:
            self.print_exc()

    def print_exc(self):
        """Properly prints an exception in the exception context."""
        errmsg = self.get_error()
        if self.path is not None:
            errmsg_lines = ["in " + self.path + ":"]
            for line in errmsg.splitlines():
                if line:
                    line = " "*taberrfmt + line
                errmsg_lines.append(line)
            errmsg = "\n".join(errmsg_lines)
        self.printerr(errmsg)

    def log(self, msg):
        """Logs a debug message if in verbose mode."""
        if self.verbose:
            self.printerr(msg)

    def log_tag(self, tag, code, multiline=False):
        """Logs a tagged message if in verbose mode."""
        if multiline:
            self.log("[" + str(tag) + "]\n" + clean(code, rem_indents=False, encoding_errors="backslashreplace"))
        else:
            self.log("[" + str(tag) + "] " + ascii(code))

    def log_cmd(self, args):
        """Logs a console command if in verbose mode."""
        self.log("> " + " ".join(args))

    def show_tabulated(self, begin, middle, end):
        """Shows a tabulated message."""
        if len(begin) < info_tabulation:
            self.show(begin + " "*(info_tabulation - len(begin)) + middle + " " + end)
        else:
            raise CoconutException("info message too long", begin)

    def log_trace(self, tag, original, location, tokens):
        """Formats and displays a trace."""
        if self.verbose:
            original = str(original)
            location = int(location)
            out = "[" + tag + "] "
            if len(tokens) == 1 and isinstance(tokens[0], str):
                out += ascii(tokens[0])
            else:
                out += str(tokens)
            out += " (line "+str(lineno(location, original))+", col "+str(col(location, original))+")"
            self.printerr(out)

    def trace(self, item, tag):
        """Traces a parse element."""
        def trace_action(original, location, tokens):
            """Callback function constructed by tracer."""
            self.log_trace(tag, original, location, tokens)
        return item.addParseAction(trace_action).setName(tag)

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

logger = Logger()
trace = logger.trace
