#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: The Coconut command-line utility.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os
import os.path
import argparse
import time

from coconut.compiler import \
    Compiler, \
    gethash
from coconut.constants import \
    code_exts, \
    comp_ext, \
    main_sig, \
    debug_sig, \
    default_prompt, \
    default_moreprompt, \
    watch_interval, \
    color_codes, \
    end_color_code, \
    version_long, \
    version_banner, \
    version_tag, \
    tutorial_url, \
    documentation_url, \
    icoconut_dir, \
    icoconut_kernel_dirs
from coconut.command.util import \
    openfile, \
    writefile, \
    readfile, \
    showpath, \
    fixpath, \
    rem_encoding, \
    try_eval, \
    escape_color, \
    Runner, \
    Console

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

class Command(object):
    """The Coconut command-line interface."""
    arguments = argparse.ArgumentParser(prog="coconut", description=documentation_url)
    arguments.add_argument("source", metavar="source", type=str, nargs="?", default=None, help="path to the Coconut file/folder to compile")
    arguments.add_argument("dest", metavar="dest", type=str, nargs="?", default=None, help="destination directory for compiled files (defaults to the source directory)")
    arguments.add_argument("-v", "--version", action="store_const", const=True, default=False, help="print Coconut and Python version information")
    arguments.add_argument("-t", "--target", metavar="version", type=str, nargs=1, default=[None], help="specify target Python version (defaults to universal)")
    arguments.add_argument("-s", "--strict", action="store_const", const=True, default=False, help="enforce code cleanliness standards")
    arguments.add_argument("-l", "--line-numbers", "--linenumbers", action="store_const", const=True, default=False, help="add line number comments for ease of debugging")
    arguments.add_argument("-p", "--package", action="store_const", const=True, default=False, help="compile source as part of a package (defaults to only if source is a directory)")
    arguments.add_argument("-a", "--standalone", action="store_const", const=True, default=False, help="compile source as standalone files (defaults to only if source is a single file)")
    arguments.add_argument("-w", "--watch", action="store_const", const=True, default=False, help="watch a directory and recompile on changes (requires watchdog)")
    arguments.add_argument("-f", "--force", action="store_const", const=True, default=False, help="force overwriting of compiled Python (otherwise only overwrites when source code or compilation parameters change)")
    arguments.add_argument("-d", "--display", action="store_const", const=True, default=False, help="print compiled Python")
    arguments.add_argument("-r", "--run", action="store_const", const=True, default=False, help="run compiled Python (often used with --nowrite)")
    arguments.add_argument("-n", "--nowrite", action="store_const", const=True, default=False, help="disable writing compiled Python")
    arguments.add_argument("-m", "--minify", action="store_const", const=True, default=False, help="compress compiled Python")
    arguments.add_argument("-i", "--interact", action="store_const", const=True, default=False, help="force the interpreter to start (otherwise starts if no other command is given)")
    arguments.add_argument("-q", "--quiet", action="store_const", const=True, default=False, help="suppress all informational output (combine with --display to write runnable code to stdout)")
    arguments.add_argument("-c", "--code", metavar="code", type=str, nargs=1, default=None, help="run a line of Coconut passed in as a string (can also be passed into stdin)")
    arguments.add_argument("--jupyter", "--ipython", type=str, nargs=argparse.REMAINDER, default=None, help="run Jupyter/IPython with Coconut as the kernel (remaining args passed to Jupyter)")
    arguments.add_argument("--autopep8", type=str, nargs=argparse.REMAINDER, default=None, help="use autopep8 to format compiled code (remaining args passed to autopep8) (requires autopep8)")
    arguments.add_argument("--recursion-limit", "--recursionlimit", metavar="limit", type=int, nargs=1, default=[None], help="set maximum recursion depth (defaults to "+str(sys.getrecursionlimit())+")")
    arguments.add_argument("--tutorial", action="store_const", const=True, default=False, help="open the Coconut tutorial in the default web browser")
    arguments.add_argument("--documentation", action="store_const", const=True, default=False, help="open the Coconut documentation in the default web browser")
    arguments.add_argument("--color", metavar="color", type=str, nargs=1, default=[None], help="show all Coconut messages in the given color")
    arguments.add_argument("--verbose", action="store_const", const=True, default=False, help="print verbose debug output")
    tabulation = 18 # offset for tabulated info messages
    proc = None # current .compiler.Compiler
    show = False # corresponds to --display flag
    running = False # whether the interpreter is currently active
    runner = None # the current Runner
    target = None # corresponds to --target flag

    def __init__(self, prompt=default_prompt, moreprompt=default_moreprompt):
        """Creates the CLI."""
        self.console = Console(main_sig, debug_sig)
        self.prompt, self.moreprompt = prompt, moreprompt

    def start(self):
        """Processes command-line arguments."""
        self.cmd(self.arguments.parse_args())

    def setup(self, target=None, strict=False, minify=False, line_numbers=False, quiet=False, color=None):
        """Sets parameters for the compiler."""
        if color is not None:
            self.console.set_color(color)
            self.prompt = self.console.add_color(self.prompt)
            self.moreprompt = self.console.add_color(self.moreprompt)
        self.console.on = not quiet
        if self.proc is None:
            self.proc = Compiler(target, strict, minify, line_numbers, self.console.printerr)
        else:
            self.proc.setup(target, strict, minify, line_numbers)

    def indebug(self):
        """Determines whether the compiler is in debug mode."""
        if self.proc is None:
            return False
        else:
            return self.proc.indebug()

    def print_exc(self):
        """Properly prints an exception in the exception context."""
        self.console.printerr(get_error(self.indebug()))

    def log(self, msg):
        """Logs a debug message if indebug."""
        if self.indebug():
            self.console.printerr(msg)

    def show_tabulated(self, begin, middle, end):
        """Shows a tabulated message."""
        if len(begin) < self.tabulation:
            self.console.show(begin + " "*(self.tabulation - len(begin)) + middle + " " + end)
        else:
            raise CoconutException("info message too long", begin)

    def cmd(self, args, interact=True):
        """Parses command-line arguments."""
        try:
            if args.recursion_limit[0] is not None:
                sys.setrecursionlimit(args.recursion_limit[0])
            self.setup(args.target[0], args.strict, args.minify, args.line_numbers, args.quiet, args.color[0])
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
                elif args.watch and os.path.isfile(args.source):
                    raise CoconutException("source path must point to directory not file when --watch is enabled")
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
            elif (args.run
                  or args.nowrite
                  or args.force
                  or args.package
                  or args.standalone
                  or args.watch):
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
                    or args.watch
                    or args.jupyter is not None
                    )):
                self.start_prompt()
            if args.watch:
                self.watch(args.source, dest, package, args.run, args.force)
        except CoconutException:
            self.print_exc()
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
            if write is None or write is True:
                writedir = write
            else:
                writedir = os.path.join(write, os.path.relpath(dirpath, directory))
            for filename in filenames:
                if os.path.splitext(filename)[1] in code_exts:
                    self.compile_file(os.path.join(dirpath, filename), writedir, package, run, force)
            for name in dirnames[:]:
                if name != "."*len(name) and name.startswith("."):
                    self.show_tabulated("Skipped directory", name, "(explicitly pass as source to override).")
                    dirnames.remove(name) # directories removed from dirnames won't appear in further os.walk iteration

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
        self.show_tabulated("Compiling", showpath(codepath), "...")
        with openfile(codepath, "r") as opened:
            code = readfile(opened)
        if destpath is not None:
            destdir = os.path.dirname(destpath)
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            if package is True:
                self.create_package(destdir)
        foundhash = None if force else self.hashashof(destpath, code, package)
        if foundhash:
            self.show_tabulated("Left unchanged", showpath(destpath), "(pass --force to override).")
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
                with openfile(destpath, "w") as opened:
                    writefile(opened, compiled)
                self.show_tabulated("Compiled to", showpath(destpath), ".")
            if run:
                self.execute(compiled, path=(destpath if destpath is not None else codepath), isolate=True)
            elif self.show:
                print(compiled)

    def create_package(self, dirpath):
        """Sets up a package directory."""
        filepath = os.path.join(fixpath(dirpath), "__coconut__.py")
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
            return input(prompt) # using input from coconut.root
        except KeyboardInterrupt:
            print()
            self.console.printerr("KeyboardInterrupt")
        except EOFError:
            print()
            self.exit()
        except ValueError:
            self.print_exc()
            self.exit()
        return None

    def start_running(self):
        """Starts running the Executor."""
        self.check_runner()
        self.running = True

    def start_prompt(self):
        """Starts the interpreter."""
        self.console.print("Coconut Interpreter:")
        self.console.print('(type "exit()" or press Ctrl-D to end)')
        self.start_running()
        while self.running:
            code = self.prompt_with(self.prompt)
            if code:
                compiled = self.handle(code)
                if compiled:
                    self.execute(compiled, error=False, print_expr=True)

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
                self.print_exc()
        return compiled

    def execute(self, compiled=None, error=True, path=None, isolate=False, print_expr=False):
        """Executes compiled code."""
        self.check_runner(path, isolate)
        if compiled is not None:
            if self.show:
                print(compiled)
            if isolate: # isolate means header is included, and thus encoding must be removed
                compiled = rem_encoding(compiled)
            if print_expr:
                result = self.runner.run(compiled, error, run_func=try_eval)
                if result is not None: # if the input was an expression, we should print it
                    print(result)
            else:
                self.runner.run(compiled, error)

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
        self.runner = Runner(proc, self.exit, path)

    def launch_tutorial(self):
        """Opens the Coconut tutorial."""
        import webbrowser
        webbrowser.open(tutorial_url, 2)

    def launch_documentation(self):
        """Opens the Coconut documentation."""
        import webbrowser
        webbrowser.open(documentation_url, 2)

    def log_cmd(self, args):
        """Logs a console command if indebug."""
        self.log("> " + " ".join(args))

    def start_jupyter(self, args):
        """Starts Jupyter with the Coconut kernel."""
        import subprocess
        if args and not self.indebug():
            install_func = lambda args: subprocess.check_output(args) # stdout is returned and ignored
        else:
            install_func = lambda args: subprocess.check_call(args)
        check_args = ["jupyter", "--version"]
        self.log_cmd(check_args)
        try:
            install_func(check_args)
        except subprocess.CalledProcessError:
            jupyter = "ipython"
        else:
            jupyter = "jupyter"
        for icoconut_kernel_dir in icoconut_kernel_dirs:
            install_args = [jupyter, "kernelspec", "install", icoconut_kernel_dir, "--replace"]
            self.log_cmd(install_args)
            try:
                install_func(install_args)
            except subprocess.CalledProcessError:
                user_install_args = install_args + ["--user"]
                self.log_cmd(user_install_args)
                try:
                    install_func(user_install_args)
                except subprocess.CalledProcessError:
                    errmsg = 'unable to install Jupyter kernel (failed command "'+" ".join(install_args)+'")'
                    if args:
                        self.proc.warn(CoconutWarning(errmsg))
                    else:
                        raise CoconutException(errmsg)
        if args:
            if args[0] == "console":
                ver = "2" if PY2 else "3"
                check_args = ["python"+ver, "-m", "coconut", "--version"]
                self.log_cmd(check_args)
                try:
                    install_func(check_args)
                except subprocess.CalledProcessError:
                    kernel_name = "coconut"
                else:
                    kernel_name = "coconut"+ver
                self.console.print(version_banner)
                run_args = [jupyter, "console", "--kernel", kernel_name] + args[1:]
            elif args[0] == "notebook":
                run_args = [jupyter, "notebook"] + args[1:]
            else:
                raise CoconutException('first argument after --jupyter must be either "console" or "notebook"')
            self.log_cmd(run_args)
            subprocess.call(run_args)

    def watch(self, source, write=True, package=None, run=False, force=False):
        """Watches a source and recompiles on change."""
        from coconut.command.watch import Observer, RecompilationWatcher

        source = fixpath(source)

        self.console.show("Watching        "+showpath(source)+" ...")
        self.console.print("(press Ctrl-C to end)")

        def recompile(path):
            if os.path.isfile(path) and os.path.splitext(path)[1] in code_exts:
                self.compile_path(path, write, package, run, force)

        observer.schedule(RecompilationWatcher(recompile), source, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(watch_interval)
        except KeyboardInterrupt:
            pass
        finally:
            observer.stop()
            observer.join()
