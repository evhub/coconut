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
from coconut.constants import version_tag, version_long, main_sig

#-----------------------------------------------------------------------------------------------------------------------
# COMMAND:
#-----------------------------------------------------------------------------------------------------------------------

CLI = Command()


def cmd(args, interact=False):
    """Processes command-line arguments."""
    if isinstance(args, (str, bytes)):
        args = args.split()
    return CLI.cmd(args=args, interact=interact)


def version(which="num"):
    """Gets the Coconut version."""
    if which == "num":
        return VERSION
    elif which == "name":
        return VERSION_NAME
    elif which == "spec":
        return VERSION_STR
    elif which == "tag":
        return version_tag
    elif which == "-v":
        return main_sig + version_long
    else:
        raise CoconutException("invalid version type " + ascii(which)
                               + "; valid versions are 'num', 'name', 'spec', 'tag', and '-v'")

#-----------------------------------------------------------------------------------------------------------------------
# COMPILER:
#-----------------------------------------------------------------------------------------------------------------------

setup = CLI.setup


def parse(code, mode="exec"):
    """Parses Coconut code."""
    if CLI.comp is None:
        setup()
    if mode == "single":
        return CLI.comp.parse_single(code)
    elif mode == "file":
        return CLI.comp.parse_file(code)
    elif mode == "exec":
        return CLI.comp.parse_exec(code)
    elif mode == "module":
        return CLI.comp.parse_module(code)
    elif mode == "block":
        return CLI.comp.parse_block(code)
    elif mode == "eval":
        return CLI.comp.parse_eval(code)
    elif mode == "debug":
        return CLI.comp.parse_debug(code)
    else:
        raise CoconutException("invalid parse mode " + ascii(mode)
                               + "; valid modes are 'exec', 'file', 'single', 'module', 'block', 'eval', and 'debug'")
