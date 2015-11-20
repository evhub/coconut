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

VERSION = "0.3.4"
VERSION_NAME = "Macapuno"
DEVELOP = True

ENCODING = "UTF-8"

if DEVELOP:
    VERSION += "-post_dev"
VERSION_STR = VERSION + " [" + VERSION_NAME + "]"

PY2 = sys.version_info < (3,)

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if PY2:
    from future_builtins import *
    from io import open
    class _coconut_metaint(type):
        def __instancecheck__(cls, inst):
            return isinstance(inst, (int, long))
    class int(int):
        """Python 3 int."""
        __metaclass__ = _coconut_metaint
    def bytes(*args, **kwargs):
        """Python 3 bytes."""
        if len(args) == 1 and isinstance(args[0], _coconut_int):
            return b'\x00' * args[0]
        else:
            return str(*args, **kwargs)
    def str(*args, **kwargs):
        """Python 3 str."""
        if len(args) == 1 and isinstance(args[0], _coconut_str):
            return unicode(repr(args[0]))
        else:
            return unicode(*args, **kwargs)
    def print(*args, **kwargs):
        """Python 3 print."""
        return print(*(str(x).encode(ENCODING) for x in args), **kwargs)
    def input(*args, **kwargs):
        """Python 3 input."""
        return input(*args, **kwargs).decode(ENCODING)
