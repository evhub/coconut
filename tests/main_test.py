#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: Runs Coconut tests.
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

base = os.path.dirname(os.path.relpath(__file__))
src = os.path.join(base, "src")
dest = os.path.join(base, "dest")


def call(cmd, assert_output=False):
    """Executes a shell command."""
    print("\n>", " ".join(cmd))
    if assert_output:
        for line in subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.readlines():
            line = line.rstrip()
            print(line)
        assert line == b"<success>"
    else:
        subprocess.check_call(cmd)


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
    if "--jobs" not in args and platform.python_implementation() == "PyPy":
        args += ["--jobs", "0"]
    call(["coconut", source, compdest] + args)


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


def run(args=[], agnostic_target=None):
    """Compiles and runs tests."""
    if agnostic_target is None:
        agnostic_args = []
    else:
        agnostic_args = ["--target", str(agnostic_target)]

    with create_dest():

        comp_runner(args + agnostic_args)
        comp_agnostic(args + agnostic_args)
        if PY2:
            comp_2(args)
        else:
            comp_3(args)
            if sys.version_info >= (3, 5):
                comp_35(args)
        run_src()

        if (PY2 and not PY26) or (not PY2 and sys.version_info >= (3, 3)):
            comp_extras(args)
            run_extras()

#-----------------------------------------------------------------------------------------------------------------------
# TESTS:
#-----------------------------------------------------------------------------------------------------------------------


class TestCompilation(unittest.TestCase):

    def test_normal(self):
        run()

    def test_jobs_zero(self):
        run(["--jobs", "0"])

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

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------


def main():
    """Run Coconut tests."""
    unittest.main()
