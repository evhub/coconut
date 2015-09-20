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

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from .root import *

#-----------------------------------------------------------------------------------------------------------------------
# IPYTHON:
#-----------------------------------------------------------------------------------------------------------------------

def load_ipython_extension(ipython):
    """Loads Coconut as an IPython extension."""
    from .convenience import cmd, parse
    def magic(line, cell=None):
        """Coconut IPython magic."""
        if cell is None:
            code = line
        else:
            cmd(line)
            code = cell
        compiled = parse(code)
        ipython.run_cell(compiled, shell_futures=False)
    ipython.register_magic_function(magic, "line_cell", "coconut")
