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
        for __k, __v in list(globals().items()):
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
    extension = ".coc.py"
    commandline = argparse.ArgumentParser(description="The Coconut Programming Language.")
    commandline.add_argument("filenames", metavar="path", type=str, nargs="*", default=[], help="names of files to compile")
    commandline.add_argument("-c", "--code", type=str, nargs=argparse.REMAINDER, default=[], help="run code passed in as string")
    commandline.add_argument("-r", "--run", action="store_const", const=True, default=False, help="run files after compiling them")
    commandline.add_argument("-n", "--nowrite", action="store_const", const=True, default=False, help="disable writing of compiled code")
    commandline.add_argument("-i", "--interact", action="store_const", const=True, default=False, help="start the interpreter after compiling files")
    commandline.add_argument("-d", "--debug", action="store_const", const=True, default=False, help="shows compiled python being executed")
    commandline.add_argument("--autopep8", type=str, nargs=argparse.REMAINDER, default=None, help="use autopep8 to format compiled code")
    running = False
    runner = None

    def __init__(self, color=None, prompt=">>> ", moreprompt="    "):
        """Creates The CLI."""
        self.processor = parser.processor()
        self.gui = terminal(color)
        self.prompt = self.gui.addcolor(prompt, color)
        self.moreprompt = self.gui.addcolor(moreprompt, color)

    def start(self):
        """Gets Command-Line Arguments."""
        args = self.commandline.parse_args()
        self.parse(args)

    def parse(self, args):
        """Parses Command-Line Arguments."""
        self.debug = args.debug
        if args.autopep8 is not None:
            self.processor.autopep8(args.autopep8)
        for code in args.code:
            self.execute(self.processor.parse_single(code))
        for filename in args.filenames:
            if args.nowrite:
                codefilename = filename
                destfilename = None
            else:
                codefilename, destfilename = self.resolve(filename)
            self.compile(codefilename, destfilename, args.run)
        if args.interact or not (args.filenames or args.code):
            self.start_prompt()

    def compile(self, codefilename, destfilename, run=False):
        """Compiles A Source Coconut File To A Destination Python File."""
        self.gui.print("[Coconut] Compiling "+repr(codefilename)+"...")
        compiled = self.processor.parse_file(readfile(openfile(codefilename, "r")))
        if destfilename is not None:
            writefile(openfile(destfilename, "w"), compiled)
            self.gui.print("[Coconut] Compiled "+repr(destfilename)+".")
        if run:
            self.execute(compiled)

    def resolve(self, filename):
        """Resolves A Filename Into Source And Destination Files."""
        base, ext = os.path.splitext(filename)
        codefilename = base + ext
        destfilename = base + self.extension
        return codefilename, destfilename

    def start_prompt(self):
        """Starts The Interpreter."""
        self.gui.print("[Coconut] Interpreter:")
        self.running = True
        while self.running:
            self.execute(self.handle(input(self.prompt)))

    def exit(self):
        """Exits The Interpreter."""
        self.running = False

    def handle(self, code):
        """Compiles Coconut Interpreter Input."""
        try:
            compiled = self.processor.parse_single(code)
        except (parser.ParseFatalException, parser.ParseException):
            while True:
                line = input(self.moreprompt)
                if line:
                    code += "\n"+line
                else:
                    break
            try:
                compiled = self.processor.parse_single(code)
            except (parser.ParseFatalException, parser.ParseException):
                return print_error()
        return compiled

    def execute(self, compiled):
        """Executes Compiled Code."""
        if self.runner is None:
            self.start_runner()
        if self.debug:
            self.gui.print("[Coconut] Executing "+repr(compiled)+"...")
        self.runner.run(compiled)

    def start_runner(self):
        """Starts The Runner."""
        self.runner = executor({
            "exit" : self.exit
            })
        self.runner.run(parser.HEADER)
