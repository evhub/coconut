#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Syntax highlighting for Coconut code.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#----------------------gme------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from .root import *
import pygments

#-----------------------------------------------------------------------------------------------------------------------
# LEXER:
#-----------------------------------------------------------------------------------------------------------------------

class pylexer(pygments.lexers.python.PythonLexer):
    """Lenient Python syntax highlighter."""
    def add_filter(*args, **kwargs):
        """Disables the raiseonerror filter."""
        if len(args) >= 1 and args[0] == "raiseonerror":
            super(pylexer, self).add_filter(*args, **kwargs)

class pyconlexer(pygments.lexers.python.PythonConsoleLexer):
    """Lenient Python console syntax highlighter."""
    def add_filter(*args, **kwargs):
        """Disables the raiseonerror filter."""
        if len(args) >= 1 and args[0] == "raiseonerror":
            super(pyconlexer, self).add_filter(*args, **kwargs)
