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
PY2_HEADER_BASE = r'''py2_filter, py2_hex, py2_map, py2_oct, py2_zip, py2_open, py2_range, py2_xrange, py2_int, py2_chr, py2_str, py2_print, py2_input, py2_raw_input = filter, hex, map, oct, zip, open, range, xrange, int, chr, str, print, input, raw_input
_coconut_NameError, _coconut_int, _coconut_long, _coconut_str, _coconut_unicode, _coconut_bytearray, _coconut_slice, _coconut_reversed, _coconut_isinstance, _coconut_iter, _coconut_len, _coconut_repr, _coconut_print, _coconut_xrange, _coconut_raw_input = NameError, int, long, str, unicode, bytearray, slice, reversed, isinstance, iter, len, repr, print, xrange, raw_input
chr, str = unichr, unicode
from future_builtins import *
from io import open
class range(object):
    __doc__ = _coconut_xrange.__doc__
    __slots__ = ("_xrange",)
    def __init__(self, *args):
        self._xrange = _coconut_xrange(*args)
    def __iter__(self):
        return _coconut_iter(self._xrange)
    def __reversed__(self):
        return _coconut_reversed(self._xrange)
    def __len__(self):
        return _coconut_len(self._xrange)
    def __getitem__(self, index):
        if _coconut_isinstance(index, _coconut_slice):
            start, stop, step = index.start, index.stop, index.step
            if start is None:
                start = 0
            elif start < 0:
                start += _coconut_len(self._xrange)
            if stop is None:
                stop = _coconut_len(self._xrange)
            elif stop is not None and stop < 0:
                stop += _coconut_len(self._xrange)
            if step is None:
                step = 1
            return map(self._xrange.__getitem__, range(start, stop, step))
        else:
            return self._xrange[index]
    def __repr__(self):
        return _coconut_repr(self._xrange)[1:]
class _coconut_metaint(type):
    def __instancecheck__(cls, inst):
        return _coconut_isinstance(inst, (_coconut_int, _coconut_long))
class int(_coconut_int):
    __doc__ = _coconut_int.__doc__
    __metaclass__ = _coconut_metaint
    __slots__ = ()
class _coconut_metabytes(type):
    def __instancecheck__(cls, inst):
        return _coconut_isinstance(inst, _coconut_str)
class bytes(_coconut_str):
    __doc__ = _coconut_str.__doc__
    __metaclass__ = _coconut_metabytes
    __slots__ = ()
    def __new__(cls, *args, **kwargs):
        return _coconut_str.__new__(cls, _coconut_bytearray(*args, **kwargs))
def print(*args, **kwargs):
    return _coconut_print(*(_coconut_unicode(x).encode(_coconut_sys.stdout.encoding) for x in args), **kwargs)
def input(*args, **kwargs):
    return _coconut_raw_input(*args, **kwargs).decode(_coconut_sys.stdout.encoding)
print.__doc__, input.__doc__ = _coconut_print.__doc__, _coconut_raw_input.__doc__
def raw_input(*args):
    """Raises NameError."""
    raise _coconut_NameError('Coconut uses Python 3 "input" instead of Python 2 "raw_input"')
def xrange(*args):
    """Raises NameError."""
    raise _coconut_NameError('Coconut uses Python 3 "range" instead of Python 2 "xrange"')'''
PY2_HEADER = "import sys as _coconut_sys, os as _coconut_os\n" + PY2_HEADER_BASE + "\n"
PY2_HEADER_CHECK = r'''import sys as _coconut_sys
if _coconut_sys.version_info < (3,):
    import os as _coconut_os
'''
for _line in PY2_HEADER_BASE.splitlines():
    PY2_HEADER_CHECK += "    " + _line + "\n"
PY3_HEADER = "import sys as _coconut_sys\n"

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if PY2:
    exec(PY2_HEADER)
