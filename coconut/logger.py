#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Logging utilities.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

from coconut.constants import \
    default_encoding, \
    color_codes, \
    end_color_code, \
    info_tabulation
from coconut.exceptions import CoconutException

#-----------------------------------------------------------------------------------------------------------------------
# LOGGING:
#-----------------------------------------------------------------------------------------------------------------------

def printerr(*args):
    """Prints to standard error."""
    print(*args, file=sys.stderr)

class logging(object):
    """Container object for various logging functions."""
    verbose = False
    print = print
    printerr = printerr

    @classmethod
    def print_exc(logging, path=None):
        """Properly prints an exception in the exception context."""
        errmsg = get_error(logging.verbose)
        if path is not None:
            errmsg_lines = ["in " + os.path.abspath(path) + ":"]
            for line in errmsg.splitlines():
                if line:
                    line = "  " + line
                errmsg_lines.append(line)
            errmsg = "\n".join(errmsg_lines)
        logging.printerr(errmsg)

    @classmethod
    def log(logging, msg):
        """Logs a debug message if in verbose mode."""
        if logging.verbose:
            logging.printerr(msg)

    @classmethod
    def log_tag(logging, tag, code):
        """Logs a tagged message if in verbose mode."""
        logging.log("["+str(tag)+"] " + ascii(code))

    @classmethod
    def log_cmd(logging, args):
        """Logs a console command if in verbose mode."""
        logging.log("> " + " ".join(args))

    @classmethod
    def show_tabulated(logging, begin, middle, end):
        """Shows a tabulated message."""
        if len(begin) < info_tabulation:
            logging.show(begin + " "*(info_tabulation - len(begin)) + middle + " " + end)
        else:
            raise CoconutException("info message too long", begin)

#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------

class Tracer(object):
    """Debug tracer."""

    def show_trace(self, tag, original, location, tokens):
        """Formats and displays a trace."""
        original = str(original)
        location = int(location)
        out = "[" + tag + "] "
        if len(tokens) == 1 and isinstance(tokens[0], str):
            out += ascii(tokens[0])
        else:
            out += str(tokens)
        out += " (line "+str(lineno(location, original))+", col "+str(col(location, original))+")"
        logging.printerr(out)

    def trace(self, item, tag):
        """Traces a parse element."""
        def callback(original, location, tokens):
            """Callback function constructed by tracer."""
            if logging.verbose:
                self.show_trace(tag, original, location, tokens)
            return tokens
        bound = attach(item, callback)
        bound.setName(tag)
        return bound

class Console(object):
    """Manages printing and reading data to the console."""
    color_code = None
    on = True

    def __init__(self, main_sig="", debug_sig=""):
        """Creates the console."""
        self.main_sig, self.debug_sig = main_sig, debug_sig
        self.bind_logging()

    def bind_logging(self):
        """Binds logging to use this console."""
        logging.print, logging.printerr, logging.show = self.print, self.printerr, self.show

    def quiet(self, quiet=True):
        """Quiet the console."""
        self.on = not quiet

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
        message = " ".join(str(msg) for msg in messages)
        for line in message.splitlines():
            msg = sig + line
            if msg:
                msg = self.add_color(msg)
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
        if self.on:
            self.display(messages, self.main_sig)
