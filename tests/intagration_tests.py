#!/usr/bin/env python
"""
Authors: Fred Buchanan
License: Apache 2.0
Description: Intgation tests for coconut
"""

from __future__ import print_function, absolute_import, unicode_literals, division

import unittest
import sys
import os
import subprocess
import shutil


class OldCocoTest(unittest.TestCase):


    def compile_extras(self):
        src = os.path.join(self.src,"extras.coco")
        subprocess.check_call(["coconut",src,self.bin])

    def compile_runner(self):
        src = os.path.join(self.src,"src","runner.coco")
        subprocess.check_call(["coconut",src,self.bin])

    def compile_agnostic(self):
        src = os.path.join(self.src,"src","agnostic")
        bin = os.path.join(self.bin,"cocotest")
        subprocess.check_call(["coconut",src,bin])

    def compile_2(self):
        src = os.path.join(self.src,"src","python2")
        bin = os.path.join(self.bin,"cocotest")
        subprocess.check_call(["coconut","--target","2",src,bin])

    def compile_3(self):
        src = os.path.join(self.src,"src","python3")
        bin = os.path.join(self.bin,"cocotest")
        subprocess.check_call(["coconut","--target","3",src,bin])

    def compile_35(self):
        src = os.path.join(self.src,"src","python35")
        bin = os.path.join(self.bin,"cocotest")
        subprocess.check_call(["coconut","--target","35",src,bin])


    def compile_source(self):
        self.compile_extras()
        self.compile_runner()
        self.compile_agnostic()
        
        if sys.version_info >= (3,):
            self.compile_3()
        if sys.version_info >= (3,5):
            self.compile_35()
        if (sys.version_info >= (2,)) & (sys.version_info < (3,)):
            self.compile_2()

    def test_compile_and_run_src(self):
        self.src = os.path.join(os.path.abspath(os.path.dirname(__file__)),"src")
        self.bin = os.path.join(os.path.abspath(os.path.dirname(__file__)),"bin")

        self.compile_source()
        subprocess.check_call(["python",os.path.join(self.bin,"runner.py")])
        shutil.rmtree(self.bin)

if __name__ == '__main__':
    unittest.main()