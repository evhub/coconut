#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Convenience functions for using Coconut as a module.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from coconut.exceptions import CoconutException
from coconut.command import Command
from coconut.constants import version_tag, version_long

#-----------------------------------------------------------------------------------------------------------------------
# COMMAND:
#-----------------------------------------------------------------------------------------------------------------------

CLI = Command()


def cmd(args, interact=False):
    """Processes command-line arguments."""
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
    """Gets the Coconut version."""
    if which in VERSIONS:
        return VERSIONS[which]
    else:
        raise CoconutException("invalid version type " + ascii(which),
                               extra="valid versions are " + ", ".join(VERSIONS))


#-----------------------------------------------------------------------------------------------------------------------
# COMPILER:
#-----------------------------------------------------------------------------------------------------------------------

setup = CLI.setup


PARSERS = {
    "single": lambda comp: comp.parse_single,
    "file": lambda comp: comp.parse_file,
    "exec": lambda comp: comp.parse_exec,
    "package": lambda comp: comp.parse_package,
    "block": lambda comp: comp.parse_block,
    "sys": lambda comp: comp.parse_sys,
    "eval": lambda comp: comp.parse_eval,
    "debug": lambda comp: comp.parse_debug,
}


def parse(code, mode="sys"):
    """Parses Coconut code."""
    if CLI.comp is None:
        setup()
    if mode in PARSERS:
        return PARSERS[mode](CLI.comp)(code)
    else:
        raise CoconutException("invalid parse mode " + ascii(mode),
                               extra="valid modes are " + ", ".join(PARSERS))
