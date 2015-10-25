#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: The Coconut root.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

try:
    import readline
except ImportError:
    pass

import sys

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

VERSION = "0.3.2-dev"
VERSION_NAME = "Jawz"

VERSION_STR = VERSION + " [" + VERSION_NAME + "]"

ENCODING = "UTF-8"

PY2 = sys.version_info < (3,)

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if PY2:

    from future_builtins import *
    range = xrange

    py2_int = int
    class metaint(type):
        def __instancecheck__(cls, inst):
            return isinstance(inst, (py2_int, long))
    class int(py2_int):
        """Python 3 int."""
        __metaclass__ = metaint

    chr = unichr
    bytes, str = str, unicode

    py2_print = print
    def print(*args, **kwargs):
        """Python 3 print."""
        return py2_print(*(str(x).encode(ENCODING) for x in args), **kwargs)

    py2_input = raw_input
    def input(*args, **kwargs):
        """Python 3 input."""
        return py2_input(*args, **kwargs).decode(ENCODING)

    from .py2_exec import execfunc

else:

    from .py3_exec import execfunc
