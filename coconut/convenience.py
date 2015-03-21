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
        raise CoconutException("invalid mode "+repr(mode)+"; valid modes are 'single', 'file', 'module', 'block', 'eval', and 'debug'")

autopep8 = PARSER.autopep8

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# COMPILING:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

COMPILER = cli()

def cmd(args):
    """Processes Command-Line Arguments."""
    return COMPILER.cmd(COMPILER.commandline.parse_args(args))

version = COMPILER.version()
