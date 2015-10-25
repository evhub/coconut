#!/usr/bin/env python2

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: The Python 3 exec function in Python 2.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from .root import *
import os
import os.path
import tempfile

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTION:
#-----------------------------------------------------------------------------------------------------------------------

def execfunc(code, gvars, lvars):
    """Wraps exec."""
    exec code in gvars, lvars

def execheader(code, gvars, lvars):
    """Special header executor."""
    basefilename = os.path.join(tempfile.gettempdir(), "_coconut_temp")
    i = 0
    filename = basefilename
    while os.path.isfile(filename):
        filename = basefilename + "_" + i
        i += 1
    try:
        with openfile(filename) as codefile:
            writefile(codefile, code)
            execfile(filename, gvars, lvars)
    finally:
        os.remove(filename)
