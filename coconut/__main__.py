#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Starts the Coconut command line utility.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coconut.root import *
from coconut import compiler

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

def main():
    """Runs the Coconut CLI."""
    from os import name
    if name == "nt":
        cmd = compiler.cli()
    else:
        cmd = compiler.cli(main_color="cyan", debug_color="yellow")
    cmd.start()

if __name__ == "__main__":
    main()
