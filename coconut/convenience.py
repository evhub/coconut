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

from coconut.exceptions import CoconutException
from coconut.command import Command
from coconut.constants import (
    version_tag,
    version_long,
    code_exts,
    coconut_import_hook_args,
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
    "-v": version_long,
}


def version(which="num"):
    """Get the Coconut version."""
    if which in VERSIONS:
        return VERSIONS[which]
    else:
        raise CoconutException(
            "invalid version type " + ascii(which),
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
    "any": lambda comp: comp.parse_any,
}


def parse(code="", mode="sys"):
    """Compile Coconut code."""
    if CLI.comp is None:
        setup()
    if mode in PARSERS:
        return PARSERS[mode](CLI.comp)(code)
    else:
        raise CoconutException(
            "invalid parse mode " + ascii(mode),
            extra="valid modes are " + ", ".join(PARSERS),
        )


# -----------------------------------------------------------------------------------------------------------------------
# IMPORTER:
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
