#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Coconut convenience functions.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from .root import *
from .parser import processor, CoconutException
from .compiler import cli

#-----------------------------------------------------------------------------------------------------------------------
# COMPILING:
#-----------------------------------------------------------------------------------------------------------------------

COMPILER = cli()

def cmd(args, interact=False):
    """Processes command-line arguments."""
    if isinstance(args, (str, bytes)):
        args = args.split()
    return COMPILER.cmd(COMPILER.commandline.parse_args(args), interact)

def version(which="num"):
    """Gets the Coconut version."""
    if which == "num":
        return VERSION
    elif which == "name":
        return VERSION_NAME
    elif which == "spec":
        return VERSION_STR
    elif which == "-v":
        return COMPILER.version
    else:
        raise CoconutException("invalid version type "+ascii(which)+"; valid versions are 'num', 'name', 'spec', and '-v'")

#-----------------------------------------------------------------------------------------------------------------------
# PARSING:
#-----------------------------------------------------------------------------------------------------------------------

def setup(strict=False, target=None):
    """Gets COMPILER.processor."""
    if COMPILER.processor is None:
        COMPILER.setup(strict, target)
    return COMPILER.processor

def parse(code, mode="exec"):
    """Parses Coconut code."""
    PARSER = setup()
    if mode == "single":
        return PARSER.parse_single(code)
    elif mode == "file":
        return PARSER.parse_file(code)
    elif mode == "exec":
        return PARSER.parse_exec(code)
    elif mode == "module":
        return PARSER.parse_module(code)
    elif mode == "block":
        return PARSER.parse_block(code)
    elif mode == "eval":
        return PARSER.parse_eval(code)
    elif mode == "debug":
        return PARSER.parse_debug(code)
    else:
        raise CoconutException("invalid parse mode " + ascii(mode)
            + "; valid modes are 'exec', 'file', 'single', 'module', 'block', 'eval', and 'debug'")
