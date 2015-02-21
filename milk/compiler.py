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
import sys
import traceback

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

def print_error():
    """Processes An Error."""
    err_type, err_value, err_trace = sys.exc_info()
    traceback.print_exception(err_type, err_value, err_trace)

class executor(object):
    """Compiled Python Executor."""
    def __init__(self, extras=None):
        """Creates The Executor."""
        self.variables = {}
        if extras is not None:
            for k,v in extras.items():
                self.variables[k] = v
    def run(__self, __code, __error=print_error):
        """Executes Python Code."""
        for __k, __v in __self.variables.items():
            locals()[__k] = __v
        __snapshot = locals().copy()
        try:
            exec(__code)
        except Exception as err:
            __error()
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
    arguments = argparse.ArgumentParser(description="The Coconut Programming Language.")
    arguments.add_argument("filenames", metavar="files", type=str, nargs="*", help="the names of the files to compile; if no file names are passed, the REPL is started instead")
    running = False

    def __init__(self, color=None, prompt=">>>", moreprompt="...", prompt_color=None, error_color=None, debug=False):
        """Creates The CLI."""
        self.debug = debug
        self.gui = terminal(color)
        self.prompt = self.gui.addcolor(prompt, prompt_color)+" "
        self.moreprompt = self.gui.addcolor(moreprompt, prompt_color)+" "
        self.error_color = error_color

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
        self.runner = executor({"print" : self.gui.print, "exit" : self.exit})
        self.runner.run(parser.HEADER)
        self.running = True
        while self.running:
            self.process(raw_input(self.prompt))

    def exit(self):
        """Exits The REPL."""
        self.running = False

    def process(self, code):
        """Executes Coconut REPL Input."""
        try:
            compiled = parser.parse_single(code)
        except parser.ParseException:
            while True:
                line = raw_input(self.moreprompt)
                if line:
                    code += "\n"+line
                else:
                    break
            compiled = parser.parse_single(code)
        if self.debug:
            self.gui.print("[Coconut] Executing "+repr(py)+"...")
        self.runner.run(compiled)

if __name__ == "__main__":
    cli(debug=True).start()
