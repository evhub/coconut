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

from coconut.root import *

import sys
import os
import time
import subprocess
from contextlib import contextmanager

from concurrent.futures import ProcessPoolExecutor

from coconut.compiler import Compiler, gethash
from coconut.exceptions import CoconutException
from coconut.logging import logger
from coconut.constants import \
    code_exts, \
    comp_ext, \
    default_prompt, \
    default_moreprompt, \
    watch_interval, \
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
    fixpath, \
    showpath, \
    rem_encoding, \
    try_eval, \
    Runner, \
    multiprocess_wrapper
from coconut.command.cli import arguments

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

class Command(object):
    """The Coconut command-line interface."""
    comp = None # current .compiler.Compiler
    show = False # corresponds to --display flag
    running = False # whether the interpreter is currently active
    runner = None # the current Runner
    target = None # corresponds to --target flag
    executor = None # runs --jobs
    exit_code = 0 # exit status to return

    def __init__(self, prompt=default_prompt, moreprompt=default_moreprompt):
        """Creates the CLI."""
        self.prompt, self.moreprompt = prompt, moreprompt

    def start(self):
        """Processes command-line arguments."""
        self.cmd(arguments.parse_args())

    def setup(self, *args, **kwargs):
        """Sets parameters for the compiler."""
        if self.comp is None:
            self.comp = Compiler(*args, **kwargs)
        else:
            self.comp.setup(*args, **kwargs)

    def set_color(self, color):
        """Sets the color."""
        logger.set_color(color)
        self.prompt = logger.add_color(self.prompt)
        self.moreprompt = logger.add_color(self.moreprompt)

    def cmd(self, args, interact=True):
        """Processes command-line arguments."""
        self.exit_code = 0
        with self.handling_exceptions():
            self.use_args(args, interact)
        self.exit_on_error()

    def exit_on_error(self):
        """Exits if exit_code is abnormal."""
        if self.exit_code:
            sys.exit(self.exit_code)

    def use_args(self, args, interact=True):
        """Handles command-line arguments."""
        if args.recursion_limit[0] is not None:
            sys.setrecursionlimit(args.recursion_limit[0])
        logger.quiet, logger.verbose = args.quiet, args.verbose
        if args.color[0] is not None:
            self.set_color(args.color[0])
        if args.version:
            logger.show(version_long)
        if args.tutorial:
            self.launch_tutorial()
        if args.documentation:
            self.launch_documentation()
        if args.display:
            self.show = True

        self.setup(
            target = args.target[0],
            strict = args.strict,
            minify = args.minify,
            line_numbers = args.line_numbers,
            keep_lines = args.keep_lines,
            autopep8 = args.autopep8,
            )

        with self.running_jobs(args.jobs[0]):

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
            self.execute(self.comp.parse_block(args.code[0]))
        stdin = not sys.stdin.isatty() # check if input was piped in
        if stdin:
            self.execute(self.comp.parse_block(sys.stdin.read()))
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

    @contextmanager
    def handling_exceptions(self):
        """Handles CoconutExceptions."""
        try:
            yield
        except CoconutException:
            logger.print_exc()
            self.exit_code = 1

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
                    if logger.verbose:
                        logger.show_tabulated("Skipped directory", name, "(explicitly pass as source to override).")
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
        logger.show_tabulated("Compiling", showpath(codepath), "...")

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
            logger.show_tabulated("Left unchanged", showpath(destpath), "(pass --force to override).")
            if run:
                self.execute(foundhash, path=destpath, isolate=True)
            elif self.show:
                print(foundhash)

        else:

            if package is True:
                compile_method = "parse_module"
            elif package is False:
                compile_method = "parse_file"
            else:
                raise CoconutException("invalid value for package", package)

            def callback(compiled):
                if destpath is None:
                    logger.show_tabulated("Finished", showpath(codepath), "without writing to file.")
                else:
                    with openfile(destpath, "w") as opened:
                        writefile(opened, compiled)
                    logger.show_tabulated("Compiled to", showpath(destpath), ".")
                if run:
                    runpath = destpath if destpath is not None else codepath
                    self.execute(compiled, path=runpath, isolate=True)
                elif self.show:
                    print(compiled)


                self.submit_comp_job(codepath, callback, compile_method, code)

    def submit_comp_job(self, path, callback, method, *args, **kwargs):
        """Submits a job on self.comp to be run in parallel."""
        if self.executor is None:
            with self.handling_exceptions():
                callback(getattr(self.comp, method)(*args, **kwargs))
        else:
            with logger.in_path(path):
                future = self.executor.submit(multiprocess_wrapper(self.comp, method), *args, **kwargs)
            def callback_wrapper(completed_future):
                with logger.in_path(path):
                    with self.handling_exceptions():
                        result = completed_future.result()
                with self.handling_exceptions():
                    callback(result)
            future.add_done_callback(callback_wrapper)

    @contextmanager
    def running_jobs(self, jobs):
        """Initialize multiprocessing."""
        if jobs is None or jobs >= 1:
            try:
                with ProcessPoolExecutor(jobs) as self.executor:
                    yield
            finally:
                self.executor = None
                self.exit_on_error()
        elif jobs == 0:
            yield
        else:
            raise CoconutException("the number of processes passed to --jobs must be >= 0")

    def create_package(self, dirpath):
        """Sets up a package directory."""
        filepath = os.path.join(fixpath(dirpath), "__coconut__.py")
        with openfile(filepath, "w") as opened:
            writefile(opened, self.comp.headers("package"))

    def hashashof(self, destpath, code, package):
        """Determines if a file has the hash of the code."""
        if destpath is not None and os.path.isfile(destpath):
            with openfile(destpath, "r") as opened:
                compiled = readfile(opened)
                hashash = gethash(compiled)
                if hashash is not None and hashash == self.comp.genhash(package, code):
                    return compiled
        return None

    def prompt_with(self, prompt):
        """Prompts for code."""
        try:
            return input(prompt) # using input from coconut.root
        except KeyboardInterrupt:
            logger.printerr("\nKeyboardInterrupt")
        except EOFError:
            print()
            self.exit_runner()
        except ValueError:
            logger.print_exc()
            self.exit_runner()
        return None

    def start_running(self):
        """Starts running the Runner."""
        self.check_runner()
        self.running = True

    def start_prompt(self):
        """Starts the interpreter."""
        logger.print("Coconut Interpreter:")
        logger.print('(type "exit()" or press Ctrl-D to end)')
        self.start_running()
        while self.running:
            code = self.prompt_with(self.prompt)
            if code:
                compiled = self.handle_input(code)
                if compiled:
                    self.execute(compiled, error=False, print_expr=True)

    def exit_runner(self):
        """Exits the interpreter."""
        self.running = False

    def handle_input(self, code):
        """Compiles Coconut interpreter input."""
        compiled = None
        if not self.comp.should_indent(code):
            try:
                compiled = self.comp.parse_block(code)
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
                compiled = self.comp.parse_block(code)
            except CoconutException:
                logger.print_exc()
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
            comp = None
        else:
            comp = self.comp
        self.runner = Runner(comp, self.exit_runner, path)

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
        if args and not logger.verbose:
            install_func = subprocess.check_output # stdout is returned and ignored
        else:
            install_func = subprocess.check_call

        check_args = ["jupyter", "--version"]
        logger.log_cmd(check_args)
        try:
            install_func(check_args)
        except subprocess.CalledProcessError:
            jupyter = "ipython"
        else:
            jupyter = "jupyter"

        for icoconut_kernel_dir in icoconut_kernel_dirs:
            install_args = [jupyter, "kernelspec", "install", icoconut_kernel_dir, "--replace"]
            logger.log_cmd(install_args)
            try:
                install_func(install_args)
            except subprocess.CalledProcessError:
                user_install_args = install_args + ["--user"]
                logger.log_cmd(user_install_args)
                try:
                    install_func(user_install_args)
                except subprocess.CalledProcessError:
                    errmsg = 'unable to install Jupyter kernel (failed command "'+" ".join(install_args)+'")'
                    if args:
                        self.comp.warn(CoconutWarning(errmsg))
                    else:
                        raise CoconutException(errmsg)

        if args:
            if args[0] == "console":
                ver = "2" if PY2 else "3"
                check_args = ["python"+ver, "-m", "coconut", "--version"]
                logger.log_cmd(check_args)
                try:
                    install_func(check_args)
                except subprocess.CalledProcessError:
                    kernel_name = "coconut"
                else:
                    kernel_name = "coconut"+ver
                logger.print(version_banner)
                run_args = [jupyter, "console", "--kernel", kernel_name] + args[1:]
            elif args[0] == "notebook":
                run_args = [jupyter, "notebook"] + args[1:]
            else:
                raise CoconutException('first argument after --jupyter must be either "console" or "notebook"')
            logger.log_cmd(run_args)
            subprocess.call(run_args)

    def watch(self, source, write=True, package=None, run=False, force=False):
        """Watches a source and recompiles on change."""
        from coconut.command.watch import Observer, RecompilationWatcher

        source = fixpath(source)

        logger.print()
        logger.show_tabulated("Watching", showpath(source), "(press Ctrl-C to end)...")

        def recompile(path):
            if os.path.isfile(path) and os.path.splitext(path)[1] in code_exts:
                try:
                    self.compile_path(path, write, package, run, force)
                except CoconutException:
                    logger.print_exc()

        observer = Observer()
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
