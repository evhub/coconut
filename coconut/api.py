#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Coconut's main external API.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os.path
import codecs
from functools import partial
try:
    from encodings import utf_8
except ImportError:
    utf_8 = None

from coconut.root import _coconut_exec
from coconut.integrations import embed
from coconut.exceptions import CoconutException
from coconut.command import Command
from coconut.command.cli import cli_version
from coconut.command.util import proc_run_args
from coconut.compiler import Compiler
from coconut.constants import (
    PY34,
    version_tag,
    code_exts,
    coconut_kernel_kwargs,
    default_use_cache_dir,
    coconut_cache_dir,
    coconut_run_kwargs,
)

# -----------------------------------------------------------------------------------------------------------------------
# COMMAND:
# -----------------------------------------------------------------------------------------------------------------------

GLOBAL_STATE = None


def get_state(state=None):
    """Get a Coconut state object; None gets a new state, False gets the global state."""
    global GLOBAL_STATE
    if state is None:
        return Command()
    elif state is False:
        if GLOBAL_STATE is None:
            GLOBAL_STATE = Command()
        return GLOBAL_STATE
    else:
        return state


def cmd(cmd_args, **kwargs):
    """Process command-line arguments."""
    state = kwargs.pop("state", False)
    if isinstance(cmd_args, (str, bytes)):
        cmd_args = cmd_args.split()
    return get_state(state).cmd(cmd_args, **kwargs)


VERSIONS = {
    "num": VERSION,
    "name": VERSION_NAME,
    "spec": VERSION_STR,
    "tag": version_tag,
    "-v": cli_version,
}


def version(which="num"):
    """Get the Coconut version."""
    if which in VERSIONS:
        return VERSIONS[which]
    else:
        raise CoconutException(
            "invalid version type " + repr(which),
            extra="valid versions are " + ", ".join(VERSIONS),
        )


# -----------------------------------------------------------------------------------------------------------------------
# COMPILER:
# -----------------------------------------------------------------------------------------------------------------------

def setup(*args, **kwargs):
    """Set up the given state object."""
    state = kwargs.pop("state", False)
    return get_state(state).setup(*args, **kwargs)


def warm_up(*args, **kwargs):
    """Warm up the given state object."""
    state = kwargs.pop("state", False)
    return get_state(state).comp.warm_up(*args, **kwargs)


PARSERS = {
    "sys": lambda comp: comp.parse_sys,
    "exec": lambda comp: comp.parse_exec,
    "file": lambda comp: comp.parse_file,
    "package": lambda comp: comp.parse_package,
    "block": lambda comp: comp.parse_block,
    "single": lambda comp: comp.parse_single,
    "eval": lambda comp: comp.parse_eval,
    "lenient": lambda comp: comp.parse_lenient,
    "xonsh": lambda comp: comp.parse_xonsh,
}

# deprecated aliases
PARSERS["any"] = PARSERS["debug"] = PARSERS["lenient"]


def parse(code="", mode="sys", state=False, keep_internal_state=None):
    """Compile Coconut code."""
    if keep_internal_state is None:
        keep_internal_state = bool(state)
    command = get_state(state)
    if command.comp is None:
        command.setup()
    if mode not in PARSERS:
        raise CoconutException(
            "invalid parse mode " + repr(mode),
            extra="valid modes are " + ", ".join(PARSERS),
        )
    return PARSERS[mode](command.comp)(code, keep_state=keep_internal_state)


def coconut_base_exec(exec_func, mode, expression, globals=None, locals=None, state=False, **kwargs):
    """Compile and evaluate Coconut code."""
    command = get_state(state)
    if command.comp is None:
        setup()
    command.check_runner(set_sys_vars=False)
    if globals is None:
        globals = {}
    command.runner.update_vars(globals)
    compiled_python = parse(expression, mode, state, **kwargs)
    return exec_func(compiled_python, globals, locals)


coconut_exec = partial(coconut_base_exec, _coconut_exec, "sys")
coconut_eval = partial(coconut_base_exec, eval, "eval")


# -----------------------------------------------------------------------------------------------------------------------
# BREAKPOINT:
# -----------------------------------------------------------------------------------------------------------------------


def _coconut_breakpoint():
    """Determine coconut.embed depth based on whether we're being
    called by Coconut's breakpoint() or Python's breakpoint()."""
    if sys.version_info >= (3, 7):
        return embed(depth=1)
    else:
        return embed(depth=2)


def use_coconut_breakpoint(on=True):
    """Switches the breakpoint() built-in (universally accessible via
    coconut.__coconut__.breakpoint) to use coconut.embed."""
    if on:
        sys.breakpointhook = _coconut_breakpoint
    else:
        sys.breakpointhook = sys.__breakpointhook__


use_coconut_breakpoint()


# -----------------------------------------------------------------------------------------------------------------------
# AUTOMATIC COMPILATION:
# -----------------------------------------------------------------------------------------------------------------------


class CoconutImporter(object):
    """Finder and loader for compiling Coconut files at import time."""
    ext = code_exts[0]
    command = None

    def __init__(self, *args):
        self.use_cache_dir(default_use_cache_dir)
        self.set_args(args)

    def use_cache_dir(self, use_cache_dir):
        """Set the cache directory if any to use for compiled Coconut files."""
        if use_cache_dir:
            if not PY34:
                raise CoconutException("coconut.api.auto_compilation only supports the usage of a cache directory on Python 3.4+")
            self.cache_dir = coconut_cache_dir
        else:
            self.cache_dir = None

    def set_args(self, args):
        """Set the Coconut command line args to use for auto compilation."""
        self.args = proc_run_args(args)

    def cmd(self, *args):
        """Run the Coconut compiler with the given args."""
        if self.command is None:
            self.command = Command()
        return self.command.cmd(list(args) + self.args, interact=False, **coconut_run_kwargs)

    def compile(self, path, package):
        """Compile a path to a file or package."""
        extra_args = []
        if self.cache_dir:
            if package:
                cache_dir = os.path.join(path, self.cache_dir)
            else:
                cache_dir = os.path.join(os.path.dirname(path), self.cache_dir)
            extra_args.append(cache_dir)
        else:
            cache_dir = None

        if package:
            self.cmd(path, *extra_args)
            return cache_dir or path
        else:
            destpath, = self.cmd(path, *extra_args)
            return destpath

    def find_coconut(self, fullname, path=None):
        """Searches for a Coconut file of the given name and compiles it."""
        basepaths = list(sys.path) + [""]
        if fullname.startswith("."):
            if path is None:
                # we can't do a relative import if there's no package path
                return None
            fullname = fullname[1:]
            basepaths.insert(0, path)

        path_tail = os.path.join(*fullname.split("."))
        for path_head in basepaths:
            path = os.path.join(path_head, path_tail)
            filepath = path + self.ext
            initpath = os.path.join(path, "__init__" + self.ext)
            if os.path.exists(filepath):
                return self.compile(filepath, package=False)
            if os.path.exists(initpath):
                return self.compile(path, package=True)
        return None

    def find_module(self, fullname, path=None):
        """Get a loader for a Coconut module if it exists."""
        destpath = self.find_coconut(fullname, path)
        # return None to let Python do the import when nothing was found or compiling in-place
        if destpath is None or not self.cache_dir:
            return None
        else:
            from importlib.machinery import SourceFileLoader
            return SourceFileLoader(fullname, destpath)

    def find_spec(self, fullname, path=None, target=None):
        """Get a modulespec for a Coconut module if it exists."""
        loader = self.find_module(fullname, path)
        if loader is None:
            return None
        else:
            from importlib.util import spec_from_loader
            return spec_from_loader(fullname, loader)


coconut_importer = CoconutImporter()


def auto_compilation(on=True, args=None, use_cache_dir=None):
    """Turn automatic compilation of Coconut files on or off."""
    if args is not None:
        coconut_importer.set_args(args)
    if use_cache_dir is not None:
        coconut_importer.use_cache_dir(use_cache_dir)
    if on:
        if coconut_importer not in sys.meta_path:
            sys.meta_path.insert(0, coconut_importer)
    else:
        try:
            sys.meta_path.remove(coconut_importer)
        except ValueError:
            pass


auto_compilation()


# -----------------------------------------------------------------------------------------------------------------------
# ENCODING:
# -----------------------------------------------------------------------------------------------------------------------


if utf_8 is not None:
    class CoconutStreamReader(utf_8.StreamReader, object):
        """Compile Coconut code from a stream of UTF-8."""
        coconut_compiler = None

        @classmethod
        def compile_coconut(cls, source):
            """Compile the given Coconut source text."""
            if cls.coconut_compiler is None:
                cls.coconut_compiler = Compiler(**coconut_kernel_kwargs)
            return cls.coconut_compiler.parse_sys(source)

        @classmethod
        def decode(cls, input_bytes, errors="strict"):
            """Decode and compile the given Coconut source bytes."""
            input_str, len_consumed = super(CoconutStreamReader, cls).decode(input_bytes, errors)
            return cls.compile_coconut(input_str), len_consumed

    class CoconutIncrementalDecoder(utf_8.IncrementalDecoder, object):
        """Compile Coconut at the end of incrementally decoding UTF-8."""
        invertible = False
        _buffer_decode = CoconutStreamReader.decode


def get_coconut_encoding(encoding="coconut"):
    """Get a CodecInfo for the given Coconut encoding."""
    if not encoding.startswith("coconut"):
        return None
    if encoding != "coconut":
        raise CoconutException("unknown Coconut encoding: " + repr(encoding))
    if utf_8 is None:
        raise CoconutException("coconut encoding requires encodings.utf_8")
    return codecs.CodecInfo(
        name=encoding,
        encode=utf_8.encode,
        decode=CoconutStreamReader.decode,
        incrementalencoder=utf_8.IncrementalEncoder,
        incrementaldecoder=CoconutIncrementalDecoder,
        streamreader=CoconutStreamReader,
        streamwriter=utf_8.StreamWriter,
    )


codecs.register(get_coconut_encoding)
