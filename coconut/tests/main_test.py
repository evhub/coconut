#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: Main Coconut tests.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import unittest
import sys
import os
import shutil
import functools
from contextlib import contextmanager
if sys.version_info >= (2, 7):
    import importlib
else:
    import imp

import pytest
import pexpect

from coconut.util import noop_ctx, get_target_info
from coconut.terminal import (
    logger,
    LoggingStringIO,
)
from coconut.command.util import (
    call_output,
    reload,
)
from coconut.compiler.util import (
    get_psf_target,
)
from coconut.constants import (
    WINDOWS,
    PYPY,
    IPY,
    XONSH,
    MYPY,
    PY35,
    PY36,
    PY38,
    PY39,
    PY310,
    supported_py2_vers,
    supported_py3_vers,
    icoconut_default_kernel_names,
    icoconut_custom_kernel_name,
    mypy_err_infixes,
    get_bool_env_var,
    coconut_cache_dir,
    default_use_cache_dir,
)

from coconut.api import (
    auto_compilation,
    setup,
)


# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------


auto_compilation(False)

logger.verbose = property(lambda self: True, lambda self, value: print("WARNING: ignoring attempt to set logger.verbose = {value}".format(value=value)))

os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"


# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------


default_recursion_limit = "6144"
default_stack_size = "6144"

jupyter_timeout = 120

base = os.path.dirname(os.path.relpath(__file__))
src = os.path.join(base, "src")
dest = os.path.join(base, "dest")
additional_dest = os.path.join(base, "dest", "additional_dest")

src_cache_dir = os.path.join(src, coconut_cache_dir)

runnable_coco = os.path.join(src, "runnable.coco")
runnable_py = os.path.join(src, "runnable.py")
runnable_compiled_loc = src_cache_dir if default_use_cache_dir else runnable_py

importable_coco = os.path.join(src, "importable.coco")
importable_py = os.path.join(src, "importable.py")
importable_compiled_loc = src_cache_dir if default_use_cache_dir else importable_py

pyston = os.path.join(os.curdir, "pyston")
pyprover = os.path.join(os.curdir, "pyprover")
prelude = os.path.join(os.curdir, "coconut-prelude")
bbopt = os.path.join(os.curdir, "bbopt")

pyston_git = "https://github.com/evhub/pyston.git"
pyprover_git = "https://github.com/evhub/pyprover.git"
prelude_git = "https://github.com/evhub/coconut-prelude"
bbopt_git = "https://github.com/evhub/bbopt.git"

coconut_snip = "msg = '<success>'; pmsg = print$(msg); `pmsg`"
target_3_snip = "assert super is py_super; print('<success>')"

always_err_strs = (
    "CoconutInternalException",
    "<unprintable",
    "*** glibc detected ***",
    "INTERNAL ERROR",
)

mypy_snip = "a: str = count()[0]"
mypy_snip_err_2 = '''error: Incompatible types in assignment (expression has type\n"int", variable has type "unicode")'''
mypy_snip_err_3 = '''error: Incompatible types in assignment (expression has type\n"int", variable has type "str")'''

mypy_args = ["--follow-imports", "silent", "--ignore-missing-imports", "--allow-redefinition"]

ignore_mypy_errs_with = (
    "with error: MyPy error",
    "tutorial.py",
    "unused 'type: ignore' comment",
    "site-packages/numpy",
)

ignore_atexit_errors_with = (
    "Traceback (most recent call last):",
    "sqlite3.ProgrammingError",
    "OSError: handle is closed",
)

ignore_last_lines_with = (
    "DeprecationWarning: The distutils package is deprecated",
    "from distutils.version import LooseVersion",
    ": SyntaxWarning: 'int' object is not ",
    " assert_raises(",
)

kernel_installation_msg = (
    "Coconut: Successfully installed Jupyter kernels: '"
    + "', '".join((icoconut_custom_kernel_name,) + icoconut_default_kernel_names) + "'"
)

always_sys_versions = (
    supported_py2_vers[-1],
    supported_py3_vers[-2],
    supported_py3_vers[-1],
)


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------

def escape(inputstring):
    """Performs basic shell escaping.
    Not by any means complete, should only be used on coconut_snip."""
    if WINDOWS:
        return inputstring.replace("<", "^^^<").replace(">", "^^^>")
    else:
        return '"' + inputstring.replace("$", "\\$").replace("`", "\\`") + '"'


def call_with_import(module_name, extra_argv=[], assert_result=True):
    """Import module_name and run module.main() with given argv, capturing output."""
    pytest.register_assert_rewrite(py_str(module_name))
    print("import", module_name, "with extra_argv=" + repr(extra_argv))
    old_stdout, sys.stdout = sys.stdout, LoggingStringIO(sys.stdout)
    old_stderr, sys.stderr = sys.stderr, LoggingStringIO(sys.stderr)
    old_argv = sys.argv
    try:
        with using_coconut():
            if sys.version_info >= (2, 7):
                module = importlib.import_module(module_name)
            else:
                module = imp.load_module(module_name, *imp.find_module(module_name))
            sys.argv = [module.__file__] + extra_argv
            result = module.main()
            if assert_result:
                assert result
    except SystemExit as err:
        retcode = err.code or 0
    except BaseException:
        logger.print_exc()
        retcode = 1
    else:
        retcode = 0
    finally:
        sys.argv = old_argv
        stdout = sys.stdout.getvalue()
        stderr = sys.stderr.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    return stdout, stderr, retcode


def call(
    raw_cmd,
    assert_output=False,
    check_mypy=False,
    check_errors=True,
    stderr_first=False,
    expect_retcode=0,
    convert_to_import=False,
    assert_output_only_at_end=None,
    **kwargs
):
    """Execute a shell command and assert that no errors were encountered."""
    if isinstance(raw_cmd, str):
        cmd = raw_cmd.split()
    else:
        cmd = raw_cmd

    print()
    logger.log_cmd(cmd)

    if assert_output is False:
        assert_output = ("",)
    elif assert_output is True:
        assert_output = ("<success>",)
    elif isinstance(assert_output, str):
        if assert_output_only_at_end is None and "\n" in assert_output:
            assert_output_only_at_end = False
        assert_output = (assert_output,)
    else:
        assert_output = tuple(x if x is not True else "<success>" for x in assert_output)
    if assert_output_only_at_end is None:
        assert_output_only_at_end = True

    if convert_to_import is None:
        convert_to_import = (
            cmd[0] == sys.executable
            and cmd[1] != "-c"
            and cmd[1:3] != ["-m", "coconut"]
        )

    if convert_to_import:
        assert cmd[0] == sys.executable
        if cmd[1] == "-m":
            module_name = cmd[2]
            extra_argv = cmd[3:]
            stdout, stderr, retcode = call_with_import(module_name, extra_argv)
        else:
            module_path = cmd[1]
            extra_argv = cmd[2:]
            module_dir = os.path.dirname(module_path)
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            if os.path.isdir(module_path):
                module_name += ".__main__"
            with using_sys_path(module_dir):
                stdout, stderr, retcode = call_with_import(module_name, extra_argv)
    else:
        stdout, stderr, retcode = call_output(raw_cmd, **kwargs)

    if expect_retcode is not None:
        assert retcode == expect_retcode, "Return code not as expected ({retcode} != {expect_retcode}) in: {cmd!r}".format(
            retcode=retcode,
            expect_retcode=expect_retcode,
            cmd=raw_cmd,
        )
    if stderr_first:
        out = stderr + stdout
    else:
        out = stdout + stderr
    out = "".join(out)

    raw_lines = out.splitlines()
    lines = []
    i = 0
    while True:
        if i >= len(raw_lines):
            break
        line = raw_lines[i]

        # ignore https://bugs.python.org/issue39098 errors
        if sys.version_info < (3, 9) and (
            line == "Error in atexit._run_exitfuncs:"
            or (
                line == "Traceback (most recent call last):"
                and i + 1 < len(raw_lines)
                and "concurrent/futures/process.py" in raw_lines[i + 1]
                and "_python_exit" in raw_lines[i + 1]
            )
        ):
            while True:
                i += 1
                if i >= len(raw_lines):
                    break

                new_line = raw_lines[i]
                if not new_line.startswith(" ") and not any(test in new_line for test in ignore_atexit_errors_with):
                    i -= 1
                    break
            continue

        # combine mypy error lines
        if any(infix in line for infix in mypy_err_infixes):
            # always add the next line, since it might be a continuation of the error message
            line += "\n" + raw_lines[i + 1]
            i += 1
            # then keep adding more lines if they start with whitespace, since they might be the referenced code
            for j in range(i + 2, len(raw_lines)):
                next_line = raw_lines[j]
                if next_line.lstrip() == next_line:
                    break
                line += "\n" + next_line
                i += 1

        lines.append(line)
        i += 1

    for line in lines:
        for errstr in always_err_strs:
            assert errstr not in line, "{errstr!r} in {line!r}".format(errstr=errstr, line=line)
        # ignore SyntaxWarnings containing assert_raises
        if check_errors and "assert_raises(" not in line:
            assert "Traceback (most recent call last):" not in line, "Traceback in " + repr(line)
            assert "Exception" not in line, "Exception in " + repr(line)
            assert "Error" not in line, "Error in " + repr(line)
        if check_mypy and all(test not in line for test in ignore_mypy_errs_with):
            assert "error:" not in line, "MyPy error in " + repr(line)

    if assert_output_only_at_end:
        last_line = ""
        for line in reversed(lines):
            if not any(ignore in line for ignore in ignore_last_lines_with):
                last_line = line
                break
        if assert_output is None:
            assert not last_line, "Expected nothing; got:\n" + "\n".join(repr(li) for li in raw_lines)
        else:
            assert any(x in last_line for x in assert_output), (
                "Expected " + ", ".join(repr(s) for s in assert_output)
                + " in " + repr(last_line)
                + "; got:\n" + "\n".join(repr(li) for li in raw_lines)
            )
    else:
        got_output = "\n".join(raw_lines) + "\n"
        assert any(x in got_output for x in assert_output), "Expected " + repr(assert_output) + "; got " + repr(got_output)


def call_python(args, **kwargs):
    """Calls the current Python."""
    if get_bool_env_var("COCONUT_TEST_DEBUG_PYTHON"):
        args = ["-X", "dev"] + args
    call([sys.executable] + args, **kwargs)


def call_coconut(args, **kwargs):
    """Calls Coconut."""
    if default_recursion_limit is not None and "--recursion-limit" not in args:
        args = ["--recursion-limit", default_recursion_limit] + args
    if default_stack_size is not None and "--stack-size" not in args:
        args = ["--stack-size", default_stack_size] + args
    if "--mypy" in args and "check_mypy" not in kwargs:
        kwargs["check_mypy"] = True
    if PY26:
        call(["coconut"] + args, **kwargs)
    else:
        call_python(["-m", "coconut"] + args, **kwargs)


def comp(path=None, folder=None, file=None, args=[], **kwargs):
    """Compiles a test file or directory."""
    paths = []
    if path is not None:
        paths.append(path)
    compdest = os.path.join(dest, *paths)
    if folder is not None:
        paths.append(folder)
    if file is not None:
        paths.append(file)
    source = os.path.join(src, *paths)
    if "--and" in args:
        additional_compdest = os.path.join(additional_dest, *paths)
        args.remove("--and")
        args = ["--and", source, additional_compdest] + args
    call_coconut([source, compdest] + args, **kwargs)


def rm_path(path, allow_keep=False):
    """Delete a path."""
    if allow_keep and get_bool_env_var("COCONUT_KEEP_TEST_FILES"):
        return
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except OSError:
            logger.print_exc()
    elif os.path.isfile(path):
        os.remove(path)


@contextmanager
def using_paths(*paths):
    """Removes paths at the beginning and end."""
    for path in paths:
        if os.path.exists(path):
            rm_path(path)
    try:
        yield
    finally:
        for path in paths:
            try:
                rm_path(path, allow_keep=True)
            except OSError:
                logger.print_exc()


@contextmanager
def using_dest(dest=dest, allow_existing=False):
    """Makes and removes the dest folder."""
    try:
        os.mkdir(dest)
    except Exception:
        if not allow_existing:
            rm_path(dest)
            os.mkdir(dest)
    try:
        yield
    finally:
        try:
            rm_path(dest, allow_keep=True)
        except OSError:
            logger.print_exc()


@contextmanager
def using_coconut(fresh_logger=True, fresh_api=False):
    """Decorator for ensuring that coconut.terminal.logger and coconut.api.* are reset."""
    saved_logger = logger.copy()
    if fresh_api:
        setup()
        auto_compilation(False)
    if fresh_logger:
        logger.reset()
    try:
        yield
    finally:
        setup()
        auto_compilation(False)
        logger.copy_from(saved_logger)


@contextmanager
def using_sys_path(path, prepend=False):
    """Adds a path to sys.path."""
    old_sys_path = sys.path[:]
    if prepend:
        sys.path.insert(0, path)
    else:
        sys.path.append(path)
    try:
        yield
    finally:
        sys.path[:] = old_sys_path


def add_test_func_name(test_func, cls):
    """Decorator for test functions."""
    @functools.wraps(test_func)
    def new_test_func(*args, **kwargs):
        print(
            """

===============================================================================
running {cls_name}.{name}...
===============================================================================""".format(
                cls_name=cls.__name__,
                name=test_func.__name__,
            ),
        )
        return test_func(*args, **kwargs)
    return new_test_func


def add_test_func_names(cls):
    """Decorator for test classes."""
    for name, attr in cls.__dict__.items():
        if name.startswith("test_") and callable(attr):
            setattr(cls, name, add_test_func_name(attr, cls))
    return cls


def spawn_cmd(cmd):
    """Version of pexpect.spawn that prints the command being run."""
    print("\n>", cmd)
    return pexpect.spawn(cmd)


# -----------------------------------------------------------------------------------------------------------------------
# RUNNERS:
# -----------------------------------------------------------------------------------------------------------------------

def comp_extras(args=[], **kwargs):
    """Compiles extras.coco."""
    comp(file="extras.coco", args=args, **kwargs)


def comp_runner(args=[], **kwargs):
    """Compiles runner.coco."""
    comp(file="runner.coco", args=args, **kwargs)


def comp_agnostic(args=[], **kwargs):
    """Compiles agnostic."""
    comp(path="cocotest", folder="agnostic", args=args, **kwargs)


def comp_2(args=[], always_sys=False, **kwargs):
    """Compiles target_2."""
    # remove --mypy checking for target_2 to avoid numpy errors
    try:
        mypy_ind = args.index("--mypy")
    except ValueError:
        pass
    else:
        args = args[:mypy_ind]
    comp(path="cocotest", folder="target_2", args=["--target", "2" if not always_sys else "sys"] + args, **kwargs)


def comp_3(args=[], always_sys=False, **kwargs):
    """Compiles target_3."""
    comp(path="cocotest", folder="target_3", args=["--target", "3" if not always_sys else "sys"] + args, **kwargs)


def comp_35(args=[], always_sys=False, **kwargs):
    """Compiles target_35."""
    comp(path="cocotest", folder="target_35", args=["--target", "35" if not always_sys else "sys"] + args, **kwargs)


def comp_36(args=[], always_sys=False, **kwargs):
    """Compiles target_36."""
    comp(path="cocotest", folder="target_36", args=["--target", "36" if not always_sys else "sys"] + args, **kwargs)


def comp_38(args=[], always_sys=False, **kwargs):
    """Compiles target_38."""
    comp(path="cocotest", folder="target_38", args=["--target", "38" if not always_sys else "sys"] + args, **kwargs)


def comp_sys(args=[], **kwargs):
    """Compiles target_sys."""
    comp(path="cocotest", folder="target_sys", args=["--target", "sys"] + args, **kwargs)


def comp_non_strict(args=[], **kwargs):
    """Compiles non_strict."""
    non_strict_args = [arg for arg in args if arg != "--strict"]
    comp(path="cocotest", folder="non_strict", args=non_strict_args, **kwargs)


def run_src(**kwargs):
    """Runs runner.py."""
    call_python([os.path.join(dest, "runner.py")], assert_output=True, **kwargs)


def run_extras(**kwargs):
    """Runs extras.py."""
    call_python([os.path.join(dest, "extras.py")], assert_output=True, check_errors=False, stderr_first=True, **kwargs)


def run(args=[], agnostic_target=None, use_run_arg=False, convert_to_import=False, always_sys=False, **kwargs):
    """Compiles and runs tests."""
    if agnostic_target is None:
        agnostic_args = args
    else:
        agnostic_args = ["--target", str(agnostic_target)] + args

    with using_dest():
        with (using_dest(additional_dest) if "--and" in args else noop_ctx()):

            spec_kwargs = kwargs.copy()
            spec_kwargs["always_sys"] = always_sys
            if PY2:
                comp_2(args, **spec_kwargs)
            else:
                comp_3(args, **spec_kwargs)
                if sys.version_info >= (3, 5):
                    comp_35(args, **spec_kwargs)
                if sys.version_info >= (3, 6):
                    comp_36(args, **spec_kwargs)
                if sys.version_info >= (3, 8):
                    comp_38(args, **spec_kwargs)

            comp_agnostic(agnostic_args, **kwargs)
            comp_sys(args, **kwargs)
            comp_non_strict(args, **kwargs)

            if use_run_arg:
                _kwargs = kwargs.copy()
                _kwargs["assert_output"] = True
                comp_runner(["--run"] + agnostic_args, **_kwargs)
            else:
                comp_runner(agnostic_args, **kwargs)
                run_src(convert_to_import=convert_to_import)  # **kwargs are for comp, not run

            if use_run_arg:
                _kwargs = kwargs.copy()
                _kwargs["assert_output"] = True
                _kwargs["check_errors"] = False
                _kwargs["stderr_first"] = True
                comp_extras(["--run"] + agnostic_args, **_kwargs)
            else:
                comp_extras(agnostic_args, **kwargs)
                run_extras(convert_to_import=convert_to_import)  # **kwargs are for comp, not run


def comp_all(args=[], agnostic_target=None, **kwargs):
    """Compile Coconut tests."""
    if agnostic_target is None:
        agnostic_args = args
    else:
        agnostic_args = ["--target", str(agnostic_target)] + args

    try:
        os.mkdir(dest)
    except Exception:
        pass

    comp_2(args, **kwargs)
    comp_3(args, **kwargs)
    comp_35(args, **kwargs)
    comp_36(args, **kwargs)
    comp_38(args, **kwargs)
    comp_sys(args, **kwargs)
    comp_non_strict(args, **kwargs)

    comp_agnostic(agnostic_args, **kwargs)
    comp_runner(agnostic_args, **kwargs)
    comp_extras(agnostic_args, **kwargs)


def comp_pyston(args=[], **kwargs):
    """Compiles evhub/pyston."""
    call(["git", "clone", pyston_git])
    call_coconut(["pyston", "--force"] + args, check_errors=False, **kwargs)


def run_pyston(**kwargs):
    """Runs pyston."""
    call_python([os.path.join(pyston, "runner.py")], assert_output=True, **kwargs)


def comp_pyprover(args=[], **kwargs):
    """Compiles evhub/pyprover."""
    call(["git", "clone", pyprover_git])
    call_coconut([os.path.join(pyprover, "setup.coco"), "--force"] + args, **kwargs)
    call_coconut([os.path.join(pyprover, "pyprover-source"), os.path.join(pyprover, "pyprover"), "--force"] + args, **kwargs)


def run_pyprover(**kwargs):
    """Runs pyprover."""
    call(["pip", "install", "-e", pyprover])
    call_python([os.path.join(pyprover, "pyprover", "tests.py")], assert_output=True, **kwargs)


def comp_prelude(args=[], **kwargs):
    """Compiles evhub/coconut-prelude."""
    call(["git", "clone", prelude_git])
    if MYPY and not WINDOWS:
        args.extend(["--target", "3.5", "--mypy"])
        kwargs["check_errors"] = False
    call_coconut([os.path.join(prelude, "setup.coco"), "--force"] + args, **kwargs)
    call_coconut([os.path.join(prelude, "prelude-source"), os.path.join(prelude, "prelude"), "--force"] + args, **kwargs)


def run_prelude(**kwargs):
    """Runs coconut-prelude."""
    call(["make", "base-install"], cwd=prelude)
    call(["pytest", "--strict-markers", "-s", os.path.join(prelude, "prelude")], assert_output="passed", **kwargs)


def comp_bbopt(args=[], **kwargs):
    """Compiles evhub/bbopt."""
    call(["git", "clone", bbopt_git])
    call_coconut([os.path.join(bbopt, "setup.coco"), "--force"] + args, **kwargs)
    call_coconut([os.path.join(bbopt, "bbopt-source"), os.path.join(bbopt, "bbopt"), "--force"] + args, **kwargs)


def install_bbopt():
    """Runs bbopt."""
    call(["pip", "install", "-Ue", bbopt])


def run_runnable(args=[]):
    """Call coconut-run on runnable_coco."""
    paths_being_used = [importable_compiled_loc]
    if "--no-write" not in args and "-n" not in args:
        paths_being_used.append(runnable_compiled_loc)
    with using_paths(*paths_being_used):
        call(["coconut-run"] + args + [runnable_coco, "--arg"], assert_output=True)


def comp_runnable(args=[]):
    """Just compile runnable."""
    if "--target" not in args:
        args += ["--target", "sys"]
    call_coconut([runnable_coco, "--and", importable_coco] + args)
    call_coconut([runnable_coco, "--and", importable_coco] + args, assert_output="Left unchanged", assert_output_only_at_end=False)


# -----------------------------------------------------------------------------------------------------------------------
# TESTS:
# -----------------------------------------------------------------------------------------------------------------------

@add_test_func_names
class TestShell(unittest.TestCase):

    def test_version(self):
        call(["coconut", "--version"])

    def test_code(self):
        call(["coconut", "-s", "-c", coconut_snip], assert_output=True)

    if not PY2:
        def test_target_3_snip(self):
            call(["coconut", "-t3", "-c", target_3_snip], assert_output=True)

    if MYPY:
        def test_universal_mypy_snip(self):
            call(
                ["coconut", "-c", mypy_snip, "--mypy"],
                assert_output=mypy_snip_err_3,
                check_errors=False,
                check_mypy=False,
            )

        def test_sys_mypy_snip(self):
            call(
                ["coconut", "--target", "sys", "-c", mypy_snip, "--mypy"],
                assert_output=mypy_snip_err_3,
                check_errors=False,
                check_mypy=False,
            )

        def test_no_wrap_mypy_snip(self):
            call(
                ["coconut", "--target", "sys", "--no-wrap", "-c", mypy_snip, "--mypy"],
                assert_output=mypy_snip_err_3,
                check_errors=False,
                check_mypy=False,
            )

    def test_pipe(self):
        call('echo ' + escape(coconut_snip) + "| coconut -s", shell=True, assert_output=True)

    def test_api(self):
        call_python(["-c", 'from coconut.api import parse; exec(parse("' + coconut_snip + '"))'], assert_output=True)

    def test_import_hook(self):
        with using_sys_path(src):
            with using_paths(runnable_compiled_loc, importable_compiled_loc):
                with using_coconut():
                    auto_compilation(True)
                    import runnable
                    reload(runnable)
        assert runnable.success == "<success>"

    def test_runnable(self):
        run_runnable()

    def test_runnable_nowrite(self):
        run_runnable(["-n"])

    def test_compile_runnable(self):
        with using_paths(runnable_py, importable_py):
            comp_runnable()
            call_python([runnable_py, "--arg"], assert_output=True)

    def test_import_runnable(self):
        with using_paths(runnable_py, importable_py):
            comp_runnable()
            for _ in range(2):  # make sure we can import it twice
                call_python([runnable_py, "--arg"], assert_output=True, convert_to_import=True)

    if not WINDOWS and XONSH:
        def test_xontrib(self):
            p = spawn_cmd("xonsh")
            p.expect("$")
            p.sendline("xontrib load coconut")
            p.expect("$")
            p.sendline("!(ls -la) |> bool")
            p.expect("True")
            p.sendline('$ENV_VAR = "ABC"')
            p.expect("$")
            p.sendline('echo f"{$ENV_VAR}"; echo f"{$ENV_VAR}"')
            p.expect("ABC")
            p.expect("ABC")
            if not PYPY or PY39:
                if PY36:
                    p.sendline("echo 123;; 123")
                    p.expect("123;; 123")
                    p.sendline("echo abc; echo abc")
                    p.expect("abc")
                    p.expect("abc")
                    p.sendline("echo abc; print(1 |> (.+1))")
                    p.expect("abc")
                    p.expect("2")
                p.sendline('execx("10 |> print")')
                p.expect("subprocess mode")
            p.sendline("xontrib unload coconut")
            p.expect("$")
            if (not PYPY or PY39) and PY36:
                p.sendline("1 |> print")
                p.expect("subprocess mode")
            p.sendeof()
            if p.isalive():
                p.terminate()

    if IPY and (not WINDOWS or PY35):
        def test_ipython_extension(self):
            call(
                ["ipython", "--ext", "coconut", "-c", r'%coconut ' + coconut_snip],
                assert_output=(True,) + (("Jupyter error",) if WINDOWS else ()),
                stderr_first=WINDOWS,
                check_errors=not WINDOWS,
                expect_retcode=0 if not WINDOWS else None,
            )

        def test_kernel_installation(self):
            call(["coconut", "--jupyter"], assert_output=kernel_installation_msg)
            stdout, stderr, retcode = call_output(["jupyter", "kernelspec", "list"])
            stdout, stderr = "".join(stdout), "".join(stderr)
            if not stdout:
                stdout, stderr = stderr, ""
            assert not retcode and not stderr, stderr
            for kernel in (icoconut_custom_kernel_name,) + icoconut_default_kernel_names:
                assert kernel in stdout

        if not WINDOWS and not PYPY:
            def test_jupyter_console(self):
                p = spawn_cmd("coconut --jupyter console")
                p.expect("In", timeout=jupyter_timeout)
                p.sendline("%load_ext coconut")
                p.expect("In", timeout=jupyter_timeout)
                p.sendline("`exit`")
                if sys.version_info[:2] != (3, 6):
                    p.expect("Shutting down kernel|shutting down", timeout=jupyter_timeout)
                if p.isalive():
                    p.terminate()


@add_test_func_names
class TestCompilation(unittest.TestCase):

    def test_simple_no_line_numbers(self):
        run_runnable(["-n", "--no-line-numbers"])

    def test_simple_keep_lines(self):
        run_runnable(["-n", "--keep-lines"])

    def test_simple_no_line_numbers_keep_lines(self):
        run_runnable(["-n", "--no-line-numbers", "--keep-lines"])

    def test_simple_minify(self):
        run_runnable(["-n", "--minify"])

    if sys.version_info >= get_target_info(get_psf_target()):
        def test_simple_psf(self):
            run_runnable(["-n", "--target", "psf"])

    def test_normal(self):
        run()

    if MYPY:
        def test_mypy_sys(self):
            run(["--mypy"] + mypy_args, agnostic_target="sys", expect_retcode=None, check_errors=False)  # fails due to tutorial mypy errors

    if sys.version_info[:2] in always_sys_versions:
        def test_always_sys(self):
            run(agnostic_target="sys", always_sys=True)

    def test_target(self):
        run(agnostic_target=(2 if PY2 else 3))

    def test_standalone(self):
        run(["--standalone"])

    def test_package(self):
        run(["--package"])

    def test_no_tco(self):
        run(["--no-tco"])

    # run fewer tests on Windows so appveyor doesn't time out
    if not WINDOWS:
        def test_keep_lines(self):
            run(["--keep-lines"])

        def test_strict(self):
            run(["--strict"])

        def test_and(self):
            run(["--and"])  # src and dest built by comp

    if PY35:
        def test_no_wrap(self):
            run(["--no-wrap"])

    if get_bool_env_var("COCONUT_TEST_VERBOSE"):
        def test_verbose(self):
            run(["--jobs", "0", "--verbose"])

    if get_bool_env_var("COCONUT_TEST_TRACE"):
        def test_trace(self):
            run(["--jobs", "0", "--trace"], check_errors=False)

    # avoids a strange, unreproducable failure on appveyor
    if not (WINDOWS and sys.version_info[:2] == (3, 8)):
        def test_run_arg(self):
            run(use_run_arg=True)

    # not WINDOWS is for appveyor timeout prevention
    if not WINDOWS and not PYPY and not PY26:
        def test_jobs_zero(self):
            run(["--jobs", "0"])


# more appveyor timeout prevention
if not WINDOWS:
    @add_test_func_names
    class TestExternal(unittest.TestCase):

        if not PYPY or PY2:
            def test_prelude(self):
                with using_paths(prelude):
                    comp_prelude()
                    if MYPY and PY38:
                        run_prelude()

        def test_bbopt(self):
            with using_paths(bbopt):
                comp_bbopt()
                if not PYPY and PY38 and not PY310:
                    install_bbopt()

        def test_pyprover(self):
            with using_paths(pyprover):
                comp_pyprover()
                if PY38:
                    run_pyprover()

        def test_pyston(self):
            with using_paths(pyston):
                comp_pyston(["--no-tco"])
                if PYPY and PY2:
                    run_pyston()


# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
