#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from coconut.root import *  # NOQA

import sys
import os
import traceback
import functools
import time
import imp
import subprocess
from copy import copy
from contextlib import contextmanager
try:
    import readline  # improves built-in input
except ImportError:
    readline = None

if PY26 or (3,) <= sys.version_info < (3, 3):
    prompt_toolkit = None
else:
    import prompt_toolkit
    import pygments
    from coconut.highlighter import CoconutLexer

from coconut.constants import (
    fixpath,
    default_encoding,
    main_prompt,
    more_prompt,
    default_style,
    default_multiline,
    default_vi_mode,
    default_mouse_support,
    ensure_elapsed_time,
)
from coconut.logging import logger
from coconut.exceptions import CoconutException, CoconutInternalException

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------


def openfile(filename, opentype="r+"):
    """Returns an open file object."""
    return open(filename, opentype, encoding=default_encoding)  # using open from coconut.root


def writefile(openedfile, newcontents):
    """Sets the contents of a file."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(newcontents)


def readfile(openedfile):
    """Reads the contents of a file."""
    openedfile.seek(0)
    return str(openedfile.read())


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


def exec_func(code, in_vars):
    """Wrapper around exec."""
    exec(code, in_vars)


def interpret(code, in_vars):
    """Try to evaluate the given code, otherwise execute it."""
    try:
        result = eval(code, in_vars)
    except SyntaxError:
        pass  # exec code outside of exception context
    else:
        if result is not None:
            print(ascii(result))
        return  # don't also exec code
    exec_func(code, in_vars)


@contextmanager
def ensure_time_elapsed():
    """Ensures ensure_elapsed_time has elapsed."""
    if sys.version_info < (3, 2):
        try:
            yield
        finally:
            time.sleep(ensure_elapsed_time)
    else:
        yield


def handling_prompt_toolkit_errors(func):
    """Handles prompt_toolkit and pygments errors."""
    @functools.wraps(func)
    def handles_prompt_toolkit_errors_func(self, *args, **kwargs):
        if self.style is not None:
            try:
                return func(self, *args, **kwargs)
            except (KeyboardInterrupt, EOFError):
                raise
            except (Exception, AssertionError):
                logger.print_exc()
                logger.show("Syntax highlighting failed; switching to --style none.")
                self.style = None
        return func(self, *args, **kwargs)
    return handles_prompt_toolkit_errors_func


@contextmanager
def handling_broken_process_pool():
    """Handles BrokenProcessPool error."""
    if sys.version_info < (3, 3):
        yield
    else:
        from concurrent.futures.process import BrokenProcessPool
        try:
            yield
        except BrokenProcessPool:
            raise KeyboardInterrupt()


def kill_children():
    """Terminates all child processes."""
    import psutil
    master = psutil.Process()
    children = master.children(recursive=True)
    while children:
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass  # process is already dead, so do nothing
        children = master.children(recursive=True)


def splitname(path):
    """Split a path into a directory and a name."""
    dirpath, filename = os.path.split(path)
    name = filename.split(os.path.extsep, 1)[0]
    return dirpath, name


def run_cmd(cmd, show_output=True, raise_errs=True):
    """Runs a console command."""
    if not isinstance(cmd, list):
        raise CoconutInternalException("console commands must be passed as lists")
    else:
        if sys.version_info >= (3, 3):
            import shutil
            cmd[0] = shutil.which(cmd[0]) or cmd[0]
        logger.log_cmd(cmd)
        if show_output and raise_errs:
            return subprocess.check_call(cmd)
        elif not show_output:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        elif not raise_errs:
            return subprocess.call(cmd)
        else:
            raise CoconutInternalException("cannot not show console output and not raise errors")


@contextmanager
def in_mypy_path(mypy_path):
    """Temporarily adds to MYPYPATH."""
    original = os.environ.get("MYPYPATH")
    if original is None:
        os.environ["MYPYPATH"] = mypy_path
    else:
        os.environ["MYPYPATH"] += os.pathsep + mypy_path
    try:
        yield
    finally:
        if original is None:
            del os.environ["MYPYPATH"]
        else:
            os.environ["MYPYPATH"] = original


#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------


class Prompt(object):
    """Manages prompting for code on the command line."""
    if prompt_toolkit is None:
        style = None
    else:
        style = default_style
    multiline = default_multiline
    vi_mode = default_vi_mode
    mouse_support = default_mouse_support

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
        elif style == "list":
            logger.print("Coconut Styles: none, " + ", ".join(pygments.styles.get_all_styles()))
            sys.exit(0)
        elif style in pygments.styles.get_all_styles():
            self.style = style
        else:
            raise CoconutException("unrecognized pygments style", style, "try '--style list' to show all valid styles")

    @handling_prompt_toolkit_errors
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
            return prompt_toolkit.prompt(msg, **self.prompt_kwargs())

    def prompt_kwargs(self):
        """Gets prompt_toolkit.prompt keyword args."""
        return {
            "history": self.history,
            "multiline": self.multiline,
            "vi_mode": self.vi_mode,
            "mouse_support": self.mouse_support,
            "lexer": prompt_toolkit.layout.lexers.PygmentsLexer(CoconutLexer),
            "style": prompt_toolkit.styles.style_from_pygments(pygments.styles.get_style_by_name(self.style)),
        }


class Runner(object):
    """Compiled Python executor."""

    def __init__(self, comp=None, exit=None, path=None):
        """Creates the executor."""
        self.exit = sys.exit if exit is None else exit
        self.vars = self.build_vars(path)
        self.lines = []
        if comp is not None:
            self.lines.append(comp.headers("module"))
            self.run(comp.headers("code"), add_to_lines=False)
            self.fixpickle()

    def build_vars(self, path=None):
        """Builds initial vars."""
        init_vars = {
            "__name__": "__main__",
            "__package__": None,
        }
        if path is not None:
            init_vars["__file__"] = fixpath(path)
        return init_vars

    def fixpickle(self):
        """Fixes pickling of Coconut header objects."""
        from coconut import __coconut__
        for var in self.vars:
            if not var.startswith("__") and var in dir(__coconut__):
                self.vars[var] = getattr(__coconut__, var)

    @contextmanager
    def handling_errors(self, all_errors_exit=False):
        """Handles execution errors."""
        try:
            yield
        except SystemExit as err:
            self.exit(err.code)
        except:
            traceback.print_exc()
            if all_errors_exit:
                self.exit(1)

    def run(self, code, use_eval=None, path=None, all_errors_exit=False, add_to_lines=True):
        """Executes Python code."""
        if use_eval is None:
            run_func = interpret
        elif use_eval:
            run_func = eval
        else:
            run_func = exec_func
        with self.handling_errors(all_errors_exit):
            if path is None:
                result = run_func(code, self.vars)
            else:
                use_vars = self.build_vars(path)
                try:
                    result = run_func(code, use_vars)
                finally:
                    self.vars.update(use_vars)
            if add_to_lines:
                self.lines.append(code)
            return result

    def run_file(self, path, all_errors_exit=True):
        """Executes a Python file."""
        path, name = splitname(path)
        found = imp.find_module(name, [path])
        try:
            with self.handling_errors(all_errors_exit):
                module = imp.load_module("__main__", *found)
                self.vars.update(vars(module))
                self.lines.append("from " + name + " import *")
        finally:
            found[0].close()

    def was_run_code(self, get_all=True):
        """Gets all the code that was run."""
        if get_all:
            self.lines = ["\n".join(self.lines)]
        return self.lines[-1]


class multiprocess_wrapper(object):
    """Wrapper for a method that needs to be multiprocessed."""

    def __init__(self, base, method):
        """Creates new multiprocessable method."""
        self.recursion = sys.getrecursionlimit()
        self.logger = copy(logger)
        self.base, self.method = base, method

    def __call__(self, *args, **kwargs):
        """Sets up new process then calls the method."""
        sys.setrecursionlimit(self.recursion)
        with ensure_time_elapsed():
            logger.copy_from(self.logger)
            return getattr(self.base, self.method)(*args, **kwargs)
