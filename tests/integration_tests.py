#!/usr/bin/env python
"""
Authors: Fred Buchanan
License: Apache 2.0
Description: Integration tests for coconut
"""

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

import unittest
import sys
import os
import subprocess
import shutil
import functools

call = functools.partial(subprocess.check_call,stderr=sys.stdout.fileno())

class OldCocoTest(unittest.TestCase):

    def _compile_extras(self,extraCommands = []):
        src = os.path.join(self.src,"extras.coco")

        cmd = ["coconut"] + extraCommands + [src,self.bin]
        call(cmd)

    def _compile_runner(self,extraCommands = []):
        src = os.path.join(self.src,"src","runner.coco")

        cmd = ["coconut"] + extraCommands + [src,self.bin]
        call(cmd)

    def _compile_agnostic(self,extraCommands = []):
        src = os.path.join(self.src,"src","agnostic")
        bin = os.path.join(self.bin,"cocotest")

        cmd = ["coconut"] + extraCommands + [src,bin]
        call(cmd)

    def _compile_2(self,extraCommands = []):
        src = os.path.join(self.src,"src","python2")
        bin = os.path.join(self.bin,"cocotest")

        cmd = ["coconut","--target","2"] + extraCommands + [src,bin]
        call(cmd)

    def _compile_3(self,extraCommands = []):
        src = os.path.join(self.src,"src","python3")
        bin = os.path.join(self.bin,"cocotest")

        cmd = ["coconut","--target","3"] + extraCommands + [src,bin]
        call(cmd)

    def _compile_35(self,extraCommands = []):
        src = os.path.join(self.src,"src","python35")
        bin = os.path.join(self.bin,"cocotest")

        cmd = ["coconut","--target","35"] + extraCommands + [src,bin]
        call(cmd)

    def _run_source(self):
        call(["python",os.path.join(self.bin,"runner.py")])

    def _compile_source(self,agnosticTarget = None, stict = False, minify = False, line_numbers = False, keep_lines = False):

        agnosticCommands = []
        extraCommands = []
        if agnosticTarget != None:
            agnosticCommands += ["--target",agnosticTarget]
        if stict:
            extraCommands += ["--strict"]
        if line_numbers:
            extraCommands += ["--line-numbers"]
        if keep_lines:
            extraCommands += ["--keep-lines"]

        self._compile_runner(extraCommands+agnosticCommands)
        self._compile_agnostic(extraCommands+agnosticCommands)
        
        if sys.version_info >= (3,):
            self._compile_3(extraCommands)
        if sys.version_info >= (3,5):
            self._compile_35(extraCommands)
        if (sys.version_info >= (2,)) & (sys.version_info < (3,)):
            self._compile_2(extraCommands)

    def _clean(self):
        shutil.rmtree(self.bin)

    def setUp(self):
        self.src = os.path.join(os.path.abspath(os.path.dirname(__file__)),"src")
        self.bin = os.path.join(os.path.abspath(os.path.dirname(__file__)),"bin")

    def tearDown(self):
        try:
            pass
            #self._clean()
        except:
            pass

    def test_normal(self):
        self._compile_source()
        self._run_source()
        self._clean()

    def test_strict(self):
        self._compile_source(stict = True)
        self._run_source()
        self._clean()

    def test_minify(self):
        self._compile_source(minify = True)
        self._run_source()
        self._clean()

    def test_line_numbers(self):
        self._compile_source(line_numbers = True)
        self._run_source()
        self._clean()

    def test_keep_lines(self):
        self._compile_source(keep_lines = True)
        self._run_source()
        self._clean()
        
    def test_version_target(self):
        version = "".join([str(sys.version_info.major),str(sys.version_info.minor)])
        self._compile_source(agnosticTarget = version)
        self._run_source()
        self._clean()
        
    def test_extra(self):
        self._compile_extras()
        #call(["python",os.path.join(self.bin,"extras.py")])
        self._clean()

if __name__ == '__main__':
    unittest.main()