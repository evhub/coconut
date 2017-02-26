#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from coconut.root import *  # NOQA

from pygments.lexers import Python3Lexer, PythonConsoleLexer
from pygments.token import Text, Operator, Keyword, Name, Number
from pygments.lexer import words, bygroups
from pygments.util import shebang_matches

from coconut.constants import (
    builtins,
    new_operators,
    tabideal,
    default_encoding,
    code_exts,
    reserved_vars,
    shebang_regex,
)

#-----------------------------------------------------------------------------------------------------------------------
# LEXERS:
#-----------------------------------------------------------------------------------------------------------------------


def lenient_add_filter(self, *args, **kwargs):
    """Disables the raiseonerror filter."""
    if args and args[0] != "raiseonerror":
        self.original_add_filter(*args, **kwargs)


class CoconutPythonLexer(Python3Lexer):
    """Coconut-style Python syntax highlighter."""
    name = "coconut_python"
    aliases = ["coconut_python", "coconut_py", "coconut_python3", "coconut_py3"]
    filenames = []

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tabideal, encoding=default_encoding):
        """Initialize the Python syntax highlighter."""
        Python3Lexer.__init__(self, stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=default_encoding)
        self.original_add_filter, self.add_filter = self.add_filter, lenient_add_filter


class CoconutPythonConsoleLexer(PythonConsoleLexer):
    """Coconut-style Python console syntax highlighter."""
    name = "coconut_pycon"
    aliases = ["coconut_pycon", "coconut_pycon3"]
    filenames = []

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tabideal, encoding=default_encoding, python3=True):
        """Initialize the Python console syntax highlighter."""
        PythonConsoleLexer.__init__(self, stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=default_encoding, python3=python3)
        self.original_add_filter, self.add_filter = self.add_filter, lenient_add_filter


class CoconutLexer(Python3Lexer):
    """Coconut syntax highlighter."""
    name = "coconut"
    aliases = ["coconut", "coco", "coc"]
    filenames = ["*" + ext for ext in code_exts]

    tokens = Python3Lexer.tokens.copy()
    tokens["root"] = [
        (r"|".join(new_operators), Operator),
        (r'(?<!\\)(data)((?:\s|\\\s)+)', bygroups(Keyword, Text), py_str("classname")),
        (r'def(?=\s*\()', Keyword),
        (r'\?', Keyword),
    ] + tokens["root"]
    tokens["keywords"] = tokens["keywords"] + [
        (words(reserved_vars, prefix=r"(?<!\\)", suffix=r"\b"), Keyword),
    ]
    tokens["builtins"] = tokens["builtins"] + [
        (words(builtins, suffix=r"\b"), Name.Builtin),
        (r"MatchError\b", Name.Exception),
    ]
    tokens["numbers"] = [
        (r"0b[01_]+", Number.Integer),
        (r"0o[0-7_]+", Number.Integer),
        (r"0x[\da-fA-F_]+", Number.Integer),
        (r"\d[\d_]*(\.\d[\d_]*)?((e|E)[\d_]+)?(j|J)?", Number.Integer),
    ] + tokens["numbers"]

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tabideal, encoding=default_encoding):
        """Initialize the Python syntax highlighter."""
        Python3Lexer.__init__(self, stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=default_encoding)
        self.original_add_filter, self.add_filter = self.add_filter, lenient_add_filter

    def analyse_text(text):
        return shebang_matches(text, shebang_regex)
