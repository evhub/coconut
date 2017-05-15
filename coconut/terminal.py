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
import time
from contextlib import contextmanager

from pyparsing import lineno, col, ParserElement
if DEVELOP:
    from pyparsing import _trim_arity

from coconut.constants import (
    info_tabulation,
    main_sig,
    taberrfmt,
    use_packrat,
)
from coconut.exceptions import (
    CoconutWarning,
    CoconutInternalException,
    CoconutException,
    debug_clean,
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
    """Raises in develop; warns in release."""
    if DEVELOP:
        raise error
    else:
        logger.warn_err(error)


#-----------------------------------------------------------------------------------------------------------------------
# logger:
#-----------------------------------------------------------------------------------------------------------------------


class Logger(object):
    """Container object for various logger functions and variables."""
    verbose = False
    quiet = False
    tracing = False
    path = None
    name = None

    def __init__(self, other=None):
        """Create a logger, optionally from another logger."""
        if other is not None:
            self.copy_from(other)
        self.patch_logging()

    def copy_from(self, other):
        """Copy other onto self."""
        self.verbose, self.quiet, self.path, self.name, self.tracing = other.verbose, other.quiet, other.path, other.name, other.tracing

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
            printerr(*messages)

    def log_show(self, *messages):
        """Logs debug messages with main signature."""
        if self.verbose:
            self.display(messages, main_sig, debug=True)

    def log_vars(self, message, variables, rem_vars=("self",)):
        """Logs variables with given message."""
        if self.verbose:
            new_vars = dict(variables)
            for v in rem_vars:
                del new_vars[v]
            printerr(message, new_vars)

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

    def warn(self, *args, **kwargs):
        """Creates and displays a warning."""
        return self.warn_err(CoconutWarning(*args, **kwargs))

    def warn_err(self, warning):
        """Displays a warning."""
        try:
            raise warning
        except Exception:
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
            printerr(errmsg)

    def log_cmd(self, args):
        """Logs a console command if in verbose mode."""
        self.log("> " + " ".join(args))

    def show_tabulated(self, begin, middle, end):
        """Shows a tabulated message."""
        if len(begin) < info_tabulation:
            self.show(begin + " " * (info_tabulation - len(begin)) + middle + " " + end)
        else:
            raise CoconutInternalException("info message too long", begin)

    def log_tag(self, tag, code, multiline=False):
        """Logs a tagged message if tracing."""
        if self.tracing:
            tagstr = "[" + str(tag) + "]"
            if multiline:
                printerr(tagstr + "\n" + debug_clean(code))
            else:
                printerr(tagstr, ascii(code))

    def log_trace(self, tag, original, loc, tokens=None):
        """Formats and displays a trace if tracing."""
        if self.tracing:
            original = str(original)
            loc = int(loc)
            tag = str(tag)
            if " " in tag:
                tag = "..."
            out = ["[" + tag + "]"]
            if tokens is not None:
                if not isinstance(tokens, Exception) and len(tokens) == 1 and isinstance(tokens[0], str):
                    out.append(ascii(tokens[0]))
                else:
                    out.append(str(tokens))
            out.append("(line " + str(lineno(loc, original)) + ", col " + str(col(loc, original)) + ")")
            printerr(*out)

    def _trace_start_action(self, original, loc, expr):
        self.log_trace(expr, original, loc)

    def _trace_success_action(self, original, start_loc, end_loc, expr, tokens):
        self.log_trace(expr, original, start_loc, tokens)

    def _trace_exc_action(self, original, loc, expr, exc):
        self.log_trace(expr, original, loc, exc)

    def trace(self, item):
        """Traces a parse element (only enabled in develop)."""
        if DEVELOP:
            item = item.setDebugActions(
                self._trace_start_action,
                self._trace_success_action,
                self._trace_exc_action,
            )
        return item

    def wrap_handler(self, handler):
        """Wraps a handler to catch errors (only enabled in develop)."""
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

    @contextmanager
    def gather_parsing_stats(self):
        """Times parsing if in verbose mode."""
        if self.verbose:
            start_time = time.clock()
            try:
                yield
            finally:
                elapsed_time = time.clock() - start_time
                printerr("Time while parsing:", elapsed_time, "seconds")
                if use_packrat:
                    hits, misses = ParserElement.packrat_cache_stats
                    printerr("Packrat parsing stats:", hits, "hits;", misses, "misses")
        else:
            yield

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
        printerr(self.name, args, kwargs, traceback.format_exc())
    debug = info = warning = error = critical = exception = pylog


#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

logger = Logger()

trace = logger.trace
