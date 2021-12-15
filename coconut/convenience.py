#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Convenience functions for using Coconut as a module.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os.path
import codecs
import encodings

from coconut import embed
from coconut.exceptions import CoconutException
from coconut.command import Command
from coconut.command.cli import cli_version
from coconut.compiler import Compiler
from coconut.constants import (
    version_tag,
    code_exts,
    coconut_import_hook_args,
    coconut_kernel_kwargs,
)

# -----------------------------------------------------------------------------------------------------------------------
# COMMAND:
# -----------------------------------------------------------------------------------------------------------------------

CLI = Command()


def cmd(args, interact=False):
    """Process command-line arguments."""
    if isinstance(args, (str, bytes)):
        args = args.split()
    return CLI.cmd(args=args, interact=interact)


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

setup = CLI.setup


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


def parse(code="", mode="sys"):
    """Compile Coconut code."""
    if CLI.comp is None:
        setup()
    if mode not in PARSERS:
        raise CoconutException(
            "invalid parse mode " + repr(mode),
            extra="valid modes are " + ", ".join(PARSERS),
        )
    return PARSERS[mode](CLI.comp)(code)


def coconut_eval(expression, globals=None, locals=None):
    """Compile and evaluate Coconut code."""
    if CLI.comp is None:
        setup()
    CLI.check_runner(set_sys_vars=False)
    if globals is None:
        globals = {}
    CLI.runner.update_vars(globals)
    return eval(parse(expression, "eval"), globals, locals)


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

    @staticmethod
    def run_compiler(path):
        """Run the Coconut compiler on the given path."""
        cmd([path] + list(coconut_import_hook_args))

    def find_module(self, fullname, path=None):
        """Searches for a Coconut file of the given name and compiles it."""
        basepaths = [""] + list(sys.path)
        if fullname.startswith("."):
            if path is None:
                # we can't do a relative import if there's no package path
                return
            fullname = fullname[1:]
            basepaths.insert(0, path)
        fullpath = os.path.join(*fullname.split("."))
        for head in basepaths:
            path = os.path.join(head, fullpath)
            filepath = path + self.ext
            dirpath = os.path.join(path, "__init__" + self.ext)
            if os.path.exists(filepath):
                self.run_compiler(filepath)
                # Coconut file was found and compiled, now let Python import it
                return
            if os.path.exists(dirpath):
                self.run_compiler(path)
                # Coconut package was found and compiled, now let Python import it
                return


coconut_importer = CoconutImporter()


def auto_compilation(on=True):
    """Turn automatic compilation of Coconut files on or off."""
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


class CoconutStreamReader(encodings.utf_8.StreamReader, object):
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


class CoconutIncrementalDecoder(encodings.utf_8.IncrementalDecoder, object):
    """Compile Coconut at the end of incrementally decoding UTF-8."""
    invertible = False
    _buffer_decode = CoconutStreamReader.decode


def get_coconut_encoding(encoding="coconut"):
    """Get a CodecInfo for the given Coconut encoding."""
    if not encoding.startswith("coconut"):
        return None
    if encoding != "coconut":
        raise CoconutException("unknown Coconut encoding: " + repr(encoding))
    return codecs.CodecInfo(
        name=encoding,
        encode=encodings.utf_8.encode,
        decode=CoconutStreamReader.decode,
        incrementalencoder=encodings.utf_8.IncrementalEncoder,
        incrementaldecoder=CoconutIncrementalDecoder,
        streamreader=CoconutStreamReader,
        streamwriter=encodings.utf_8.StreamWriter,
    )


codecs.register(get_coconut_encoding)
