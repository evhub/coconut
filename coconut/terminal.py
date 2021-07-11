#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: logger utilities.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import traceback
import logging
import time
from contextlib import contextmanager

from coconut import embed
from coconut.root import _indent
from coconut._pyparsing import (
    lineno,
    col,
    ParserElement,
)

from coconut.constants import (
    info_tabulation,
    main_sig,
    taberrfmt,
    packrat_cache,
    embed_on_internal_exc,
)
from coconut.util import printerr
from coconut.exceptions import (
    CoconutWarning,
    CoconutException,
    CoconutInternalException,
    displayable,
)

# -----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------------------------------------------------


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
            error = error()
        else:
            return
    if not isinstance(error, CoconutInternalException) and isinstance(error, CoconutException):
        error = CoconutInternalException(str(error))
    if not DEVELOP:
        logger.warn_err(error)
    elif embed_on_internal_exc:
        logger.warn_err(error)
        embed(depth=1)
    else:
        raise error


def internal_assert(condition, message=None, item=None, extra=None):
    """Raise InternalException if condition is False. Execute functions on DEVELOP only."""
    if DEVELOP and callable(condition):
        condition = condition()
    if not condition:
        if message is None:
            message = "assertion failed"
            if item is None:
                item = condition
        elif callable(message):
            message = message()
        if callable(extra):
            extra = extra()
        error = CoconutInternalException(message, item, extra)
        if embed_on_internal_exc:
            logger.warn_err(error)
            embed(depth=1)
        else:
            raise error


def get_name(expr):
    """Get the name of an expression for displaying."""
    name = expr if isinstance(expr, str) else None
    if name is None:
        name = getattr(expr, "name", None)
    if name is None:
        name = displayable(expr)
    return name


def get_clock_time():
    """Get a time to use for performance metrics."""
    if PY2:
        return time.clock()
    else:
        return time.process_time()


# -----------------------------------------------------------------------------------------------------------------------
# logger:
# -----------------------------------------------------------------------------------------------------------------------


class Logger(object):
    """Container object for various logger functions and variables."""
    verbose = False
    quiet = False
    path = None
    name = None
    tracing = False
    trace_ind = 0

    def __init__(self, other=None):
        """Create a logger, optionally from another logger."""
        if other is not None:
            self.copy_from(other)
        self.patch_logging()

    def copy_from(self, other):
        """Copy other onto self."""
        self.verbose, self.quiet, self.path, self.name, self.tracing, self.trace_ind = other.verbose, other.quiet, other.path, other.name, other.tracing, other.trace_ind

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

    def log_func(self, func):
        """Calls a function and logs the results if --verbose."""
        if self.verbose:
            to_log = func()
            if isinstance(to_log, tuple):
                printerr(*to_log)
            else:
                printerr(to_log)

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

    def get_error(self, err=None):
        """Properly formats the current error."""
        if err is None:
            exc_info = sys.exc_info()
        else:
            exc_info = type(err), err, err.__traceback__

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

    def warn_err(self, warning, force=False):
        """Displays a warning."""
        if not self.quiet or force:
            try:
                raise warning
            except Exception:
                self.display_exc()

    def display_exc(self, err=None):
        """Properly prints an exception in the exception context."""
        errmsg = self.get_error(err)
        if errmsg is not None:
            if self.path is not None:
                errmsg_lines = ["in " + self.path + ":"]
                for line in errmsg.splitlines():
                    if line:
                        line = " " * taberrfmt + line
                    errmsg_lines.append(line)
                errmsg = "\n".join(errmsg_lines)
            printerr(errmsg)

    def log_exc(self, err=None):
        """Display an exception only if --verbose."""
        if self.verbose:
            self.display_exc(err)

    def log_cmd(self, args):
        """Logs a console command if --verbose."""
        self.log("> " + " ".join(args))

    def show_tabulated(self, begin, middle, end):
        """Shows a tabulated message."""
        internal_assert(len(begin) < info_tabulation, "info message too long", begin)
        self.show(begin + " " * (info_tabulation - len(begin)) + middle + " " + end)

    @contextmanager
    def indent_tracing(self):
        """Indent wrapped tracing."""
        self.trace_ind += 1
        try:
            yield
        finally:
            self.trace_ind -= 1

    def print_trace(self, *args):
        """Print to stderr with tracing indent."""
        trace = " ".join(str(arg) for arg in args)
        printerr(_indent(trace, self.trace_ind))

    def log_tag(self, tag, code, multiline=False):
        """Logs a tagged message if tracing."""
        if self.tracing:
            if callable(code):
                code = code()
            tagstr = "[" + str(tag) + "]"
            if multiline:
                self.print_trace(tagstr + "\n" + displayable(code))
            else:
                self.print_trace(tagstr, ascii(code))

    def log_trace(self, expr, original, loc, item=None, extra=None):
        """Formats and displays a trace if tracing."""
        if self.tracing:
            tag = get_name(expr)
            original = displayable(original)
            loc = int(loc)
            if "{" not in tag:
                out = ["[" + tag + "]"]
                add_line_col = True
                if item is not None:
                    if isinstance(item, Exception):
                        msg = displayable(str(item))
                        if "{" in msg:
                            head, middle = msg.split("{", 1)
                            middle, tail = middle.rsplit("}", 1)
                            msg = head + "{...}" + tail
                        out.append(msg)
                        add_line_col = False
                    elif len(item) == 1 and isinstance(item[0], str):
                        out.append(ascii(item[0]))
                    else:
                        out.append(ascii(item))
                if add_line_col:
                    out.append("(line:" + str(lineno(loc, original)) + ", col:" + str(col(loc, original)) + ")")
                if extra is not None:
                    out.append("from " + ascii(extra))
                self.print_trace(*out)

    def _trace_success_action(self, original, start_loc, end_loc, expr, tokens):
        if self.verbose:
            self.log_trace(expr, original, start_loc, tokens)

    def _trace_exc_action(self, original, loc, expr, exc):
        if self.tracing:  # avoid the overhead of an extra function call
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
            start_time = get_clock_time()
            try:
                yield
            finally:
                elapsed_time = get_clock_time() - start_time
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


# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------

logger = Logger()

trace = logger.trace
