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
    info_tabulation, \
    main_sig, \
    debug_sig
from coconut.exceptions import CoconutException

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------

def printerr(*args):
    """Prints to standard error."""
    print(*args, file=sys.stderr)

#-----------------------------------------------------------------------------------------------------------------------
# LOGGING:
#-----------------------------------------------------------------------------------------------------------------------

class Logging(object):
    """Container object for various logging functions and variables."""
    verbose = False
    quiet = False
    color_code = None

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
        for line in full_message.splitlines():
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
        self.display(messages, debug_sig, True)

    def show(self, *messages):
        """Prints messages with color and main signature."""
        if self.verbose:
            self.display(messages, main_sig)

    def print_exc(self, path=None):
        """Properly prints an exception in the exception context."""
        errmsg = get_error(self.verbose)
        if path is not None:
            errmsg_lines = ["in " + os.path.abspath(path) + ":"]
            for line in errmsg.splitlines():
                if line:
                    line = "  " + line
                errmsg_lines.append(line)
            errmsg = "\n".join(errmsg_lines)
        self.printerr(errmsg)

    def log(self, msg):
        """Logs a debug message if in verbose mode."""
        if self.verbose:
            self.printerr(msg)

    def log_tag(self, tag, code):
        """Logs a tagged message if in verbose mode."""
        self.log("["+str(tag)+"] " + ascii(code))

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
        if logging.verbose:
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
        def trace_action(original, location, tokens):
            """Callback function constructed by tracer."""
            self.log_trace(tag, original, location, tokens)
        bound = attach(item, trace_action)
        bound.setName(tag)
        return bound

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

logging = Logging()
