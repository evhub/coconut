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

EXTENSION = ".coc.py"
def compile_cmd(filename):
    """Compiles A Coconut File Using The Command Line Argument."""
    base, ext = os.path.splitext(filename)
    codefilename = base + ext
    destfilename = base + EXTENSION
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
        __globals = globals().copy()
        __locals = locals().copy()
        for __k, __v in __self.variables.items():
            globals()[__k] = __v
        try:
            exec(__code)
        except Exception:
            __error()
        __overrides = {}
        for __k, __v in globals().items():
            if __k in __self.variables:
                __self.variables[__k] = __v
                del globals()[__k]
            elif __k not in __globals:
                __overrides[__k] = __v
                del globals()[__k]
        for __k, __v in locals().items():
            if __k in __self.variables:
                __self.variables[__k] = __v
            elif __k not in __locals:
                __self.variables[__k] = __v
        for __k, __v in __overrides.items():
            __self.variables[__k] = __v
        for __k, __v in __globals.items():
            globals()[__k] = __v

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class cli(object):
    """The Coconut Command-Line Interface."""
    arguments = argparse.ArgumentParser(description="The Coconut Programming Language.")
    arguments.add_argument("filenames", metavar="path", type=str, nargs="*", help="the names of the files to compile; if no file names are passed, the interpreter is started instead")
    running = False

    def __init__(self, color=None, prompt=">>> ", moreprompt="    ", prompt_color=None, debug=False):
        """Creates The CLI."""
        self.debug = debug
        self.gui = terminal(color)
        self.prompt = self.gui.addcolor(prompt, prompt_color)
        self.moreprompt = self.gui.addcolor(moreprompt, prompt_color)

    def start(self):
        """Starts The CLI."""
        args = self.arguments.parse_args()
        if args.filenames is None or len(args.filenames) == 0:
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
        self.gui.print("[Coconut] Interpreter:")
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
        except parser.ParseFatalException:
            return print_error()
        except parser.ParseException:
            while True:
                line = raw_input(self.moreprompt)
                if line:
                    code += "\n"+line
                else:
                    break
            try:
                compiled = parser.parse_single(code)
            except parser.ParseException, parser.ParseFatalException:
                return print_error()
        if self.debug:
            self.gui.print("[Coconut] Executing "+repr(compiled)+"...")
        self.runner.run(compiled)

if __name__ == "__main__":
    cli(debug=True).start()
