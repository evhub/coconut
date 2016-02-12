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
        print(args, kwargs)
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
        print(args, kwargs)
        if len(args) >= 1 and args[0] != "raiseonerror":
            super(pyconlexer, self).add_filter(*args, **kwargs)

class coclexer(pylexer):
    """Coconut syntax highlighter."""
    name = "coconut"
    aliases = ["coc", "coconut", "force_coc" "force_coconut"]
    filenames = ["*"+code_ext]

    tokens["keywords"] = [
        (words(keywords + reserved_vars, suffix=r"\b"), Keyword),
        (words(const_vars, suffix=r"\b"), Keyword.Constant),
    ]
    tokens["backtick"] = [("`.*?`", String.Backtick)]
    tokens["name"].append((r"[$\\]", Operator))

class cocconlexer(pyconlexer):
    """Coconut console syntax highlighter."""
    name = "coconutcon"
    aliases = ["coccon", "coconutcon", "force_coccon", "force_coconutcon"]
    filenames = []

    def get_tokens_unprocessed(self, text):
        if not self.python3:
            raise CoconutException("Coconut code is always Python 3")
        pylexer = coclexer(**self.options)
        tblexer = Python3TracebackLexer(**self.options)

        # taken with modifications from pygments/lexers/python.py under the BSD
        curcode = ""
        insertions = []
        curtb = ""
        tbindex = 0
        tb = 0
        for match in line_re.finditer(text):
            line = match.group()
            if line.startswith(default_prompt) or line.startswith(default_moreprompt):
                tb = 0
                insertions.append((len(curcode), [(0, Generic.Prompt, line[:4])]))
                curcode += line[4:]
            elif not line.rstrip() and not tb:
                curcode += line[3:]
            else:
                if curcode:
                    for item in do_insertions(insertions, pylexer.get_tokens_unprocessed(curcode)):
                        yield item
                    curcode = ""
                    insertions = []
                if line.startswith("Coconut"):
                    yield match.start(), Name, line
                elif (line.startswith("Traceback (most recent call last):")
                        or re.match('  File "[^"]+", line \\d+\\n$', line)):
                    tb = 1
                    curtb = line
                    tbindex = match.start()
                elif line == "KeyboardInterrupt\n":
                    yield match.start(), Name.Class, line
                elif tb:
                    curtb += line
                    if not line.startswith(" "):
                        tb = 0
                        for i, t, v in tblexer.get_tokens_unprocessed(curtb):
                            yield tbindex+i, t, v
                        curtb = ""
                else:
                    yield match.start(), Generic.Output, line
        if curcode:
            for item in do_insertions(insertions, pylexer.get_tokens_unprocessed(curcode)):
                yield item
        if curtb:
            for i, t, v in tblexer.get_tokens_unprocessed(curtb):
                yield tbindex+i, t, v
