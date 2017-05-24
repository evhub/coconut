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
import subprocess
import webbrowser
from copy import copy
from contextlib import contextmanager
from select import select
if PY26:
    import imp
else:
    import runpy
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
    style_env_var,
    mypy_path_env_var,
    tutorial_url,
    documentation_url,
    reserved_vars,
)
from coconut.exceptions import (
    CoconutException,
    CoconutInternalException,
    get_encoding,
)
from coconut.terminal import logger

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------


def openfile(filename, opentype="r+"):
    """Open a file using default_encoding."""
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


def launch_tutorial():
    """Opens the Coconut tutorial."""
    webbrowser.open(tutorial_url, 2)


def launch_documentation():
    """Opens the Coconut documentation."""
    webbrowser.open(documentation_url, 2)


def showpath(path):
    """Formats a path for displaying."""
    if logger.verbose:
        return os.path.abspath(path)
    else:
        path = os.path.relpath(path)
        if path.startswith(os.curdir + os.sep):
            path = path[len(os.curdir + os.sep):]
        return path


def is_special_dir(dirname):
    """Determines if a directory name is a special directory."""
    return dirname == os.curdir or dirname == os.pardir


def rem_encoding(code):
    """Removes encoding declarations from compiled code so it can be passed to exec."""
    old_lines = code.splitlines()
    new_lines = []
    for i in range(min(2, len(old_lines))):
        line = old_lines[i]
        if not (line.lstrip().startswith("#") and "coding" in line):
            new_lines.append(line)
    new_lines += old_lines[2:]
    return "\n".join(new_lines)


def exec_func(code, glob_vars, loc_vars=None):
    """Wrapper around exec."""
    if loc_vars is None:
        exec(code, glob_vars)
    else:
        exec(code, glob_vars, loc_vars)


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
    try:
        import psutil
    except ImportError:
        logger.warn("missing psutil; --jobs may not properly terminate",
                    extra="run 'pip install coconut[jobs]' to fix")
    else:
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
    """Split a path into a directory, name, and extensions."""
    dirpath, filename = os.path.split(path)
    # we don't use os.path.splitext here because we want all extensions,
    #  not just the last, to be put in exts
    name, exts = filename.split(os.extsep, 1)
    return dirpath, name, exts


def run_file(path):
    """Run a module from a path and return its variables."""
    if PY26:
        dirpath, name, _ = splitname(path)
        found = imp.find_module(name, [dirpath])
        module = imp.load_module("__main__", *found)
        return vars(module)
    else:
        return runpy.run_path(path, run_name="__main__")


def call_output(cmd, **kwargs):
    """Run command and read output."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    stdout, stderr, retcode = [], [], None
    while retcode is None:
        out, err = p.communicate()
        if out is not None:
            stdout.append(out.decode(get_encoding(sys.stdout)))
        if err is not None:
            stderr.append(err.decode(get_encoding(sys.stderr)))
        retcode = p.poll()
    return stdout, stderr, retcode


def run_cmd(cmd, show_output=True, raise_errs=True):
    """Runs a console command."""
    if not cmd or not isinstance(cmd, list):
        raise CoconutInternalException("console commands must be passed as non-empty lists")
    else:
        try:
            from shutil import which
        except ImportError:
            pass
        else:
            cmd[0] = which(cmd[0]) or cmd[0]
        logger.log_cmd(cmd)
        if show_output and raise_errs:
            return subprocess.check_call(cmd)
        elif show_output:
            return subprocess.call(cmd)
        else:
            stdout, stderr, _ = call_output(cmd)
            return "".join(stdout + stderr)


def set_mypy_path(mypy_path):
    """Prepends to MYPYPATH."""
    original = os.environ.get(mypy_path_env_var)
    if original is None:
        os.environ[mypy_path_env_var] = mypy_path
    elif not original.startswith(mypy_path):
        os.environ[mypy_path_env_var] = mypy_path + os.pathsep + original


def stdin_readable():
    """Determines whether stdin has any data to read."""
    if sys.stdin.isatty():
        return False
    try:
        return bool(select([sys.stdin], [], [], 0)[0])
    except OSError:
        pass
    if not sys.stdout.isatty():
        return False
    return True


#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------


class Prompt(object):
    """Manages prompting for code on the command line."""
    style = None
    multiline = default_multiline
    vi_mode = default_vi_mode
    mouse_support = default_mouse_support

    def __init__(self):
        """Set up the prompt."""
        if prompt_toolkit is not None:
            if style_env_var in os.environ:
                self.set_style(os.environ[style_env_var])
            else:
                self.style = default_style
            self.history = prompt_toolkit.history.InMemoryHistory()

    def set_style(self, style):
        """Set pygments syntax highlighting style."""
        if style == "none":
            self.style = None
        elif prompt_toolkit is None:
            raise CoconutException("syntax highlighting is not supported on this Python version")
        elif style == "list":
            print("Coconut Styles: none, " + ", ".join(pygments.styles.get_all_styles()))
            sys.exit(0)
        elif style in pygments.styles.get_all_styles():
            self.style = style
        else:
            raise CoconutException("unrecognized pygments style", style, extra="use '--style list' to show all valid styles")

    def input(self, more=False):
        """Prompts for code input."""
        sys.stdout.flush()
        if more:
            msg = more_prompt
        else:
            msg = main_prompt
        if self.style is not None:
            if prompt_toolkit is None:
                raise CoconutInternalException("cannot highlight style without prompt_toolkit", self.style)
            try:
                return prompt_toolkit.prompt(msg, **self.prompt_kwargs())
            except EOFError:
                raise  # issubclass(EOFError, Exception), so we have to do this
            except Exception:
                logger.print_exc()
                logger.show("Syntax highlighting failed; switching to --style none.")
                self.style = None
        return input(msg)

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

    def __init__(self, comp=None, exit=None, store=False, path=None):
        """Creates the executor."""
        self.exit = exit if exit is not None else sys.exit
        self.vars = self.build_vars(path)
        self.stored = [] if store else None
        if comp is not None:
            self.store(comp.getheader("package"))
            self.run(comp.getheader("code"), store=False)
            self.fix_pickle()

    def store(self, line):
        """Stores a line."""
        if self.stored is not None:
            self.stored.append(line)

    def build_vars(self, path=None):
        """Builds initial vars."""
        init_vars = {
            "__name__": "__main__",
            "__package__": None,
        }
        for var in reserved_vars:
            init_vars[var] = None
        if path is not None:
            init_vars["__file__"] = fixpath(path)
        return init_vars

    def fix_pickle(self):
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
        except BaseException:
            traceback.print_exc()
            if all_errors_exit:
                self.exit(1)

    def update_vars(self, global_vars):
        """Adds Coconut built-ins to given vars."""
        global_vars.update(self.vars)

    def run(self, code, use_eval=None, path=None, all_errors_exit=False, store=True):
        """Executes Python code."""
        if use_eval is None:
            run_func = interpret
        elif use_eval is True:
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
            if store:
                self.store(code)
            return result

    def run_file(self, path, all_errors_exit=True):
        """Executes a Python file."""
        path = fixpath(path)
        with self.handling_errors(all_errors_exit):
            module_vars = run_file(path)
            self.vars.update(module_vars)
            self.store("from " + splitname(path)[1] + " import *")

    def was_run_code(self, get_all=True):
        """Gets all the code that was run."""
        if self.stored is None:
            return ""
        else:
            if get_all:
                self.stored = ["\n".join(self.stored)]
            return self.stored[-1]


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
        logger.copy_from(self.logger)
        return getattr(self.base, self.method)(*args, **kwargs)
