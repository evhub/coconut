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
from .parser import CoconutException
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

def setup(target=None, strict=False, quiet=False):
    """Gets COMPILER.processor."""
    COMPILER.setup(strict, target)
    COMPILER.quiet(quiet)

def parse(code, mode="exec"):
    """Parses Coconut code."""
    if COMPILER.processor is None:
        setup()
    if mode == "single":
        return COMPILER.processor.parse_single(code)
    elif mode == "file":
        return COMPILER.processor.parse_file(code)
    elif mode == "exec":
        return COMPILER.processor.parse_exec(code)
    elif mode == "module":
        return COMPILER.processor.parse_module(code)
    elif mode == "block":
        return COMPILER.processor.parse_block(code)
    elif mode == "eval":
        return COMPILER.processor.parse_eval(code)
    elif mode == "debug":
        return COMPILER.processor.parse_debug(code)
    else:
        raise CoconutException("invalid parse mode " + ascii(mode)
            + "; valid modes are 'exec', 'file', 'single', 'module', 'block', 'eval', and 'debug'")
