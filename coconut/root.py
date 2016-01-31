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
    readline = None

import sys

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

VERSION = "0.3.6"
VERSION_NAME = "Odisha"
DEVELOP = True

if DEVELOP:
    VERSION += "-post_dev"
__version__ = VERSION
VERSION_STR = VERSION + " [" + VERSION_NAME + "]"
VERSION_TAG = "v" + VERSION_STR
PY2 = sys.version_info < (3,)
PY2_HEADER_BASE = r'''
py2_filter, py2_hex, py2_map, py2_oct, py2_zip, py2_open, py2_range, py2_int, py2_chr, py2_str, py2_print, py2_input, py2_raw_input = filter, hex, map, oct, zip, open, range, int, chr, str, print, input, raw_input
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
    return _coconut_print(*(_coconut_unicode(x).encode(_coconut_sys.stdout.encoding) for x in args), **kwargs)
def input(*args, **kwargs):
    """Python 3 input."""
    return _coconut_raw_input(*args, **kwargs).decode(_coconut_sys.stdout.encoding)
def raw_input(*args):
    """Raises NameError."""
    raise NameError('Coconut uses Python 3 "input" instead of Python 2 "raw_input"')'''
PY2_HEADER = r'import sys as _coconut_sys, os as _coconut_os' + PY2_HEADER_BASE + "\n"
PY2_HEADER_CHECK = r'''import sys as _coconut_sys
if _coconut_sys.version_info < (3,):
    import os as _coconut_os'''
for _line in PY2_HEADER_BASE.splitlines():
    PY2_HEADER_CHECK += "    " + _line + "\n"
PY3_HEADER = "import sys as _coconut_sys\n"

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if PY2:
    exec(PY2_HEADER)
