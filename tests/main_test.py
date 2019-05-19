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
from contextlib import contextmanager

import pexpect

from coconut.terminal import logger, Logger
from coconut.command.util import call_output, reload
from coconut.constants import (
    WINDOWS,
    PYPY,
    IPY,
    PY34,
    PY35,
    PY36,
    icoconut_kernel_names,
)

from coconut.convenience import auto_compilation
auto_compilation(False)

# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

logger.verbose = True

MYPY = PY34 and not WINDOWS and not PYPY

base = os.path.dirname(os.path.relpath(__file__))
src = os.path.join(base, "src")
dest = os.path.join(base, "dest")

runnable_coco = os.path.join(src, "runnable.coco")
runnable_py = os.path.join(src, "runnable.py")
pyston = os.path.join(os.curdir, "pyston")
pyprover = os.path.join(os.curdir, "pyprover")
prelude = os.path.join(os.curdir, "coconut-prelude")

pyston_git = "https://github.com/evhub/pyston.git"
pyprover_git = "https://github.com/evhub/pyprover.git"
prelude_git = "https://github.com/evhub/coconut-prelude"

coconut_snip = r"msg = '<success>'; pmsg = print$(msg); `pmsg`"

mypy_snip = r"a: str = count()[0]"
mypy_snip_err = 'error: Incompatible types in assignment (expression has type "int", variable has type "str")'

mypy_args = ["--follow-imports", "silent", "--ignore-missing-imports"]

ignore_mypy_errs_with = (
    "tutorial.py",
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


def call(cmd, assert_output=False, check_mypy=False, check_errors=True, stderr_first=False, expect_retcode=0, **kwargs):
    """Executes a shell command."""
    print("\n>", (cmd if isinstance(cmd, str) else " ".join(cmd)))
    if assert_output is False:
        assert_output = ("",)
    elif assert_output is True:
        assert_output = ("<success>",)
    elif isinstance(assert_output, str):
        assert_output = (assert_output,)
    else:
        assert_output = tuple(x if x is not True else "<success>" for x in assert_output)
    stdout, stderr, retcode = call_output(cmd, **kwargs)
    if stderr_first:
        out = stderr + stdout
    else:
        out = stdout + stderr
    out = "".join(out)
    lines = out.splitlines()
    if expect_retcode is not None:
        assert retcode == expect_retcode, "Return code not as expected ({retcode} != {expect_retcode}) in: {cmd!r}".format(
            retcode=retcode,
            expect_retcode=expect_retcode,
            cmd=cmd,
        )
    for line in lines:
        assert "CoconutInternalException" not in line, "CoconutInternalException in " + repr(line)
        assert "<unprintable" not in line, "Unprintable error in " + repr(line)
        assert "*** glibc detected ***" not in line, "C error in " + repr(line)
        if check_errors:
            assert "Traceback (most recent call last):" not in line, "Traceback in " + repr(line)
            assert "Exception" not in line, "Exception in " + repr(line)
            assert "Error" not in line, "Error in " + repr(line)
        if check_mypy and all(test not in line for test in ignore_mypy_errs_with):
            assert "INTERNAL ERROR" not in line, "MyPy INTERNAL ERROR in " + repr(line)
            assert "error:" not in line, "MyPy error in " + repr(line)
    last_line = lines[-1] if lines else ""
    if assert_output is None:
        assert not last_line, "Expected nothing; got " + repr(last_line)
    else:
        assert any(x in last_line for x in assert_output), "Expected " + ", ".join(assert_output) + "; got " + repr(last_line)


def call_python(args, **kwargs):
    """Calls the current Python."""
    call([sys.executable] + args, **kwargs)


def call_coconut(args, **kwargs):
    """Calls Coconut."""
    if "--jobs" not in args and not PYPY and not PY26:
        args = ["--jobs", "sys"] + args
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
    call_coconut([source, compdest] + args, **kwargs)


@contextmanager
def remove_when_done(path):
    """Removes a path when done."""
    try:
        yield
    finally:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
        except OSError:
            logger.display_exc()


@contextmanager
def using_dest():
    """Makes and removes the dest folder."""
    try:
        os.mkdir(dest)
    except Exception:
        shutil.rmtree(dest)
        os.mkdir(dest)
    with remove_when_done(dest):
        yield


@contextmanager
def using_logger():
    """Use a temporary logger, then restore the old logger."""
    saved_logger = Logger(logger)
    try:
        yield
    finally:
        logger.copy_from(saved_logger)


# -----------------------------------------------------------------------------------------------------------------------
# RUNNER:
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


def comp_2(args=[], **kwargs):
    """Compiles target_2."""
    comp(path="cocotest", folder="target_2", args=["--target", "2"] + args, **kwargs)


def comp_3(args=[], **kwargs):
    """Compiles target_3."""
    comp(path="cocotest", folder="target_3", args=["--target", "3"] + args, **kwargs)


def comp_35(args=[], **kwargs):
    """Compiles target_35."""
    comp(path="cocotest", folder="target_35", args=["--target", "35"] + args, **kwargs)


def comp_36(args=[], **kwargs):
    """Compiles target_35."""
    comp(path="cocotest", folder="target_36", args=["--target", "36"] + args, **kwargs)


def comp_sys(args=[], **kwargs):
    """Compiles target_sys."""
    comp(path="cocotest", folder="target_sys", args=["--target", "sys"] + args, **kwargs)


def run_src(**kwargs):
    """Runs runner.py."""
    call_python([os.path.join(dest, "runner.py")], assert_output=True, **kwargs)


def run_extras(**kwargs):
    """Runs extras.py."""
    call_python([os.path.join(dest, "extras.py")], assert_output=True, check_errors=False, stderr_first=True, **kwargs)


def run(args=[], agnostic_target=None, use_run_arg=False, expect_retcode=0):
    """Compiles and runs tests."""
    if agnostic_target is None:
        agnostic_args = args
    else:
        agnostic_args = ["--target", str(agnostic_target)] + args

    with using_dest():

        if PY2:
            comp_2(args, expect_retcode=expect_retcode)
        else:
            comp_3(args, expect_retcode=expect_retcode)
            if sys.version_info >= (3, 5):
                comp_35(args, expect_retcode=expect_retcode)
            if sys.version_info >= (3, 6):
                comp_36(args, expect_retcode=expect_retcode)
        comp_agnostic(agnostic_args, expect_retcode=expect_retcode)
        comp_sys(args, expect_retcode=expect_retcode)

        if use_run_arg:
            comp_runner(["--run"] + agnostic_args, expect_retcode=expect_retcode, assert_output=True)
        else:
            comp_runner(agnostic_args, expect_retcode=expect_retcode)
            run_src()

        if use_run_arg:
            comp_extras(["--run"] + agnostic_args, assert_output=True, check_errors=False, stderr_first=True, expect_retcode=expect_retcode)
        else:
            comp_extras(agnostic_args, expect_retcode=expect_retcode)
            run_extras()


def comp_pyston(args=[], **kwargs):
    """Compiles evhub/pyston."""
    call(["git", "clone", pyston_git])
    call_coconut(["pyston"] + args, **kwargs)


def run_pyston(**kwargs):
    """Runs pyston."""
    call_python([os.path.join(pyston, "runner.py")], assert_output=True, **kwargs)


def comp_pyprover(args=[], **kwargs):
    """Compiles evhub/pyprover."""
    call(["git", "clone", pyprover_git])
    call_coconut([os.path.join(pyprover, "setup.coco"), "--strict"] + args, **kwargs)
    call_coconut([os.path.join(pyprover, "pyprover-source"), os.path.join(pyprover, "pyprover"), "--strict"] + args, **kwargs)


def run_pyprover(**kwargs):
    """Runs pyprover."""
    call(["pip", "install", "-e", pyprover])
    call_python([os.path.join(pyprover, "pyprover", "tests.py")], assert_output=True, **kwargs)


def comp_prelude(args=[], **kwargs):
    """Compiles evhub/coconut-prelude."""
    call(["git", "clone", prelude_git])
    call_coconut([os.path.join(prelude, "setup.coco"), "--strict"] + args, **kwargs)
    if PY36:
        args.append("--target", "3.6", "--mypy")
    call_coconut([os.path.join(prelude, "prelude-source"), os.path.join(prelude, "prelude"), "--strict"] + args, **kwargs)


def run_prelude(**kwargs):
    """Runs coconut-prelude."""
    call(["pip", "install", "-e", prelude])
    call_python([os.path.join(prelude, "prelude", "prelude_test.py")], assert_output=True, **kwargs)


def comp_all(args=[], **kwargs):
    """Compile Coconut tests."""
    try:
        os.mkdir(dest)
    except Exception:
        pass
    comp_2(args, **kwargs)
    comp_3(args, **kwargs)
    comp_35(args, **kwargs)
    comp_36(args, **kwargs)
    comp_agnostic(args, **kwargs)
    comp_sys(args, **kwargs)
    comp_runner(args, **kwargs)
    comp_extras(args, **kwargs)


def run_runnable(args=[]):
    """Call coconut-run on runnable_coco."""
    call(["coconut-run"] + args + [runnable_coco, "--arg"], assert_output=True)

# -----------------------------------------------------------------------------------------------------------------------
# TESTS:
# -----------------------------------------------------------------------------------------------------------------------


class TestShell(unittest.TestCase):

    def test_code(self):
        call(["coconut", "-s", "-c", coconut_snip], assert_output=True)

    def test_pipe(self):
        call('echo ' + escape(coconut_snip) + "| coconut -s", shell=True, assert_output=True)

    def test_convenience(self):
        call_python(["-c", 'from coconut.convenience import parse; exec(parse("' + coconut_snip + '"))'], assert_output=True)

    def test_import_hook(self):
        sys.path.append(src)
        auto_compilation(True)
        try:
            with remove_when_done(runnable_py):
                with using_logger():
                    import runnable
                    reload(runnable)
        finally:
            auto_compilation(False)
            sys.path.remove(src)
        assert runnable.success == "<success>"

    def test_runnable(self):
        with remove_when_done(runnable_py):
            run_runnable()

    def test_runnable_nowrite(self):
        run_runnable(["-n"])

    def test_compile_to_file(self):
        with remove_when_done(runnable_py):
            call_coconut([runnable_coco, runnable_py])
            call_python([runnable_py, "--arg"], assert_output=True)

    if IPY:
        def test_ipython_extension(self):
            call(
                ["ipython", "--ext", "coconut", "-c", r'%coconut ' + coconut_snip],
                assert_output=(True,) + (("Jupyter error",) if WINDOWS else ()),
                stderr_first=WINDOWS,
                check_errors=not WINDOWS,
                expect_retcode=0 if not WINDOWS else None,
            )

        def test_kernel_installation(self):
            call(["coconut", "--jupyter"], assert_output="Coconut: Successfully installed Coconut Jupyter kernel.")
            stdout, stderr, retcode = call_output(["jupyter", "kernelspec", "list"])
            stdout, stderr = "".join(stdout), "".join(stderr)
            assert not retcode and not stderr, stderr
            for kernel in icoconut_kernel_names:
                assert kernel in stdout

        if not WINDOWS and not PYPY:
            def test_jupyter_console(self):
                cmd = "coconut --jupyter console"
                print("\n>", cmd)
                p = pexpect.spawn(cmd)
                p.expect("In", timeout=100)
                p.sendeof()
                p.sendline("y")
                p.expect("Shutting down kernel|shutting down|Jupyter error")
                if p.isalive():
                    p.terminate()


class TestCompilation(unittest.TestCase):

    def test_normal(self):
        run()

    if MYPY:
        def test_mypy_snip(self):
            call(["coconut", "-c", mypy_snip, "--mypy"], assert_output=mypy_snip_err, check_mypy=False, expect_retcode=1)

        def test_mypy(self):
            run(["--mypy"] + mypy_args, expect_retcode=None)  # fails due to tutorial mypy errors

        def test_mypy_sys(self):
            run(["--mypy"] + mypy_args, agnostic_target="sys", expect_retcode=None)  # fails due to tutorial mypy errors

    def test_target(self):
        run(agnostic_target=(2 if PY2 else 3))

    def test_standalone(self):
        run(["--standalone"])

    def test_package(self):
        run(["--package"])

    def test_no_tco(self):
        run(["--no-tco"])

    def test_strict(self):
        run(["--strict"])

    def test_run(self):
        run(use_run_arg=True)

    if not PYPY and not PY26:
        def test_jobs_zero(self):
            run(["--jobs", "0"])

    def test_simple_line_numbers(self):
        run_runnable(["-n", "--linenumbers"])

    def test_simple_keep_lines(self):
        run_runnable(["-n", "--keeplines"])

    def test_simple_line_numbers_keep_lines(self):
        run_runnable(["-n", "--linenumbers", "--keeplines"])

    def test_simple_minify(self):
        run_runnable(["-n", "--minify"])


class TestExternal(unittest.TestCase):

    def test_pyprover(self):
        with remove_when_done(pyprover):
            comp_pyprover()
            run_pyprover()

    if not PYPY or PY2:
        def test_prelude(self):
            with remove_when_done(prelude):
                comp_prelude()
                if PY35:  # has typing
                    run_prelude()

    def test_pyston(self):
        with remove_when_done(pyston):
            comp_pyston(["--no-tco"])
            if PY2 and PYPY:
                run_pyston()
