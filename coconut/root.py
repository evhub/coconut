#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Basic Coconut constants and compatibility handling.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

try:
    import readline
except ImportError:
    pass

import sys

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

VERSION = "0.3.6"
VERSION_NAME = "Odisha"
DEVELOP = True

ENCODING = "UTF-8"

if DEVELOP:
    VERSION += "-post_dev"
VERSION_STR = VERSION + " [" + VERSION_NAME + "]"
__version__ = VERSION

PY2 = sys.version_info < (3,)
PY2_HEADER = r'''_coconut_console_encoding = "'''+ENCODING+r'''"
py2_filter, py2_hex, py2_map, py2_oct, py2_zip, py2_open, py2_range, py2_int, py2_chr, py2_str, py2_print, py2_input = filter, hex, map, oct, zip, open, range, int, chr, str, print, input
_coconut_int, _coconut_long, _coconut_str, _coconut_bytearray, _coconut_print, _coconut_unicode, _coconut_raw_input = int, long, str, bytearray, print, unicode, raw_input
range, chr, str = xrange, unichr, unicode
from future_builtins import *
from io import open
class _coconut_metaint(type):
    def __instancecheck__(cls, inst):
        return isinstance(inst, (_coconut_int, _coconut_long))
class int(_coconut_int):
    """Python 3 int."""
    __metaclass__ = _coconut_metaint
    __slots__ = ()
class _coconut_metabytes(type):
    def __instancecheck__(cls, inst):
        return isinstance(inst, _coconut_str)
class bytes(_coconut_str):
    """Python 3 bytes."""
    __metaclass__ = _coconut_metabytes
    __slots__ = ()
    def __new__(cls, *args, **kwargs):
        """Python 3 bytes constructor."""
        return _coconut_str.__new__(cls, _coconut_bytearray(*args, **kwargs))
def print(*args, **kwargs):
    """Python 3 print."""
    return _coconut_print(*(_coconut_unicode(x).encode(_coconut_console_encoding) for x in args), **kwargs)
def input(*args, **kwargs):
    """Python 3 input."""
    return _coconut_raw_input(*args, **kwargs).decode(_coconut_console_encoding)'''

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if PY2:
    exec(PY2_HEADER)
