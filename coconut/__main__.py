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
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

from os import name as os_name

use_color = True
main_color = "cyan"
debug_color = "yellow"

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------

def main(color=use_color):
    """Runs the Coconut CLI."""
    if not color or os_name == "nt": # don't use unix color codes on windows
        cmd = cli()
    else:
        cmd = cli(main_color=main_color, debug_color=debug_color)
    cmd.start()

if __name__ == "__main__":
    main()
