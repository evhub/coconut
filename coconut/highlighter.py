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
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number, Punctuation, Generic, Other, Error
from pygments.lexer import words

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

builtins = (
    "reduce",
    "takewhile",
    "dropwhile",
    "tee",
    "count",
    "recursive",
    "datamaker",
    "consume",
    "parallel_map"
    )

operators = (
    r">>>",
    r"@",
    r"\$",
    r"`",
    r"::",
    r"\u2192",
    r"\u21a6",
    r"\u21a4",
    r"\u22c5",
    r"\u2191",
    r"\xf7",
    r"\u2212",
    r"\u207b",
    r"\xac",
    r"\u2260",
    r"\u2264",
    r"\u2265",
    r"\u2227",
    r"\u2229",
    r"\u2228",
    r"\u222a",
    r"\u22bb",
    r"\u2295",
    r"\xab",
    r"\xbb",
    r"\xd7",
    r"\u2026"
    )

#-----------------------------------------------------------------------------------------------------------------------
# LEXERS:
#-----------------------------------------------------------------------------------------------------------------------

def lenient_add_filter(self, *args, **kwargs):
    """Disables the raiseonerror filter."""
    if len(args) >= 1 and args[0] != "raiseonerror":
        self.original_add_filter(*args, **kwargs)

class pylexer(Python3Lexer):
    """Coconut-style Python syntax highlighter."""
    name = "coc_python"
    aliases = ["coc_python", "coc_py", "coc_python3", "coc_py3"]
    filenames = []

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tabideal, encoding=encoding):
        """Initialize the Python syntax highlighter."""
        Python3Lexer.__init__(self, stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=encoding)
        self.original_add_filter, self.add_filter = self.add_filter, lenient_add_filter

class pyconlexer(PythonConsoleLexer):
    """Coconut-style Python console syntax highlighter."""
    name = "coc_pycon"
    aliases = ["coc_pycon", "coc_pycon3"]
    filenames = []

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tabideal, encoding=encoding, python3=True):
        """Initialize the Python console syntax highlighter."""
        PythonConsoleLexer.__init__(self, stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=encoding, python3=python3)
        self.original_add_filter, self.add_filter = self.add_filter, lenient_add_filter

class coclexer(Python3Lexer):
    """Coconut syntax highlighter."""
    name = "coconut"
    aliases = ["coconut", "coc", "coconutcon"]
    filenames = ["*"+code_ext]

    tokens = Python3Lexer.tokens.copy()
    tokens["root"] = [
        (r"|".join(operators), Operator)
    ] + tokens["root"]
    tokens["keywords"] = [
        (words(keywords, suffix="r\b"), Keyword),
        (words(reserved_vars, prefix=r"(?<!\\)", suffix=r"\b"), Keyword),
        (words(const_vars, suffix=r"\b"), Keyword.Constant)
    ]
    tokens["builtins"] = tokens["builtins"] + [
        (words(builtins, prefix=r"(?<!\.)", suffix=r"\b"), Name.Builtin),
        (r"(?<!\.)MatchError\b", Name.Exception)
    ]
    magicvars = [
        (r"(?<!\.)__coconut_version__\b", Name.Variable.Magic),
        (r"__coconut_is_lazy__\b", Name.Variable.Magic)
    ]
    if "magicvars" in tokens:
        tokens["magicvars"] = tokens["magicvars"] + magicvars
    elif "magicfuncs" in tokens:
        tokens["magicfuncs"] = tokens["magicfuncs"] + magicvars
    else:
        tokens["builtins"] = tokens["builtins"] + magicvars
    tokens["numbers"] = [
        (r"\d[\d_]*(\.\d[\d_]*)?", Number.Integer),
        (r"0b[01_]+", Number.Integer),
        (r"0o[0-7_]+", Number.Integer),
        (r"0x[\da-fA-F_]+", Number.Integer)
    ] + tokens["numbers"]

    def __init__(self, stripnl=False, stripall=False, ensurenl=True, tabsize=tabideal, encoding=encoding):
        """Initialize the Python syntax highlighter."""
        Python3Lexer.__init__(self, stripnl=stripnl, stripall=stripall, ensurenl=ensurenl, tabsize=tabsize, encoding=encoding)
        self.original_add_filter, self.add_filter = self.add_filter, lenient_add_filter
