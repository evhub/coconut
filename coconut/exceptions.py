#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Exceptions for use in the compiler.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys

from coconut._pyparsing import lineno

from coconut.constants import (
    openindent,
    closeindent,
    taberrfmt,
    default_encoding,
    report_this_text,
)

# -----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------------------------------------------------


def get_encoding(fileobj):
    """Get encoding of a file."""
    # sometimes fileobj.encoding is undefined, but sometimes it is None; we need to handle both cases
    obj_encoding = getattr(fileobj, "encoding", None)
    return obj_encoding if obj_encoding is not None else default_encoding


def clean(inputline, strip=True, rem_indents=True, encoding_errors="replace"):
    """Clean and strip a line."""
    stdout_encoding = get_encoding(sys.stdout)
    inputline = str(inputline)
    if rem_indents:
        inputline = inputline.replace(openindent, "").replace(closeindent, "")
    if strip:
        inputline = inputline.strip()
    return inputline.encode(stdout_encoding, encoding_errors).decode(stdout_encoding)


def displayable(inputstr, strip=True):
    """Make a string displayable with minimal loss of information."""
    return clean(str(inputstr), strip, rem_indents=False, encoding_errors="backslashreplace")


# -----------------------------------------------------------------------------------------------------------------------
# EXCEPTIONS:
# ----------------------------------------------------------------------------------------------------------------------


class CoconutException(Exception):
    """Base Coconut exception."""

    def __init__(self, message, item=None, extra=None):
        """Creates the Coconut exception."""
        self.args = (message, item, extra)

    def message(self, message, item, extra):
        """Uses arguments to create the message."""
        if item is not None:
            message += ": " + ascii(item)
        if extra is not None:
            message += " (" + str(extra) + ")"
        return message

    def syntax_err(self):
        """Converts to a SyntaxError."""
        return SyntaxError(str(self))

    def __str__(self):
        """Get the exception message."""
        return self.message(*self.args)

    def __reduce__(self):
        """Get pickling information."""
        return (self.__class__, self.args)

    def __repr__(self):
        """Get a representation of the exception."""
        return self.__class__.__name__ + "(" + ", ".join(
            repr(arg) for arg in self.args if arg is not None
        ) + ")"


class CoconutSyntaxError(CoconutException):
    """Coconut SyntaxError."""

    def __init__(self, message, source=None, point=None, ln=None, extra=None):
        """Creates the Coconut SyntaxError."""
        self.args = (message, source, point, ln, extra)

    def message(self, message, source, point, ln, extra=None):
        """Creates a SyntaxError-like message."""
        if message is None:
            message = "parsing failed"
        if extra is not None:
            message += " (" + str(extra) + ")"
        if ln is not None:
            message += " (line " + str(ln) + ")"
        if source:
            if point is None:
                message += "\n" + " " * taberrfmt + clean(source)
            else:
                part = clean(source.splitlines()[lineno(point, source) - 1], False).lstrip()
                point -= len(source) - len(part)  # adjust all points based on lstrip
                part = part.rstrip()  # adjust only points that are too large based on rstrip
                message += "\n" + " " * taberrfmt + part
                if point > 0:
                    if point >= len(part):
                        point = len(part) - 1
                    message += "\n" + " " * (taberrfmt + point) + "^"
        return message

    def syntax_err(self):
        """Creates a SyntaxError."""
        args = self.args[:2] + (None, None) + self.args[4:]
        err = SyntaxError(self.message(*args))
        err.offset = args[2]
        err.lineno = args[3]
        return err


class CoconutStyleError(CoconutSyntaxError):
    """Coconut --strict error."""

    def __init__(self, message, source=None, point=None, ln=None):
        """Creates the --strict Coconut error."""
        self.args = (message, source, point, ln)

    def message(self, message, source, point, ln):
        """Creates the --strict Coconut error message."""
        return super(CoconutStyleError, self).message(
            message,
            source,
            point,
            ln,
            extra="remove --strict to dismiss",
        )


class CoconutTargetError(CoconutSyntaxError):
    """Coconut --target error."""

    def __init__(self, message, source=None, point=None, ln=None, target=None):
        """Creates the --target Coconut error."""
        self.args = (message, source, point, ln, target)

    def message(self, message, source, point, ln, target):
        """Creates the --target Coconut error message."""
        if target is None:
            extra = None
        else:
            extra = "pass --target " + target + " to fix"
        return super(CoconutTargetError, self).message(message, source, point, ln, extra)


class CoconutParseError(CoconutSyntaxError):
    """Coconut ParseError."""

    def __init__(self, message=None, source=None, point=None, ln=None, extra=None):
        """Creates the ParseError."""
        self.args = (message, source, point, ln, extra)


class CoconutWarning(CoconutException):
    """Base Coconut warning."""


class CoconutSyntaxWarning(CoconutSyntaxError, CoconutWarning):
    """CoconutWarning with CoconutSyntaxError semantics."""


class CoconutInternalException(CoconutException):
    """Internal Coconut exception."""

    def message(self, message, item, extra):
        """Creates the Coconut internal exception message."""
        return (
            super(CoconutInternalException, self).message(message, item, extra)
            + " " + report_this_text
        )


class CoconutDeferredSyntaxError(CoconutException):
    """Deferred Coconut SyntaxError."""

    def __init__(self, message, loc):
        """Creates the Coconut exception."""
        self.args = (message, loc)

    def message(self, message, loc):
        """Uses arguments to create the message."""
        return message + " (loc " + str(loc) + ")"
