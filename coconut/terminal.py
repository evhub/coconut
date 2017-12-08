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
import logging
import time
from contextlib import contextmanager

from coconut.pyparsing import (
    lineno,
    col,
    ParserElement,
)

from coconut.constants import (
    info_tabulation,
    main_sig,
    taberrfmt,
    packrat_cache,
)
from coconut.exceptions import (
    CoconutWarning,
    displayable,
    internal_assert,
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
        err_parts = "".join(traceback.format_exception_only(err_type, err_value)).strip().split(": ", 1)
        if len(err_parts) == 1:
            err_name, err_msg = err_parts[0], ""
        else:
            err_name, err_msg = err_parts
        err_name = err_name.split(".")[-1]
        return err_name + ": " + err_msg
    else:
        return "".join(traceback.format_exception(err_type, err_value, err_trace)).strip()


def complain(error):
    """Raises in develop; warns in release."""
    if callable(error):
        if DEVELOP:
            raise error()
    elif DEVELOP:
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
        if not full_message:
            full_message = sig.rstrip()
        if debug:
            printerr(full_message)
        else:
            print(full_message)

    def show(self, *messages):
        """Prints messages if not --quiet."""
        if not self.quiet:
            self.display(messages)

    def show_sig(self, *messages):
        """Prints messages with main signature if not --quiet."""
        if not self.quiet:
            self.display(messages, main_sig)

    def show_error(self, *messages):
        """Prints error messages with main signature if not --quiet."""
        if not self.quiet:
            self.display(messages, main_sig, debug=True)

    def log(self, *messages):
        """Logs debug messages if --verbose."""
        if self.verbose:
            printerr(*messages)

    def log_prefix(self, prefix, *messages):
        """Logs debug messages with the given signature if --verbose."""
        if self.verbose:
            self.display(messages, prefix, debug=True)

    def log_sig(self, *messages):
        """Logs debug messages with the main signature if --verbose."""
        self.log_prefix(main_sig, *messages)

    def log_vars(self, message, variables, rem_vars=("self",)):
        """Logs variables with given message if --verbose."""
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
                self.display_exc()

    def display_exc(self):
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

    def log_exc(self):
        """Display an exception only if --verbose."""
        if self.verbose:
            self.display_exc()

    def log_cmd(self, args):
        """Logs a console command if --verbose."""
        self.log("> " + " ".join(args))

    def show_tabulated(self, begin, middle, end):
        """Shows a tabulated message."""
        internal_assert(len(begin) < info_tabulation, "info message too long", begin)
        self.show(begin + " " * (info_tabulation - len(begin)) + middle + " " + end)

    def log_tag(self, tag, code, multiline=False):
        """Logs a tagged message if tracing."""
        if self.tracing:
            if callable(code):
                code = code()
            tagstr = "[" + str(tag) + "]"
            if multiline:
                printerr(tagstr + "\n" + displayable(code))
            else:
                printerr(tagstr, ascii(code))

    def log_trace(self, tag, original, loc, tokens=None, extra=None):
        """Formats and displays a trace if tracing."""
        if self.tracing:
            tag, original, loc = displayable(tag), displayable(original), int(loc)
            if "{" not in tag:
                out = ["[" + tag + "]"]
                add_line_col = True
                if tokens is not None:
                    if isinstance(tokens, Exception):
                        msg = displayable(str(tokens))
                        if "{" in msg:
                            head, middle = msg.split("{", 1)
                            middle, tail = middle.rsplit("}", 1)
                            msg = head + "{...}" + tail
                        out.append(msg)
                        add_line_col = False
                    elif len(tokens) == 1 and isinstance(tokens[0], str):
                        out.append(ascii(tokens[0]))
                    else:
                        out.append(ascii(tokens))
                if add_line_col:
                    out.append("(line:" + str(lineno(loc, original)) + ", col:" + str(col(loc, original)) + ")")
                if extra is not None:
                    out.append("from " + ascii(extra))
                printerr(*out)

    def _trace_success_action(self, original, start_loc, end_loc, expr, tokens):
        self.log_trace(expr, original, start_loc, tokens)

    def _trace_exc_action(self, original, loc, expr, exc):
        self.log_trace(expr, original, loc, exc)

    def trace(self, item):
        """Traces a parse element (only enabled in develop)."""
        if DEVELOP:
            item.debugActions = (
                None,  # no start action
                self._trace_success_action,
                self._trace_exc_action,
            )
            item.debug = True
        return item

    @contextmanager
    def gather_parsing_stats(self):
        """Times parsing if --verbose."""
        if self.verbose:
            start_time = time.clock()
            try:
                yield
            finally:
                elapsed_time = time.clock() - start_time
                printerr("Time while parsing:", elapsed_time, "seconds")
                if packrat_cache:
                    hits, misses = ParserElement.packrat_cache_stats
                    printerr("Packrat parsing stats:", hits, "hits;", misses, "misses")
        else:
            yield

    def patch_logging(self):
        """Patches built-in Python logging if necessary."""
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
