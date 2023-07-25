#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan, Noah Lipsyc, Ishaan Verma
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
import shutil
import random
from contextlib import contextmanager
from subprocess import CalledProcessError

from coconut._pyparsing import (
    unset_fast_pyparsing_reprs,
    collect_timing_info,
    print_timing_info,
)

from coconut.compiler import Compiler
from coconut.exceptions import (
    CoconutException,
    CoconutInternalException,
)
from coconut.terminal import (
    logger,
    format_error,
    internal_assert,
)
from coconut.constants import (
    PY32,
    PY35,
    fixpath,
    code_exts,
    comp_ext,
    watch_interval,
    icoconut_default_kernel_names,
    icoconut_default_kernel_dirs,
    icoconut_custom_kernel_name,
    icoconut_old_kernel_names,
    exit_chars,
    verbose_mypy_args,
    default_mypy_args,
    report_this_text,
    mypy_silent_non_err_prefixes,
    mypy_silent_err_prefixes,
    mypy_err_infixes,
    mypy_install_arg,
    jupyter_install_arg,
    mypy_builtin_regex,
    coconut_pth_file,
    error_color_code,
    jupyter_console_commands,
    default_jobs,
    create_package_retries,
    default_use_cache_dir,
    coconut_cache_dir,
    coconut_run_kwargs,
    interpreter_uses_incremental,
)
from coconut.util import (
    univ_open,
    ver_tuple_to_str,
    install_custom_kernel,
    get_clock_time,
    first_import_time,
)
from coconut.command.util import (
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
    can_parse,
    invert_mypy_arg,
    run_with_stack_size,
    proc_run_args,
)
from coconut.compiler.util import (
    should_indent,
    get_target_info_smart,
)
from coconut.compiler.header import gethash
from coconut.compiler.grammar import set_grammar_names
from coconut.command.cli import arguments, cli_version

# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------


class Command(object):
    """Coconut command-line interface."""
    comp = None  # current coconut.compiler.Compiler
    runner = None  # the current Runner
    executor = None  # runs --jobs
    exit_code = 0  # exit status to return
    errmsg = None  # error message to display

    show = False  # corresponds to --display flag
    jobs = 0  # corresponds to --jobs flag
    mypy_args = None  # corresponds to --mypy flag
    argv_args = None  # corresponds to --argv flag
    stack_size = 0  # corresponds to --stack-size flag

    _prompt = None

    @property
    def prompt(self):
        """Delay creation of a Prompt() until it's needed."""
        if self._prompt is None:
            self._prompt = Prompt()
        return self._prompt

    def start(self, run=False):
        """Endpoint for coconut and coconut-run."""
        if run:
            args, argv = [], []
            # for coconut-run, all args beyond the source file should be wrapped in an --argv
            source = None
            for i in range(1, len(sys.argv)):
                arg = sys.argv[i]
                # if arg is source file, put everything else in argv
                if not arg.startswith("-") and can_parse(arguments, args):
                    source = arg
                    argv = sys.argv[i + 1:]
                    break
                else:
                    args.append(arg)
            args = proc_run_args(args)
            if "--run" in args:
                logger.warn("extraneous --run argument passed; coconut-run implies --run")
            else:
                args.append("--run")
            dest = None
            if source is not None:
                source = fixpath(source)
                args.append(source)
                if default_use_cache_dir:
                    if os.path.isfile(source):
                        dest = os.path.join(os.path.dirname(source), coconut_cache_dir)
                    else:
                        dest = os.path.join(source, coconut_cache_dir)
            self.cmd(args, argv=argv, use_dest=dest, **coconut_run_kwargs)
        else:
            self.cmd()

    # new external parameters should be updated in api.pyi and DOCS
    def cmd(self, args=None, argv=None, interact=True, default_target=None, use_dest=None):
        """Process command-line arguments."""
        result = None
        with self.handling_exceptions():
            if args is None:
                parsed_args = arguments.parse_args()
            else:
                parsed_args = arguments.parse_args(args)
            if argv is not None:
                if parsed_args.argv is not None:
                    raise CoconutException("cannot pass --argv/--args when using coconut-run (coconut-run interprets any arguments after the source file as --argv/--args)")
                parsed_args.argv = argv
            if parsed_args.target is None:
                parsed_args.target = default_target
            if use_dest is not None and not parsed_args.no_write:
                internal_assert(parsed_args.dest is None, "coconut-run got passed a dest", parsed_args)
                parsed_args.dest = use_dest
            self.exit_code = 0
            self.stack_size = parsed_args.stack_size
            result = self.run_with_stack_size(self.execute_args, parsed_args, interact, original_args=args)
        self.exit_on_error()
        return result

    def run_with_stack_size(self, func, *args, **kwargs):
        """Execute func with the correct stack size."""
        if self.stack_size:
            return run_with_stack_size(self.stack_size, func, *args, **kwargs)
        else:
            return func(*args, **kwargs)

    def setup(self, *args, **kwargs):
        """Set parameters for the compiler."""
        if self.comp is None:
            self.comp = Compiler(*args, **kwargs)
        else:
            self.comp.setup(*args, **kwargs)

    def parse_block(self, code):
        """Compile a block of code for the interpreter."""
        return self.comp.parse_block(code, keep_state=True)

    def exit_on_error(self):
        """Exit if exit_code is abnormal."""
        if self.exit_code:
            if self.errmsg is not None:
                # show on stdout with error color code so that stdout
                #  listeners see the error
                logger.show("Coconut exiting with error: " + self.errmsg, color=error_color_code)
                self.errmsg = None
            if self.using_jobs:
                kill_children()
            sys.exit(self.exit_code)

    def execute_args(self, args, interact=True, original_args=None):
        """Handle command-line arguments."""
        with self.handling_exceptions():
            # fix args
            if not DEVELOP:
                args.trace = args.profile = False

            # set up logger
            logger.setup(
                quiet=args.quiet,
                verbose=args.verbose,
                tracing=args.trace,
            )
            if args.verbose or args.trace or args.profile:
                set_grammar_names()
            if args.trace or args.profile:
                unset_fast_pyparsing_reprs()
            if args.profile:
                collect_timing_info()
            logger.enable_colors()

            logger.log(cli_version)
            if original_args is not None:
                logger.log("Directly passed args:", original_args)
            logger.log("Parsed args:", args)

            # validate general command args
            if args.stack_size and args.stack_size % 4 != 0:
                logger.warn("--stack-size should generally be a multiple of 4, not {stack_size} (to support 4 KB pages)".format(stack_size=args.stack_size))
            if args.mypy is not None and args.no_line_numbers:
                logger.warn("using --mypy running with --no-line-numbers is not recommended; mypy error messages won't include Coconut line numbers")
            if args.line_numbers and args.no_line_numbers:
                raise CoconutException("cannot compile with both --line-numbers and --no-line-numbers")
            if args.site_install and args.site_uninstall:
                raise CoconutException("cannot --site-install and --site-uninstall simultaneously")
            for and_args in getattr(args, "and") or []:
                if len(and_args) > 2:
                    raise CoconutException(
                        "--and accepts at most two arguments, source and dest ({n} given: {args!r})".format(
                            n=len(and_args),
                            args=and_args,
                        ),
                    )

            # process general command args
            self.set_jobs(args.jobs, args.profile)
            if args.recursion_limit is not None:
                set_recursion_limit(args.recursion_limit)
            if args.display:
                self.show = True
            if args.style is not None:
                self.prompt.set_style(args.style)
            if args.history_file is not None:
                self.prompt.set_history_file(args.history_file)
            if args.vi_mode:
                self.prompt.vi_mode = True
            if args.docs:
                launch_documentation()
            if args.tutorial:
                launch_tutorial()
            if args.site_uninstall:
                self.site_uninstall()
            if args.site_install:
                self.site_install()
            if args.argv is not None:
                self.argv_args = list(args.argv)

            # process general compiler args
            if args.line_numbers:
                line_numbers = True
            elif args.no_line_numbers:
                line_numbers = False
            else:
                line_numbers = (
                    not args.minify
                    or args.mypy is not None
                )
            self.setup(
                target=args.target,
                strict=args.strict,
                minify=args.minify,
                line_numbers=line_numbers,
                keep_lines=args.keep_lines,
                no_tco=args.no_tco,
                no_wrap=args.no_wrap_types,
            )
            if args.watch:
                self.comp.warm_up(enable_incremental_mode=True)

            # process mypy args and print timing info (must come after compiler setup)
            if args.mypy is not None:
                self.set_mypy_args(args.mypy)
            logger.log("Grammar init time: " + str(self.comp.grammar_init_time) + " secs / Total init time: " + str(get_clock_time() - first_import_time) + " secs")

            # do compilation, keeping track of compiled filepaths
            filepaths = []
            if args.source is not None:
                # warnings if source is given
                if args.interact and args.run:
                    logger.warn("extraneous --run argument passed; --interact implies --run")
                if args.package and self.mypy:
                    logger.warn("extraneous --package argument passed; --mypy implies --package")

                # errors if source is given
                if args.standalone and args.package:
                    raise CoconutException("cannot compile as both --package and --standalone")
                if args.standalone and self.mypy:
                    raise CoconutException("cannot compile as both --package (implied by --mypy) and --standalone")
                if args.no_write and self.mypy:
                    raise CoconutException("cannot compile with --no-write when using --mypy")

                # process all source, dest pairs
                src_dest_package_triples = []
                for and_args in [(args.source, args.dest)] + (getattr(args, "and") or []):
                    if len(and_args) == 1:
                        src, = and_args
                        dest = None
                    else:
                        src, dest = and_args
                    src_dest_package_triples.append(self.process_source_dest(src, dest, args))

                # disable jobs if we know we're only compiling one file
                if len(src_dest_package_triples) <= 1 and not any(os.path.isdir(source) for source, dest, package in src_dest_package_triples):
                    self.disable_jobs()

                # do compilation
                with self.running_jobs(exit_on_error=not args.watch):
                    for source, dest, package in src_dest_package_triples:
                        filepaths += self.compile_path(source, dest, package, run=args.run or args.interact, force=args.force)
                self.run_mypy(filepaths)

            # validate args if no source is given
            elif (
                args.run
                or args.no_write
                or args.force
                or args.package
                or args.standalone
                or args.watch
                or args.jobs
            ):
                raise CoconutException("a source file/folder must be specified when options that depend on the source are enabled")
            elif getattr(args, "and"):
                raise CoconutException("--and should only be used for extra source/dest pairs, not the first source/dest pair")

            # handle extra cli tasks
            if args.code is not None:
                self.execute(self.parse_block(args.code))
            got_stdin = False
            if args.jupyter is not None:
                self.start_jupyter(args.jupyter)
            elif stdin_readable():
                logger.log("Reading piped input from stdin...")
                self.execute(self.parse_block(sys.stdin.read()))
                got_stdin = True
            if args.interact or (
                interact and not (
                    got_stdin
                    or args.source
                    or args.code
                    or args.tutorial
                    or args.docs
                    or args.watch
                    or args.site_uninstall
                    or args.site_install
                    or args.jupyter is not None
                    or args.mypy == [mypy_install_arg]
                )
            ):
                self.start_prompt()
            if args.watch:
                # src_dest_package_triples is always available here
                self.watch(src_dest_package_triples, args.run, args.force)
            if args.profile:
                print_timing_info()

            # make sure to return inside handling_exceptions to ensure filepaths is available
            return filepaths

    def process_source_dest(self, source, dest, args):
        """Determine the correct source, dest, package mode to use for the given source, dest, and args."""
        # determine source
        processed_source = fixpath(source)

        # validate args
        if (args.run or args.interact) and os.path.isdir(processed_source):
            if args.run:
                raise CoconutException("source path %r must point to file not directory when --run is enabled" % (source,))
            if args.interact:
                raise CoconutException("source path %r must point to file not directory when --run (implied by --interact) is enabled" % (source,))
        if args.watch and os.path.isfile(processed_source):
            raise CoconutException("source path %r must point to directory not file when --watch is enabled" % (source,))

        # determine dest
        if dest is None:
            if args.no_write:
                processed_dest = False  # no dest
            else:
                processed_dest = True  # auto-generate dest
        elif args.no_write:
            raise CoconutException("destination path cannot be given when --no-write is enabled")
        else:
            processed_dest = dest

        # determine package mode
        if args.package or self.mypy:
            package = True
        elif args.standalone:
            package = False
        else:
            # auto-decide package
            if os.path.isfile(processed_source):
                package = False
            elif os.path.isdir(processed_source):
                package = True
            else:
                raise CoconutException("could not find source path", source)

        return processed_source, processed_dest, package

    def register_exit_code(self, code=1, errmsg=None, err=None):
        """Update the exit code and errmsg."""
        if err is not None:
            internal_assert(errmsg is None, "register_exit_code accepts only one of errmsg or err")
            if logger.verbose:
                errmsg = format_error(err)
            else:
                errmsg = err.__class__.__name__
        if errmsg is not None:
            if self.errmsg is None:
                self.errmsg = errmsg
            elif errmsg not in self.errmsg:
                if logger.verbose:
                    self.errmsg += "\nAnd error: " + errmsg
                else:
                    self.errmsg += "; " + errmsg
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
            self.register_exit_code(err.code)
        except BaseException as err:
            if isinstance(err, GeneratorExit):
                raise
            elif isinstance(err, CoconutException):
                logger.print_exc()
            elif not isinstance(err, KeyboardInterrupt):
                logger.print_exc()
                logger.printerr(report_this_text)
            self.register_exit_code(err=err)

    def compile_path(self, path, write=True, package=True, **kwargs):
        """Compile a path and return paths to compiled files."""
        if not isinstance(write, bool):
            write = fixpath(write)
        if os.path.isfile(path):
            destpath = self.compile_file(path, write, package, **kwargs)
            return [destpath] if destpath is not None else []
        elif os.path.isdir(path):
            return self.compile_folder(path, write, package, **kwargs)
        else:
            raise CoconutException("could not find source path", path)

    def compile_folder(self, directory, write=True, package=True, **kwargs):
        """Compile a directory and return paths to compiled files."""
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
                        destpath = self.compile_file(os.path.join(dirpath, filename), writedir, package, **kwargs)
                        if destpath is not None:
                            filepaths.append(destpath)
            for name in dirnames[:]:
                if not is_special_dir(name) and name.startswith("."):
                    if logger.verbose:
                        logger.show_tabulated("Skipped directory", name, "(explicitly pass as source to override).")
                    dirnames.remove(name)  # directories removed from dirnames won't appear in further os.walk iterations
        return filepaths

    def compile_file(self, filepath, write=True, package=False, force=False, **kwargs):
        """Compile a file and return the compiled file's path."""
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
        if destpath is not None:
            dest_ext = os.path.splitext(destpath)[1]
            if dest_ext in code_exts:
                if force:
                    logger.warn("found destination path with " + dest_ext + " extension; compiling anyway due to --force")
                else:
                    raise CoconutException(
                        "found destination path with " + dest_ext + " extension; aborting compilation",
                        extra="pass --force to override",
                    )
        self.compile(filepath, destpath, package, force=force, **kwargs)
        return destpath

    def compile(self, codepath, destpath=None, package=False, run=False, force=False, show_unchanged=True):
        """Compile a source Coconut file to a destination Python file."""
        with univ_open(codepath, "r") as opened:
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
                logger.show_tabulated("Left unchanged", showpath(destpath), "(pass --force to overwrite).")
            if self.show:
                logger.print(foundhash)
            if run:
                self.execute_file(destpath, argv_source_path=codepath)

        else:
            logger.show_tabulated("Compiling", showpath(codepath), "...")

            def callback(compiled):
                if destpath is None:
                    logger.show_tabulated("Compiled", showpath(codepath), "without writing to file.")
                else:
                    with univ_open(destpath, "w") as opened:
                        writefile(opened, compiled)
                    logger.show_tabulated("Compiled to", showpath(destpath), ".")
                if self.show:
                    logger.print(compiled)
                if run:
                    if destpath is None:
                        self.execute(compiled, path=codepath, allow_show=False)
                    else:
                        self.execute_file(destpath, argv_source_path=codepath)

            if package is True:
                self.submit_comp_job(codepath, callback, "parse_package", code, package_level=package_level, filename=os.path.basename(codepath))
            elif package is False:
                self.submit_comp_job(codepath, callback, "parse_file", code, filename=os.path.basename(codepath))
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
            if self.comp.strict:
                logger.warn("missing __init__" + code_exts[0] + " in package", check_dir, extra="remove --strict to dismiss")
            package_level = 0
        return package_level
        return 0

    def create_package(self, dirpath, retries_left=create_package_retries):
        """Set up a package directory."""
        filepath = os.path.join(dirpath, "__coconut__.py")
        try:
            with univ_open(filepath, "w") as opened:
                writefile(opened, self.comp.getheader("__coconut__"))
        except OSError:
            logger.log_exc()
            if retries_left <= 0:
                logger.warn("Failed to write header file at", filepath)
            else:
                # sleep a random amount of time from 0 to 0.1 seconds to
                #  stagger calls across processes
                time.sleep(random.random() / 10)
                self.create_package(dirpath, retries_left - 1)

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

    def set_jobs(self, jobs, profile=False):
        """Set --jobs."""
        if jobs in (None, "sys"):
            self.jobs = jobs
        else:
            try:
                jobs = int(jobs)
            except ValueError:
                jobs = -1  # will raise error below
            if jobs < 0:
                raise CoconutException("--jobs must be an integer >= 0 or 'sys'")
            self.jobs = jobs
        logger.log("Jobs:", self.jobs)
        if profile and self.jobs != 0:
            raise CoconutException("--profile incompatible with --jobs {jobs}".format(jobs=jobs))

    def disable_jobs(self):
        """Disables use of --jobs."""
        if self.jobs not in (0, 1, None):
            logger.warn("got --jobs {jobs} but only compiling one file; disabling --jobs".format(jobs=self.jobs))
        self.jobs = 0
        logger.log("Jobs:", self.jobs)

    def get_max_workers(self):
        """Get the max_workers to use for creating ProcessPoolExecutor."""
        jobs = self.jobs if self.jobs is not None else default_jobs
        if jobs == "sys":
            return None
        else:
            return jobs

    @property
    def using_jobs(self):
        """Determine whether or not multiprocessing is being used."""
        max_workers = self.get_max_workers()
        return max_workers is None or max_workers > 1

    @contextmanager
    def running_jobs(self, exit_on_error=True):
        """Initialize multiprocessing."""
        with self.handling_exceptions():
            if self.using_jobs:
                from concurrent.futures import ProcessPoolExecutor
                try:
                    with ProcessPoolExecutor(self.get_max_workers()) as self.executor:
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
            with univ_open(destpath, "r") as opened:
                compiled = readfile(opened)
            hashash = gethash(compiled)
            if hashash is not None:
                newhash = self.comp.genhash(code, package_level)
                if hashash == newhash:
                    return True
                logger.log("old __coconut_hash__", hashash, "!= new __coconut_hash__", newhash)
        return False

    def get_input(self, more=False):
        """Prompt for code input."""
        received = None
        try:
            received = self.prompt.input(more)
        except KeyboardInterrupt:
            logger.printerr("\nKeyboardInterrupt")
        except EOFError:
            logger.print()
            self.exit_runner()
        else:
            if received.startswith(exit_chars):
                self.exit_runner()
                received = None
        return received

    def start_running(self):
        """Start running the Runner."""
        self.comp.warm_up(enable_incremental_mode=interpreter_uses_incremental)
        self.check_runner()
        self.running = True
        logger.log("Time till prompt: " + str(get_clock_time() - first_import_time) + " secs")

    def start_prompt(self):
        """Start the interpreter."""
        logger.show(
            "Coconut Interpreter v{co_ver} (Python {py_ver}):".format(
                co_ver=VERSION,
                py_ver=".".join(str(v) for v in sys.version_info[:2]),
            ),
        )
        logger.show("(enter 'exit()' or press Ctrl-D to end)")
        self.start_running()
        while self.running:
            try:
                code = self.get_input()
                if code:
                    compiled = self.handle_input(code)
                    if compiled:
                        self.execute(compiled, use_eval=None)
            except KeyboardInterrupt:
                logger.printerr("\nKeyboardInterrupt")

    def exit_runner(self, exit_code=0):
        """Exit the interpreter."""
        self.register_exit_code(exit_code)
        self.running = False

    def handle_input(self, code):
        """Compile Coconut interpreter input."""
        if not self.prompt.multiline:
            if not should_indent(code):
                try:
                    return self.parse_block(code)
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
            return self.parse_block(code)
        except CoconutException:
            logger.print_exc()
        return None

    def execute(self, compiled=None, path=None, use_eval=False, allow_show=True):
        """Execute compiled code."""
        self.check_runner()
        if compiled is not None:

            if allow_show and self.show:
                logger.print(compiled)

            if path is None:  # header is not included
                if not self.mypy:
                    no_str_code = self.comp.remove_strs(compiled)
                    result = mypy_builtin_regex.search(no_str_code)
                    if result:
                        logger.warn("found mypy-only built-in " + repr(result.group(0)) + "; pass --mypy to use mypy-only built-ins at the interpreter")

            else:  # header is included
                compiled = rem_encoding(compiled)

            self.runner.run(compiled, use_eval=use_eval, path=path, all_errors_exit=path is not None)

            self.run_mypy(code=self.runner.was_run_code())

    def execute_file(self, destpath, **kwargs):
        """Execute compiled file."""
        self.check_runner(**kwargs)
        self.runner.run_file(destpath)

    def check_runner(self, set_sys_vars=True, argv_source_path=""):
        """Make sure there is a runner."""
        if set_sys_vars:
            # set sys.path
            if os.getcwd() not in sys.path:
                sys.path.append(os.getcwd())

            # set sys.argv
            if self.argv_args is not None:
                sys.argv = [argv_source_path] + self.argv_args

        # set up runner
        if self.runner is None:
            self.runner = Runner(self.comp, exit=self.exit_runner, store=self.mypy)

        # pass runner to prompt
        self.prompt.set_runner(self.runner)

    @property
    def mypy(self):
        """Whether using MyPy or not."""
        return self.mypy_args is not None

    def set_mypy_args(self, mypy_args=None):
        """Set MyPy arguments."""
        if mypy_args is None:
            self.mypy_args = None

        elif mypy_install_arg in mypy_args:
            if mypy_args != [mypy_install_arg]:
                raise CoconutException("'--mypy install' cannot be used alongside other --mypy arguments")
            stub_dir = set_mypy_path()
            logger.show_sig("Successfully installed MyPy stubs into " + repr(stub_dir))
            self.mypy_args = None

        else:
            self.mypy_args = list(mypy_args)

            if not any(arg.startswith("--python-version") for arg in self.mypy_args):
                self.mypy_args += [
                    "--python-version",
                    ver_tuple_to_str(get_target_info_smart(self.comp.target, mode="highest")),
                ]

            if not any(arg.startswith("--python-executable") for arg in self.mypy_args):
                self.mypy_args += [
                    "--python-executable",
                    sys.executable,
                ]

            add_mypy_args = default_mypy_args + (verbose_mypy_args if logger.verbose else ())

            for arg in add_mypy_args:
                no_arg = invert_mypy_arg(arg)
                arg_prefixes = (arg,) + ((no_arg,) if no_arg is not None else ())
                if not any(arg.startswith(arg_prefixes) for arg in self.mypy_args):
                    self.mypy_args.append(arg)

            logger.log("MyPy args:", self.mypy_args)
            self.mypy_errs = []

    def run_mypy(self, paths=(), code=None):
        """Run MyPy with arguments."""
        if self.mypy:
            set_mypy_path()
            from coconut.command.mypy import mypy_run
            args = list(paths) + self.mypy_args
            if code is not None:  # interpreter
                args += ["-c", code]
            for line, is_err in mypy_run(args):
                line = line.rstrip()
                logger.log("[MyPy:{std}]".format(std="err" if is_err else "out"), line)
                if line.startswith(mypy_silent_err_prefixes):
                    if code is None:  # file
                        logger.printerr(line)
                        self.register_exit_code(errmsg="MyPy error")
                elif line.startswith(mypy_silent_non_err_prefixes):
                    if code is None:  # file
                        logger.print("MyPy", line)
                else:
                    if code is None:  # file
                        logger.printerr(line)
                        if any(infix in line for infix in mypy_err_infixes):
                            self.register_exit_code(errmsg="MyPy error")
                    if line not in self.mypy_errs:
                        if code is not None:  # interpreter
                            logger.printerr(line)
                        self.mypy_errs.append(line)

    def run_silent_cmd(self, *args):
        """Same as run_cmd$(show_output=logger.verbose)."""
        return run_cmd(*args, show_output=logger.verbose)

    def install_jupyter_kernel(self, jupyter, kernel_dir, install_args=[]):
        """Install the given kernel via the command line and return whether successful."""
        install_args = jupyter + ["kernelspec", "install", kernel_dir, "--replace"] + install_args
        try:
            self.run_silent_cmd(install_args)
        except CalledProcessError:
            user_install_args = install_args + ["--user"]
            try:
                self.run_silent_cmd(user_install_args)
            except CalledProcessError:
                logger.warn("kernel install failed on command", " ".join(install_args))
                self.register_exit_code(errmsg="Jupyter kernel error")
                return False
        return True

    def remove_jupyter_kernel(self, jupyter, kernel_name):
        """Remove the given kernel via the command line and return whether successful."""
        remove_args = jupyter + ["kernelspec", "remove", kernel_name, "-f"]
        try:
            self.run_silent_cmd(remove_args)
        except CalledProcessError:
            logger.warn("kernel removal failed on command", " ".join(remove_args))
            self.register_exit_code(errmsg="Jupyter kernel error")
            return False
        return True

    def install_default_jupyter_kernels(self, jupyter, kernel_list, install_args=[]):
        """Install icoconut default kernels."""
        logger.show_sig("Installing Jupyter kernels '" + "', '".join(icoconut_default_kernel_names) + "'...")
        overall_success = True

        for old_kernel_name in icoconut_old_kernel_names:
            if old_kernel_name in kernel_list:
                success = self.remove_jupyter_kernel(jupyter, old_kernel_name)
                overall_success = overall_success and success

        for kernel_dir in icoconut_default_kernel_dirs:
            success = self.install_jupyter_kernel(jupyter, kernel_dir, install_args)
            overall_success = overall_success and success

        if overall_success:
            return icoconut_default_kernel_names
        else:
            return []

    def get_jupyter_kernels(self, jupyter):
        """Get the currently installed Jupyter kernels."""
        raw_kernel_list = run_cmd(jupyter + ["kernelspec", "list"], show_output=False, raise_errs=False)

        kernel_list = []
        for line in raw_kernel_list.splitlines():
            kernel_list.append(line.split()[0])
        return kernel_list

    def get_jupyter_command(self):
        """Get the correct jupyter command."""
        for jupyter in (
            [sys.executable, "-m", "jupyter"],
            [sys.executable, "-m", "ipython"],
        ):
            if PY35:  # newer Python versions should only use "jupyter", not "ipython"
                break
            try:
                self.run_silent_cmd(jupyter + ["--help"])  # --help is much faster than --version
            except CalledProcessError:
                logger.warn("failed to find Jupyter command at " + repr(" ".join(jupyter)))
            else:
                break
        else:  # no break
            raise CoconutException("'coconut --jupyter' requires Jupyter (run 'pip install coconut[jupyter]' to fix)")
        return jupyter

    def start_jupyter(self, args):
        """Start Jupyter with the Coconut kernel."""
        jupyter = self.get_jupyter_command()

        # get a list of installed kernels
        kernel_list = self.get_jupyter_kernels(jupyter)
        newly_installed_kernels = []

        # determine if we're just installing
        if not args:
            just_install = True
        elif args[0].startswith("-"):
            just_install = True
        elif args[0] == jupyter_install_arg:
            just_install = True
            args = args[1:]
        else:
            just_install = False
        install_args = args if just_install else []

        # always update the custom kernel, but only reinstall it if it isn't already there or just installing
        custom_kernel_dir = install_custom_kernel(logger=logger)
        if custom_kernel_dir is not None and (icoconut_custom_kernel_name not in kernel_list or just_install):
            logger.show_sig("Installing Jupyter kernel {name!r}...".format(name=icoconut_custom_kernel_name))
            if self.install_jupyter_kernel(jupyter, custom_kernel_dir, install_args):
                newly_installed_kernels.append(icoconut_custom_kernel_name)

        if just_install:
            # install default kernels if just installing
            newly_installed_kernels += self.install_default_jupyter_kernels(jupyter, kernel_list)
            run_args = None

        else:
            # use the custom kernel if it exists
            if icoconut_custom_kernel_name in kernel_list or icoconut_custom_kernel_name in newly_installed_kernels:
                kernel = icoconut_custom_kernel_name

            # otherwise determine which default kernel to use and install them if necessary
            else:
                ver = "2" if PY2 else "3"
                try:
                    self.run_silent_cmd(["python" + ver, "-m", "coconut.main", "--version"])
                except CalledProcessError:
                    kernel = "coconut_py"
                else:
                    kernel = "coconut_py" + ver
                if kernel not in kernel_list:
                    newly_installed_kernels += self.install_default_jupyter_kernels(jupyter, kernel_list, install_args)
                logger.warn("could not find {name!r} kernel; using {kernel!r} kernel instead".format(name=icoconut_custom_kernel_name, kernel=kernel))

            # pass the kernel to the console or otherwise just launch Jupyter now that we know our kernel is available
            if args[0] in jupyter_console_commands:
                if any(a.startswith("--kernel") for a in args):
                    logger.warn("unable to specify Coconut kernel in 'jupyter " + args[0] + "' command as --kernel was already specified in the given arguments")
                else:
                    args += ["--kernel", kernel]
            run_args = jupyter + args

        if newly_installed_kernels:
            logger.show_sig("Successfully installed Jupyter kernels: '" + "', '".join(newly_installed_kernels) + "'")

        # run the Jupyter command
        if run_args is not None:
            self.register_exit_code(run_cmd(run_args, raise_errs=False), errmsg="Jupyter error")

    def watch(self, src_dest_package_triples, run=False, force=False):
        """Watch a source and recompile on change."""
        from coconut.command.watch import Observer, RecompilationWatcher

        for src, _, _ in src_dest_package_triples:
            logger.show()
            logger.show_tabulated("Watching", showpath(src), "(press Ctrl-C to end)...")

        def recompile(path, src, dest, package):
            path = fixpath(path)
            if os.path.isfile(path) and os.path.splitext(path)[1] in code_exts:
                with self.handling_exceptions():
                    if dest is True or dest is None:
                        writedir = dest
                    else:
                        # correct the compilation path based on the relative position of path to src
                        dirpath = os.path.dirname(path)
                        writedir = os.path.join(dest, os.path.relpath(dirpath, src))
                    filepaths = self.compile_path(path, writedir, package, run=run, force=force, show_unchanged=False)
                    self.run_mypy(filepaths)

        observer = Observer()
        watchers = []
        for src, dest, package in src_dest_package_triples:
            watcher = RecompilationWatcher(recompile, src, dest, package)
            observer.schedule(watcher, src, recursive=True)
            watchers.append(watcher)

        with self.running_jobs():
            observer.start()
            try:
                while True:
                    time.sleep(watch_interval)
                    for wcher in watchers:
                        wcher.keep_watching()
            except KeyboardInterrupt:
                logger.show_sig("Got KeyboardInterrupt; stopping watcher.")
            finally:
                observer.stop()
                observer.join()

    def get_python_lib(self):
        """Get current Python lib location."""
        # these are expensive, so should only be imported here
        if PY32:
            from sysconfig import get_path
            python_lib = get_path("purelib")
        else:
            from distutils import sysconfig
            python_lib = sysconfig.get_python_lib()
        return fixpath(python_lib)

    def site_install(self):
        """Add Coconut's pth file to site-packages."""
        python_lib = self.get_python_lib()

        shutil.copy(coconut_pth_file, python_lib)
        logger.show_sig("Added %s to %s" % (os.path.basename(coconut_pth_file), python_lib))

    def site_uninstall(self):
        """Remove Coconut's pth file from site-packages."""
        python_lib = self.get_python_lib()
        pth_file = os.path.join(python_lib, os.path.basename(coconut_pth_file))

        if os.path.isfile(pth_file):
            os.remove(pth_file)
            logger.show_sig("Removed %s from %s" % (os.path.basename(coconut_pth_file), python_lib))
        else:
            raise CoconutException("failed to find %s file to remove" % (os.path.basename(coconut_pth_file),))
