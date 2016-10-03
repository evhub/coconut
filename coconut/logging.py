#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from coconut.root import *  # NOQA

import sys
import traceback
import functools
import logging
from contextlib import contextmanager

from pyparsing import lineno, col
if DEVELOP:
    from pyparsing import _trim_arity

from coconut.constants import (
    info_tabulation,
    main_sig,
    taberrfmt,
)
from coconut.exceptions import (
    CoconutWarning,
    CoconutInternalException,
    CoconutException,
    clean,
)

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
    name = None

    def __init__(self, other=None):
        """Create a logger, optionally from another logger."""
        if other is not None:
            self.copy_from(other)
        self.patch_logging()

    def copy_from(self, other):
        """Copy other onto self."""
        self.verbose, self.quiet, self.path, self.name = other.verbose, other.quiet, other.path, other.name

    def display(self, messages, sig="", debug=False):
        """Prints an iterator of messages."""
        full_message = "".join(
            sig + line for line in " ".join(
                str(msg) for msg in messages
            ).splitlines(True)
        )
        if debug is True:
            printerr(full_message)
        else:
            print(full_message)

    def print(self, *messages):
        """Prints messages."""
        self.display(messages)

    def printerr(self, *messages):
        """Prints error messages with debug signature."""
        self.display(messages, debug=True)

    def show(self, *messages):
        """Prints messages with main signature."""
        if not self.quiet:
            self.display(messages, main_sig)

    def show_error(self, *messages):
        """Prints error messages with main signature."""
        if not self.quiet:
            self.display(messages, main_sig, debug=True)

    def log(self, *messages):
        """Logs debug messages if in verbose mode."""
        if self.verbose:
            self.printerr(*messages)

    def log_show(self, *messages):
        """Logs debug messages with main signature."""
        if self.verbose:
            self.display(messages, main_sig, debug=True)

    def get_error(self):
        """Properly formats the current error."""
        exc_info = sys.exc_info()
        if exc_info[0] is None:
            return None
        else:
            err_type, err_value, err_trace = exc_info[0], exc_info[1], None
            if self.verbose and len(exc_info) > 2:
                err_trace = exc_info[2]
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
        if errmsg is not None:
            if self.path is not None:
                errmsg_lines = ["in " + self.path + ":"]
                for line in errmsg.splitlines():
                    if line:
                        line = " " * taberrfmt + line
                    errmsg_lines.append(line)
                errmsg = "\n".join(errmsg_lines)
            self.printerr(errmsg)

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
            self.show(begin + " " * (info_tabulation - len(begin)) + middle + " " + end)
        else:
            raise CoconutInternalException("info message too long", begin)

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
            out += " (line " + str(lineno(location, original)) + ", col " + str(col(location, original)) + ")"
            self.printerr(out)

    def trace(self, item, tag):
        """Traces a parse element."""
        if DEVELOP:
            def trace_action(original, location, tokens):
                """Callback function constructed by tracer."""
                self.log_trace(tag, original, location, tokens)
            item = item.addParseAction(trace_action)
        return item.setName(tag)

    def wrap_handler(self, handler):
        """Wraps a handler to catch errors in verbose mode (only enabled in develop)."""
        if DEVELOP and handler.__name__ not in ("<lambda>", "join"):  # not addspace, condense, or fixto
            @functools.wraps(handler)
            def wrapped_handler(s, l, t):
                self.log_trace(handler.__name__, s, l, t)
                try:
                    return _trim_arity(handler)(s, l, t)
                except CoconutException:
                    raise
                except Exception:
                    traceback.print_exc()
                    raise CoconutInternalException("error calling handler " + handler.__name__ + " with tokens", t)
            return wrapped_handler
        else:
            return handler

    def patch_logging(self):
        """Patches built-in Python logging."""
        if not hasattr(logging, "getLogger"):
            def getLogger(name=None):
                other = Logger(self)
                if name is not None:
                    other.name = name
                return other
            logging.getLogger = getLogger

    def pylog(self, *args, **kwargs):
        """Display all available logging information."""
        self.printerr(self.name, args, kwargs, traceback.format_exc())
    debug = info = warning = error = critical = exception = pylog

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

logger = Logger()

trace = logger.trace
