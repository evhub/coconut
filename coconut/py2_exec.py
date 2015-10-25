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

from tempfile import NamedTemporaryFile

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTION:
#-----------------------------------------------------------------------------------------------------------------------

def execfunc(code, gvars=None, lvars=None):
    codefile = NamedTemporaryFile()
    codefile.write(code)
    codefilename = codefile.name
    codefile.close()
    return execfile(codefilename, gvars, lvars)
