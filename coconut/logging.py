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
    path = None

    def copy_from(self, other):
        """Copy other onto self."""
        self.verbose, self.quiet, self.path = other.verbose, other.quiet, other.path

    def display(self, messages, sig="", debug=False):
        """Prints an iterator of messages."""
        full_message = " ".join(str(msg) for msg in messages)
        if debug is True:
            printerr(full_message)
        else:
            print(full_message)

    def print(self, *messages):
        """Prints messages."""
        self.display(messages)

    def printerr(self, *messages):
        """Prints error messages with debug signature."""
        self.display(messages, debug_sig, True)

    def show(self, *messages):
        """Prints messages with main signature."""
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
            if not self.quiet:
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
