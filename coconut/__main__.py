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

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coconut.root import *
from coconut.command import cli

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

def main():
    """Runs the Coconut CLI."""
    from os import name
    if name == "nt":
        cmd = cli() # don't use unix color codes on windows
    else:
        cmd = cli(main_color="cyan", debug_color="yellow")
    cmd.start()

if __name__ == "__main__":
    main()
