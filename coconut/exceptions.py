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

import traceback

from coconut._pyparsing import (
    lineno,
    col as getcol,
)

from coconut.constants import (
    taberrfmt,
    report_this_text,
    min_squiggles_in_err_msg,
)
from coconut.util import (
    pickleable_obj,
    clip,
    logical_lines,
    clean,
    get_displayable_target,
    normalize_newlines,
)

# -----------------------------------------------------------------------------------------------------------------------
# EXCEPTIONS:
# ----------------------------------------------------------------------------------------------------------------------


class BaseCoconutException(BaseException, pickleable_obj):
    """Coconut BaseException."""

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
        try:
            return self.message(*self.args)
        except BaseException:
            return "error printing " + self.__class__.__name__ + ":\n" + traceback.format_exc()

    def __reduce__(self):
        """Get pickling information."""
        return (self.__class__, self.args)

    def __repr__(self):
        """Get a representation of the exception."""
        return self.__class__.__name__ + "(" + ", ".join(
            repr(arg) for arg in self.args if arg is not None
        ) + ")"


class CoconutException(BaseCoconutException, Exception):
    """Coconut Exception."""


class CoconutSyntaxError(CoconutException):
    """Coconut SyntaxError."""
    point_to_endpoint = False
    argnames = ("message", "source", "point", "ln", "extra", "endpoint", "filename")

    def __init__(self, message, source=None, point=None, ln=None, extra=None, endpoint=None, filename=None):
        """Creates the Coconut SyntaxError."""
        self.args = (message, source, point, ln, extra, endpoint, filename)

    @property
    def kwargs(self):
        """Get the arguments as keyword arguments."""
        return dict(zip(self.argnames, self.args))

    def message(self, message, source, point, ln, extra=None, endpoint=None, filename=None):
        """Creates a SyntaxError-like message."""
        if message is None:
            message = "parsing failed"
        if extra is not None:
            message += " (" + str(extra) + ")"
        if ln is not None:
            message += " (line " + str(ln)
            if filename is not None:
                message += " in " + repr(filename)
            message += ")"
        if source:
            if point is None:
                for line in source.splitlines():
                    message += "\n" + " " * taberrfmt + clean(line)
            else:
                source = normalize_newlines(source)
                point = clip(point, 0, len(source))

                if endpoint is None:
                    endpoint = 0
                endpoint = clip(endpoint, point, len(source))

                point_ln = lineno(point, source)
                endpoint_ln = lineno(endpoint, source)

                point_ind = getcol(point, source) - 1
                endpoint_ind = getcol(endpoint, source) - 1

                source_lines = tuple(logical_lines(source, keep_newlines=True))

                # walk the endpoint line back until it points to real text
                while endpoint_ln > point_ln and not "".join(source_lines[endpoint_ln - 1:endpoint_ln]).strip():
                    endpoint_ln -= 1
                    endpoint_ind = len(source_lines[endpoint_ln - 1])

                # single-line error message
                if point_ln == endpoint_ln:
                    part = source_lines[point_ln - 1]
                    part_len = len(part)

                    part = part.lstrip()

                    # adjust all cols based on lstrip
                    point_ind -= part_len - len(part)
                    endpoint_ind -= part_len - len(part)

                    part = clean(part)

                    # adjust only cols that are too large based on clean/rstrip
                    point_ind = clip(point_ind, 0, len(part))
                    endpoint_ind = clip(endpoint_ind, point_ind, len(part))

                    message += "\n" + " " * taberrfmt + part

                    if point_ind > 0 or endpoint_ind > 0:
                        err_len = endpoint_ind - point_ind
                        message += "\n" + " " * (taberrfmt + point_ind)
                        if err_len <= min_squiggles_in_err_msg:
                            if not self.point_to_endpoint:
                                message += "^"
                            message += "~" * err_len  # err_len ~'s when there's only an extra char in one spot
                            if self.point_to_endpoint:
                                message += "^"
                        else:
                            message += (
                                ("^" if not self.point_to_endpoint else "\\")
                                + "~" * (err_len - 1)  # err_len-1 ~'s when there's an extra char at the start and end
                                + ("^" if self.point_to_endpoint else "/" if endpoint_ind < len(part) else "|")
                            )

                # multi-line error message
                else:
                    lines = []
                    for line in source_lines[point_ln - 1:endpoint_ln]:
                        lines.append(clean(line))

                    point_ind = clip(point_ind, 0, len(lines[0]))
                    endpoint_ind = clip(endpoint_ind, 0, len(lines[-1]))

                    message += "\n" + " " * (taberrfmt + point_ind)
                    if point_ind >= len(lines[0]):
                        message += "|\n"
                    else:
                        message += "/" + "~" * (len(lines[0]) - point_ind - 1) + "\n"
                    for line in lines:
                        message += "\n" + " " * taberrfmt + line
                    message += (
                        "\n\n" + " " * taberrfmt + "~" * endpoint_ind
                        + ("^" if self.point_to_endpoint else "/" if 0 < endpoint_ind < len(lines[-1]) else "|")
                    )

        return message

    def syntax_err(self):
        """Creates a SyntaxError."""
        kwargs = self.kwargs
        if self.point_to_endpoint and "endpoint" in kwargs:
            point = kwargs["endpoint"]
        else:
            point = kwargs.get("point")
        ln = kwargs.get("ln")
        filename = kwargs.get("filename")
        kwargs["point"] = kwargs["endpoint"] = kwargs["ln"] = kwargs["filename"] = None

        err = SyntaxError(self.message(**kwargs))
        if point is not None:
            err.offset = point
        if ln is not None:
            err.lineno = ln
        if filename is not None:
            err.filename = filename
        return err

    def set_point_to_endpoint(self, point_to_endpoint):
        """Sets whether to point to the endpoint."""
        self.point_to_endpoint = point_to_endpoint
        return self


class CoconutStyleError(CoconutSyntaxError):
    """Coconut --strict error."""

    def __init__(self, message, source=None, point=None, ln=None, extra="remove --strict to dismiss", endpoint=None, filename=None):
        """Creates the --strict Coconut error."""
        self.args = (message, source, point, ln, extra, endpoint, filename)


class CoconutTargetError(CoconutSyntaxError):
    """Coconut --target error."""
    argnames = ("message", "source", "point", "ln", "target", "endpoint", "filename")

    def __init__(self, message, source=None, point=None, ln=None, target=None, endpoint=None, filename=None):
        """Creates the --target Coconut error."""
        self.args = (message, source, point, ln, target, endpoint, filename)

    def message(self, message, source, point, ln, target, endpoint, filename):
        """Creates the --target Coconut error message."""
        if target is None:
            extra = None
        else:
            extra = "pass --target " + get_displayable_target(target) + " to fix"
        return super(CoconutTargetError, self).message(message, source, point, ln, extra, endpoint, filename)


class CoconutParseError(CoconutSyntaxError):
    """Coconut ParseError."""
    point_to_endpoint = True


class CoconutWarning(CoconutException):
    """Base Coconut warning."""


class CoconutSyntaxWarning(CoconutSyntaxError, CoconutWarning):
    """CoconutWarning with CoconutSyntaxError semantics."""


class CoconutInternalException(CoconutException):
    """Internal Coconut exception."""

    def message(self, *args, **kwargs):
        """Creates the Coconut internal exception message."""
        base_msg = super(CoconutInternalException, self).message(*args, **kwargs)
        if "\n" in base_msg:
            return base_msg + "\n" + report_this_text
        else:
            return base_msg + " " + report_this_text


class CoconutInternalSyntaxError(CoconutInternalException, CoconutSyntaxError):
    """Internal Coconut SyntaxError."""


class CoconutDeferredSyntaxError(CoconutException):
    """Deferred Coconut SyntaxError."""

    def __init__(self, message, loc):
        """Creates the Coconut exception."""
        self.args = (message, loc)

    def message(self, message, loc):
        """Uses arguments to create the message."""
        return message + " (loc " + str(loc) + ")"
