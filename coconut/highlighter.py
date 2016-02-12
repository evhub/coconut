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
#----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from .root import *
import pygments

#-----------------------------------------------------------------------------------------------------------------------
# LEXERS:
#-----------------------------------------------------------------------------------------------------------------------

class pylexer(pygments.lexers.PythonLexer):
    """Lenient Python syntax highlighter."""
    name = "force_python"
    aliases = ["force_python", "force_py"]
    filenames = []
    def add_filter(self, *args, **kwargs):
        """Disables the raiseonerror filter."""
        print(args, kwargs)
        if len(args) >= 1 and args[0] != "raiseonerror":
            super(pylexer, self).add_filter(*args, **kwargs)

class pyconlexer(pygments.lexers.PythonConsoleLexer):
    """Lenient Python console syntax highlighter."""
    name = "force_pycon"
    aliases = ["force_pycon"]
    filenames = []
    def add_filter(self, *args, **kwargs):
        """Disables the raiseonerror filter."""
        print(args, kwargs)
        if len(args) >= 1 and args[0] != "raiseonerror":
            super(pyconlexer, self).add_filter(*args, **kwargs)
