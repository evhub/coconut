#!/usr/bin/env python

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

from .root import *
from .command import CoconutException, cli

#-----------------------------------------------------------------------------------------------------------------------
# COMPILING:
#-----------------------------------------------------------------------------------------------------------------------

CLI = cli()

def cmd(args, interact=False):
    """Processes command-line arguments."""
    if isinstance(args, (str, bytes)):
        args = args.split()
    return CLI.cmd(CLI.commandline.parse_args(args), interact)

def version(which="num"):
    """Gets the Coconut version."""
    if which == "num":
        return VERSION
    elif which == "name":
        return VERSION_NAME
    elif which == "spec":
        return VERSION_STR
    elif which == "-v":
        return CLI.version
    else:
        raise CoconutException("invalid version type " + ascii(which)
                               + "; valid versions are 'num', 'name', 'spec', and '-v'")

#-----------------------------------------------------------------------------------------------------------------------
# PARSING:
#-----------------------------------------------------------------------------------------------------------------------

def setup(target=None, strict=False, minify=False, quiet=False):
    """Gets CLI.proc."""
    CLI.setup(target, strict, minify)
    CLI.quiet(quiet)

def parse(code, mode="exec"):
    """Parses Coconut code."""
    if CLI.proc is None:
        setup()
    if mode == "single":
        return CLI.proc.parse_single(code)
    elif mode == "file":
        return CLI.proc.parse_file(code)
    elif mode == "exec":
        return CLI.proc.parse_exec(code)
    elif mode == "module":
        return CLI.proc.parse_module(code)
    elif mode == "block":
        return CLI.proc.parse_block(code)
    elif mode == "eval":
        return CLI.proc.parse_eval(code)
    elif mode == "debug":
        return CLI.proc.parse_debug(code)
    else:
        raise CoconutException("invalid parse mode " + ascii(mode)
            + "; valid modes are 'exec', 'file', 'single', 'module', 'block', 'eval', and 'debug'")
