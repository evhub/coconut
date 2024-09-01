#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: Utility functions for the main command module.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os
import subprocess
import shutil
import threading
import json
from select import select
from contextlib import contextmanager
from functools import partial
if PY2:
    import __builtin__ as builtins
    import Queue as queue
else:
    import builtins
    import queue

from coconut.root import _coconut_exec
from coconut.terminal import (
    logger,
    complain,
    internal_assert,
    isatty,
)
from coconut.exceptions import (
    CoconutException,
    BaseCoconutException,
)
from coconut.util import (
    pickleable_obj,
    get_encoding,
    get_clock_time,
    assert_remove_prefix,
    univ_open,
)
from coconut.constants import (
    WINDOWS,
    CPYTHON,
    PY26,
    PY32,
    PY34,
    fixpath,
    base_dir,
    main_prompt,
    more_prompt,
    default_style,
    prompt_histfile,
    prompt_multiline,
    prompt_vi_mode,
    prompt_wrap_lines,
    prompt_history_search,
    prompt_use_suggester,
    style_env_var,
    mypy_path_env_var,
    tutorial_url,
    documentation_url,
    reserved_vars,
    minimum_recursion_limit,
    oserror_retcode,
    base_stub_dir,
    stub_dir_names,
    installed_stub_dir,
    interpreter_uses_auto_compilation,
    interpreter_uses_coconut_breakpoint,
    interpreter_compiler_var,
    must_use_specific_target_builtins,
    kilobyte,
    min_stack_size_kbs,
    coconut_base_run_args,
    high_proc_prio,
    call_timeout,
    use_fancy_call_output,
    extra_pyright_args,
    pyright_config_file,
    tabideal,
)

if PY26:
    import imp
else:
    import runpy
if PY34:
    from importlib import reload
else:
    from imp import reload
try:
    # just importing readline improves built-in input()
    import readline  # NOQA
except ImportError:
    pass

try:
    import prompt_toolkit
    try:
        # prompt_toolkit v2
        from prompt_toolkit.lexers.pygments import PygmentsLexer
        from prompt_toolkit.styles.pygments import style_from_pygments_cls
        from prompt_toolkit.completion import FuzzyWordCompleter
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    except ImportError:
        # prompt_toolkit v1
        from prompt_toolkit.layout.lexers import PygmentsLexer
        from prompt_toolkit.styles import style_from_pygments as style_from_pygments_cls
        from prompt_toolkit.contrib.completers import WordCompleter as FuzzyWordCompleter
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

    import pygments
    import pygments.styles

    from coconut.highlighter import CoconutLexer
except ImportError:
    complain(
        ImportError(
            "failed to import prompt_toolkit and/or pygments (run '{python} -m pip install --upgrade prompt_toolkit pygments' to fix)".format(python=sys.executable),
        ),
    )
    prompt_toolkit = None
except KeyError:
    complain(
        ImportError(
            "detected outdated pygments version (run '{python} -m pip install --upgrade pygments' to fix)".format(python=sys.executable),
        ),
    )
    prompt_toolkit = None
try:
    import psutil
except ImportError:
    psutil = None


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def writefile(openedfile, newcontents, in_json=False, **kwargs):
    """Set the entire contents of a file regardless of current position."""
    openedfile.seek(0)
    openedfile.truncate()
    if in_json:
        json.dump(newcontents, openedfile, **kwargs)
    else:
        openedfile.write(newcontents, **kwargs)


def readfile(openedfile, in_json=False, **kwargs):
    """Read the entire contents of a file regardless of current position."""
    openedfile.seek(0)
    if in_json:
        return json.load(openedfile, **kwargs)
    else:
        return str(openedfile.read(**kwargs))


def open_website(url):
    """Open a website in the default web browser."""
    import webbrowser  # this is expensive, so only do it here
    webbrowser.open(url, 2)


def launch_tutorial():
    """Open the Coconut tutorial."""
    open_website(tutorial_url)


def launch_documentation():
    """Open the Coconut documentation."""
    open_website(documentation_url)


def showpath(path):
    """Format a path for displaying."""
    if logger.verbose:
        return os.path.abspath(path)
    else:
        path = os.path.relpath(path)
        if path.startswith(os.curdir + os.sep):
            path = assert_remove_prefix(path, os.curdir + os.sep)
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


def interpret(code, in_vars):
    """Try to evaluate the given code, otherwise execute it."""
    try:
        result = eval(code, in_vars)
    except SyntaxError:
        pass  # exec code outside of exception context
    else:
        if result is not None:
            logger.print(ascii(result))
        return result  # don't also exec code
    _coconut_exec(code, in_vars)


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
            logger.log_exc()
            raise BaseCoconutException("broken process pool (if this is due to a stack overflow, you may be able to fix by re-running with a larger '--stack-size', otherwise try disabling multiprocessing with '--jobs 0')")


def kill_children():
    """Terminate all child processes."""
    if psutil is None:
        logger.warn(
            "missing psutil; --jobs may not properly terminate",
            extra="run '{python} -m pip install psutil' to fix".format(python=sys.executable),
        )
    else:
        parent = psutil.Process()
        children = parent.children(recursive=True)
        while children:
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass  # process is already dead, so do nothing
            children = parent.children(recursive=True)


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


def interrupt_thread(thread, exctype=OSError):
    """Attempt to interrupt the given thread."""
    if not CPYTHON:
        return False
    if thread is None or not thread.is_alive():
        return True
    import ctypes
    tid = ctypes.c_long(thread.ident)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid,
        ctypes.py_object(exctype),
    )
    if res == 0:
        return False
    elif res == 1:
        return True
    else:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        return False


def readline_to_queue(file_obj, q):
    """Read a line from file_obj and put it in the queue."""
    if not is_empty_pipe(file_obj, False):
        try:
            q.put(file_obj.readline())
        except OSError:
            pass


def call_output(cmd, stdin=None, encoding_errors="replace", color=None, **kwargs):
    """Run command and read output."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, **kwargs)

    stdout_q = queue.Queue()
    stderr_q = queue.Queue()

    if not use_fancy_call_output:
        raw_stdout, raw_stderr = p.communicate(stdin)
        stdout_q.put(raw_stdout)
        stderr_q.put(raw_stderr)
        stdin = None

    if stdin is not None:
        logger.log_prefix("STDIN < ", stdin.rstrip())
        p.stdin.write(stdin)

    # list for mutability
    stdout_t_obj = [None]
    stderr_t_obj = [None]

    stdout, stderr, retcode = [], [], None
    checking_stdout = True  # alternate between stdout and stderr
    try:
        while (
            retcode is None
            or not stdout_q.empty()
            or not stderr_q.empty()
            or not is_empty_pipe(p.stdout, True)
            or not is_empty_pipe(p.stderr, True)
        ):
            if checking_stdout:
                proc_pipe = p.stdout
                sys_pipe = sys.stdout
                q = stdout_q
                t_obj = stdout_t_obj
                log_func = logger.log_stdout
                out_list = stdout
            else:
                proc_pipe = p.stderr
                sys_pipe = sys.stderr
                q = stderr_q
                t_obj = stderr_t_obj
                log_func = logger.log
                out_list = stderr

            retcode = p.poll()

            if (
                retcode is None
                or not is_empty_pipe(proc_pipe, True)
            ):
                if t_obj[0] is None or not t_obj[0].is_alive():
                    t_obj[0] = threading.Thread(target=readline_to_queue, args=(proc_pipe, q))
                    t_obj[0].daemon = True
                    t_obj[0].start()

                t_obj[0].join(timeout=call_timeout)

            try:
                raw_out = q.get(block=False)
            except queue.Empty:
                raw_out = None

            out = raw_out.decode(get_encoding(sys_pipe), encoding_errors) if raw_out else ""

            if out:
                log_func(out, color=color, end="")
                out_list.append(out)

            checking_stdout = not checking_stdout
    finally:
        interrupt_thread(stdout_t_obj[0])
        interrupt_thread(stderr_t_obj[0])

    return "".join(stdout), "".join(stderr), retcode


def run_cmd(cmd, show_output=True, raise_errs=True, **kwargs):
    """Run a console command.

    When show_output=True, prints output and returns exit code, otherwise returns output.
    When raise_errs=True, raises a subprocess.CalledProcessError if the command fails.
    """
    internal_assert(cmd and isinstance(cmd, list), "console commands must be passed as non-empty lists")
    if hasattr(shutil, "which"):
        cmd[0] = shutil.which(cmd[0]) or cmd[0]
    logger.log_cmd(cmd)
    try:
        if show_output and raise_errs:
            return subprocess.check_call(cmd, **kwargs)
        elif show_output:
            return subprocess.call(cmd, **kwargs)
        else:
            stdout, stderr, retcode = call_output(cmd, **kwargs)
            output = stdout + stderr
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


def unlink(link_path):
    """Remove a symbolic link if one exists. Return whether anything was done."""
    if os.path.islink(link_path):
        os.unlink(link_path)
        return True
    return False


def rm_dir_or_link(dir_to_rm):
    """Safely delete a directory without deleting the contents of symlinks."""
    if not unlink(dir_to_rm) and os.path.exists(dir_to_rm):
        if PY2:  # shutil.rmtree doesn't seem to be fully safe on Python 2
            try:
                os.rmdir(dir_to_rm)
            except OSError:
                logger.warn_exc()
        elif WINDOWS:
            try:
                os.rmdir(dir_to_rm)
            except OSError:
                logger.log_exc()
                shutil.rmtree(dir_to_rm)
        else:
            shutil.rmtree(dir_to_rm)


def symlink(link_to, link_from):
    """Link link_from to the directory link_to universally."""
    rm_dir_or_link(link_from)
    try:
        if PY32:
            os.symlink(link_to, link_from, target_is_directory=True)
        elif not WINDOWS:
            os.symlink(link_to, link_from)
    except OSError:
        logger.log_exc()
    if not os.path.islink(link_from):
        shutil.copytree(link_to, link_from)


def install_stubs():
    """Properly symlink stub files for type-checking purposes."""
    # unlink stub_dirs so we know rm_dir_or_link won't clear them
    for stub_name in stub_dir_names:
        unlink(os.path.join(base_stub_dir, stub_name))

    # clean out the installed_stub_dir (which shouldn't follow symlinks,
    #  but we still do the previous unlinking just to be sure)
    rm_dir_or_link(installed_stub_dir)

    # recreate installed_stub_dir
    os.makedirs(installed_stub_dir)

    # link stub dirs into the installed_stub_dir
    for stub_name in stub_dir_names:
        current_stub = os.path.join(base_stub_dir, stub_name)
        install_stub = os.path.join(installed_stub_dir, stub_name)
        symlink(current_stub, install_stub)

    return installed_stub_dir


def set_env_var(name, value):
    """Universally set an environment variable."""
    os.environ[py_str(name)] = py_str(value)


def set_mypy_path(ensure_stubs=True):
    """Put Coconut stubs in MYPYPATH."""
    if ensure_stubs:
        install_stubs()
    # mypy complains about the path if we don't use / over \
    install_dir = installed_stub_dir.replace(os.sep, "/")
    original = os.getenv(mypy_path_env_var)
    if original is None:
        new_mypy_path = install_dir
    elif not original.startswith(install_dir):
        new_mypy_path = install_dir + ":" + original
    else:
        new_mypy_path = None
    if new_mypy_path is not None:
        set_env_var(mypy_path_env_var, new_mypy_path)
    logger.log_func(lambda: (mypy_path_env_var, "=", os.getenv(mypy_path_env_var)))
    return install_dir


def update_pyright_config(python_version=None):
    """Save an updated pyrightconfig.json."""
    stubs_dir = install_stubs()
    update_existing = os.path.exists(pyright_config_file)
    with univ_open(pyright_config_file, "r+" if update_existing else "w") as config_file:
        if update_existing:
            try:
                config = readfile(config_file, in_json=True)
            except ValueError:
                raise CoconutException("invalid JSON syntax in " + repr(pyright_config_file))
        else:
            config = extra_pyright_args.copy()
        if "extraPaths" not in config:
            config["extraPaths"] = []
        if stubs_dir not in config["extraPaths"]:
            config["extraPaths"].append(stubs_dir)
        if python_version is not None:
            config["pythonVersion"] = python_version
        writefile(config_file, config, in_json=True, indent=tabideal)
    return pyright_config_file


def is_empty_pipe(pipe, default=None):
    """Determine if the given pipe file object is empty."""
    if pipe.closed:
        return True
    if not WINDOWS:
        try:
            return not select([pipe], [], [], 0)[0]
        except Exception:
            logger.log_exc()
    return default


def stdin_readable():
    """Determine whether stdin has any data to read."""
    stdin_is_empty = is_empty_pipe(sys.stdin)
    if stdin_is_empty is not None:
        return not stdin_is_empty
    # by default assume not readable
    return not isatty(sys.stdin, default=True)


def set_recursion_limit(limit):
    """Set the Python recursion limit."""
    if limit < minimum_recursion_limit:
        raise CoconutException("--recursion-limit must be at least " + str(minimum_recursion_limit))
    sys.setrecursionlimit(limit)


def _raise_ValueError(msg):
    """Raise ValueError(msg)."""
    raise ValueError(msg)


def can_parse(argparser, args):
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


def subpath(path, base_path):
    """Check if path is a subpath of base_path."""
    path = fixpath(path)
    base_path = fixpath(base_path)
    return path == base_path or path.startswith(base_path + os.sep)


def invert_mypy_arg(arg):
    """Convert --arg into --no-arg or equivalent."""
    if arg.startswith("--no-"):
        return "--" + assert_remove_prefix(arg, "--no-")
    elif arg.startswith("--allow-"):
        return "--disallow-" + assert_remove_prefix(arg, "--allow-")
    elif arg.startswith("--disallow-"):
        return "--allow-" + assert_remove_prefix(arg, "--disallow-")
    elif arg.startswith("--"):
        return "--no-" + assert_remove_prefix(arg, "--")
    else:
        return None


def run_with_stack_size(stack_kbs, func, *args, **kwargs):
    """Run the given function with a stack of the given size in KBs."""
    if stack_kbs < min_stack_size_kbs:
        raise CoconutException("--stack-size must be at least " + str(min_stack_size_kbs) + " KB")
    old_stack_size = threading.stack_size(stack_kbs * kilobyte)
    out = []
    thread = threading.Thread(target=lambda *args, **kwargs: out.append(func(*args, **kwargs)), args=args, kwargs=kwargs)
    thread.start()
    thread.join()
    logger.log("Stack size used:", old_stack_size, "->", stack_kbs * kilobyte)
    internal_assert(len(out) == 1, "invalid threading results", out)
    return out[0]


def proc_run_args(args=()):
    """Process args to use for coconut-run or the import hook."""
    args = list(args)
    if "--verbose" not in args and "--quiet" not in args:
        args.append("--quiet")
    for run_arg in coconut_base_run_args:
        run_arg_name = run_arg.split("=", 1)[0]
        if not any(arg.startswith(run_arg_name) for arg in args):
            args.append(run_arg)
    return args


def get_python_lib():
    """Get current Python lib location."""
    # these are expensive, so should only be imported here
    if PY32:
        from sysconfig import get_path
        python_lib = get_path("purelib")
    else:
        from distutils import sysconfig
        python_lib = sysconfig.get_python_lib()
    return fixpath(python_lib)


def import_coconut_header():
    """Import the coconut.__coconut__ header.
    This is expensive, so only do it here."""
    try:
        from coconut import __coconut__
        return __coconut__
    except ImportError:
        # fixes an issue where, when running from the base coconut directory,
        #  the base coconut directory is treated as a namespace package
        try:
            from coconut.coconut import __coconut__
        except ImportError:
            __coconut__ = None
        if __coconut__ is not None:
            return __coconut__
        else:
            raise  # the original ImportError, since that's the normal one


# -----------------------------------------------------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------------------------------------------------

class Prompt(object):
    """Manages prompting for code on the command line."""
    # config options
    multiline = prompt_multiline
    vi_mode = prompt_vi_mode
    wrap_lines = prompt_wrap_lines
    history_search = prompt_history_search

    # default values
    session = None
    style = None
    runner = None
    lexer = None
    suggester = True if prompt_use_suggester else None

    def __init__(self, setup_now=False):
        """Set up the prompt."""
        if prompt_toolkit is not None:
            self.set_style(os.getenv(style_env_var, default_style))
            self.set_history_file(prompt_histfile)
            if setup_now:
                self.setup()

    def setup(self):
        """Actually initialize the underlying Prompt.
        We do this lazily since it's expensive."""
        if self.lexer is None:
            self.lexer = PygmentsLexer(CoconutLexer)
        if self.suggester is True:
            self.suggester = AutoSuggestFromHistory()

    def set_style(self, style):
        """Set pygments syntax highlighting style."""
        if style == "none":
            self.style = None
        elif prompt_toolkit is None:
            raise CoconutException("syntax highlighting requires prompt_toolkit (run 'pip install -U prompt_toolkit' to fix)")
        elif style == "list":
            logger.print("Coconut Styles: none, " + ", ".join(pygments.styles.get_all_styles()))
            sys.exit(0)
        elif style in pygments.styles.get_all_styles():
            self.style = style
        else:
            raise CoconutException("unrecognized pygments style", style, extra="use '--style list' to show all valid styles")

    def set_history_file(self, path):
        """Set path to history file. Pass empty string for in-memory history."""
        if path:
            self.history = prompt_toolkit.history.FileHistory(fixpath(path))
        else:
            self.history = prompt_toolkit.history.InMemoryHistory()

    def set_runner(self, runner):
        """Specify the runner from which to extract completions."""
        self.runner = runner

    def get_completer(self):
        """Get the autocompleter to use."""
        internal_assert(self.runner is not None, "Prompt.set_runner must be called before Prompt.prompt")
        return FuzzyWordCompleter(self.runner.vars)

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
                return self.prompt(msg)
            except EOFError:
                raise  # issubclass(EOFError, Exception), so we have to do this
            except (Exception, AssertionError):
                logger.print_exc()
                logger.show_sig("Syntax highlighting failed; switching to --style none.")
                self.style = None
        return input(msg)

    def prompt(self, msg):
        """Get input using prompt_toolkit."""
        self.setup()
        try:
            # prompt_toolkit v2
            if self.session is None:
                self.session = prompt_toolkit.PromptSession(history=self.history)
            prompt = self.session.prompt
        except AttributeError:
            # prompt_toolkit v1
            prompt = partial(prompt_toolkit.prompt, history=self.history)
        return prompt(
            msg,
            multiline=self.multiline,
            vi_mode=self.vi_mode,
            wrap_lines=self.wrap_lines,
            enable_history_search=self.history_search,
            lexer=self.lexer,
            style=style_from_pygments_cls(
                pygments.styles.get_style_by_name(self.style),
            ),
            completer=self.get_completer(),
            auto_suggest=self.suggester,
        )


class Runner(object):
    """Compiled Python executor."""

    def __init__(self, comp=None, exit=sys.exit, store=False, path=None):
        """Create the executor."""
        from coconut.api import auto_compilation, use_coconut_breakpoint
        auto_compilation(on=interpreter_uses_auto_compilation, args=comp.get_cli_args() if comp else None)
        use_coconut_breakpoint(on=interpreter_uses_coconut_breakpoint)
        self.exit = exit
        self.vars = self.build_vars(path, init=True)
        self.stored = [] if store else None
        if comp is not None:
            self.store(comp.getheader("package:0"))
            self.run(comp.getheader("code"), use_eval=False, store=False)
            self.fix_pickle()
            self.vars[interpreter_compiler_var] = comp

    @staticmethod
    def build_vars(path=None, init=False):
        """Build initial vars."""
        init_vars = {
            "__name__": "__main__",
            "__package__": None,
            "reload": reload,
            "__file__": None if path is None else fixpath(path)
        }
        if init:
            # put reserved_vars in for auto-completion purposes only at the very beginning
            for var in reserved_vars:
                # but don't override any default Python built-ins
                if var not in dir(builtins):
                    init_vars[var] = None
        return init_vars

    def store(self, line):
        """Store a line."""
        if self.stored is not None:
            self.stored.append(line)

    def fix_pickle(self):
        """Fix pickling of Coconut header objects."""
        __coconut__ = import_coconut_header()
        for var in self.vars:
            if not var.startswith("__") and var in dir(__coconut__) and var not in must_use_specific_target_builtins:
                cur_val = self.vars[var]
                static_val = getattr(__coconut__, var)
                if getattr(cur_val, "__doc__", None) == getattr(static_val, "__doc__", None):
                    self.vars[var] = static_val

    @contextmanager
    def handling_errors(self, all_errors_exit=False):
        """Handle execution errors."""
        try:
            yield
        except SystemExit as err:
            self.exit(err.code)
        except BaseException:
            etype, value, tb = sys.exc_info()
            while True:
                if tb is None or not subpath(tb.tb_frame.f_code.co_filename, base_dir):
                    break
                tb = tb.tb_next
            logger.print_exception(etype, value, tb)
            if all_errors_exit:
                self.exit(1)

    def update_vars(self, global_vars, ignore_vars=None):
        """Add Coconut built-ins to given vars."""
        if ignore_vars:
            update_vars = self.vars.copy()
            for del_var in ignore_vars:
                del update_vars[del_var]
        else:
            update_vars = self.vars
        global_vars.update(update_vars)

    def run(self, code, use_eval=False, path=None, all_errors_exit=False, store=True):
        """Execute Python code."""
        if use_eval is None:
            run_func = interpret
        elif use_eval:
            run_func = eval
        else:
            run_func = _coconut_exec
        logger.log("Running {func}()...".format(func=getattr(run_func, "__name__", run_func)))
        start_time = get_clock_time()
        result = None
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
        logger.log("\tFinished in {took_time} secs.".format(took_time=get_clock_time() - start_time))
        return result

    def run_file(self, path, all_errors_exit=True):
        """Execute a Python file."""
        path = fixpath(path)
        logger.log("Running " + repr(path) + "...")
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


def highten_process():
    """Set the current process to high priority."""
    if high_proc_prio and psutil is not None:
        try:
            p = psutil.Process()
            if WINDOWS:
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                p.nice(-10)
        except Exception:
            logger.log_exc()


class multiprocess_wrapper(pickleable_obj):
    """Wrapper for a method that needs to be multiprocessed."""
    __slots__ = ("base", "method", "stack_size", "rec_limit", "logger", "argv")

    def __init__(self, base, method, stack_size=None, _rec_limit=None, _logger=None, _argv=None):
        """Create new multiprocessable method."""
        self.base = base
        self.method = method
        self.stack_size = stack_size
        self.rec_limit = sys.getrecursionlimit() if _rec_limit is None else _rec_limit
        self.logger = logger.copy() if _logger is None else _logger
        self.argv = sys.argv if _argv is None else _argv

    def __reduce__(self):
        """Pickle for transfer across processes."""
        return (self.__class__, (self.base, self.method, self.stack_size, self.rec_limit, self.logger, self.argv))

    def __call__(self, *args, **kwargs):
        """Call the method."""
        highten_process()
        sys.setrecursionlimit(self.rec_limit)
        logger.copy_from(self.logger)
        sys.argv = self.argv
        func = getattr(self.base, self.method)
        if self.stack_size:
            return run_with_stack_size(self.stack_size, func, args, kwargs)
        else:
            return func(*args, **kwargs)
