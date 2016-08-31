#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger
License: Apache 2.0
Description: Defines arguments for the Coconut CLI.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

import sys
import argparse

from coconut.constants import documentation_url

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

arguments = argparse.ArgumentParser(
    prog="coconut",
    description=documentation_url)

arguments.add_argument(
    "source",
    metavar="source",
    type=str,
    nargs="?",
    default=None,
    help="path to the Coconut file/folder to compile")

arguments.add_argument(
    "dest",
    metavar="dest",
    type=str,
    nargs="?",
    default=None,
    help="destination directory for compiled files (defaults to the source directory)")

arguments.add_argument(
    "-v", "--version",
    action="store_const",
    const=True,
    default=False,
    help="print Coconut and Python version information")

arguments.add_argument(
    "-t", "--target",
    metavar="version",
    type=str,
    nargs=1,
    default=[None],
    help="specify target Python version (defaults to universal)")

arguments.add_argument(
    "-s", "--strict",
    action="store_const",
    const=True,
    default=False,
    help="enforce code cleanliness standards")

arguments.add_argument(
    "-l", "--line-numbers", "--linenumbers",
    action="store_const",
    const=True,
    default=False,
    help="add line number comments for ease of debugging")

arguments.add_argument(
    "-k", "--keep-lines", "--keeplines",
    action="store_const",
    const=True,
    default=False,
    help="include source code in comments for ease of debugging")

arguments.add_argument(
    "-p", "--package",
    action="store_const",
    const=True,
    default=False,
    help="compile source as part of a package (defaults to only if source is a directory)")

arguments.add_argument(
    "-a", "--standalone",
    action="store_const",
    const=True,
    default=False,
    help="compile source as standalone files (defaults to only if source is a single file)")

arguments.add_argument(
    "-w", "--watch",
    action="store_const",
    const=True,
    default=False,
    help="watch a directory and recompile on changes (requires watchdog)")

arguments.add_argument(
    "-d", "--display",
    action="store_const",
    const=True,
    default=False,
    help="print compiled Python")

arguments.add_argument(
    "-r", "--run",
    action="store_const",
    const=True,
    default=False,
    help="run compiled Python (often used with --nowrite)")

arguments.add_argument(
    "-n", "--nowrite",
    action="store_const",
    const=True,
    default=False,
    help="disable writing compiled Python")

arguments.add_argument(
    "-m", "--minify",
    action="store_const",
    const=True,
    default=False,
    help="compress compiled Python")

arguments.add_argument(
    "-i", "--interact",
    action="store_const",
    const=True,
    default=False,
    help="force the interpreter to start (otherwise starts if no other command is given)")

arguments.add_argument(
    "-q", "--quiet",
    action="store_const",
    const=True,
    default=False,
    help="suppress all informational output (combine with --display to write runnable code to stdout)")

arguments.add_argument(
    "-f", "--force",
    action="store_const",
    const=True,
    default=False,
    help="force overwriting of compiled Python (otherwise only overwrites when source code or compilation parameters change)")

arguments.add_argument(
    "-c", "--code",
    metavar="code",
    type=str,
    nargs=1,
    default=None,
    help="run a line of Coconut passed in as a string (can also be passed into stdin)")

arguments.add_argument(
    "-j", "--jobs",
    metavar="processes",
    type=int,
    nargs=1,
    default=[None],
    help="number of additional processes to use (set to 0 to use a single process) (defaults to the number of processors on your machine)")

arguments.add_argument(
    "--jupyter", "--ipython",
    type=str,
    nargs=argparse.REMAINDER,
    default=None,
    help="run Jupyter/IPython with Coconut as the kernel (remaining args passed to Jupyter)")

arguments.add_argument(
    "--recursion-limit", "--recursionlimit",
    metavar="limit",
    type=int,
    nargs=1,
    default=[None],
    help="set maximum recursion depth (defaults to "+str(sys.getrecursionlimit())+")")

arguments.add_argument(
    "--tutorial",
    action="store_const",
    const=True,
    default=False,
    help="open the Coconut tutorial in the default web browser")

arguments.add_argument(
    "--documentation",
    action="store_const",
    const=True,
    default=False,
    help="open the Coconut documentation in the default web browser")

arguments.add_argument(
    "--color",
    metavar="color",
    type=str,
    nargs=1,
    default=[None],
    help="show all Coconut messages in the given color")

arguments.add_argument(
    "--verbose",
    action="store_const",
    const=True,
    default=False,
    help="print verbose debug output")
