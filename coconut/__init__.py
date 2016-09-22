#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: The Coconut Programming Language.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

#-----------------------------------------------------------------------------------------------------------------------
# IPYTHON:
#-----------------------------------------------------------------------------------------------------------------------


def load_ipython_extension(ipython):
    """Loads Coconut as an IPython extension."""
    from coconut.convenience import cmd, parse, CoconutException
    from coconut.logging import logger

    def magic(line, cell=None):
        """Coconut IPython magic."""
        try:
            if cell is None:
                code = line
            else:
                cmd(line)  # first line in block is cmd
                code = cell
            compiled = parse(code)
        except CoconutException:
            logger.print_exc()
        else:
            ipython.run_cell(compiled, shell_futures=False)
    ipython.register_magic_function(magic, "line_cell", "coconut")
