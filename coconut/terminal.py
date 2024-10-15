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
import os
import traceback
import logging
from contextlib import contextmanager
from collections import defaultdict
from functools import wraps
if sys.version_info < (2, 7):
    from StringIO import StringIO
else:
    from io import StringIO

from coconut._pyparsing import (
    MODERN_PYPARSING,
    lineno,
    col,
    ParserElement,
    maybe_make_safe,
)

from coconut.root import _indent
from coconut.integrations import embed
from coconut.constants import (
    info_tabulation,
    main_sig,
    taberrfmt,
    use_packrat_parser,
    embed_on_internal_exc,
    use_color_env_var,
    get_bool_env_var,
    error_color_code,
    log_color_code,
    ansii_escape,
    force_verbose_logger,
    max_orig_lines_in_log_loc,
)
from coconut.util import (
    get_clock_time,
    get_name,
    displayable,
    first_import_time,
    assert_remove_prefix,
    split_trailing_whitespace,
)
from coconut.exceptions import (
    CoconutWarning,
    CoconutException,
    CoconutInternalException,
)


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------

ansii_reset = ansii_escape + "[0m"


def isatty(stream, default=None):
    """Check if a stream is a terminal interface."""
    try:
        return stream.isatty()
    except Exception:
        logger.log_exc()
    return default


def format_error(err_value, err_type=None, err_trace=None):
    """Properly formats the specified error."""
    if err_type is None:
        err_type = err_value.__class__
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


def complain(error_or_msg, *args, **kwargs):
    """Raises in develop; warns in release."""
    if callable(error_or_msg):
        if DEVELOP:
            error_or_msg = error_or_msg()
        else:
            return
    if not isinstance(error_or_msg, BaseException) or (not isinstance(error_or_msg, CoconutInternalException) and isinstance(error_or_msg, CoconutException)):
        error_or_msg = CoconutInternalException(str(error_or_msg), *args, **kwargs)
    else:
        internal_assert(not args and not kwargs, "if error_or_msg is an error, args and kwargs must be empty, not", (args, kwargs))
    if not DEVELOP:
        logger.warn_err(error_or_msg)
    elif embed_on_internal_exc:
        logger.warn_err(error_or_msg)
        embed(depth=1)
    else:
        raise error_or_msg


def internal_assert(condition, message=None, item=None, extra=None, exc_maker=None):
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
        # ensure the item is pickleable so that the exception can be transferred back across processes
        item = str(item)
        if callable(extra):
            extra = extra()
        if exc_maker is None:
            error = CoconutInternalException(message, item, extra)
        else:
            error = exc_maker(message, item, extra)
        if embed_on_internal_exc:
            logger.warn_err(error)
            embed(depth=1)
        else:
            raise error


class LoggingStringIO(StringIO):
    """StringIO that logs whenever it's written to."""

    def __init__(self, log_to=None, prefix=""):
        """Initialize the buffer."""
        super(LoggingStringIO, self).__init__()
        self.log_to = log_to or sys.stderr
        self.prefix = prefix

    def write(self, s):
        """Write to the buffer."""
        super(LoggingStringIO, self).write(s)
        self.log(s)

    def writelines(self, lines):
        """Write lines to the buffer."""
        super(LoggingStringIO, self).writelines(lines)
        self.log("".join(lines))

    def log(self, *args):
        """Log the buffer."""
        with self.logging():
            logger.display(args, self.prefix, end="")

    @contextmanager
    def logging(self):
        if self.log_to:
            old_stdout, sys.stdout = sys.stdout, self.log_to
        try:
            yield
        finally:
            if self.log_to:
                sys.stdout = old_stdout


def should_use_color(file=None):
    """Determine if colors should be used for the given file object."""
    use_color = get_bool_env_var(use_color_env_var, default=None)
    if use_color is None:
        use_color = get_bool_env_var("PYTHON_COLORS", default=None)
    if use_color is not None:
        return use_color
    if get_bool_env_var("NO_COLOR"):
        return False
    if get_bool_env_var("FORCE_COLOR") or get_bool_env_var("CLICOLOR_FORCE"):
        return True
    return file is not None and isatty(file)


# -----------------------------------------------------------------------------------------------------------------------
# LOGGER:
# -----------------------------------------------------------------------------------------------------------------------

class Logger(object):
    """Container object for various logger functions and variables."""
    force_verbose = force_verbose_logger
    colors_enabled = False

    verbose = force_verbose
    quiet = False
    path = None
    name = None
    tracing = False
    trace_ind = 0

    recorded_stats = defaultdict(lambda: [0, 0])

    def __init__(self, other=None):
        """Create a logger, optionally from another logger."""
        if other is not None:
            self.copy_from(other)
        self.patch_logging()

    @classmethod
    def enable_colors(cls, file=None):
        """Attempt to enable CLI colors."""
        if not should_use_color(file):
            return False
        if not cls.colors_enabled:
            # necessary to resolve https://bugs.python.org/issue40134
            try:
                os.system("")
            except BaseException:
                logger.log_exc()
            cls.colors_enabled = True
        return True

    def copy_from(self, other):
        """Copy other onto self."""
        self.verbose, self.quiet, self.path, self.name, self.tracing, self.trace_ind = other.verbose, other.quiet, other.path, other.name, other.tracing, other.trace_ind

    def reset(self):
        """Completely reset the logger."""
        self.copy_from(Logger())

    def copy(self):
        """Make a copy of the logger."""
        return Logger(self)

    def setup(self, quiet=None, verbose=None, tracing=None):
        """Set up the logger with the given parameters."""
        if quiet is not None:
            self.quiet = quiet
        if not self.force_verbose and verbose is not None:
            self.verbose = verbose
        if tracing is not None:
            self.tracing = tracing
        ParserElement.verbose_stacktrace = self.verbose

    def display(
        self,
        messages,
        sig="",
        end="\n",
        file=None,
        level="normal",
        color=None,
        # flush by default to ensure our messages show up when printing from a child process
        flush=True,
        **kwargs
    ):
        """Prints an iterator of messages."""
        if level == "normal":
            file = file or sys.stdout
        elif level == "logging":
            file = file or sys.stderr
            if color is None:
                color = log_color_code
        elif level == "error":
            file = file or sys.stderr
            if color is None:
                color = error_color_code
        else:
            raise CoconutInternalException("invalid logging level", level)

        if color:
            color = self.enable_colors(file) and color

        raw_message = " ".join(str(msg) for msg in messages)
        # if there's nothing to display but there is a sig, display the sig
        if not raw_message and sig:
            raw_message = "\n"

        components = []
        for line in raw_message.splitlines(True):
            line, endline = split_trailing_whitespace(line)
            if color:
                components.append(ansii_escape + "[" + color + "m")
            if sig:
                components.append(sig)
            components.append(line)
            if color:
                components.append(ansii_reset)
            components.append(endline)
        components.append(end)
        full_message = "".join(components)

        if full_message:
            # we use end="" to ensure atomic printing (and so we add the end in earlier)
            print(full_message, file=file, end="", flush=flush, **kwargs)

    def print(self, *messages, **kwargs):
        """Print messages to stdout."""
        self.display(messages, **kwargs)

    def printerr(self, *messages, **kwargs):
        """Print errors to stderr."""
        self.display(messages, level="error", **kwargs)

    def printlog(self, *messages, **kwargs):
        """Print messages to stderr."""
        self.display(messages, level="logging", **kwargs)

    def show(self, *messages, **kwargs):
        """Prints messages if not --quiet."""
        if not self.quiet:
            self.display(messages, **kwargs)

    def show_sig(self, *messages, **kwargs):
        """Prints messages with main signature if not --quiet."""
        if not self.quiet:
            self.display(messages, main_sig, **kwargs)

    def show_error(self, *messages, **kwargs):
        """Prints error messages with main signature if not --quiet."""
        if not self.quiet:
            self.display(messages, main_sig, level="error", **kwargs)

    def log(self, *messages, **kwargs):
        """Logs debug messages if --verbose."""
        if self.verbose:
            self.printlog(*messages, **kwargs)

    def log_stdout(self, *messages, **kwargs):
        """Logs debug messages to stdout if --verbose."""
        if self.verbose:
            self.print(*messages, **kwargs)

    def log_lambda(self, *msg_funcs):
        if self.verbose:
            messages = []
            for msg in msg_funcs:
                if callable(msg):
                    msg = msg()
                messages.append(msg)
            self.printlog(*messages)

    def log_func(self, func):
        """Calls a function and logs the results if --verbose."""
        if self.verbose:
            to_log = func()
            if not isinstance(to_log, tuple):
                to_log = (to_log,)
            self.printlog(*to_log)

    def log_prefix(self, prefix, *messages):
        """Logs debug messages with the given signature if --verbose."""
        if self.verbose:
            self.display(messages, prefix, level="logging")

    def log_sig(self, *messages):
        """Logs debug messages with the main signature if --verbose."""
        self.log_prefix(main_sig, *messages)

    def log_vars(self, message, variables, rem_vars=("self",)):
        """Logs variables with given message if --verbose."""
        if self.verbose:
            new_vars = dict(variables)
            for v in rem_vars:
                del new_vars[v]
            self.printlog(message, new_vars)

    def log_loc(self, name, original, loc):
        """Log a location in source code."""
        if self.tracing:
            if isinstance(loc, int):
                pre_loc_orig, post_loc_orig = original[:loc], original[loc:]
                if pre_loc_orig.count("\n") > max_orig_lines_in_log_loc:
                    pre_loc_orig_repr = "... " + repr(pre_loc_orig.rsplit("\n", 1)[-1])
                else:
                    pre_loc_orig_repr = repr(pre_loc_orig)
                if post_loc_orig.count("\n") > max_orig_lines_in_log_loc:
                    post_loc_orig_repr = repr(post_loc_orig.split("\n", 1)[0]) + " ..."
                else:
                    post_loc_orig_repr = repr(post_loc_orig)
                self.printlog("in error construction:", str(name), "=", pre_loc_orig_repr, "|", post_loc_orig_repr)
            else:
                self.printlog("in error construction:", str(name), "=", repr(loc))

    def get_error(self, err=None, show_tb=None):
        """Properly formats the current error."""
        if err is None:
            exc_info = sys.exc_info()
        else:
            exc_info = type(err), err, err.__traceback__

        if exc_info[0] is None:
            return None
        else:
            err_type, err_value, err_trace = exc_info[0], exc_info[1], None
            if show_tb is None:
                show_tb = (
                    self.verbose
                    or issubclass(err_type, CoconutInternalException)
                    or not issubclass(err_type, CoconutException)
                )
            if show_tb and len(exc_info) > 2:
                err_trace = exc_info[2]
            return format_error(err_value, err_type, err_trace)

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
                self.warn_exc()

    def log_warn(self, *args, **kwargs):
        """Log a warning."""
        if self.verbose:
            return self.warn(*args, **kwargs)

    def print_exc(self, err=None, show_tb=None, warning=False):
        """Properly prints an exception."""
        self.print_formatted_error(self.get_error(err, show_tb), warning)

    def warn_exc(self, err=None):
        """Warn about the current or given exception."""
        self.print_exc(err, warning=True)

    def print_exception(self, err_type, err_value, err_tb):
        """Properly prints the given exception details."""
        self.print_formatted_error(format_error(err_value, err_type, err_tb))

    def print_formatted_error(self, errmsg, warning=False):
        """Print a formatted error message in the current context."""
        if errmsg is not None:
            if self.path is not None:
                errmsg_lines = ["in " + self.path + ":"]
                for line in errmsg.splitlines():
                    if line:
                        line = " " * taberrfmt + line
                    errmsg_lines.append(line)
                errmsg = "\n".join(errmsg_lines)
            if warning:
                self.printlog(errmsg)
            else:
                self.printerr(errmsg)

    def log_exc(self, err=None):
        """Display an exception only if --verbose."""
        if self.verbose:
            self.print_exc(err)

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
        self.printlog(_indent(trace, self.trace_ind))

    def log_tag(self, tag, block, multiline=False, wrap=True, force=False):
        """Logs a tagged message if tracing."""
        if self.tracing or force:
            assert not (not DEVELOP and force), tag
            if callable(block):
                block = block()
            tagstr = "[" + str(tag) + "]"
            if multiline:
                self.print_trace(tagstr + "\n" + displayable(block))
            else:
                self.print_trace(tagstr, ascii(block) if wrap else block)

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
                            if "}" in middle:
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
        if self.tracing:  # avoid the overhead of an extra function call
            self.log_trace(expr, original, start_loc, tokens)

    def _trace_exc_action(self, original, loc, expr, exc):
        if self.tracing and self.verbose:  # avoid the overhead of an extra function call
            self.log_trace(expr, original, loc, exc)

    def trace(self, item):
        """Traces a parse element (only enabled in develop)."""
        if DEVELOP and not MODERN_PYPARSING:
            # setDebugActions doesn't work as it won't let us set any actions to None
            item.debugActions = (
                None,  # no start action
                self._trace_success_action,
                self._trace_exc_action,
            )
            item.debug = True
        return item

    def record_stat(self, stat_name, stat_bool):
        """Record the given boolean statistic for the given stat_name.

        All stats recorded here must have some printing logic added to gather_parsing_stats or log_compiler_stats.
        Printed stats should also be added to the regex in the Makefile for getting non-informational lines."""
        self.recorded_stats[stat_name][stat_bool] += 1

    @contextmanager
    def gather_parsing_stats(self):
        """Times parsing if --verbose."""
        if self.verbose:
            self.recorded_stats.pop("adaptive", None)
            self.recorded_stats.pop("cached_parse", None)
            start_time = get_clock_time()
            try:
                yield
            finally:
                elapsed_time = get_clock_time() - start_time
                self.printlog("Time while parsing" + (" " + self.path if self.path else "") + ":", elapsed_time, "secs")
                if use_packrat_parser:
                    hits, misses = ParserElement.packrat_cache_stats
                    self.printlog("\tPackrat parsing stats:", hits, "hits;", misses, "misses")
                    # reset stats after printing if in incremental mode
                    if ParserElement._incrementalEnabled:
                        ParserElement.packrat_cache_stats[:] = [0] * len(ParserElement.packrat_cache_stats)
                if "adaptive" in self.recorded_stats:
                    failures, successes = self.recorded_stats["adaptive"]
                    self.printlog("\tAdaptive parsing stats:", successes, "successes;", failures, "failures")
                if "cached_parse" in self.recorded_stats:
                    misses, hits = self.recorded_stats["cached_parse"]
                    self.printlog("\tComputation graph cache stats:", hits, "hits;", misses, "misses")
                if maybe_make_safe is not None:
                    hits, misses = maybe_make_safe.stats
                    self.printlog("\tErrorless parsing stats:", hits, "errorless;", misses, "with errors")
        else:
            yield

    def log_compiler_stats(self, comp):
        """Log stats for the given compiler."""
        if self.verbose:
            self.log("Grammar init time: " + str(comp.grammar_init_time) + " secs / Total init time: " + str(get_clock_time() - first_import_time) + " secs")
            for stat_name, (no_copy, yes_copy) in self.recorded_stats.items():
                if stat_name.startswith("maybe_copy_"):
                    name = assert_remove_prefix(stat_name, "maybe_copy_")
                    self.printlog("\tGrammar copying stats (" + name + "):", no_copy, "not copied;", yes_copy, "copied")

    total_block_time = defaultdict(int)

    @contextmanager
    def time_block(self, name):
        start_time = get_clock_time()
        try:
            yield
        finally:
            elapsed_time = get_clock_time() - start_time
            self.total_block_time[name] += elapsed_time
            self.printlog("Time while running", name + ":", elapsed_time, "secs (total so far:", self.total_block_time[name], "secs)")

    def time_func(self, func):
        """Decorator to print timing info for a function."""
        @wraps(func)
        def timed_func(*args, **kwargs):
            """Function timed by logger.time_func."""
            if not DEVELOP or self.quiet:
                return func(*args, **kwargs)
            with self.time_block(func.__name__):
                return func(*args, **kwargs)
        return timed_func

    def debug_func(self, func, func_name=None):
        """Decorates a function to print the input/output behavior."""
        if func_name is None:
            func_name = func

        @wraps(func)
        def printing_func(*args, **kwargs):
            """Function decorated by logger.debug_func."""
            if not DEVELOP or self.quiet:
                return func(*args, **kwargs)
            if not kwargs:
                self.printerr(func_name, "<*|", args)
            elif not args:
                self.printerr(func_name, "<**|", kwargs)
            else:
                self.printerr(func_name, "<<|", args, kwargs)
            out = func(*args, **kwargs)
            self.printerr(func_name, "=>", repr(out))
            return out
        return printing_func

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
        self.printlog(self.name, args, kwargs, traceback.format_exc())
    debug = info = warning = pylog

    def pylogerr(self, *args, **kwargs):
        """Display all available error information."""
        self.printerr(self.name, args, kwargs, traceback.format_exc())
    error = critical = exception = pylogerr


# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------

logger = Logger()

trace = logger.trace
