#!/usr/bin/env python

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
Date Created: 2014
Description: The Coconut Compiler.
"""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from .util import *
from . import parser
import argparse

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def compile_file(codefilename, destfilename):
    """Compiles A Source Coconut File To A Destination Python File."""
    writefile(openfile(destfilename, "w"), parser.parse_file(readfile(openfile(codefilename, "r"))))

def compile_cmd(filename):
    """Compiles A Coconut File Using The Command Line Argument."""
    basename, extension = os.path.splitext(filename)
    codefilename = basename + extension
    destfilename = basename + ".py"
    compile_file(codefilename, destfilename)

class executor(object):
    """Compiled Python Executor."""
    def __init__(self, extras=None):
        """Creates The Executor."""
        self.variables = {}
        if extras is not None:
            for k,v in extras.items():
                self.variables[k] = v
    def run(__self, __code):
        """Executes Python Code."""
        for __k, __v in __self.variables.items():
            locals()[__k] = __v
        __snapshot = locals().copy()
        exec(__code)
        for __k, __v in locals().items():
            if __k not in __snapshot:
                __self.variables[__k] = __v
            elif __k in __self.variables:
                __self.variables[__k] = __v

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class cli(object):
    """The Coconut Command-Line Interface."""
    arguments = argparse.ArgumentParser(description="The Coconut Compiler.")
    arguments.add_argument("filenames", metavar="file", type=str, nargs="?", help="The name of the file to compile.")
    running = False

    def __init__(self, color=None, prompt=">>>", prompt_color=None, debug=False):
        """Creates The CLI."""
        self.debug = debug
        self.gui = terminal(color)
        self.prompt = self.gui.addcolor(prompt, prompt_color)+" "

    def start(self):
        """Starts The CLI."""
        args = self.arguments.parse_args()
        if args.filenames is None:
            self.repl()
        else:
            for filename in args.filenames:
                self.compile(filename)

    def compile(self, filename):
        """Compiles A File With Printing."""
        self.gui.print("[Coconut] Compiling '"+codefilename+"'...")
        compile_cmd(filename)
        self.gui.print("[Coconut] Compiled '"+destfilename+"'.")

    def repl(self):
        """Starts The REPL."""
        self.gui.print("[Coconut] REPL:")
        self.running = True
        self.runner = executor({"print" : self.gui.print})
        self.runner.run(parser.HEADER)
        while self.running:
            self.process(raw_input(self.prompt))

    def process(self, code):
        """Executes Coconut REPL Input."""
        py = parser.parse_single(code)
        if self.debug:
            self.gui.print("[Coconut] Executing "+repr(py)+"...")
        self.runner.run(py)

if __name__ == "__main__":
    cli(debug=True).start()
