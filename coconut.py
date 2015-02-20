#!/usr/bin/env python

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
Date Created: 2014
Description: The Coconut Compiler.
"""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from milk.root import *
import milk
import argparse

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def compile_file(codefilename, destfilename):
    """Compiles A Source Coconut File To A Destination Python File."""
    writefile(openfile(destfilename, "w"), milk.parser.parse_file(readfile(openfile(codefilename, "r"))))

def compile_cmd(filename):
    """Compiles A Coconut File Using The Command Line Argument."""
    basename, extension = os.path.splitext(filename)
    codefilename = basename + extension
    destfilename = basename + ".py"
    compile_file(codefilename, destfilename)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

commandline = argparse.ArgumentParser(description="The Coconut Compiler.")
commandline.add_argument("filename", metavar="file", type=str, nargs=1, help="The name of the file to compile.")

if __name__ == "__main__":
    args = commandline.parse_args()
    print("[Coconut] Compiling '"+codefilename+"'...")
    compile_cmd(args.filename[0])
    print("[Coconut] Compiled '"+destfilename+"'.")

