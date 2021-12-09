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

from coconut._pyparsing import (
    lineno,
    col as getcol,
)

from coconut.constants import (
    taberrfmt,
    report_this_text,
)
from coconut.util import (
    clip,
    logical_lines,
    clean,
    get_displayable_target,
)

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

    def __init__(self, message, source=None, point=None, ln=None, extra=None, endpoint=None):
        """Creates the Coconut SyntaxError."""
        self.args = (message, source, point, ln, extra, endpoint)

    def message(self, message, source, point, ln, extra=None, endpoint=None):
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
                if endpoint is None:
                    endpoint = 0
                endpoint = clip(endpoint, point, len(source))

                point_ln = lineno(point, source)
                endpoint_ln = lineno(endpoint, source)

                source_lines = tuple(logical_lines(source))

                # single-line error message
                if point_ln == endpoint_ln:
                    part = clean(source_lines[point_ln - 1], False).lstrip()

                    # adjust all points based on lstrip
                    point -= len(source) - len(part)
                    endpoint -= len(source) - len(part)

                    part = part.rstrip()

                    # adjust only points that are too large based on rstrip
                    point = clip(point, 0, len(part) - 1)
                    endpoint = clip(endpoint, point, len(part))

                    message += "\n" + " " * taberrfmt + part

                    if point > 0 or endpoint > 0:
                        message += "\n" + " " * (taberrfmt + point)
                        if endpoint - point > 1:
                            message += "~" * (endpoint - point - 1) + "^"
                        else:
                            message += "^"

                # multi-line error message
                else:
                    lines = source_lines[point_ln - 1:endpoint_ln]

                    point_col = getcol(point, source)
                    endpoint_col = getcol(endpoint, source)

                    message += "\n" + " " * (taberrfmt + point_col - 1) + "|" + "~" * (len(lines[0]) - point_col) + "\n"
                    for line in lines:
                        message += "\n" + " " * taberrfmt + clean(line, False).rstrip()
                    message += "\n\n" + " " * taberrfmt + "~" * (endpoint_col - 1) + "^"

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

    def __init__(self, message, source=None, point=None, ln=None, endpoint=None):
        """Creates the --strict Coconut error."""
        self.args = (message, source, point, ln, endpoint)

    def message(self, message, source, point, ln, endpoint):
        """Creates the --strict Coconut error message."""
        return super(CoconutStyleError, self).message(
            message,
            source,
            point,
            ln,
            extra="remove --strict to dismiss",
            endpoint=endpoint,
        )


class CoconutTargetError(CoconutSyntaxError):
    """Coconut --target error."""

    def __init__(self, message, source=None, point=None, ln=None, target=None, endpoint=None):
        """Creates the --target Coconut error."""
        self.args = (message, source, point, ln, target, endpoint)

    def message(self, message, source, point, ln, target, endpoint):
        """Creates the --target Coconut error message."""
        if target is None:
            extra = None
        else:
            extra = "pass --target " + get_displayable_target(target) + " to fix"
        return super(CoconutTargetError, self).message(message, source, point, ln, extra, endpoint)


class CoconutParseError(CoconutSyntaxError):
    """Coconut ParseError."""


class CoconutWarning(CoconutException):
    """Base Coconut warning."""


class CoconutSyntaxWarning(CoconutSyntaxError, CoconutWarning):
    """CoconutWarning with CoconutSyntaxError semantics."""


class CoconutInternalException(CoconutException):
    """Internal Coconut exception."""

    def message(self, message, item, extra):
        """Creates the Coconut internal exception message."""
        base_msg = super(CoconutInternalException, self).message(message, item, extra)
        if "\n" in base_msg:
            return base_msg + "\n" + report_this_text
        else:
            return base_msg + " " + report_this_text


class CoconutDeferredSyntaxError(CoconutException):
    """Deferred Coconut SyntaxError."""

    def __init__(self, message, loc):
        """Creates the Coconut exception."""
        self.args = (message, loc)

    def message(self, message, loc):
        """Uses arguments to create the message."""
        return message + " (loc " + str(loc) + ")"
