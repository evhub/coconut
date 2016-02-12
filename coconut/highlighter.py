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
from .command import code_ext, encoding, tablen
import pygments

#-----------------------------------------------------------------------------------------------------------------------
# LEXERS:
#-----------------------------------------------------------------------------------------------------------------------

class pylexer(pygments.lexers.Python3Lexer):
    """Lenient Python syntax highlighter."""
    name = "force_python"
    aliases = ["force_python", "force_py", "force_python3", "force_py3"]
    filenames = []
    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tablen, encoding=encoding):
        """Initialize the Python syntax highlighter."""
        super(pylexer, self).__init__(stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=encoding)
    def add_filter(self, *args, **kwargs):
        """Disables the raiseonerror filter."""
        print(args, kwargs)
        if len(args) >= 1 and args[0] != "raiseonerror":
            super(pylexer, self).add_filter(*args, **kwargs)

class pyconlexer(pygments.lexers.PythonConsoleLexer):
    """Lenient Python console syntax highlighter."""
    name = "force_pycon"
    aliases = ["force_pycon", "force_pycon3"]
    filenames = []
    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tablen, encoding=encoding, python3=True):
        """Initialize the Python console syntax highlighter."""
        super(pyconlexer, self).__init__(stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=encoding, python3=python3)
    def add_filter(self, *args, **kwargs):
        """Disables the raiseonerror filter."""
        print(args, kwargs)
        if len(args) >= 1 and args[0] != "raiseonerror":
            super(pyconlexer, self).add_filter(*args, **kwargs)

class coclexer(pylexer):
    """Coconut syntax highlighter."""
    name = "coconut"
    aliases = ["coc", "coconut", "force_coc" "force_coconut"]
    filenames = ["*"+code_ext]

class cocconlexer(pyconlexer):
    """Coconut console syntax highlighter."""
    name = "coconutcon"
    aliases = ["coccon", "coconutcon", "force_coccon", "force_coconutcon"]
    filenames = []
