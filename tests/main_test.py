#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: Main Coconut tests.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import unittest
import sys
import os
import shutil
import platform
from contextlib import contextmanager

from coconut.command.util import call_output

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

IPY = (PY2 and not PY26) or sys.version_info >= (3, 3)
PYPY = platform.python_implementation() == "PyPy"

base = os.path.dirname(os.path.relpath(__file__))
src = os.path.join(base, "src")
dest = os.path.join(base, "dest")

runnable_coco = os.path.join(src, "runnable.coco")
runnable_py = os.path.join(src, "runnable.py")
prisoner = os.path.join(os.curdir, "prisoner")
pyston = os.path.join(os.curdir, "pyston")
pyprover = os.path.join(os.curdir, "pyprover")

prisoner_git = "https://github.com/evhub/prisoner.git"
pyston_git = "https://github.com/evhub/pyston.git"
pyprover_git = "https://github.com/evhub/pyprover.git"

coconut_snip = r"msg = '<success>'; pmsg = print$(msg); `pmsg`"

mypy_snip = r"a: str = count()[0]"
mypy_snip_err = 'error: Incompatible types in assignment (expression has type "int", variable has type "str")'

ignore_mypy_errs_with = (
    "already defined",
    "Cannot determine type of",
)

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


def escape(inputstring):
    """Performs basic shell escaping."""
    return inputstring.replace("$", "\\$").replace("`", "\\`")


def call(cmd, assert_output=False, check_mypy=False, check_errors=True, stderr_first=False, **kwargs):
    """Executes a shell command."""
    print("\n>", (cmd if isinstance(cmd, str) else " ".join(cmd)))
    if assert_output is True:
        assert_output = "<success>"
    stdout, stderr, retcode = call_output(cmd, **kwargs)
    if stderr_first:
        out = stderr + stdout
    else:
        out = stdout + stderr
    out = "".join(out)
    lines = out.splitlines()
    for line in lines:
        print(line)
    assert not retcode, "Command failed: " + repr(cmd)
    for line in lines:
        assert "CoconutInternalException" not in line, "CoconutInternalException in " + repr(line)
        assert "INTERNAL ERROR" not in line, "MyPy INTERNAL ERROR in " + repr(line)
        assert "<unprintable" not in line, "Unprintable error in " + repr(line)
        assert "*** glibc detected ***" not in line, "C error in " + repr(line)
        if check_errors:
            assert "Traceback (most recent call last):" not in line, "Traceback in " + repr(line)
            assert "Exception" not in line, "Exception in " + repr(line)
            assert "Error" not in line, "Error in " + repr(line)
        if check_mypy and all(test not in line for test in ignore_mypy_errs_with):
            assert "error:" not in line, "MyPy error in " + repr(line)
    last_line = lines[-1] if lines else ""
    if assert_output is None:
        assert not last_line, "Expected nothing; got " + repr(last_line)
    elif assert_output is not False:
        assert assert_output in last_line, "Expected " + repr(assert_output) + "; got " + repr(last_line)


def call_coconut(args, **kwargs):
    """Calls Coconut."""
    if "--jobs" not in args and not PYPY and not PY26:
        args = ["--jobs", "sys"] + args
    if "--mypy" in args and "check_mypy" not in kwargs:
        kwargs["check_mypy"] = True
    call(["coconut"] + args, **kwargs)


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
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)


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

#-----------------------------------------------------------------------------------------------------------------------
# RUNNER:
#-----------------------------------------------------------------------------------------------------------------------


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
    """Compiles python2."""
    comp(path="cocotest", folder="python2", args=["--target", "2"] + args, **kwargs)


def comp_3(args=[], **kwargs):
    """Compiles python3."""
    comp(path="cocotest", folder="python3", args=["--target", "3"] + args, **kwargs)


def comp_35(args=[], **kwargs):
    """Compiles python35."""
    comp(path="cocotest", folder="python35", args=["--target", "35"] + args, **kwargs)


def run_src(**kwargs):
    """Runs runner.py."""
    call(["python", os.path.join(dest, "runner.py")], assert_output=True, **kwargs)


def run_extras(**kwargs):
    """Runs extras.py."""
    call(["python", os.path.join(dest, "extras.py")], assert_output=True, check_mypy=False, check_errors=False, stderr_first=True, **kwargs)


def run(args=[], agnostic_target=None, use_run_arg=False):
    """Compiles and runs tests."""
    if agnostic_target is None:
        agnostic_args = args
    else:
        agnostic_args = ["--target", str(agnostic_target)] + args

    with using_dest():

        if PY2:
            comp_2(args)
        else:
            comp_3(args)
            if sys.version_info >= (3, 5):
                comp_35(args)
        comp_agnostic(agnostic_args)
        if use_run_arg:
            comp_runner(["--run"] + agnostic_args, assert_output=True)
        else:
            comp_runner(agnostic_args)
            run_src()

        if use_run_arg:
            comp_extras(["--run"] + agnostic_args, assert_output=True, check_mypy=False, check_errors=False, stderr_first=True)
        else:
            comp_extras(agnostic_args)
            run_extras()


def comp_prisoner(args=[], **kwargs):
    """Compiles evhub/prisoner."""
    call(["git", "clone", prisoner_git])
    call_coconut(["prisoner", "--strict"] + args, **kwargs)


def comp_pyston(args=[], **kwargs):
    """Compiles evhub/pyston."""
    call(["git", "clone", pyston_git])
    call_coconut(["pyston"] + args, **kwargs)


def run_pyston(**kwargs):
    """Runs pyston."""
    call(["python", os.path.join(pyston, "runner.py")], assert_output=True, **kwargs)


def comp_pyprover(args=[], **kwargs):
    """Compiles evhub/pyprover."""
    call(["git", "clone", pyprover_git])
    call_coconut([os.path.join("pyprover", "setup.coco"), "--strict"] + args, **kwargs)
    call_coconut([os.path.join("pyprover", "pyprover-source"), os.path.join("pyprover", "pyprover"), "--strict"] + args, **kwargs)


def run_pyprover(**kwargs):
    """Runs pyprover."""
    call(["pip", "install", "-e", pyprover])
    call(["python", os.path.join(pyprover, "pyprover", "tests.py")], assert_output=True, **kwargs)


def comp_all(args=[], **kwargs):
    """Compile Coconut tests."""
    try:
        os.mkdir(dest)
    except Exception:
        pass
    comp_2(args, **kwargs)
    comp_3(args, **kwargs)
    comp_35(args, **kwargs)
    comp_agnostic(args, **kwargs)
    comp_runner(args, **kwargs)
    comp_extras(args, **kwargs)


def run_runnable(args=[]):
    """Call coconut-run on runnable_coco."""
    call(["coconut-run"] + args + [runnable_coco, "--arg"], assert_output=True)

#-----------------------------------------------------------------------------------------------------------------------
# TESTS:
#-----------------------------------------------------------------------------------------------------------------------


class TestShell(unittest.TestCase):

    def test_code(self):
        call(["coconut", "-s", "-c", coconut_snip], assert_output=True)

    def test_pipe(self):
        call('echo "' + escape(coconut_snip) + '" | coconut -s', shell=True, assert_output=True)

    def test_convenience(self):
        call(["python", "-c", 'from coconut.convenience import parse; exec(parse("' + coconut_snip + '"))'], assert_output=True)

    def test_runnable(self):
        with remove_when_done(runnable_py):
            run_runnable()

    def test_runnable_nowrite(self):
        run_runnable(["-n"])

    if IPY:

        def test_ipython(self):
            call(["ipython", "--ext", "coconut", "-c", '%coconut ' + coconut_snip], assert_output=True)

        def test_jupyter(self):
            call(["coconut", "--jupyter"], assert_output="Coconut: Successfully installed Coconut Jupyter kernel.")


class TestCompilation(unittest.TestCase):

    def test_normal(self):
        run()

    def test_target(self):
        run(agnostic_target=(2 if PY2 else 3))

    def test_line_numbers(self):
        run(["--linenumbers"])

    if not PYPY and not PY26:
        def test_jobs_zero(self):
            run(["--jobs", "0"])

    if sys.version_info >= (3, 4):
        def test_mypy(self):
            call(["coconut", "-c", mypy_snip, "--mypy"], assert_output=mypy_snip_err, check_mypy=False)
            run(["--mypy", "--ignore-missing-imports"])

    def test_run(self):
        run(use_run_arg=True)

    def test_package(self):
        run(["--package"])

    def test_standalone(self):
        run(["--standalone"])

    def test_strict(self):
        run(["--strict"])

    def test_no_tco(self):
        run(["--no-tco"])

    def test_simple_keep_lines(self):
        run_runnable(["-n", "--keeplines"])

    def test_simple_line_numbers_keep_lines(self):
        run_runnable(["-n", "--linenumbers", "--keeplines"])

    def test_simple_minify(self):
        run_runnable(["-n", "--minify"])


class TestExternal(unittest.TestCase):

    def test_prisoner(self):
        with remove_when_done(prisoner):
            comp_prisoner()

    def test_pyprover(self):
        with remove_when_done(pyprover):
            comp_pyprover()
            run_pyprover()

    def test_pyston(self):
        with remove_when_done(pyston):
            comp_pyston()
            if PY2 and platform.python_implementation() == "PyPy":
                run_pyston()
