#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: Utility functions for the main command module.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

import sys
import os
import traceback
from copy import copy
try:
    import readline # improves built-in input
except ImportError:
    readline = None

if PY26 or (3,) <= sys.version_info < (3, 3):
    prompt_toolkit = None
else:
    import prompt_toolkit
    import pygments
    from coconut.highlighter import CoconutLexer

from coconut.constants import (
    default_encoding,
    main_prompt,
    more_prompt,
    default_style,
    use_vi_mode,
    use_mouse_support,
)
from coconut.logging import logger
from coconut.exceptions import CoconutException, CoconutInternalException

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------

def openfile(filename, opentype="r+"):
    """Returns an open file object."""
    return open(filename, opentype, encoding=default_encoding) # using open from coconut.root

def writefile(openedfile, newcontents):
    """Sets the contents of a file."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(newcontents)

def readfile(openedfile):
    """Reads the contents of a file."""
    openedfile.seek(0)
    return str(openedfile.read())

def fixpath(path):
    """Uniformly formats a path."""
    return os.path.normpath(os.path.realpath(path))

def showpath(path):
    """Formats a path for displaying."""
    if logger.verbose:
        return os.path.abspath(path)
    else:
        path = os.path.relpath(path)
        if path.startswith(os.curdir + os.sep):
            path = path[len(os.curdir + os.sep):]
        return path

def rem_encoding(code):
    """Removes encoding declarations from Python code so it can be passed to exec."""
    old_lines = code.splitlines()
    new_lines = []
    for i in range(min(2, len(old_lines))):
        line = old_lines[i]
        if not (line.startswith("#") and "coding" in line):
            new_lines.append(line)
    new_lines += old_lines[2:]
    return "\n".join(new_lines)

def try_eval(code, in_vars):
    """Try to evaluate the given code, otherwise execute it."""
    try:
        return eval(code, in_vars)
    except SyntaxError:
        pass # exit the exception context before executing code
    exec(code, in_vars)
    return None

#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------

class Prompt(object):
    """Manages prompting for code on the command line."""
    if prompt_toolkit is None:
        style = None
    else:
        style = default_style

    def __init__(self):
        """Set up the prompt."""
        if prompt_toolkit is not None:
            self.history = prompt_toolkit.history.InMemoryHistory()

    def set_style(self, style):
        """Set pygments syntax highlighting style."""
        if style == "none":
            self.style = None
        elif prompt_toolkit is None:
            raise CoconutException("syntax highlighting is not supported on this Python version")
        elif style in pygments.styles.get_all_styles():
            self.style = style
        else:
            raise CoconutException("unrecognized pygments style", style)

    def input(self, more=False):
        """Prompts for code input."""
        if more:
            msg = more_prompt
        else:
            msg = main_prompt
        if self.style is None:
            return input(msg)
        elif prompt_toolkit is None:
            raise CoconutInternalException("cannot highlight style without prompt_toolkit", self.style)
        else:
            return prompt_toolkit.prompt(
                msg,
                history=self.history,
                lexer=prompt_toolkit.layout.lexers.PygmentsLexer(CoconutLexer),
                style=prompt_toolkit.styles.style_from_pygments(pygments.styles.get_style_by_name(self.style)),
                vi_mode=use_vi_mode,
                mouse_support=use_mouse_support,
            )


class Runner(object):
    """Compiled Python executor."""
    def __init__(self, comp=None, exit=None, path=None):
        """Creates the executor."""
        self.exit = exit
        self.vars = {"__name__": "__main__"}
        if path is not None:
            self.vars["__file__"] = fixpath(path)
        if comp is not None:
            self.run(comp.headers("code"))
            self.fixpickle()

    def fixpickle(self):
        """Fixes pickling of Coconut header objects."""
        from coconut import __coconut__
        for var in self.vars:
            if not var.startswith("__") and var in dir(__coconut__):
                self.vars[var] = getattr(__coconut__, var)

    def run(self, code, err=False, run_func=None):
        """Executes Python code."""
        try:
            if run_func is None:
                exec(code, self.vars)
            else:
                return run_func(code, self.vars)
        except (Exception, KeyboardInterrupt):
            if err:
                raise
            else:
                traceback.print_exc()
        except SystemExit:
            if self.exit is None:
                raise
            else:
                self.exit()
        return None

class multiprocess_wrapper(object):
    """Wrapper for a method that needs to be multiprocessed."""

    def __init__(self, base, method):
        """Creates new multiprocessable method."""
        self.recursion, self.logger, self.base, self.method = sys.getrecursionlimit(), copy(logger), base, method

    def __call__(self, *args, **kwargs):
        """Sets up new process then calls the method."""
        sys.setrecursionlimit(self.recursion)
        logger.copy_from(self.logger)
        return getattr(self.base, self.method)(*args, **kwargs)
