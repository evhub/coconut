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
import imp
from copy import copy
from contextlib import contextmanager
from select import select
if not PY26:
    import runpy
try:
    # just importing readline improves built-in input()
    import readline  # NOQA
except ImportError:
    pass

from coconut.constants import (
    fixpath,
    default_encoding,
    main_prompt,
    more_prompt,
    default_style,
    default_histfile,
    prompt_multiline,
    prompt_vi_mode,
    prompt_mouse_support,
    prompt_wrap_lines,
    prompt_history_search,
    style_env_var,
    mypy_path_env_var,
    histfile_env_var,
    tutorial_url,
    documentation_url,
    reserved_vars,
    num_added_tb_layers,
    minimum_recursion_limit,
    oserror_retcode,
    WINDOWS,
)
from coconut.exceptions import (
    CoconutException,
    get_encoding,
    internal_assert,
)
from coconut.terminal import (
    logger,
    complain,
)

try:
    import prompt_toolkit
    import pygments
    import pygments.styles
    from coconut.highlighter import CoconutLexer
except ImportError:
    prompt_toolkit = None
except KeyError:
    complain(ImportError(
        "detected outdated pygments version (run 'pip install --upgrade pygments' to fix)",
    ))
    prompt_toolkit = None

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------


def openfile(filename, opentype="r+"):
    """Open a file using default_encoding."""
    return open(filename, opentype, encoding=default_encoding)  # using open from coconut.root


def writefile(openedfile, newcontents):
    """Set the contents of a file."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(newcontents)


def readfile(openedfile):
    """Read the contents of a file."""
    openedfile.seek(0)
    return str(openedfile.read())


def launch_tutorial():
    """Open the Coconut tutorial."""
    import webbrowser  # this is expensive, so only do it here
    webbrowser.open(tutorial_url, 2)


def launch_documentation():
    """Open the Coconut documentation."""
    import webbrowser  # this is expensive, so only do it here
    webbrowser.open(documentation_url, 2)


def showpath(path):
    """Format a path for displaying."""
    if logger.verbose:
        return os.path.abspath(path)
    else:
        path = os.path.relpath(path)
        if path.startswith(os.curdir + os.sep):
            path = path[len(os.curdir + os.sep):]
        return path


def is_special_dir(dirname):
    """Determine if a directory name is a special directory."""
    return dirname == os.curdir or dirname == os.pardir


def rem_encoding(code):
    """Remove encoding declarations from compiled code so it can be passed to exec."""
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
    """Handle BrokenProcessPool error."""
    if sys.version_info < (3, 3):
        yield
    else:
        from concurrent.futures.process import BrokenProcessPool
        try:
            yield
        except BrokenProcessPool:
            raise KeyboardInterrupt()


def kill_children():
    """Terminate all child processes."""
    try:
        import psutil
    except ImportError:
        logger.warn(
            "missing psutil; --jobs may not properly terminate",
            extra="run 'pip install coconut[jobs]' to fix",
        )
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


def call_output(cmd, stdin=None, encoding_errors="replace", **kwargs):
    """Run command and read output."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    stdout, stderr, retcode = [], [], None
    while retcode is None:
        if stdin is not None:
            logger.log_prefix("<0 ", stdin.rstrip())
        raw_out, raw_err = p.communicate(stdin)
        stdin = None

        out = raw_out.decode(get_encoding(sys.stdout), encoding_errors) if raw_out else ""
        if out:
            logger.log_prefix("1> ", out.rstrip())
        stdout.append(out)

        err = raw_err.decode(get_encoding(sys.stderr), encoding_errors) if raw_err else ""
        if err:
            logger.log_prefix("2> ", err.rstrip())
        stderr.append(err)

        retcode = p.poll()
    return stdout, stderr, retcode


def run_cmd(cmd, show_output=True, raise_errs=True, **kwargs):
    """Run a console command.

    When show_output=True, prints output and returns exit code, otherwise returns output.
    When raise_errs=True, raises a subprocess.CalledProcessError if the command fails.
    """
    internal_assert(cmd and isinstance(cmd, list), "console commands must be passed as non-empty lists")
    try:
        from shutil import which
    except ImportError:
        pass
    else:
        cmd[0] = which(cmd[0]) or cmd[0]
    logger.log_cmd(cmd)
    try:
        if show_output and raise_errs:
            return subprocess.check_call(cmd, **kwargs)
        elif show_output:
            return subprocess.call(cmd, **kwargs)
        else:
            stdout, stderr, retcode = call_output(cmd, **kwargs)
            output = "".join(stdout + stderr)
            if retcode and raise_errs:
                raise subprocess.CalledProcessError(retcode, cmd, output=output)
            return output
    except OSError:
        logger.log_exc()
        if raise_errs:
            raise subprocess.CalledProcessError(oserror_retcode, cmd)
        elif show_output:
            return oserror_retcode
        else:
            return ""


def set_mypy_path(mypy_path):
    """Prepend to MYPYPATH."""
    original = os.environ.get(mypy_path_env_var)
    if original is None:
        new_mypy_path = mypy_path
    elif not original.startswith(mypy_path):
        new_mypy_path = mypy_path + os.pathsep + original
    else:
        new_mypy_path = None
    if new_mypy_path is not None:
        logger.log(mypy_path_env_var + ":", new_mypy_path)
        os.environ[mypy_path_env_var] = new_mypy_path


def stdin_readable():
    """Determine whether stdin has any data to read."""
    if not WINDOWS:
        try:
            return bool(select([sys.stdin], [], [], 0)[0])
        except Exception:
            logger.log_exc()
    try:
        return not sys.stdin.isatty()
    except Exception:
        logger.log_exc()
    return False


def set_recursion_limit(limit):
    """Set the Python recursion limit."""
    if limit < minimum_recursion_limit:
        raise CoconutException("--recursion-limit must be at least " + str(minimum_recursion_limit))
    sys.setrecursionlimit(limit)


def _raise_ValueError(msg):
    raise ValueError(msg)


def canparse(argparser, args):
    """Determines if argparser can parse args."""
    old_error_method = argparser.error
    argparser.error = _raise_ValueError
    try:
        argparser.parse_args(args)
    except ValueError:
        return False
    else:
        return True
    finally:
        argparser.error = old_error_method


#-----------------------------------------------------------------------------------------------------------------------
# CLASSES:
#-----------------------------------------------------------------------------------------------------------------------

class Prompt(object):
    """Manages prompting for code on the command line."""
    style = None
    multiline = prompt_multiline
    vi_mode = prompt_vi_mode
    mouse_support = prompt_mouse_support
    wrap_lines = prompt_wrap_lines
    history_search = prompt_history_search

    def __init__(self):
        """Set up the prompt."""
        if prompt_toolkit is not None:
            if style_env_var in os.environ:
                self.set_style(os.environ[style_env_var])
            else:
                self.style = default_style

            self.set_history_file(os.environ.get(histfile_env_var, default_histfile))

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

    def set_history_file(self, path):
        """Set path to history file. "" produces no file."""
        assert isinstance(path, str)

        if path == "":
            self.history = prompt_toolkit.history.InMemoryHistory()
        else:
            self.history = prompt_toolkit.history.FileHistory(os.path.expanduser(path))

    def input(self, more=False):
        """Prompt for code input."""
        sys.stdout.flush()
        if more:
            msg = more_prompt
        else:
            msg = main_prompt
        if self.style is not None:
            internal_assert(prompt_toolkit is not None, "without prompt_toolkit cannot highlight style", self.style)
            try:
                return prompt_toolkit.prompt(msg, **self.prompt_kwargs())
            except EOFError:
                raise  # issubclass(EOFError, Exception), so we have to do this
            except (Exception, AssertionError):
                logger.display_exc()
                logger.show_sig("Syntax highlighting failed; switching to --style none.")
                self.style = None
        return input(msg)

    def prompt_kwargs(self):
        """Get prompt_toolkit.prompt keyword args."""
        return {
            "history": self.history,
            "multiline": self.multiline,
            "vi_mode": self.vi_mode,
            "mouse_support": self.mouse_support,
            "wrap_lines": self.wrap_lines,
            "enable_history_search": self.history_search,
            "lexer": prompt_toolkit.layout.lexers.PygmentsLexer(CoconutLexer),
            "style": prompt_toolkit.styles.style_from_pygments(pygments.styles.get_style_by_name(self.style)),
        }


class Runner(object):
    """Compiled Python executor."""

    def __init__(self, comp=None, exit=sys.exit, store=False, path=None):
        """Create the executor."""
        # allow direct importing of Coconut files
        import coconut.convenience  # NOQA
        self.exit = exit
        self.vars = self.build_vars(path)
        self.stored = [] if store else None
        if comp is not None:
            self.store(comp.getheader("package"))
            self.run(comp.getheader("code"), store=False)
            self.fix_pickle()

    @staticmethod
    def build_vars(path=None):
        """Build initial vars."""
        init_vars = {
            "__name__": "__main__",
            "__package__": None,
            "reload": imp.reload,
        }
        if path is not None:
            init_vars["__file__"] = fixpath(path)
        # put reserved_vars in for auto-completion purposes
        for var in reserved_vars:
            init_vars[var] = None
        return init_vars

    def store(self, line):
        """Store a line."""
        if self.stored is not None:
            self.stored.append(line)

    def fix_pickle(self):
        """Fix pickling of Coconut header objects."""
        from coconut import __coconut__  # this is expensive, so only do it here
        for var in self.vars:
            if not var.startswith("__") and var in dir(__coconut__):
                self.vars[var] = getattr(__coconut__, var)

    @contextmanager
    def handling_errors(self, all_errors_exit=False):
        """Handle execution errors."""
        try:
            yield
        except SystemExit as err:
            self.exit(err.code)
        except BaseException:
            etype, value, tb = sys.exc_info()
            for _ in range(num_added_tb_layers):
                if tb is None:
                    break
                tb = tb.tb_next
            traceback.print_exception(etype, value, tb)
            if all_errors_exit:
                self.exit(1)

    def update_vars(self, global_vars):
        """Add Coconut built-ins to given vars."""
        global_vars.update(self.vars)

    def run(self, code, use_eval=None, path=None, all_errors_exit=False, store=True):
        """Execute Python code."""
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
        """Execute a Python file."""
        path = fixpath(path)
        with self.handling_errors(all_errors_exit):
            module_vars = run_file(path)
            self.vars.update(module_vars)
            self.store("from " + splitname(path)[1] + " import *")

    def was_run_code(self, get_all=True):
        """Get all the code that was run."""
        if self.stored is None:
            return ""
        else:
            if get_all:
                self.stored = ["\n".join(self.stored)]
            return self.stored[-1]


class multiprocess_wrapper(object):
    """Wrapper for a method that needs to be multiprocessed."""

    def __init__(self, base, method):
        """Create new multiprocessable method."""
        self.recursion = sys.getrecursionlimit()
        self.logger = copy(logger)
        self.base, self.method = base, method

    def __call__(self, *args, **kwargs):
        """Set up new process then calls the method."""
        sys.setrecursionlimit(self.recursion)
        logger.copy_from(self.logger)
        return getattr(self.base, self.method)(*args, **kwargs)
