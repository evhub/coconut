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
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------

def openfile(filename, opentype="r+"):
    """Returns an open file object."""
    return open(filename, opentype, encoding=encoding) # uses io.open from .root and encoding from .compiler

def writefile(openedfile, newcontents):
    """Sets the contents of a file."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(newcontents)

def readfile(openedfile):
    """Reads the contents of a file."""
    openedfile.seek(0)
    return str(openedfile.read())

def fixpath(path):
    """Properly formats a path."""
    return os.path.normpath(os.path.realpath(path))

class executor(object):
    """Compiled Python executor."""
    def __init__(self, header=None, extras=None, exit=None):
        """Creates the executor."""
        self.exit = exit
        self.vars = {}
        if header is not None:
            self.run(header)
        if extras is not None:
            self.bindvars(extras)

    def bindvars(self, extras):
        """Adds extra variable bindings."""
        self.vars.update(extras)

    def setfile(self, path):
        """Sets __file__."""
        self.vars["__file__"] = path

    def run(self, code, err=False, dorun=exec):
        """Executes Python code."""
        try:
            return dorun(code, self.vars)
        except (Exception, KeyboardInterrupt):
            if err:
                raise
            else:
                traceback.print_exc()
        except SystemExit:
            if self.exit is None:
                raise
            else:
                self.exit()

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
                printerr(msg)
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
    commandline.add_argument("-p", "--package", action="store_const", const=True, default=False, help="compile source as part of a package (defaults to only if source is a directory)")
    commandline.add_argument("-a", "--standalone", action="store_const", const=True, default=False, help="compile source as standalone files (defaults to only if source is a single file)")
    commandline.add_argument("-f", "--force", action="store_const", const=True, default=False, help="force overwriting of compiled Python (otherwise only overwrites when the source changes)")
    commandline.add_argument("-d", "--display", action="store_const", const=True, default=False, help="print compiled Python")
    commandline.add_argument("-r", "--run", action="store_const", const=True, default=False, help="run the compiled Python")
    commandline.add_argument("-n", "--nowrite", action="store_const", const=True, default=False, help="disable writing the compiled Python")
    commandline.add_argument("-i", "--interact", action="store_const", const=True, default=False, help="force the interpreter to start (otherwise starts if no other command is given)")
    commandline.add_argument("-q", "--quiet", action="store_const", const=True, default=False, help="suppress all informational output")
    commandline.add_argument("-c", "--code", metavar="code", type=str, nargs=1, default=None, help="run a line of Coconut passed in as a string (can also be accomplished with a pipe)")
    commandline.add_argument("--jupyter", "--ipython", type=str, nargs=argparse.REMAINDER, default=None, help="run Jupyter (formerly IPython) with Coconut as the kernel (remaining args passed to Jupyter)")
    commandline.add_argument("--autopep8", type=str, nargs=argparse.REMAINDER, default=None, help="use autopep8 to format compiled code (remaining args passed to autopep8)")
    commandline.add_argument("--debug", action="store_const", const=True, default=False, help="print verbose debug output")
    proc = None
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
        """Processes command-line arguments."""
        self.cmd(self.commandline.parse_args())

    def setup(self, strict=False, target=None):
        """Creates the processor."""
        if self.proc is None:
            self.proc = processor(strict, target, self.console.debug)
        else:
            self.proc.setup(strict, target)

    def quiet(self, state=None):
        """Quiets output."""
        if state is None:
            state = self.console.on
        self.console.on = not state

    def indebug(self):
        """Determines whether the processor is in debug mode."""
        return self.proc.indebug()

    def cmd(self, args, interact=True):
        """Parses command-line arguments."""
        try:
            self.setup(args.strict, args.target[0])
            if args.debug:
                self.proc.debug(True)
            if args.quiet:
                self.quiet(True)
            if args.display:
                self.show = True
            if args.version:
                self.console.print(self.version)
            if args.autopep8 is not None:
                self.proc.autopep8(args.autopep8)
            if args.code is not None:
                self.execute(self.proc.parse_single(args.code[0]))
            stdin = not sys.stdin.isatty()
            if stdin:
                self.execute(self.proc.parse_block(sys.stdin.read()))
            if args.source is not None:
                if args.run and os.path.isdir(args.source):
                    raise CoconutException("source path must point to file not directory when --run is enabled")
                if args.dest is None:
                    if not args.nowrite:
                        dest = True # auto-generate dest
                    elif args.package or args.standalone:
                        raise CoconutException("cannot specify --package or --standalone when --nowrite is enabled")
                    else:
                        dest = None
                elif args.nowrite:
                    raise CoconutException("destination path cannot be given when --nowrite is enabled")
                elif os.path.isfile(args.dest):
                    raise CoconutException("destination path must point to directory not file")
                else:
                    dest = args.dest
                if args.package and args.standalone:
                    raise CoconutException("cannot compile both as --package and as --standalone")
                elif args.package:
                    package = True
                elif args.standalone:
                    package = False
                else:
                    package = None # auto-decide package
                self.compile_path(args.source, dest, package, run=args.run, force=args.force)
            elif args.run or args.nowrite or args.force or args.package or args.standalone:
                raise CoconutException("a source file/folder must be specified when options that depend on the source are enabled")
            if args.jupyter is not None:
                self.start_jupyter(args.jupyter)
            if args.interact or (interact and not (stdin or args.source or args.version or args.code or args.jupyter is not None)):
                self.start_prompt()
        except CoconutException:
            printerr(get_error(self.indebug()))
            sys.exit(1)

    def compile_path(self, path, write=True, package=None, run=False, force=False):
        """Compiles a path."""
        if os.path.isfile(path):
            if package is None and write is not None:
                package = False
            # if package is still None, it means write is None, and compile neither as package nor standalone
            self.compile_file(path, write, package, run, force)
        elif os.path.isdir(path):
            if package is None and write is not None:
                package = True
            # passes package unchanged to compile_file, so see above for meaning
            self.compile_folder(path, write, package, run, force)
        else:
            raise CoconutException("could not find source path "+path)

    def compile_folder(self, directory, write=True, package=True, run=False, force=False):
        """Compiles a directory."""
        for dirpath, dirnames, filenames in os.walk(directory):
            writedir = write
            if writedir is None:
                tocreate = None
            elif writedir is True:
                tocreate = dirpath
            else:
                writedir = os.path.join(writedir, os.path.relpath(dirpath, directory))
                tocreate = writedir
            wrote = False
            for filename in filenames:
                if os.path.splitext(filename)[1] == self.code_ext:
                    self.compile_file(os.path.join(dirpath, filename), writedir, package, run, force)
                    wrote = True
            if wrote and package and tocreate is not None:
                self.create_package(tocreate)

    def compile_file(self, filepath, write=True, package=False, run=False, force=False):
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
        self.compile(filepath, destpath, package, run, force)

    def compile(self, codepath, destpath=None, package=False, run=False, force=False):
        """Compiles a source Coconut file to a destination Python file."""
        self.console.print("Compiling       "+codepath+" ...")
        with openfile(codepath, "r") as opened:
            code = readfile(opened)
        foundhash = None if force else self.hashashof(destpath, code, package)
        if foundhash:
            if run:
                self.execute(foundhash, path=destpath)
            elif self.show:
                print(foundhash)
            self.console.print("Left unchanged  "+destpath+" (pass --force to overwrite).")
        else:
            if package is True:
                compiled = self.proc.parse_module(code)
            elif package is False:
                compiled = self.proc.parse_file(code)
            elif package is None:
                compiled = self.proc.parse_block(code)
            else:
                raise CoconutException("invalid value for package", package)
            if destpath is None:
                self.console.print("Compiled without writing to file.")
            else:
                destdir = os.path.dirname(destpath)
                if not os.path.exists(destdir):
                    os.makedirs(destdir)
                with openfile(destpath, "w") as opened:
                    writefile(opened, compiled)
                self.console.print("Compiled to     "+destpath+" .")
            if run:
                self.execute(compiled, path=(destpath if destpath is not None else codepath))
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
            printerr("\nKeyboardInterrupt")
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
            compiled = self.proc.parse_single(code)
        except CoconutException:
            while True:
                line = self.prompt_with(self.moreprompt)
                if line:
                    code += "\n" + line
                elif line is None:
                    return None
                else:
                    break
            try:
                compiled = self.proc.parse_single(code)
            except CoconutException:
                printerr(get_error(self.indebug()))
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
        sys.path.insert(0, os.getcwd())
        self.runner = executor(self.proc.headers("code"), exit=self.exit)

    def start_jupyter(self, args):
        """Starts Jupyter with the Coconut kernel."""
        import subprocess
        try:
            subprocess.check_output("jupyter", stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            jupyter = "ipython"
        else:
            jupyter = "jupyter"
        install_args = [jupyter, "kernelspec", "install", os.path.join(os.path.dirname(os.path.abspath(__file__)), "icoconut")]
        if args:
            install_func = lambda args: subprocess.check_output(args, stderr=subprocess.STDOUT)
        else:
            install_func = lambda args: subprocess.check_call(args)
        try:
            install_func(install_args)
        except subprocess.CalledProcessError:
            try:
                install_func(install_args + ["--user"])
            except subprocess.CalledProcessError:
                errmsg = 'unable to install jupyter kernelspec file (failed command "'+" ".join(install_args)+'")'
                if args:
                    self.processor.warn(CoconutWarning(errmsg))
                else:
                    raise CoconutException(errmsg)
        if args:
            if args[0] == "console":
                self.console.show("Coconut Kernel "+VERSION)
                run_args = [jupyter, "console", "--kernel", "icoconut"] + args[1:]
            elif args[0] == "notebook":
                run_args = [jupyter, "notebook"] + args[1:]
            else:
                raise CoconutException('first argument after --jupyter must be either "console" or "notebook"')
            subprocess.call(run_args)
