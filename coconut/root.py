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
py2_filter, py2_hex, py2_map, py2_oct, py2_zip, py2_open, py2_range, py2_int, py2_chr, py2_str, py2_print, py2_input = __builtins__.filter, __builtins__.hex, __builtins__.map, __builtins__.oct, __builtins__.zip, __builtins__.open, __builtins__.range, __builtins__.int, __builtins__.chr, __builtins__.str, __builtins__.print, __builtins__.input
_coconut_int, _coconut_long, _coconut_str, _coconut_bytearray, _coconut_print, _coconut_unicode, _coconut_raw_input = __builtins__.int, __builtins__.long, __builtins__.str, __builtins__.bytearray, __builtins__.print, __builtins__.unicode, __builtins__.raw_input
__builtins__.range, __builtins__.chr, __builtins__.str = __builtins__.xrange, __builtins__.unichr, __builtins__.unicode
import future_builtins as _coconut_future_builtins
__builtins__.ascii, __builtins__.filter, __builtins__.hex, __builtins__.map, __builtins__.oct, __builtins__.zip = _coconut_future_builtins.ascii, _coconut_future_builtins.filter, _coconut_future_builtins.hex, _coconut_future_builtins.map, _coconut_future_builtins.oct, _coconut_future_builtins.zip
from io import open as _coconut_new_open
class _coconut_metaint(type):
    def __instancecheck__(cls, inst):
        return isinstance(inst, (_coconut_int, _coconut_long))
class _coconut_new_int(_coconut_int):
    """Python 3 int."""
    __metaclass__ = _coconut_metaint
    __slots__ = ()
class _coconut_metabytes(type):
    def __instancecheck__(cls, inst):
        return isinstance(inst, _coconut_str)
class _coconut_new_bytes(_coconut_str):
    """Python 3 bytes."""
    __metaclass__ = _coconut_metabytes
    __slots__ = ()
    def __new__(cls, *args, **kwargs):
        """Python 3 bytes constructor."""
        return _coconut_str.__new__(cls, _coconut_bytearray(*args, **kwargs))
def _coconut_new_print(*args, **kwargs):
    """Python 3 print."""
    return _coconut_print(*(_coconut_unicode(x).encode(_coconut_sys.stdout.encoding) for x in args), **kwargs)
def _coconut_new_input(*args, **kwargs):
    """Python 3 input."""
    return _coconut_raw_input(*args, **kwargs).decode(_coconut_sys.stdout.encoding)
__builtins__.open, __builtins__.int, __builtins__.bytes, __builtins__.print, __builtins__.input = _coconut_new_open, _coconut_new_int, _coconut_new_bytes, _coconut_new_print, _coconut_new_input
del __builtins__.raw_input, __builtins__.apply, __builtins__.coerce, __builtins__.execfile, __builtins__.file, __builtins__.reload, __builtins__.intern'''
PY2_HEADER = r'import sys as _coconut_sys, os as _coconut_os' + PY2_HEADER_BASE + "\n"
PY2_HEADER_CHECK = r'''import sys as _coconut_sys
if _coconut_sys.version_info < (3,):
    import os as _coconut_os'''
for _line in PY2_HEADER_BASE.splitlines():
    PY2_HEADER_CHECK += "    " + _line + "\n"

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if PY2:
    exec(PY2_HEADER)
