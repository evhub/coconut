#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from coconut.root import *  # NOQA

import sys
import os
import time
import traceback
import functools
from contextlib import contextmanager
from subprocess import CalledProcessError

from coconut.compiler import Compiler
from coconut.exceptions import (
    CoconutException,
    CoconutInternalException,
)
from coconut.terminal import logger, printerr
from coconut.constants import (
    fixpath,
    code_exts,
    comp_ext,
    watch_interval,
    icoconut_kernel_dirs,
    minimum_recursion_limit,
    stub_dir,
    exit_chars,
    coconut_run_args,
)
from coconut.command.util import (
    openfile,
    writefile,
    readfile,
    showpath,
    rem_encoding,
    Runner,
    multiprocess_wrapper,
    Prompt,
    handling_broken_process_pool,
    kill_children,
    run_cmd,
    set_mypy_path,
    is_special_dir,
    launch_documentation,
    launch_tutorial,
    stdin_readable,
)
from coconut.compiler.util import should_indent
from coconut.compiler.header import gethash
from coconut.command.cli import arguments

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------


class Command(object):
    """The Coconut command-line interface."""
    comp = None  # current coconut.compiler.Compiler
    show = False  # corresponds to --display flag
    runner = None  # the current Runner
    jobs = 0  # corresponds to --jobs flag
    executor = None  # runs --jobs
    exit_code = 0  # exit status to return
    errmsg = None  # error message to display
    mypy_args = None  # corresponds to --mypy flag

    def __init__(self):
        """Creates the CLI."""
        self.prompt = Prompt()

    def start(self, run=False):
        """Processes command-line arguments."""
        if run:
            args, argv = coconut_run_args, []
            # for coconut-run, all args beyond the source file should stay in sys.argv
            for i in range(1, len(sys.argv)):
                arg = sys.argv[i]
                args.append(arg)
                if not arg.startswith("-"):  # is source file
                    argv = sys.argv[i:]
                    break
            sys.argv = argv
        else:
            args = None
        self.cmd(args)

    def cmd(self, args=None, interact=True):
        """Processes command-line arguments."""
        if args is None:
            args = arguments.parse_args()
        else:
            args = arguments.parse_args(args)
        self.exit_code = 0
        with self.handling_exceptions():
            self.use_args(args, interact)
        self.exit_on_error()

    def setup(self, *args, **kwargs):
        """Sets parameters for the compiler."""
        if self.comp is None:
            self.comp = Compiler(*args, **kwargs)
        else:
            self.comp.setup(*args, **kwargs)

    def exit_on_error(self):
        """Exits if exit_code is abnormal."""
        if self.exit_code:
            if self.errmsg is not None:
                logger.show_error("Exiting due to " + self.errmsg + ".")
                self.errmsg = None
            if self.jobs != 0:
                kill_children()
            sys.exit(self.exit_code)

    def set_recursion_limit(self, limit):
        """Sets the Python recursion limit."""
        if limit < minimum_recursion_limit:
            raise CoconutException("--recursion-limit must be at least " + str(minimum_recursion_limit))
        else:
            sys.setrecursionlimit(limit)

    def use_args(self, args, interact=True):
        """Handles command-line arguments."""
        logger.quiet, logger.verbose = args.quiet, args.verbose
        if DEVELOP:
            logger.tracing = args.trace
        logger.log("Command args:", args)

        if args.recursion_limit is not None:
            self.set_recursion_limit(args.recursion_limit)
        if args.jobs is not None:
            self.set_jobs(args.jobs)
        if args.display:
            self.show = True
        if args.style is not None:
            self.prompt.set_style(args.style)
        if args.documentation:
            launch_documentation()
        if args.tutorial:
            launch_tutorial()

        self.setup(
            target=args.target,
            strict=args.strict,
            minify=args.minify,
            line_numbers=args.line_numbers,
            keep_lines=args.keep_lines,
            no_tco=args.no_tco or args.mypy is not None,
        )

        if args.mypy is not None:
            if args.no_tco:
                logger.warn("extraneous --no-tco argument passed; --mypy implies --no-tco")
            self.set_mypy_args(args.mypy)

        if args.source is not None:
            if args.interact and args.run:
                logger.warn("extraneous --run argument passed; --interact implies --run")
            if args.package and self.mypy:
                logger.warn("extraneous --package argument passed; --mypy implies --package")
            if args.standalone and args.package:
                raise CoconutException("cannot compile as both --package and --standalone")
            if args.standalone and self.mypy:
                raise CoconutException("cannot compile as both --package (implied by --mypy) and --standalone")
            if (args.run or args.interact) and os.path.isdir(args.source):
                if args.run:
                    raise CoconutException("source path must point to file not directory when --run is enabled")
                if args.interact:
                    raise CoconutException("source path must point to file not directory when --run (implied by --interact) is enabled")
            if args.watch and os.path.isfile(args.source):
                raise CoconutException("source path must point to directory not file when --watch is enabled")

            if args.dest is None:
                if args.no_write:
                    dest = None  # no dest
                else:
                    dest = True  # auto-generate dest
            elif args.no_write:
                raise CoconutException("destination path cannot be given when --no-write is enabled")
            elif os.path.isfile(args.dest):
                raise CoconutException("destination path must point to directory not file")
            else:
                dest = args.dest

            if args.package or self.mypy:
                package = True
            elif args.standalone:
                package = False
            else:
                package = None  # auto-decide package

            with self.running_jobs(exit_on_error=not args.watch):
                filepaths = self.compile_path(args.source, dest, package, args.run or args.interact, args.force)
            self.run_mypy(filepaths)

        elif (args.run
              or args.no_write
              or args.force
              or args.package
              or args.standalone
              or args.watch):
            raise CoconutException("a source file/folder must be specified when options that depend on the source are enabled")

        if args.code is not None:
            self.execute(self.comp.parse_block(args.code))
        got_stdin = False
        if stdin_readable():
            logger.log("Reading piped input from stdin...")
            self.execute(self.comp.parse_block(sys.stdin.read()))
            got_stdin = True
        if args.jupyter is not None:
            self.start_jupyter(args.jupyter)
        if args.interact or (interact and not (
                got_stdin
                or args.source
                or args.code
                or args.tutorial
                or args.documentation
                or args.watch
                or args.jupyter is not None
        )):
            self.start_prompt()
        if args.watch:
            self.watch(args.source, dest, package, args.run, args.force)

    def register_error(self, code=1, errmsg=None):
        """Updates the exit code."""
        if errmsg is not None:
            if self.errmsg is None:
                self.errmsg = errmsg
            elif errmsg not in self.errmsg:
                self.errmsg += ", " + errmsg
        if code is not None:
            self.exit_code = max(self.exit_code, code)

    @contextmanager
    def handling_exceptions(self):
        """Performs proper exception handling."""
        try:
            with handling_broken_process_pool():
                yield
        except SystemExit as err:
            self.register_error(err.code)
        except BaseException as err:
            if isinstance(err, CoconutException):
                logger.print_exc()
            elif not isinstance(err, KeyboardInterrupt):
                traceback.print_exc()
            self.register_error(errmsg=err.__class__.__name__)

    def compile_path(self, path, write=True, package=None, *args, **kwargs):
        """Compiles a path and returns paths to compiled files."""
        path = fixpath(path)
        if write is not None and write is not True:
            write = fixpath(write)
        if os.path.isfile(path):
            if package is None:
                package = False
            destpath = self.compile_file(path, write, package, *args, **kwargs)
            return [destpath] if destpath is not None else []
        elif os.path.isdir(path):
            if package is None:
                package = True
            return self.compile_folder(path, write, package, *args, **kwargs)
        else:
            raise CoconutException("could not find source path", path)

    def compile_folder(self, directory, write=True, package=True, *args, **kwargs):
        """Compiles a directory and returns paths to compiled files."""
        filepaths = []
        for dirpath, dirnames, filenames in os.walk(directory):
            if write is None or write is True:
                writedir = write
            else:
                writedir = os.path.join(write, os.path.relpath(dirpath, directory))
            for filename in filenames:
                if os.path.splitext(filename)[1] in code_exts:
                    destpath = self.compile_file(os.path.join(dirpath, filename), writedir, package, *args, **kwargs)
                    if destpath is not None:
                        filepaths.append(destpath)
            for name in dirnames[:]:
                if not is_special_dir(name) and name.startswith("."):
                    if logger.verbose:
                        logger.show_tabulated("Skipped directory", name, "(explicitly pass as source to override).")
                    dirnames.remove(name)  # directories removed from dirnames won't appear in further os.walk iteration
        return filepaths

    def compile_file(self, filepath, write=True, package=False, *args, **kwargs):
        """Compiles a file and returns the compiled file's path."""
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
            destpath = fixpath(base + ext)
            if filepath == destpath:
                raise CoconutException("cannot compile " + showpath(filepath) + " to itself", extra="incorrect file extension")
        self.compile(filepath, destpath, package, *args, **kwargs)
        return destpath

    def compile(self, codepath, destpath=None, package=False, run=False, force=False, show_unchanged=True):
        """Compiles a source Coconut file to a destination Python file."""
        with openfile(codepath, "r") as opened:
            code = readfile(opened)

        if destpath is not None:
            destdir = os.path.dirname(destpath)
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            if package is True:
                self.create_package(destdir)

        foundhash = None if force else self.has_hash_of(destpath, code, package)
        if foundhash:
            if show_unchanged:
                logger.show_tabulated("Left unchanged", showpath(destpath), "(pass --force to override).")
            if self.show:
                print(foundhash)
            if run:
                self.execute_file(destpath)

        else:
            logger.show_tabulated("Compiling", showpath(codepath), "...")

            if package is True:
                compile_method = "parse_package"
            elif package is False:
                compile_method = "parse_file"
            else:
                raise CoconutInternalException("invalid value for package", package)

            def callback(compiled):
                if destpath is None:
                    logger.show_tabulated("Compiled", showpath(codepath), "without writing to file.")
                else:
                    with openfile(destpath, "w") as opened:
                        writefile(opened, compiled)
                    logger.show_tabulated("Compiled to", showpath(destpath), ".")
                if self.show:
                    print(compiled)
                if run:
                    if destpath is None:
                        self.execute(compiled, path=codepath, allow_show=False)
                    else:
                        self.execute_file(destpath)

            self.submit_comp_job(codepath, callback, compile_method, code)

    def submit_comp_job(self, path, callback, method, *args, **kwargs):
        """Submits a job on self.comp to be run in parallel."""
        if self.executor is None:
            with self.handling_exceptions():
                callback(getattr(self.comp, method)(*args, **kwargs))
        else:
            path = showpath(path)
            with logger.in_path(path):  # pickle the compiler in the path context
                future = self.executor.submit(multiprocess_wrapper(self.comp, method), *args, **kwargs)

            def callback_wrapper(completed_future):
                """Ensures that all errors are always caught, since errors raised in a callback won't be propagated."""
                with logger.in_path(path):  # handle errors in the path context
                    with self.handling_exceptions():
                        result = completed_future.result()
                        callback(result)
            future.add_done_callback(callback_wrapper)

    def set_jobs(self, jobs):
        """Sets --jobs."""
        if jobs == "sys":
            self.jobs = None
        else:
            try:
                jobs = int(jobs)
            except ValueError:
                jobs = -1  # will raise error below
            if jobs < 0:
                raise CoconutException("--jobs must be an integer >= 0 or 'sys'")
            else:
                self.jobs = jobs

    @contextmanager
    def running_jobs(self, exit_on_error=True):
        """Initialize multiprocessing."""
        with self.handling_exceptions():
            if self.jobs == 0:
                yield
            else:
                from concurrent.futures import ProcessPoolExecutor
                try:
                    with ProcessPoolExecutor(self.jobs) as self.executor:
                        yield
                finally:
                    self.executor = None
        if exit_on_error:
            self.exit_on_error()

    def create_package(self, dirpath):
        """Sets up a package directory."""
        dirpath = fixpath(dirpath)
        filepath = os.path.join(dirpath, "__coconut__.py")
        with openfile(filepath, "w") as opened:
            writefile(opened, self.comp.getheader("__coconut__"))

    def has_hash_of(self, destpath, code, package):
        """Determines if a file has the hash of the code."""
        if destpath is not None and os.path.isfile(destpath):
            with openfile(destpath, "r") as opened:
                compiled = readfile(opened)
            hashash = gethash(compiled)
            if hashash is not None and hashash == self.comp.genhash(package, code):
                return compiled
        return None

    def get_input(self, more=False):
        """Prompts for code input."""
        received = None
        try:
            received = self.prompt.input(more)
        except KeyboardInterrupt:
            printerr("\nKeyboardInterrupt")
        except EOFError:
            print()
            self.exit_runner()
        else:
            if received.startswith(exit_chars):
                self.exit_runner()
                received = None
        return received

    def start_running(self):
        """Starts running the Runner."""
        self.comp.bind()
        self.check_runner()
        self.running = True

    def start_prompt(self):
        """Starts the interpreter."""
        print("Coconut Interpreter:")
        print('(type "exit()" or press Ctrl-D to end)')
        self.start_running()
        while self.running:
            try:
                code = self.get_input()
                if code:
                    compiled = self.handle_input(code)
                    if compiled:
                        self.execute(compiled, use_eval=None)
            except KeyboardInterrupt:
                printerr("\nKeyboardInterrupt")

    def exit_runner(self, exit_code=0):
        """Exits the interpreter."""
        self.register_error(exit_code)
        self.running = False

    def handle_input(self, code):
        """Compiles Coconut interpreter input."""
        if not self.prompt.multiline:
            if not should_indent(code):
                try:
                    return self.comp.parse_block(code)
                except CoconutException:
                    pass
            while True:
                line = self.get_input(more=True)
                if line is None:
                    return None
                elif line:
                    code += "\n" + line
                else:
                    break
        try:
            return self.comp.parse_block(code)
        except CoconutException:
            logger.print_exc()
        return None

    def execute(self, compiled=None, path=None, use_eval=False, allow_show=True):
        """Executes compiled code."""
        self.check_runner()
        if compiled is not None:
            if allow_show and self.show:
                print(compiled)
            if path is not None:  # path means header is included, and thus encoding must be removed
                compiled = rem_encoding(compiled)
            self.runner.run(compiled, use_eval=use_eval, path=path, all_errors_exit=(path is not None))
            self.run_mypy(code=self.runner.was_run_code())

    def execute_file(self, destpath):
        """Executes compiled file."""
        self.check_runner()
        self.runner.run_file(destpath)

    def check_runner(self):
        """Makes sure there is a runner."""
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())
        if self.runner is None:
            self.runner = Runner(self.comp, exit=self.exit_runner, store=self.mypy)

    @property
    def mypy(self):
        """Whether using MyPy or not."""
        return self.mypy_args is not None

    def set_mypy_args(self, mypy_args=None):
        """Sets MyPy arguments."""
        if mypy_args is None:
            self.mypy_args = None
        else:
            self.mypy_errs = []
            self.mypy_args = list(mypy_args)

            for arg in self.mypy_args:
                if arg == "--py2" or arg == "-2":
                    logger.warn("unnecessary --mypy argument", arg, extra="passed automatically when needed")
                elif arg == "--python-version":
                    logger.warn("unnecessary --mypy argument", arg, extra="current --target passed as version automatically")

            if not ("--py2" in self.mypy_args or "-2" in self.mypy_args) and not self.comp.target.startswith("3"):
                self.mypy_args.append("--py2")

            if "--python-version" not in self.mypy_args:
                self.mypy_args += ["--python-version", ".".join(str(v) for v in self.comp.target_info_len2)]

            logger.log("MyPy args:", self.mypy_args)

    def run_mypy(self, paths=[], code=None):
        """Run MyPy with arguments."""
        set_mypy_path(stub_dir)
        if self.mypy:
            from coconut.command.mypy import mypy_run
            args = paths + self.mypy_args
            if code is not None:
                args += ["-c", code]
            for line, is_err in mypy_run(args):
                if code is None or line not in self.mypy_errs:
                    if is_err:
                        printerr(line)
                    else:
                        print(line)
                if line not in self.mypy_errs:
                    self.mypy_errs.append(line)

    def start_jupyter(self, args):
        """Starts Jupyter with the Coconut kernel."""
        install_func = functools.partial(run_cmd, show_output=logger.verbose or not args)

        try:
            install_func(["jupyter", "--version"])
        except CalledProcessError:
            jupyter = "ipython"
        else:
            jupyter = "jupyter"

        for icoconut_kernel_dir in icoconut_kernel_dirs:
            install_args = [jupyter, "kernelspec", "install", icoconut_kernel_dir, "--replace"]
            try:
                install_func(install_args)
            except CalledProcessError:
                user_install_args = install_args + ["--user"]
                try:
                    install_func(user_install_args)
                except CalledProcessError:
                    logger.warn("kernel install failed on command'", " ".join(install_args))
                    self.register_error(errmsg="Jupyter error")

        if args:
            if args[0] == "console":
                ver = "2" if PY2 else "3"
                try:
                    install_func(["python" + ver, "-m", "coconut.main", "--version"])
                except CalledProcessError:
                    kernel_name = "coconut"
                else:
                    kernel_name = "coconut" + ver
                run_args = [jupyter, "console", "--kernel", kernel_name] + args[1:]
            elif args[0] == "notebook":
                run_args = [jupyter, "notebook"] + args[1:]
            else:
                raise CoconutException("first argument after --jupyter must be either 'console' or 'notebook'")
            self.register_error(run_cmd(run_args, raise_errs=False), errmsg="Jupyter error")

    def watch(self, source, write=True, package=None, run=False, force=False):
        """Watches a source and recompiles on change."""
        from coconut.command.watch import Observer, RecompilationWatcher

        source = fixpath(source)

        print()
        logger.show_tabulated("Watching", showpath(source), "(press Ctrl-C to end)...")

        def recompile(path):
            if os.path.isfile(path) and os.path.splitext(path)[1] in code_exts:
                with self.handling_exceptions():
                    self.run_mypy(self.compile_path(path, write, package, run, force, show_unchanged=False))

        watcher = RecompilationWatcher(recompile)
        observer = Observer()
        observer.schedule(watcher, source, recursive=True)

        with self.running_jobs():
            observer.start()
            try:
                while True:
                    time.sleep(watch_interval)
                    watcher.keep_watching()
            except KeyboardInterrupt:
                logger.show("Got KeyboardInterrupt; stopping watcher.")
            finally:
                observer.stop()
                observer.join()
