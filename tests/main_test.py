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

import sys
import os
import subprocess
import shutil
import unittest
import platform
from contextlib import contextmanager

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------

IPY = (PY2 and not PY26) or (not PY2 and sys.version_info >= (3, 3))

base = os.path.dirname(os.path.relpath(__file__))
src = os.path.join(base, "src")
dest = os.path.join(base, "dest")


def call(cmd, assert_output=False, **kwargs):
    """Executes a shell command."""
    print("\n>", (cmd if isinstance(cmd, str) else " ".join(cmd)))
    if assert_output:
        line = None
        for raw_line in subprocess.Popen(cmd, stdout=subprocess.PIPE, **kwargs).stdout.readlines():
            line = raw_line.rstrip().decode(sys.stdout.encoding)
            print(line)
        assert line == "<success>"
    else:
        subprocess.check_call(cmd, **kwargs)


def call_coconut(args):
    """Calls Coconut."""
    if "--jobs" not in args and platform.python_implementation() == "PyPy":
        args += ["--jobs", "0"]
    call(["coconut"] + args)


def comp(path=None, folder=None, file=None, args=[]):
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
    call_coconut([source, compdest] + args)


@contextmanager
def create_dest():
    """Makes and removes the dest folder."""
    try:
        os.mkdir(dest)
    except FileExistsError:
        shutil.rmtree(dest)
        os.mkdir(dest)
    try:
        yield
    finally:
        shutil.rmtree(dest)

#-----------------------------------------------------------------------------------------------------------------------
# RUNNER:
#-----------------------------------------------------------------------------------------------------------------------


def comp_extras(args=[]):
    """Compiles extras.coco."""
    comp(file="extras.coco", args=args)


def comp_runner(args=[]):
    """Compiles runner.coco."""
    comp(file="runner.coco", args=args)


def comp_agnostic(args=[]):
    """Compiles agnostic."""
    comp(path="cocotest", folder="agnostic", args=args)


def comp_2(args=[]):
    """Compiles python2."""
    comp(path="cocotest", folder="python2", args=["--target", "2"] + args)


def comp_3(args=[]):
    """Compiles python3."""
    comp(path="cocotest", folder="python3", args=["--target", "3"] + args)


def comp_35(args=[]):
    """Compiles python35."""
    comp(path="cocotest", folder="python35", args=["--target", "35"] + args)


def run_src():
    """Runs runner.py."""
    call(["python", os.path.join(dest, "runner.py")], assert_output=True)


def run_extras():
    """Runs extras.py."""
    call(["python", os.path.join(dest, "extras.py")], assert_output=True)


def run(args=[], agnostic_target=None, comp_run=False):
    """Compiles and runs tests."""
    if agnostic_target is None:
        agnostic_args = args
    else:
        agnostic_args = args + ["--target", str(agnostic_target)]

    with create_dest():

        comp_agnostic(agnostic_args)
        if PY2:
            comp_2(args)
        else:
            comp_3(args)
            if sys.version_info >= (3, 5):
                comp_35(args)
        if comp_run:
            comp_runner(agnostic_args + ["--run"])
        else:
            comp_runner(agnostic_args)
            run_src()

        if IPY:
            if comp_run:
                comp_extras(agnostic_args + ["--run"])
            else:
                comp_extras(agnostic_args)
                run_extras()


def comp_prisoner(args=[]):
    """Compiles evhub/prisoner."""
    call(["git", "clone", "https://github.com/evhub/prisoner.git"])
    call_coconut(["prisoner", "--strict"] + args)


def comp_pyston(args=[]):
    """Compiles evhub/pyston."""
    call(["git", "clone", "https://github.com/evhub/pyston.git"])
    call_coconut(["pyston"] + args)


def run_pyston():
    """Runs pyston."""
    call(["python", os.path.join(os.curdir, "pyston", "runner.py")], assert_output=True)


def comp_all(args=[]):
    """Compile Coconut tests."""
    create_dest().__enter__()
    comp_agnostic(args)
    comp_2(args)
    comp_3(args)
    comp_35(args)
    comp_runner(args)
    comp_extras(args)

#-----------------------------------------------------------------------------------------------------------------------
# TESTS:
#-----------------------------------------------------------------------------------------------------------------------

coconut_snip = "msg = '<success>'; pmsg = print$(msg); `pmsg`"


class TestShell(unittest.TestCase):

    def test_code(self):
        call(["coconut", "-s", "--code", coconut_snip], assert_output=True)

    def test_pipe(self):
        call(r'echo "' + coconut_snip.replace("$", "\\$") + '" | coconut -s', shell=True, assert_output=True)

    def test_convenience(self):
        call(["python", "-c", 'from coconut.convenience import parse; exec(parse("' + coconut_snip + '"))'], assert_output=True)

    if IPY:

        def test_ipython(self):
            call(["ipython", "--ext", "coconut", "-c", '%coconut ' + coconut_snip], assert_output=True)

        def test_jupyter(self):
            call(["coconut", "--jupyter"])


class TestCompilation(unittest.TestCase):

    def test_normal(self):
        run()

    def test_jobs_zero(self):
        run(["--jobs", "0"])

    def test_run(self):
        run(comp_run=True)

    def test_target(self):
        run(agnostic_target=(2 if PY2 else 3))

    def test_standalone(self):
        run(["--standalone"])

    def test_package(self):
        run(["--package"])

    def test_line_numbers(self):
        run(["--linenumbers"])

    def test_keep_lines(self):
        run(["--keeplines"])

    def test_minify(self):
        run(["--minify"])

    def test_strict(self):
        run(["--strict"])


class TestExternal(unittest.TestCase):

    def test_prisoner(self):
        comp_prisoner()

    def test_pyston(self):
        comp_pyston()
        if platform.python_implementation() == "PyPy":
            run_pyston()
