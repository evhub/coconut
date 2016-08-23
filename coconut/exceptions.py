#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Exceptions for use in the compiler.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

import sys
import traceback
from pyparsing import lineno

from coconut.constants import openindent, closeindent, tabideal

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------

def format_error(err_type, err_value, err_trace=None):
    """Properly formats the specified error."""
    if err_trace is None:
        err_name, err_msg = "".join(traceback.format_exception_only(err_type, err_value)).strip().split(": ", 1)
        err_name = err_name.split(".")[-1]
        return err_name + ": " + err_msg
    else:
        return "".join(traceback.format_exception(err_type, err_value, err_trace)).strip()

def get_error(verbose=False):
    """Properly formats the current error."""
    err_type, err_value, err_trace = sys.exc_info()
    if not verbose:
        err_trace = None
    return format_error(err_type, err_value, err_trace)

def clean(inputline, strip=True):
    """Cleans and strips a line."""
    if hasattr(sys.stdout, "encoding") and sys.stdout.encoding is not None:
        stdout_encoding = sys.stdout.encoding
    else:
        stdout_encoding = default_encoding
    inputline = inputline.replace(openindent, "").replace(closeindent, "")
    if strip:
        inputline = inputline.strip()
    return inputline.encode(stdout_encoding, "replace").decode(stdout_encoding)

#-----------------------------------------------------------------------------------------------------------------------
# EXCEPTIONS:
#----------------------------------------------------------------------------------------------------------------------

class CoconutException(Exception):
    """Base Coconut exception."""
    def __init__(self, value, item=None):
        """Creates the Coconut exception."""
        self.value = value
        if item is not None:
            self.value += ": " + ascii(item)
    def __repr__(self):
        """Displays the Coconut exception."""
        return self.value
    def __str__(self):
        """Wraps __repr__."""
        return repr(self)

class CoconutSyntaxError(CoconutException):
    """Coconut SyntaxError."""
    def __init__(self, message, source=None, point=None, ln=None):
        """Creates the Coconut SyntaxError."""
        self.value = message
        if ln is not None:
            self.value += " (line " + str(ln) + ")"
        if source:
            if point is None:
                self.value += "\n" + " "*tabideal + clean(source)
            else:
                part = clean(source.splitlines()[lineno(point, source)-1], False).lstrip()
                point -= len(source) - len(part) # adjust all points based on lstrip
                part = part.rstrip() # adjust only points that are too large based on rstrip
                self.value += "\n" + " "*tabideal + part
                if point > 0:
                    if point >= len(part):
                        point = len(part) - 1
                    self.value += "\n" + " "*(tabideal + point) + "^"

class CoconutParseError(CoconutSyntaxError):
    """Coconut ParseError."""
    def __init__(self, source=None, point=None, lineno=None):
        """Creates The Coconut ParseError."""
        CoconutSyntaxError.__init__(self, "parsing failed", source, point, lineno)

class CoconutStyleError(CoconutSyntaxError):
    """Coconut --strict error."""
    def __init__(self, message, source=None, point=None, lineno=None):
        """Creates the --strict Coconut error."""
        message += " (disable --strict to dismiss)"
        CoconutSyntaxError.__init__(self, message, source, point, lineno)

class CoconutTargetError(CoconutSyntaxError):
    """Coconut --target error."""
    def __init__(self, message, source=None, point=None, lineno=None):
        """Creates the --target Coconut error."""
        message, target = message
        message += " (enable --target "+target+" to dismiss)"
        CoconutSyntaxError.__init__(self, message, source, point, lineno)

class CoconutWarning(CoconutSyntaxError):
    """Base Coconut warning."""
