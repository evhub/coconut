#!/usr/bin/env python

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
Date Created: 2014
Description: Coconut Convenience Functions.
"""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from .util import *
from .parser import processor, CoconutException
from .compiler import cli

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PARSING:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

PARSER = processor()

def parse(code, mode="file"):
    """Parses Coconut Code."""
    setup_parser()
    if mode == "single":
        return PARSER.parse_single(code)
    elif mode == "file":
        return PARSER.parse_file(code)
    elif mode == "module":
        return PARSER.parse_module(code)
    elif mode == "block":
        return PARSER.parse_block(code)
    elif mode == "eval":
        return PARSER.parse_eval(code)
    elif mode == "debug":
        return PARSER.parse_debug(code)
    else:
        raise CoconutException("invalid parse mode "+repr(mode)+"; valid modes are 'single', 'file', 'module', 'block', 'eval', and 'debug'")

autopep8 = processor.autopep8

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# COMPILING:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

COMPILER = cli()

def cmd(args):
    """Processes Command-Line Arguments."""
    setup_compiler()
    return COMPILER.cmd(COMPILER.commandline.parse_args(args))

def version(which="num"):
    """Gets The Coconut Version."""
    if which == "num":
        return VERSION
    elif which == "name":
        return VERSION_NAME
    elif which == "full":
        return VERSION_STR
    elif which == "-v":
        setup_compiler()
        return COMPILER.version
    else:
        raise CoconutException("invalid version type "+repr(which)+"; valid versions are 'num', 'name', 'full', and '-v'")
