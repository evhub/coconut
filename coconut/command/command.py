#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: The Coconut command-line utility.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os
import time
import traceback
from functools import partial
from contextlib import contextmanager
from subprocess import CalledProcessError

from coconut.myparsing import PYPARSING
from coconut.compiler import Compiler
from coconut.exceptions import (
    CoconutException,
    CoconutInternalException,
)
from coconut.terminal import (
    logger,
    printerr,
)
from coconut.constants import (
    fixpath,
    code_exts,
    comp_ext,
    watch_interval,
    icoconut_kernel_names,
    icoconut_kernel_dirs,
    stub_dir,
    exit_chars,
    coconut_run_args,
    coconut_run_verbose_args,
    verbose_mypy_args,
    report_this_text,
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
    set_recursion_limit,
    canparse,
)
from coconut.compiler.util import should_indent, get_target_info_len2
from coconut.compiler.header import gethash
from coconut.command.cli import arguments

# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------


class Command(object):
    """Coconut command-line interface."""
    comp = None  # current coconut.compiler.Compiler
    show = False  # corresponds to --display flag
    runner = None  # the current Runner
    jobs = 0  # corresponds to --jobs flag
    executor = None  # runs --jobs
    exit_code = 0  # exit status to return
    errmsg = None  # error message to display
    mypy_args = None  # corresponds to --mypy flag

    def __init__(self):
        """Create the CLI."""
        self.prompt = Prompt()

    def start(self, run=False):
        """Process command-line arguments."""
        if run:
            args, argv = [], []
            # for coconut-run, all args beyond the source file should be wrapped in an --argv
            for i in range(1, len(sys.argv)):
                arg = sys.argv[i]
                args.append(arg)
                # if arg is source file, put everything else in argv
                if not arg.startswith("-") and canparse(arguments, args[:-1]):
                    argv = sys.argv[i + 1:]
                    break
            if "--verbose" in args:
                args = list(coconut_run_verbose_args) + args
            else:
                args = list(coconut_run_args) + args
            self.cmd(args, argv=argv)
        else:
            self.cmd()

    def cmd(self, args=None, argv=None, interact=True):
        """Process command-line arguments."""
        if args is None:
            parsed_args = arguments.parse_args()
        else:
            parsed_args = arguments.parse_args(args)
        if argv is not None:
            parsed_args.argv = argv
        self.exit_code = 0
        with self.handling_exceptions():
            self.use_args(parsed_args, interact, original_args=args)
        self.exit_on_error()

    def setup(self, *args, **kwargs):
        """Set parameters for the compiler."""
        if self.comp is None:
            self.comp = Compiler(*args, **kwargs)
        else:
            self.comp.setup(*args, **kwargs)

    def exit_on_error(self):
        """Exit if exit_code is abnormal."""
        if self.exit_code:
            if self.errmsg is not None:
                logger.show("Exiting due to " + self.errmsg + ".")
                self.errmsg = None
            if self.using_jobs:
                kill_children()
            sys.exit(self.exit_code)

    def use_args(self, args, interact=True, original_args=None):
        """Handle command-line arguments."""
        logger.quiet, logger.verbose = args.quiet, args.verbose
        if DEVELOP:
            logger.tracing = args.trace

        logger.log("Using " + PYPARSING + ".")
        if original_args is not None:
            logger.log("Directly passed args:", original_args)
        logger.log("Parsed args:", args)

        if args.recursion_limit is not None:
            set_recursion_limit(args.recursion_limit)
        if args.jobs is not None:
            self.set_jobs(args.jobs)
        if args.display:
            self.show = True
        if args.style is not None:
            self.prompt.set_style(args.style)
        if args.history_file is not None:
            self.prompt.set_history_file(args.history_file)
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
            no_tco=args.no_tco,
        )

        if args.mypy is not None:
            self.set_mypy_args(args.mypy)

        if args.argv is not None:
            sys.argv = [args.source if args.source is not None else ""]
            sys.argv.extend(args.argv)

        if args.source is not None:
            if args.interact and args.run:
                logger.warn("extraneous --run argument passed; --interact implies --run")
            if args.package and self.mypy:
                logger.warn("extraneous --package argument passed; --mypy implies --package")

            if args.standalone and args.package:
                raise CoconutException("cannot compile as both --package and --standalone")
            if args.standalone and self.mypy:
                raise CoconutException("cannot compile as both --package (implied by --mypy) and --standalone")
            if args.no_write and self.mypy:
                raise CoconutException("cannot compile with --no-write when using --mypy")
            if (args.run or args.interact) and os.path.isdir(args.source):
                if args.run:
                    raise CoconutException("source path must point to file not directory when --run is enabled")
                if args.interact:
                    raise CoconutException("source path must point to file not directory when --run (implied by --interact) is enabled")
            if args.watch and os.path.isfile(args.source):
                raise CoconutException("source path must point to directory not file when --watch is enabled")

            if args.dest is None:
                if args.no_write:
                    dest = False  # no dest
                else:
                    dest = True  # auto-generate dest
            elif args.no_write:
                raise CoconutException("destination path cannot be given when --no-write is enabled")
            else:
                dest = args.dest

            source = fixpath(args.source)

            if args.package or self.mypy:
                package = True
            elif args.standalone:
                package = False
            else:
                # auto-decide package
                if os.path.isfile(source):
                    package = False
                elif os.path.isdir(source):
                    package = True
                else:
                    raise CoconutException("could not find source path", source)

            with self.running_jobs(exit_on_error=not args.watch):
                filepaths = self.compile_path(source, dest, package, args.run or args.interact, args.force)
            self.run_mypy(filepaths)

        elif (
            args.run
            or args.no_write
            or args.force
            or args.package
            or args.standalone
            or args.watch
        ):
            raise CoconutException("a source file/folder must be specified when options that depend on the source are enabled")

        if args.code is not None:
            self.execute(self.comp.parse_block(args.code))
        got_stdin = False
        if args.jupyter is not None:
            self.start_jupyter(args.jupyter)
        elif stdin_readable():
            logger.log("Reading piped input from stdin...")
            self.execute(self.comp.parse_block(sys.stdin.read()))
            got_stdin = True
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
            self.watch(source, dest, package, args.run, args.force)

    def register_error(self, code=1, errmsg=None):
        """Update the exit code."""
        if errmsg is not None:
            if self.errmsg is None:
                self.errmsg = errmsg
            elif errmsg not in self.errmsg:
                self.errmsg += ", " + errmsg
        if code is not None:
            self.exit_code = code or self.exit_code

    @contextmanager
    def handling_exceptions(self):
        """Perform proper exception handling."""
        try:
            if self.using_jobs:
                with handling_broken_process_pool():
                    yield
            else:
                yield
        except SystemExit as err:
            self.register_error(err.code)
        except BaseException as err:
            if isinstance(err, CoconutException):
                logger.display_exc()
            elif not isinstance(err, KeyboardInterrupt):
                traceback.print_exc()
                printerr(report_this_text)
            self.register_error(errmsg=err.__class__.__name__)

    def compile_path(self, path, write=True, package=True, *args, **kwargs):
        """Compile a path and returns paths to compiled files."""
        if not isinstance(write, bool):
            write = fixpath(write)
        if os.path.isfile(path):
            destpath = self.compile_file(path, write, package, *args, **kwargs)
            return [destpath] if destpath is not None else []
        elif os.path.isdir(path):
            return self.compile_folder(path, write, package, *args, **kwargs)
        else:
            raise CoconutException("could not find source path", path)

    def compile_folder(self, directory, write=True, package=True, *args, **kwargs):
        """Compile a directory and returns paths to compiled files."""
        if not isinstance(write, bool) and os.path.isfile(write):
            raise CoconutException("destination path cannot point to a file when compiling a directory")
        filepaths = []
        for dirpath, dirnames, filenames in os.walk(directory):
            if isinstance(write, bool):
                writedir = write
            else:
                writedir = os.path.join(write, os.path.relpath(dirpath, directory))
            for filename in filenames:
                if os.path.splitext(filename)[1] in code_exts:
                    with self.handling_exceptions():
                        destpath = self.compile_file(os.path.join(dirpath, filename), writedir, package, *args, **kwargs)
                        if destpath is not None:
                            filepaths.append(destpath)
            for name in dirnames[:]:
                if not is_special_dir(name) and name.startswith("."):
                    if logger.verbose:
                        logger.show_tabulated("Skipped directory", name, "(explicitly pass as source to override).")
                    dirnames.remove(name)  # directories removed from dirnames won't appear in further os.walk iterations
        return filepaths

    def compile_file(self, filepath, write=True, package=False, *args, **kwargs):
        """Compile a file and returns the compiled file's path."""
        set_ext = False
        if write is False:
            destpath = None
        elif write is True:
            destpath = filepath
            set_ext = True
        elif os.path.splitext(write)[1]:
            # write is a file; it is the destination filepath
            destpath = write
        else:
            # write is a dir; make the destination filepath by adding the filename
            destpath = os.path.join(write, os.path.basename(filepath))
            set_ext = True
        if set_ext:
            base, ext = os.path.splitext(os.path.splitext(destpath)[0])
            if not ext:
                ext = comp_ext
            destpath = fixpath(base + ext)
        if filepath == destpath:
            raise CoconutException("cannot compile " + showpath(filepath) + " to itself", extra="incorrect file extension")
        self.compile(filepath, destpath, package, *args, **kwargs)
        return destpath

    def compile(self, codepath, destpath=None, package=False, run=False, force=False, show_unchanged=True):
        """Compile a source Coconut file to a destination Python file."""
        with openfile(codepath, "r") as opened:
            code = readfile(opened)

        package_level = -1
        if destpath is not None:
            destpath = fixpath(destpath)
            destdir = os.path.dirname(destpath)
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            if package is True:
                package_level = self.get_package_level(codepath)
                if package_level == 0:
                    self.create_package(destdir)

        foundhash = None if force else self.has_hash_of(destpath, code, package_level)
        if foundhash:
            if show_unchanged:
                logger.show_tabulated("Left unchanged", showpath(destpath), "(pass --force to override).")
            if self.show:
                print(foundhash)
            if run:
                self.execute_file(destpath)

        else:
            logger.show_tabulated("Compiling", showpath(codepath), "...")

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

            if package is True:
                self.submit_comp_job(codepath, callback, "parse_package", code, package_level=package_level)
            elif package is False:
                self.submit_comp_job(codepath, callback, "parse_file", code)
            else:
                raise CoconutInternalException("invalid value for package", package)

    def get_package_level(self, codepath):
        """Get the relative level to the base directory of the package."""
        package_level = -1
        check_dir = os.path.dirname(os.path.abspath(codepath))
        while check_dir:
            has_init = False
            for ext in code_exts:
                init_file = os.path.join(check_dir, "__init__" + ext)
                if os.path.exists(init_file):
                    has_init = True
                    break
            if has_init:
                package_level += 1
                check_dir = os.path.dirname(check_dir)
            else:
                break
        if package_level < 0:
            logger.warn("missing __init__" + code_exts[0] + " in package", check_dir)
            package_level = 0
        return package_level
        return 0

    def create_package(self, dirpath):
        """Set up a package directory."""
        filepath = os.path.join(dirpath, "__coconut__.py")
        with openfile(filepath, "w") as opened:
            writefile(opened, self.comp.getheader("__coconut__"))

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
        """Set --jobs."""
        if jobs == "sys":
            self.jobs = None
        else:
            try:
                jobs = int(jobs)
            except ValueError:
                jobs = -1  # will raise error below
            if jobs < 0:
                raise CoconutException("--jobs must be an integer >= 0 or 'sys'")
            self.jobs = jobs

    @property
    def using_jobs(self):
        """Determine whether or not multiprocessing is being used."""
        return self.jobs != 0

    @contextmanager
    def running_jobs(self, exit_on_error=True):
        """Initialize multiprocessing."""
        with self.handling_exceptions():
            if self.using_jobs:
                from concurrent.futures import ProcessPoolExecutor
                try:
                    with ProcessPoolExecutor(self.jobs) as self.executor:
                        yield
                finally:
                    self.executor = None
            else:
                yield
        if exit_on_error:
            self.exit_on_error()

    def has_hash_of(self, destpath, code, package_level):
        """Determine if a file has the hash of the code."""
        if destpath is not None and os.path.isfile(destpath):
            with openfile(destpath, "r") as opened:
                compiled = readfile(opened)
            hashash = gethash(compiled)
            if hashash is not None and hashash == self.comp.genhash(code, package_level):
                return True
        return False

    def get_input(self, more=False):
        """Prompt for code input."""
        received = None
        try:
            received = self.prompt.input(more)
        except KeyboardInterrupt:
            print()
            printerr("KeyboardInterrupt")
        except EOFError:
            print()
            self.exit_runner()
        else:
            if received.startswith(exit_chars):
                self.exit_runner()
                received = None
        return received

    def start_running(self):
        """Start running the Runner."""
        self.comp.warm_up()
        self.check_runner()
        self.running = True

    def start_prompt(self):
        """Start the interpreter."""
        logger.show("Coconut Interpreter:")
        logger.show("(type 'exit()' or press Ctrl-D to end)")
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
        """Exit the interpreter."""
        self.register_error(exit_code)
        self.running = False

    def handle_input(self, code):
        """Compile Coconut interpreter input."""
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
            logger.display_exc()
        return None

    def execute(self, compiled=None, path=None, use_eval=False, allow_show=True):
        """Execute compiled code."""
        self.check_runner()
        if compiled is not None:
            if allow_show and self.show:
                print(compiled)
            if path is not None:  # path means header is included, and thus encoding must be removed
                compiled = rem_encoding(compiled)
            self.runner.run(compiled, use_eval=use_eval, path=path, all_errors_exit=path is not None)
            self.run_mypy(code=self.runner.was_run_code())

    def execute_file(self, destpath):
        """Execute compiled file."""
        self.check_runner()
        self.runner.run_file(destpath)

    def check_runner(self):
        """Make sure there is a runner."""
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())
        if self.runner is None:
            self.runner = Runner(self.comp, exit=self.exit_runner, store=self.mypy)

    @property
    def mypy(self):
        """Whether using MyPy or not."""
        return self.mypy_args is not None

    def set_mypy_args(self, mypy_args=None):
        """Set MyPy arguments."""
        if mypy_args is None:
            self.mypy_args = None
        else:
            self.mypy_errs = []
            self.mypy_args = list(mypy_args)

            if not any(arg.startswith("--python-version") for arg in mypy_args):
                self.mypy_args += [
                    "--python-version",
                    ".".join(str(v) for v in get_target_info_len2(self.comp.target, mode="nearest")),
                ]

            if logger.verbose:
                for arg in verbose_mypy_args:
                    if arg not in self.mypy_args:
                        self.mypy_args.append(arg)

            logger.log("MyPy args:", self.mypy_args)

    def run_mypy(self, paths=(), code=None):
        """Run MyPy with arguments."""
        if self.mypy:
            set_mypy_path(stub_dir)
            from coconut.command.mypy import mypy_run
            args = list(paths) + self.mypy_args
            if code is not None:
                args += ["-c", code]
            for line, is_err in mypy_run(args):
                if line not in self.mypy_errs:
                    printerr(line)
                    self.mypy_errs.append(line)
                elif code is None:
                    printerr(line)
                self.register_error(errmsg="MyPy error")

    def start_jupyter(self, args):
        """Start Jupyter with the Coconut kernel."""
        install_func = partial(run_cmd, show_output=logger.verbose)

        try:
            install_func(["jupyter", "--version"])
        except CalledProcessError:
            jupyter = "ipython"
        else:
            jupyter = "jupyter"

        # always install kernels if given no args, otherwise only if there's a kernel missing
        do_install = not args
        if not do_install:
            kernel_list = run_cmd([jupyter, "kernelspec", "list"], show_output=False, raise_errs=False)
            do_install = any(ker not in kernel_list for ker in icoconut_kernel_names)

        if do_install:
            success = True
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
                        success = False
            if success:
                logger.show_sig("Successfully installed Coconut Jupyter kernel.")

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
            else:
                run_args = [jupyter] + args
            self.register_error(run_cmd(run_args, raise_errs=False), errmsg="Jupyter error")

    def watch(self, source, write=True, package=True, run=False, force=False):
        """Watch a source and recompiles on change."""
        from coconut.command.watch import Observer, RecompilationWatcher

        source = fixpath(source)

        logger.show()
        logger.show_tabulated("Watching", showpath(source), "(press Ctrl-C to end)...")

        def recompile(path):
            path = fixpath(path)
            if os.path.isfile(path) and os.path.splitext(path)[1] in code_exts:
                with self.handling_exceptions():
                    if write is True or write is None:
                        writedir = write
                    else:
                        # correct the compilation path based on the relative position of path to source
                        dirpath = os.path.dirname(path)
                        writedir = os.path.join(write, os.path.relpath(dirpath, source))
                    filepaths = self.compile_path(path, writedir, package, run, force, show_unchanged=False)
                    self.run_mypy(filepaths)

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
                logger.show_sig("Got KeyboardInterrupt; stopping watcher.")
            finally:
                observer.stop()
                observer.join()
