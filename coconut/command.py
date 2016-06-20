#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Processes arguments to the Coconut command-line utility.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from .compiler import *
import os
import os.path
import argparse

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

code_exts = [".coco", ".coc", ".coconut"] # in order of preference
comp_ext = ".py"

main_sig = "Coconut: "
debug_sig = ""

default_prompt = ">>> "
default_moreprompt = "    "

color_codes = { # unix/ansii color codes, underscores in names removed
    "bold": 1,
    "dim": 2,
    "underlined": 4,
    "blink": 5,
    "reverse": 7,
    "default": 39,
    "black": 30,
    "red": 31,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "lightgray": 37,
    "darkgray": 90,
    "lightred": 91,
    "lightgreen": 92,
    "lightyellow": 93,
    "lightblue": 94,
    "lightmagenta": 95,
    "lightcyan": 96,
    "white": 97,
    "defaultbackground": 49,
    "blackbackground": 40,
    "redbackground": 41,
    "greenbackground": 42,
    "yellowbackground": 43,
    "bluebackground": 44,
    "magentabackground": 45,
    "cyanbackground": 46,
    "lightgraybackground": 47,
    "darkgraybackground": 100,
    "lightredbackground": 101,
    "lightgreenbackground": 102,
    "lightyellowbackground": 103,
    "lightbluebackground": 104,
    "lightmagentabackground": 105,
    "lightcyanbackground": 106,
    "whitebackground": 107
    }
end_color_code = 0

version_long = "Version " + VERSION_STR + " running on Python " + " ".join(sys.version.splitlines())
version_banner = "Coconut " + VERSION_STR
if DEVELOP:
    version_tag = "develop"
else:
    version_tag = "v" + VERSION
tutorial_url = "http://coconut.readthedocs.org/en/" + version_tag + "/HELP.html"
documentation_url = "http://coconut.readthedocs.org/en/" + version_tag + "/DOCS.html"

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------

def openfile(filename, opentype="r+"):
    """Returns an open file object."""
    return open(filename, opentype, encoding=default_encoding) # using open from .root

def writefile(openedfile, newcontents):
    """Sets the contents of a file."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(newcontents)

def readfile(openedfile):
    """Reads the contents of a file."""
    openedfile.seek(0)
    return str(openedfile.read())

def showpath(path):
    """Formats a path for displaying."""
    return os.path.split(path)[1]

def fixpath(path):
    """Uniformly formats a path."""
    return os.path.normpath(os.path.realpath(path))

def rem_encoding(code):
    """Removes encoding declarations from Python code so it can be passed to exec."""
    old_lines = code.splitlines()
    new_lines = []
    for i in range(min(2, len(old_lines))):
        line = old_lines[i]
        if not (line.startswith("#") and "coding" in line):
            new_lines.append(line)
    new_lines += old_lines[2:]
    return "\n".join(new_lines)

class executor(object):
    """Compiled Python executor."""
    def __init__(self, proc=None, exit=None, path=None):
        """Creates the executor."""
        self.exit = exit
        self.vars = {"__name__": "__main__"}
        if path is not None:
            self.vars["__file__"] = fixpath(path)
        if proc is not None:
            self.run(proc.headers("code"))
            self.fixpickle()

    def fixpickle(self):
        """Fixes pickling of Coconut header objects."""
        from . import __coconut__
        for var in self.vars:
            if not var.startswith("__") and var in dir(__coconut__):
                self.vars[var] = getattr(__coconut__, var)

    def run(self, code, err=False, run_func=None):
        """Executes Python code."""
        try:
            if run_func is None:
                try:
                    return eval(code, self.vars)
                except SyntaxError:
                    exec(code,self.vars)
            else:
                return run_func(code, self.vars)
        except (Exception, KeyboardInterrupt):
            if err:
                raise
            else:
                traceback.print_exc()
                return None
        except SystemExit:
            if self.exit is None:
                raise
            else:
                self.exit()

def escape_color(code):
    """Generates an ANSII color code."""
    return "\033[" + str(code) + "m"

class terminal(object):
    """Manages printing and reading data to the console."""
    color_code = None
    on = True

    def __init__(self, main_sig="", debug_sig=""):
        """Creates the terminal."""
        self.main_sig, self.debug_sig = main_sig, debug_sig

    def setcolor(self, color=None):
        """Set output color."""
        if color:
            color = color.replace("_", "")
            if color in color_codes:
                self.color_code = color_codes[color]
            else:
                try:
                    color = int(color)
                except ValueError:
                    raise CoconutException('unrecognized color "'+color+'" (enter a valid color name or code)')
                else:
                    if 0 < color <= 256:
                        self.color_code = color
                    else:
                        raise CoconutException('color code '+str(color)+' out of range (must obey 0 < color code <= 256)')
        else:
            self.color_code = None

    def addcolor(self, inputstring):
        """Adds the specified color to the string."""
        if self.color_code is None:
            return inputstring
        else:
            return escape_color(self.color_code) + inputstring + escape_color(end_color_code)

    def display(self, messages, sig="", debug=False):
        """Prints messages."""
        if self.on:
            message = " ".join(str(msg) for msg in messages)
            for line in message.splitlines():
                msg = self.addcolor(sig + line)
                if debug is True:
                    printerr(msg)
                else:
                    print(msg)

    def print(self, *messages):
        """Prints messages with color."""
        self.display(messages)

    def printerr(self, *messages):
        """Prints error messages with color and debug signature."""
        self.display(messages, self.debug_sig, True)

    def show(self, *messages):
        """Prints messages with color and main signature."""
        self.display(messages, self.main_sig)

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

class cli(object):
    """The Coconut command-line interface."""
    commandline = argparse.ArgumentParser(description="The Coconut Programming Language.")
    commandline.add_argument("source", metavar="source", type=str, nargs="?", default=None, help="path to the Coconut file/folder to compile")
    commandline.add_argument("dest", metavar="dest", type=str, nargs="?", default=None, help="destination directory for compiled files (defaults to the source directory)")
    commandline.add_argument("-v", "--version", action="store_const", const=True, default=False, help="print Coconut and Python version information")
    commandline.add_argument("-t", "--target", metavar="version", type=str, nargs=1, default=[None], help="specify target Python version (defaults to universal)")
    commandline.add_argument("-s", "--strict", action="store_const", const=True, default=False, help="enforce code cleanliness standards")
    commandline.add_argument("-l", "--linenumbers", action="store_const", const=True, default=False, help="add line number comments for ease of debugging")
    commandline.add_argument("-p", "--package", action="store_const", const=True, default=False, help="compile source as part of a package (defaults to only if source is a directory)")
    commandline.add_argument("-a", "--standalone", action="store_const", const=True, default=False, help="compile source as standalone files (defaults to only if source is a single file)")
    commandline.add_argument("-f", "--force", action="store_const", const=True, default=False, help="force overwriting of compiled Python (otherwise only overwrites when source code or compilation parameters change)")
    commandline.add_argument("-d", "--display", action="store_const", const=True, default=False, help="print compiled Python")
    commandline.add_argument("-r", "--run", action="store_const", const=True, default=False, help="run compiled Python (often used with --nowrite)")
    commandline.add_argument("-n", "--nowrite", action="store_const", const=True, default=False, help="disable writing compiled Python")
    commandline.add_argument("-m", "--minify", action="store_const", const=True, default=False, help="compress compiled Python")
    commandline.add_argument("-i", "--interact", action="store_const", const=True, default=False, help="force the interpreter to start (otherwise starts if no other command is given)")
    commandline.add_argument("-q", "--quiet", action="store_const", const=True, default=False, help="suppress all informational output (combine with --display to write runnable code to stdout)")
    commandline.add_argument("-c", "--code", metavar="code", type=str, nargs=1, default=None, help="run a line of Coconut passed in as a string (can also be passed into stdin)")
    commandline.add_argument("--jupyter", "--ipython", type=str, nargs=argparse.REMAINDER, default=None, help="run Jupyter/IPython with Coconut as the kernel (remaining args passed to Jupyter)")
    commandline.add_argument("--autopep8", type=str, nargs=argparse.REMAINDER, default=None, help="use autopep8 to format compiled code (remaining args passed to autopep8)")
    commandline.add_argument("--recursionlimit", metavar="limit", type=int, nargs=1, default=[None], help="set maximum recursion depth (defaults to "+str(sys.getrecursionlimit())+")")
    commandline.add_argument("--tutorial", action="store_const", const=True, default=False, help="open the Coconut tutorial in the default web browser")
    commandline.add_argument("--documentation", action="store_const", const=True, default=False, help="open the Coconut documentation in the default web browser")
    commandline.add_argument("--color", metavar="color", type=str, nargs=1, default=[None], help="show all Coconut messages in the given color")
    commandline.add_argument("--verbose", action="store_const", const=True, default=False, help="print verbose debug output")
    proc = None # current .compiler.processor
    show = False # corresponds to --display flag
    running = False # whether the interpreter is currently active
    runner = None # the current executor
    target = None # corresponds to --target flag

    def __init__(self, prompt=default_prompt, moreprompt=default_moreprompt):
        """Creates the CLI."""
        self.console = terminal(main_sig, debug_sig)
        self.prompt, self.moreprompt = prompt, moreprompt

    def start(self):
        """Processes command-line arguments."""
        self.cmd(self.commandline.parse_args())

    def setup(self, target=None, strict=False, minify=False, linenumbers=False, quiet=False, color=None):
        """Sets parameters for the processor."""
        if color is not None:
            self.console.setcolor(color)
            self.prompt = self.console.addcolor(self.prompt)
            self.moreprompt = self.console.addcolor(self.moreprompt)
        self.console.on = not quiet
        if self.proc is None:
            self.proc = processor(target, strict, minify, linenumbers, self.console.printerr)
        else:
            self.proc.setup(target, strict, minify, linenumbers)

    def indebug(self):
        """Determines whether the processor is in debug mode."""
        if self.proc is None:
            return False
        else:
            return self.proc.indebug()

    def cmd(self, args, interact=True):
        """Parses command-line arguments."""
        try:
            if args.recursionlimit[0] is not None:
                sys.setrecursionlimit(args.recursionlimit[0])
            self.setup(args.target[0], args.strict, args.minify, args.linenumbers, args.quiet, args.color[0])
            if args.version:
                self.console.show(version_long)
            if args.tutorial:
                self.launch_tutorial()
            if args.documentation:
                self.launch_documentation()
            if args.display:
                self.show = True
            if args.verbose:
                self.proc.debug(True)
            if args.autopep8 is not None:
                self.proc.autopep8(args.autopep8)
            if args.source is not None:
                if args.run and os.path.isdir(args.source):
                    raise CoconutException("source path must point to file not directory when --run is enabled")
                if args.dest is None:
                    if args.nowrite:
                        dest = None # no dest
                    else:
                        dest = True # auto-generate dest
                elif args.nowrite:
                    raise CoconutException("destination path cannot be given when --nowrite is enabled")
                elif os.path.isfile(args.dest):
                    raise CoconutException("destination path must point to directory not file")
                else:
                    dest = args.dest
                if args.package and args.standalone:
                    raise CoconutException("cannot compile as both --package and --standalone")
                elif args.package:
                    package = True
                elif args.standalone:
                    package = False
                else:
                    package = None # auto-decide package
                self.compile_path(args.source, dest, package, args.run, args.force)
            elif args.run or args.nowrite or args.force or args.package or args.standalone:
                raise CoconutException("a source file/folder must be specified when options that depend on the source are enabled")
            if args.code is not None:
                self.execute(self.proc.parse_block(args.code[0]))
            stdin = not sys.stdin.isatty() # check if input was piped in
            if stdin:
                self.execute(self.proc.parse_block(sys.stdin.read()))
            if args.jupyter is not None:
                self.start_jupyter(args.jupyter)
            if args.interact or (interact and not (
                    stdin
                    or args.source
                    or args.version
                    or args.code
                    or args.tutorial
                    or args.documentation
                    or args.jupyter is not None
                    )):
                self.start_prompt()
        except CoconutException:
            self.console.printerr(get_error(self.indebug()))
            sys.exit(1)

    def compile_path(self, path, write=True, package=None, run=False, force=False):
        """Compiles a path."""
        path = fixpath(path)
        if write is not None and write is not True:
            write = fixpath(write)
        if os.path.isfile(path):
            if package is None:
                package = False
            self.compile_file(path, write, package, run, force)
        elif os.path.isdir(path):
            if package is None:
                package = True
            self.compile_folder(path, write, package, run, force)
        else:
            raise CoconutException("could not find source path "+path)

    def compile_folder(self, directory, write=True, package=True, run=False, force=False):
        """Compiles a directory."""
        for dirpath, dirnames, filenames in os.walk(directory):
            writedir = write
            if writedir is None:
                headerdir = None
            elif writedir is True:
                headerdir = dirpath
            else:
                writedir = os.path.join(writedir, os.path.relpath(dirpath, directory))
                headerdir = writedir
            wrote = False
            try:
                for filename in filenames:
                    if os.path.splitext(filename)[1] in code_exts:
                        self.compile_file(os.path.join(dirpath, filename), writedir, package, run, force)
                        wrote = True
            finally: # if we wrote anything in package mode, we should always add a header file
                if wrote and package and headerdir is not None:
                    self.create_package(headerdir)

    def compile_file(self, filepath, write=True, package=False, run=False, force=False):
        """Compiles a file."""
        if write is None:
            destpath = None
        elif write is True:
            destpath = filepath
        else:
            destpath = os.path.join(write, os.path.basename(filepath))
        if destpath is not None:
            base, ext = os.path.splitext(os.path.splitext(destpath)[0])
            if not ext:
                ext = comp_ext
            destpath = base + ext
        if filepath == destpath:
            raise CoconutException("cannot compile "+showpath(filepath)+" to itself (incorrect file extension)")
        else:
            self.compile(filepath, destpath, package, run, force)

    def compile(self, codepath, destpath=None, package=False, run=False, force=False):
        """Compiles a source Coconut file to a destination Python file."""
        self.console.show("Compiling       "+showpath(codepath)+" ...")
        with openfile(codepath, "r") as opened:
            code = readfile(opened)
        foundhash = None if force else self.hashashof(destpath, code, package)
        if foundhash:
            self.console.show("Left unchanged    "+showpath(destpath)+" (pass --force to overwrite).")
            if run:
                self.execute(foundhash, path=destpath, isolate=True)
            elif self.show:
                print(foundhash)
        else:
            if package is True:
                compiled = self.proc.parse_module(code)
            elif package is False:
                compiled = self.proc.parse_file(code)
            else:
                raise CoconutException("invalid value for package", package)
            if destpath is None:
                self.console.show("Compiled without writing to file.")
            else:
                destdir = os.path.dirname(destpath)
                if not os.path.exists(destdir):
                    os.makedirs(destdir)
                with openfile(destpath, "w") as opened:
                    writefile(opened, compiled)
                self.console.show("Compiled to       "+showpath(destpath)+" .")
            if run:
                self.execute(compiled, path=(destpath if destpath is not None else codepath), isolate=True)
            elif self.show:
                print(compiled)

    def create_package(self, dirpath):
        """Sets up a package directory."""
        filepath = os.path.join(dirpath, "__coconut__.py")
        with openfile(filepath, "w") as opened:
            writefile(opened, self.proc.headers("package"))

    def hashashof(self, destpath, code, package):
        """Determines if a file has the hash of the code."""
        if destpath is not None and os.path.isfile(destpath):
            with openfile(destpath, "r") as opened:
                compiled = readfile(opened)
                hashash = gethash(compiled)
                if hashash is not None and hashash == self.proc.genhash(package, code):
                    return compiled
        return None

    def prompt_with(self, prompt):
        """Prompts for code."""
        try:
            return input(prompt) # using input from .root
        except KeyboardInterrupt:
            print()
            self.console.printerr("KeyboardInterrupt")
        except EOFError:
            print()
            self.exit()
        except ValueError:
            self.console.printerr(get_error(self.indebug()))
            self.exit()
        return None

    def start_prompt(self):
        """Starts the interpreter."""
        self.check_runner()
        self.console.print("Coconut Interpreter:")
        self.console.print('(type "exit()" or press Ctrl-D to end)')
        self.running = True
        while self.running:
            code = self.prompt_with(self.prompt)
            if code:
                compiled = self.handle(code)
                if compiled:
                    resp = self.execute(compiled, False)
                    if resp != None:
                        self.console.print(resp)

    def exit(self):
        """Exits the interpreter."""
        self.running = False

    def handle(self, code):
        """Compiles Coconut interpreter input."""
        compiled = None
        if not self.proc.should_indent(code):
            try:
                compiled = self.proc.parse_block(code)
            except CoconutException:
                pass
        if compiled is None:
            while True:
                line = self.prompt_with(self.moreprompt)
                if line is None:
                    return None
                elif line.strip():
                    code += "\n" + line
                else:
                    break
            try:
                compiled = self.proc.parse_block(code)
            except CoconutException:
                self.console.printerr(get_error(self.indebug()))
        return compiled

    def execute(self, compiled=None, error=True, path=None, isolate=False):
        """Executes compiled code."""
        self.check_runner(path, isolate)
        if compiled is not None:
            if self.show:
                print(compiled)
            if isolate: # isolate means header is included, and thus encoding must be removed
                compiled = rem_encoding(compiled)
            return self.runner.run(compiled, error)

    def check_runner(self, path=None, isolate=False):
        """Makes sure there is a runner."""
        if isolate or path is not None or self.runner is None:
            self.start_runner(path, isolate)

    def start_runner(self, path=None, isolate=False):
        """Starts the runner."""
        sys.path.insert(0, os.getcwd())
        if isolate:
            proc = None
        else:
            proc = self.proc
        self.runner = executor(proc, self.exit, path)

    def launch_tutorial(self):
        """Opens the Coconut tutorial."""
        import webbrowser
        webbrowser.open(tutorial_url, 2)

    def launch_documentation(self):
        """Opens the Coconut documentation."""
        import webbrowser
        webbrowser.open(documentation_url, 2)

    def start_jupyter(self, args):
        """Starts Jupyter with the Coconut kernel."""
        import subprocess
        if args:
            install_func = lambda args: subprocess.check_output(args, stderr=subprocess.STDOUT)
        else:
            install_func = lambda args: subprocess.check_call(args)
        try:
            install_func(["jupyter", "--version"])
        except subprocess.CalledProcessError:
            jupyter = "ipython"
        else:
            jupyter = "jupyter"
        install_args = [jupyter, "kernelspec", "install", os.path.join(os.path.dirname(os.path.abspath(__file__)), "icoconut"), "--replace"]
        try:
            install_func(install_args)
        except subprocess.CalledProcessError:
            try:
                install_func(install_args + ["--user"])
            except subprocess.CalledProcessError:
                errmsg = 'unable to install Jupyter kernel specification file (failed command "'+" ".join(install_args)+'")'
                if args:
                    self.proc.warn(CoconutWarning(errmsg))
                else:
                    raise CoconutException(errmsg)
        if args:
            if args[0] == "console":
                self.console.print(version_banner)
                run_args = [jupyter, "console", "--kernel", "icoconut"] + args[1:]
            elif args[0] == "notebook":
                run_args = [jupyter, "notebook"] + args[1:]
            else:
                raise CoconutException('first argument after --jupyter must be either "console" or "notebook"')
            subprocess.call(run_args)
