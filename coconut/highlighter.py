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

from .command import *
from pygments.lexers import Python3Lexer, PythonConsoleLexer
from pygments.lexer import Lexer, RegexLexer, include, bygroups, using, default, words, combined, do_insertions
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number, Punctuation, Generic, Other, Error

#-----------------------------------------------------------------------------------------------------------------------
# LEXERS:
#-----------------------------------------------------------------------------------------------------------------------

class pylexer(Python3Lexer):
    """Lenient Python syntax highlighter."""
    name = "force_python"
    aliases = ["force_python", "force_py", "force_python3", "force_py3"]
    filenames = []

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tablen, encoding=encoding):
        """Initialize the Python syntax highlighter."""
        super(pylexer, self).__init__(stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=encoding)
    def add_filter(self, *args, **kwargs):
        """Disables the raiseonerror filter."""
        if len(args) >= 1 and args[0] != "raiseonerror":
            super(pylexer, self).add_filter(*args, **kwargs)

class pyconlexer(PythonConsoleLexer):
    """Lenient Python console syntax highlighter."""
    name = "force_pycon"
    aliases = ["force_pycon", "force_pycon3"]
    filenames = []

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tablen, encoding=encoding, python3=True):
        """Initialize the Python console syntax highlighter."""
        super(pyconlexer, self).__init__(stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=encoding, python3=python3)
    def add_filter(self, *args, **kwargs):
        """Disables the raiseonerror filter."""
        if len(args) >= 1 and args[0] != "raiseonerror":
            super(pyconlexer, self).add_filter(*args, **kwargs)

class coclexer(Python3Lexer):
    """Coconut syntax highlighter."""
    name = "coconut"
    aliases = ["coconut", "force_coconut", "coc", "force_coc", "coconutcon", "force_coconutcon"]
    filenames = ["*"+code_ext]

    tokens = Python3Lexer.tokens.copy()
    tokens["keywords"] = [
        (words(keywords + reserved_vars, suffix=r"\b"), Keyword),
        (words(const_vars, suffix=r"\b"), Keyword.Constant)
    ]
    tokens["backtick"] = [
        (r"`.*?`", String.Backtick)
    ]
    tokens["name"] = tokens["name"] + [
        (r"\$|::", Operator)
    ]
    tokens["builtins"] = tokens["builtins"] + [
        (words((
            "reduce",
            "takewhile",
            "dropwhile",
            "tee",
            "recursive",
            "datamaker",
            "consume"
            ), prefix=r"(?<!\.)", suffix=r"\b"), Name.Builtin),
        (r"(?<!\.)MatchError\b", Name.Exception)
    ]
    tokens["magicvars"] = (tokens["magicvars"] if "magicvars" in tokens else []) + [
        (r"(?<!\.)__coconut_version__\b", Name.Variable.Magic)
    ]
    tokens["numbers"] = tokens["numbers"] + [
        (r"\d+_[A-Za-z0-9]+", Number.Integer)
    ]

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tablen, encoding=encoding):
        """Initialize the Python syntax highlighter."""
        super(coclexer, self).__init__(stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=encoding)
