#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from coconut.root import *  # NOQA

import sys

from pyparsing import lineno

from coconut.constants import (
    openindent,
    closeindent,
    taberrfmt,
    default_encoding,
)

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------


def clean(inputline, strip=True, rem_indents=True, encoding_errors="replace"):
    """Cleans and strips a line."""
    if hasattr(sys.stdout, "encoding") and sys.stdout.encoding is not None:
        stdout_encoding = sys.stdout.encoding
    else:
        stdout_encoding = default_encoding
    inputline = str(inputline)
    if rem_indents:
        inputline = inputline.replace(openindent, "").replace(closeindent, "")
    if strip:
        inputline = inputline.strip()
    return inputline.encode(stdout_encoding, encoding_errors).decode(stdout_encoding)


def debug_clean(inputline, strip=True):
    """Call clean with debug parameters."""
    return clean(inputline, strip, False, "backslashreplace")


#-----------------------------------------------------------------------------------------------------------------------
# EXCEPTIONS:
#----------------------------------------------------------------------------------------------------------------------


class CoconutException(Exception):
    """Base Coconut exception."""

    def __init__(self, message, item=None, extra=None):
        """Creates the Coconut exception."""
        self.message = message
        if item is not None:
            self.message += ": " + ascii(item)
        if extra is not None:
            self.message += " (" + str(extra) + ")"

    @property
    def args(self):
        """Get the arguments to the exception."""
        return (self.message,)

    def __reduce__(self):
        """Get pickling information."""
        return (self.__class__, self.args)

    def __str__(self):
        """Get the exception message."""
        return self.message

    def __repr__(self):
        """Get a representation of the exception."""
        return self.__class__.__name__ + "(" + ", ".join(self.args) + ")"


class CoconutSyntaxError(CoconutException):
    """Coconut SyntaxError."""

    def __init__(self, message, source=None, point=None, ln=None):
        """Creates the Coconut SyntaxError."""
        self.message = message
        if ln is not None:
            self.message += " (line " + str(ln) + ")"
        if source:
            if point is None:
                self.message += "\n" + " " * taberrfmt + clean(source)
            else:
                part = clean(source.splitlines()[lineno(point, source) - 1], False).lstrip()
                point -= len(source) - len(part)  # adjust all points based on lstrip
                part = part.rstrip()  # adjust only points that are too large based on rstrip
                self.message += "\n" + " " * taberrfmt + part
                if point > 0:
                    if point >= len(part):
                        point = len(part) - 1
                    self.message += "\n" + " " * (taberrfmt + point) + "^"


class CoconutParseError(CoconutSyntaxError):
    """Coconut ParseError."""

    def __init__(self, message=None, source=None, point=None, lineno=None):
        """Creates The Coconut ParseError."""
        if message is None:
            message = "parsing failed"
        CoconutSyntaxError.__init__(self, message, source, point, lineno)


class CoconutStyleError(CoconutSyntaxError):
    """Coconut --strict error."""

    def __init__(self, message, source=None, point=None, lineno=None):
        """Creates the --strict Coconut error."""
        message += " (disable --strict to dismiss)"
        CoconutSyntaxError.__init__(self, message, source, point, lineno)


class CoconutTargetError(CoconutSyntaxError):
    """Coconut --target error."""

    def __init__(self, message, source=None, point=None, lineno=None, target=None):
        """Creates the --target Coconut error."""
        if target is not None:
            message += " (enable --target " + target + " to dismiss)"
        CoconutSyntaxError.__init__(self, message, source, point, lineno)


class CoconutWarning(CoconutException):
    """Base Coconut warning."""


class CoconutStyleWarning(CoconutStyleError, CoconutWarning):
    """Coconut --strict warning."""


class CoconutInternalException(CoconutException):
    """Internal Coconut exceptions."""
