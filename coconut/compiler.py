#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: The Coconut CLI.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from .root import *
from . import parser
import traceback
import os
import os.path
import argparse

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------

def openfile(filename, opentype="r+"):
    """Returns an open file object."""
    return open(filename, opentype, encoding=ENCODING)

def writefile(openedfile, writer):
    """Sets the contents of a file."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(writer)

def readfile(openedfile):
    """Reads the contents of a file."""
    openedfile.seek(0)
    return str(openedfile.read())

def fixpath(path):
    """Properly formats a path."""
    return os.path.normpath(os.path.realpath(path))

def hashashof(destpath, code):
    """Determines if a file has the hash of the code."""
    if destpath is not None and os.path.isfile(destpath):
        with openfile(destpath, "r") as opened:
            compiled = readfile(opened)
            hashash = parser.gethash(compiled)
            if hashash is not None and hashash == parser.genhash(code):
                return compiled
    return None

def print_error(verbose=False):
    """Displays a formatted error."""
    err_type, err_value, err_trace = sys.exc_info()
    if verbose:
        err = "".join(traceback.format_exception(err_type, err_value, err_trace)).strip()
    else:
        err_name, err_msg = "".join(traceback.format_exception_only(err_type, err_value)).strip().split(": ", 1)
        err_name = err_name.split(".")[-1]
        err = err_name+": "+err_msg
    print(err, file=sys.stderr)

class executor(object):
    """Compiled Python executor."""
    def __init__(self, extras=None):
        """Creates the executor."""
        self.vars = {}
        if extras is not None:
            self.vars.update(extras)
    def setfile(self, path):
        """Sets __file__."""
        self.vars["__file__"] = path
    def run(self, code, err=False):
        """Executes Python code."""
        try:
            exec(code, self.vars)
        except Exception:
            if err:
                raise
            else:
                traceback.print_exc()

class terminal(object):
    """Manages printing and reading data to the console."""
    colors = {
        "end": "\033[0m",
        "bold": "\033[1m",
        "blink": "\033[5m",
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "blackhighlight": "\033[40m",
        "redhighlight": "\033[41m",
        "greenhighlight": "\033[42m",
        "yellowhighlight": "\033[43m",
        "bluehighlight": "\033[44m",
        "magentahighlight": "\033[45m",
        "cyanhighlight": "\033[46m",
        "whitehighlight": "\033[47m",
        "pink": "\033[95m",
        "purple": "\033[94m",
        "lightgreen": "\033[92m",
        "lightyellow": "\033[93m",
        "lightred": "\033[91m"
        }
    on = True

    def __init__(self, main_color=None, debug_color=None, main_sig="", debug_sig=""):
        """Creates the terminal."""
        self.main_color = main_color
        self.debug_color = debug_color
        self.main_sig = main_sig
        self.debug_sig = debug_sig

    def addcolor(self, inputstring, color):
        """Adds the specified color to the string."""
        if color is not None:
            return self.colors[color] + inputstring + self.colors["end"]
        else:
            return inputstring

    def delcolor(self, inputstring):
        """Removes recognized colors from a string."""
        inputstring = str(inputstring)
        for x in self.colors:
            inputstring = inputstring.replace(x, "")
        return inputstring

    def display(self, messages, color=None, sig="", debug=False):
        """Prints messages."""
        message = " ".join(str(msg) for msg in messages)
        for line in message.splitlines():
            msg = self.addcolor(sig+line, color)
            if debug is True:
                print(msg, file=sys.stderr)
            else:
                print(msg)

    def show(self, *messages):
        """Prints messages with main color without a signature."""
        if self.on:
            self.display(messages, color=self.main_color)

    def print(self, *messages):
        """Prints messages with main color."""
        if self.on:
            self.display(messages, self.main_color, self.main_sig)

    def debug(self, *messages):
        """Prints messages with debug color."""
        self.display(messages, self.debug_color, self.debug_sig, True)

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

class cli(object):
    """The Coconut command-line interface."""
    version = "Version "+VERSION_STR+" running on Python "+" ".join(sys.version.splitlines())
    code_ext = ".coc"
    comp_ext = ".py"
    commandline = argparse.ArgumentParser(description="The Coconut Programming Language.")
    commandline.add_argument("source", metavar="source", type=str, nargs="?", default=None, help="path to the Coconut file/folder to compile")
    commandline.add_argument("dest", metavar="dest", type=str, nargs="?", default=None, help="destination directory for compiled files (defaults to the source directory)")
    commandline.add_argument("-v", "--version", action="store_const", const=True, default=False, help="print Coconut and Python version information")
    commandline.add_argument("-t", "--target", metavar="version", type=str, nargs=1, default=[None], help="specify target Python version")
    commandline.add_argument("-s", "--strict", action="store_const", const=True, default=False, help="enforce code cleanliness standards")
    commandline.add_argument("-p", "--print", action="store_const", const=True, default=False, help="print the compiled Python")
    commandline.add_argument("-f", "--force", action="store_const", const=True, default=False, help="force overwriting of compiled Python (otherwise only overwrites when the source changes)")
    commandline.add_argument("-r", "--run", action="store_const", const=True, default=False, help="run the compiled Python")
    commandline.add_argument("-n", "--nowrite", action="store_const", const=True, default=False, help="disable writing the compiled Python")
    commandline.add_argument("-i", "--interact", action="store_const", const=True, default=False, help="force the interpreter to start (otherwise starts if no other command is given)")
    commandline.add_argument("-q", "--quiet", action="store_const", const=True, default=False, help="suppress all informational output")
    commandline.add_argument("-d", "--debug", action="store_const", const=True, default=False, help="print verbose debug output")
    commandline.add_argument("-c", "--code", metavar="code", type=str, nargs=1, default=None, help="run a line of Coconut passed in as a string (can also be accomplished with a pipe)")
    commandline.add_argument("--autopep8", type=str, nargs=argparse.REMAINDER, default=None, help="use autopep8 to format compiled code (remaining args passed to autopep8)")
    processor = None
    show = False
    running = False
    runner = None
    target = None

    def __init__(self, main_color=None, debug_color=None, prompt=">>> ", moreprompt="    ", main_sig="Coconut: ", debug_sig=""):
        """Creates the CLI."""
        self.console = terminal(main_color, debug_color, main_sig, debug_sig)
        self.prompt = self.console.addcolor(prompt, main_color)
        self.moreprompt = self.console.addcolor(moreprompt, main_color)

    def start(self):
        """Gets command-line arguments."""
        args = self.commandline.parse_args()
        self.cmd(args)

    def setup(self, strict=False, target=None):
        """Creates the processor."""
        if self.processor is None:
            self.processor = parser.processor(strict, target, self.console.show)
            self.processor.TRACER.show = self.console.debug
        else:
            self.processor.setup(strict, target)

    def quiet(self, state=None):
        """Quiets output."""
        if state is None:
            state = self.console.on
        self.console.on = not state

    def indebug(self):
        """Determines whether the parser is in debug mode."""
        return self.processor.indebug()

    def cmd(self, args, interact=True):
        """Parses command-line arguments."""
        try:
            self.setup(args.strict, args.target[0])
            if args.debug:
                self.processor.debug(True)
            if args.quiet:
                self.quiet(True)
            if args.print:
                self.show = True
            if args.version:
                self.console.print(self.version)
            if args.autopep8 is not None:
                self.processor.autopep8(args.autopep8)
            if args.code is not None:
                self.execute(self.processor.parse_single(args.code[0]))
            if args.source is not None:
                if args.run and os.path.isdir(args.source):
                    raise parser.CoconutException("source path must point to file not directory when --run is enabled")
                if args.dest is None:
                    if args.nowrite:
                        self.compile_path(args.source, None, run=args.run, force=args.force)
                    else:
                        self.compile_path(args.source, run=args.run, force=args.force)
                elif args.nowrite:
                    raise parser.CoconutException("destination path can't be given when --nowrite is enabled")
                elif os.path.isfile(args.dest):
                    raise parser.CoconutException("destination path must point to directory not file")
                else:
                    self.compile_path(args.source, args.dest, run=args.run, force=args.force)
            elif args.run:
                raise parser.CoconutException("a source file must be specified when --run is enabled")
            stdin = not sys.stdin.isatty()
            if stdin:
                self.execute(self.processor.parse_block(sys.stdin.read()))
            if args.interact or (interact and not (stdin or args.source or args.version or args.code)):
                self.start_prompt()
        except parser.CoconutException:
            print_error(self.indebug())
            sys.exit(1)

    def compile_path(self, path, write=True, run=False, force=False):
        """Compiles a path."""
        if os.path.isfile(path):
            if write is None:
                module = None
            else:
                module = False
            self.compile_file(path, write, module, run, force)
        elif os.path.isdir(path):
            self.compile_module(path, write, run, force)
        else:
            raise parser.CoconutException("could not find source path "+path)

    def compile_module(self, directory, write=True, run=False, force=False):
        """Compiles a module."""
        for dirpath, dirnames, filenames in os.walk(directory):
            writedir = write
            module = True
            if writedir is None:
                tocreate = None
                module = None
            elif writedir is True:
                tocreate = dirpath
            else:
                writedir = os.path.join(writedir, os.path.relpath(dirpath, directory))
                tocreate = writedir
            wrote = False
            for filename in filenames:
                if os.path.splitext(filename)[1] == self.code_ext:
                    self.compile_file(os.path.join(dirpath, filename), writedir, module, run, force)
                    wrote = True
            if wrote and tocreate is not None:
                self.create_module(tocreate)

    def compile_file(self, filepath, write=True, module=False, run=False, force=False):
        """Compiles a file."""
        filepath = fixpath(filepath)
        if write is None:
            destpath = None
        elif write is True:
            destpath = filepath
        else:
            destpath = os.path.join(write, os.path.basename(filepath))
        if destpath is not None:
            base, ext = os.path.splitext(os.path.splitext(destpath)[0])
            if not ext:
                ext = self.comp_ext
            destpath = fixpath(base + ext)
        self.compile(filepath, destpath, module, run, force)

    def compile(self, codepath, destpath=None, module=False, run=False, force=False):
        """Compiles a source Coconut file to a destination Python file."""
        self.console.print("Compiling       "+codepath+" ...")
        with openfile(codepath, "r") as opened:
            code = readfile(opened)
        foundhash = None if force else hashashof(destpath, code)
        if foundhash:
            if run:
                self.execute(foundhash, path=destpath)
            elif self.show:
                print(foundhash)
            self.console.print("Left unchanged  "+destpath+" (pass --force to overwrite).")
        else:
            if module is True:
                compiled = self.processor.parse_module(code)
            elif module is None:
                compiled = self.processor.parse_block(code)
            elif module is False:
                compiled = self.processor.parse_file(code)
            else:
                raise parser.CoconutException("invalid value for module boolean", module)
            if run:
                self.execute(compiled, path=(destpath if destpath is not None else codepath))
            elif self.show:
                print(compiled)
            if destpath is None:
                self.console.print("Compiled without writing to file.")
            else:
                destdir = os.path.dirname(destpath)
                if not os.path.exists(destdir):
                    os.makedirs(destdir)
                with openfile(destpath, "w") as opened:
                    writefile(opened, compiled)
                self.console.print("Compiled to     "+destpath+" .")

    def create_module(self, dirpath):
        """Sets up a module directory."""
        filepath = os.path.join(dirpath, "__coconut__.py")
        with openfile(filepath, "w") as opened:
            writefile(opened, parser.headers("package", self.processor.version))

    def prompt_with(self, prompt):
        """Prompts for code."""
        try:
            return input(prompt)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
        except EOFError:
            print()
            self.exit()
        return None

    def start_prompt(self):
        """Starts the interpreter."""
        self.check_runner()
        self.console.show("Coconut Interpreter:")
        self.console.show('(type "exit()" or press Ctrl-D to end)')
        self.running = True
        while self.running:
            code = self.prompt_with(self.prompt)
            if code:
                compiled = self.handle(code)
                if compiled:
                    self.execute(compiled, False)

    def exit(self):
        """Exits the interpreter."""
        self.running = False

    def handle(self, code):
        """Compiles Coconut interpreter input."""
        try:
            compiled = self.processor.parse_single(code)
        except parser.CoconutException:
            while True:
                line = self.prompt_with(self.moreprompt)
                if line:
                    code += "\n" + line
                elif line is None:
                    return None
                else:
                    break
            try:
                compiled = self.processor.parse_single(code)
            except parser.CoconutException:
                print_error(self.indebug())
                return None
        return compiled

    def execute(self, compiled=None, error=True, path=None):
        """Executes compiled code."""
        self.check_runner(path)
        if compiled is not None:
            if self.show:
                print(compiled)
            self.runner.run(compiled, error)

    def check_runner(self, path=None):
        """Makes sure there is a runner."""
        if self.runner is None:
            self.start_runner()
        if path is not None:
            self.runner.setfile(path)

    def start_runner(self):
        """Starts the runner."""
        sys.path.append(os.getcwd())
        self.runner = executor({
            "exit": self.exit
            })
        self.runner.run(parser.headers("code", "2" if PY2 else "3"))
