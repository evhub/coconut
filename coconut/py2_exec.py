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

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTION:
#-----------------------------------------------------------------------------------------------------------------------

def execfunc(object, globals=None, locals=None):
    if globals is None and locals is None:
        exec object
    elif locals is None:
        exec object in globals
    elif globals is None:
        exec object in locals
    else:
        exec object in globals, locals
