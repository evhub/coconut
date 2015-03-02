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
import os
import os.path

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
    code_ext = ".coc"
    comp_ext = ".py"
    max_debug = 2
    commandline = argparse.ArgumentParser(description="The Coconut Programming Language.")
    commandline.add_argument("source", metavar="source", type=str, nargs="?", default=None, help="path to the coconut file/module to compile")
    commandline.add_argument("dest", metavar="dest", type=str, nargs="?", default=None, help="destination directory for compiled files (defaults to the source directory)")
    commandline.add_argument("-v", "--version", action="store_const", const=True, default=False, help="print coconut and python version information")
    commandline.add_argument("-s", "--strict", action="store_const", const=True, default=False, help="enforce code cleanliness standards")
    commandline.add_argument("-r", "--run", action="store_const", const=True, default=False, help="run the compiled source instead of writing it")
    commandline.add_argument("-i", "--interact", action="store_const", const=True, default=False, help="force the interpreter to start (otherwise starts if no other command is given)")
    commandline.add_argument("-d", "--debug", metavar="level", type=int, nargs="?", default=0, const=1, help="enable debug output (level: 0 is off, no arg defaults to 1, max is "+str(max_debug)+")")
    commandline.add_argument("-c", "--code", metavar="code", type=str, nargs=1, help="run a line of coconut passed in as a string")
    commandline.add_argument("--autopep8", type=str, nargs=argparse.REMAINDER, default=None, help="use autopep8 to format compiled code (remaining args passed to autopep8)")
    processor = None
    debug = False
    running = False
    runner = None

    def __init__(self, main_color=None, debug_color=None, prompt=">>> ", moreprompt="    ", main_sig="Coconut: ", debug_sig=None):
        """Creates The CLI."""
        self.console = terminal(main_color, debug_color, main_sig, debug_sig)
        self.prompt = self.console.addcolor(prompt, main_color)
        self.moreprompt = self.console.addcolor(moreprompt, main_color)

    def start(self):
        """Gets Command-Line Arguments."""
        args = self.commandline.parse_args()
        self.cmd(args)

    def setup(self, strict=False):
        """Creates The Processor."""
        self.processor = parser.processor(strict)
        self.processor.TRACER.show = self.console.debug

    def debug_set(self, level=0):
        """Sets The Debug Level."""
        self.debug = level >= 1
        self.processor.debug(level >= 2)

    def debug_level(self, level=0):
        """Processes A Debug Level."""
        if level < 0 or self.max_debug < level:
            raise parser.CoconutException("debug level must be in range(0, "+str(self.max_debug+1)+")")
        else:
            self.debug_set(level)

    def cmd(self, args):
        """Parses Command-Line Arguments."""
        self.setup(args.strict)
        self.debug_level(args.debug)
        if args.version:
            self.console.print("Version "+repr(VERSION)+" running on Python "+sys.version)
        if args.autopep8 is not None:
            self.processor.autopep8(args.autopep8)
        if args.code is not None:
            self.execute(self.processor.parse_single(args.code))
        if args.source is not None:
            if args.run:
                if args.dest is not None:
                    raise parser.CoconutException("a destination cannot be given when --run is enabled")
                elif not os.isfile(args.source):
                    raise parser.CoconutException("the source path must point to a file when --run is enabled")
                else:
                    self.compile_file(args.source, None, None)
            elif args.dest is None:
                self.compile_path(args.source)
            elif os.path.isfile(args.dest):
                raise parser.CoconutException("destination path points to file "+repr(args.dest))
            else:
                if not os.path.exists(args.dest):
                    os.makedirs(args.dest)
                self.compile_path(args.source, args.dest)
        if args.interact or not (args.source or args.code or args.version):
            self.start_prompt()

    def compile_path(self, path, write=True):
        """Compiles A Path."""
        if os.path.isfile(path):
            self.compile_file(path, write)
        elif os.path.isdir(path):
            self.compile_module(path, write)
        else:
            raise parser.CoconutException("could not find source path "+repr(path))

    def compile_module(self, directory, write=True):
        """Compiles A Module."""
        for dirpath, dirnames, filenames in os.walk(directory):
            writedir = write
            if writedir is True:
                self.create_module(dirpath)
            elif writedir:
                writedir = os.path.join(writedir, os.path.relpath(dirpath, directory))
            for filename in filenames:
                if os.path.splitext(filename)[1] == self.code_ext:
                    self.compile_file(os.path.join(dirpath, filename), writedir, True)

    def compile_file(self, filename, write=True, module=False):
        """Compiles A File."""
        if write is None:
            destfilename = None
        elif write is True:
            destfilename = os.path.splitext(filename)[0]+self.comp_ext
        else:
            destfilename = os.path.join(write, os.path.splitext(os.path.basename(filename))[0]+self.comp_ext)
        self.compile(filename, destfilename, module)

    def compile(self, codefilename, destfilename=None, module=False):
        """Compiles A Source Coconut File To A Destination Python File."""
        self.console.print("Compiling "+repr(codefilename)+"...")
        with openfile(codefilename, "r") as opened:
            code = readfile(opened)
        if module is True:
            compiled = self.processor.parse_module(code)
        elif module is None:
            compiled = self.processor.parse_block(code)
        elif module is False:
            compiled = self.processor.parse_file(code)
        else:
            raise parser.CoconutException("invalid value for module boolean of "+repr(module))
        if destfilename is None:
            self.execute(compiled)
        else:
            with openfile(destfilename, "w") as opened:
                writefile(opened, compiled)
            self.console.print("Compiled "+repr(destfilename)+".")

    def create_module(self, dirpath):
        """Sets Up A Module Directory."""
        with openfile(os.path.join(dirpath, "__coconut__.py"), "w") as opened:
            writefile(opened, parser.headers["code"])

    def start_prompt(self):
        """Starts The Interpreter."""
        self.console.print("[Interpreter:]")
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

    def execute(self, compiled=None):
        """Executes Compiled Code."""
        if self.runner is None:
            self.start_runner()
        if compiled is not None:
            if self.debug:
                self.console.debug("Executing "+repr(compiled)+"...")
            self.runner.run(compiled)

    def start_runner(self):
        """Starts The Runner."""
        self.runner = executor({
            "exit" : self.exit
            })
        self.runner.run(parser.headers["code"])
