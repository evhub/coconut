#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import sys as _coconut_sys

#-----------------------------------------------------------------------------------------------------------------------
# VERSION:
#-----------------------------------------------------------------------------------------------------------------------

VERSION = "1.2.0"
VERSION_NAME = "Colonel"
DEVELOP = 11

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

if DEVELOP:
    VERSION += "-post_dev" + str(int(DEVELOP))
__version__ = VERSION
VERSION_STR = VERSION + " [" + VERSION_NAME + "]"
VERSION_TAG = "v" + VERSION
VERSION_STR_TAG = "v" + VERSION_STR

PY2 = _coconut_sys.version_info < (3,)
PY26 = _coconut_sys.version_info < (2, 7)

PY3_HEADER = r'''py_chr, py_filter, py_hex, py_input, py_int, py_map, py_oct, py_open, py_print, py_range, py_str, py_zip = chr, filter, hex, input, int, map, oct, open, print, range, str, zip
'''
PY27_HEADER = PY3_HEADER + r'''py_raw_input, py_xrange = raw_input, xrange
_coconut_raw_input, _coconut_xrange, _coconut_int, _coconut_long, _coconut_print, _coconut_str, _coconut_unicode, _coconut_repr = raw_input, xrange, int, long, print, str, unicode, repr
from future_builtins import *
chr, str = unichr, unicode
from io import open
class range(object):
    __slots__ = ("_xrange",)
    if hasattr(_coconut_xrange, "__doc__"):
        __doc__ = _coconut_xrange.__doc__
    def __init__(self, *args):
        self._xrange = _coconut_xrange(*args)
    def __iter__(self):
        return _coconut.iter(self._xrange)
    def __reversed__(self):
        return _coconut.reversed(self._xrange)
    def __len__(self):
        return _coconut.len(self._xrange)
    def __contains__(self, elem):
        return elem in self._xrange
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            start, stop, step = index.start, index.stop, index.step
            if start is None:
                start = 0
            elif start < 0:
                start += _coconut.len(self._xrange)
            if stop is None:
                stop = _coconut.len(self._xrange)
            elif stop is not None and stop < 0:
                stop += _coconut.len(self._xrange)
            if step is None:
                step = 1
            return _coconut_map(self._xrange.__getitem__, self.__class__(start, stop, step))
        else:
            return self._xrange[index]
    def count(self, elem):
        """Count the number of times elem appears in the range."""
        return int(elem in self._xrange)
    def index(self, elem):
        """Find the index of elem in the range."""
        if elem not in self._xrange: raise _coconut.ValueError(_coconut.repr(elem) + " is not in range")
        start, _, step = self._xrange.__reduce_ex__(2)[1]
        return (elem - start) // step
    def __repr__(self):
        return _coconut.repr(self._xrange)[1:]
    def __reduce_ex__(self, protocol):
        return (self.__class__, self._xrange.__reduce_ex__(protocol)[1])
    def __reduce__(self):
        return self.__reduce_ex__(_coconut.pickle.HIGHEST_PROTOCOL)
    def __hash__(self):
        return _coconut.hash(self._xrange.__reduce__()[1])
    def __copy__(self):
        return self.__class__(*self._xrange.__reduce__()[1])
    def __eq__(self, other):
        reduction = self.__reduce__()
        return _coconut.isinstance(other, reduction[0]) and reduction[1] == other.__reduce__()[1]
from collections import Sequence as _coconut_Sequence
_coconut_Sequence.register(range)
class int(_coconut_int):
    __slots__ = ()
    if hasattr(_coconut_int, "__doc__"):
        __doc__ = _coconut_int.__doc__
    class __metaclass__(type):
        def __instancecheck__(cls, inst):
            return _coconut.isinstance(inst, (_coconut_int, _coconut_long))
class bytes(_coconut_str):
    __slots__ = ()
    if hasattr(_coconut_str, "__doc__"):
        __doc__ = _coconut_str.__doc__
    class __metaclass__(type):
        def __instancecheck__(cls, inst):
            return _coconut.isinstance(inst, _coconut_str)
    def __new__(cls, *args, **kwargs):
        return _coconut_str.__new__(cls, _coconut.bytearray(*args, **kwargs))
from functools import wraps as _coconut_wraps
@_coconut_wraps(_coconut_print)
def print(*args, **kwargs):
    if _coconut.hasattr(_coconut_sys.stdout, "encoding") and _coconut_sys.stdout.encoding is not None:
        return _coconut_print(*(_coconut_unicode(x).encode(_coconut_sys.stdout.encoding) for x in args), **kwargs)
    else:
        return _coconut_print(*(_coconut_unicode(x).encode() for x in args), **kwargs)
@_coconut_wraps(_coconut_raw_input)
def input(*args, **kwargs):
    if _coconut.hasattr(_coconut_sys.stdout, "encoding") and _coconut_sys.stdout.encoding is not None:
        return _coconut_raw_input(*args, **kwargs).decode(_coconut_sys.stdout.encoding)
    else:
        return _coconut_raw_input(*args, **kwargs).decode()
@_coconut_wraps(_coconut_repr)
def repr(obj):
    if isinstance(obj, _coconut_unicode):
        return _coconut_repr(obj)[1:]
    else:
        return _coconut_repr(obj)
ascii = repr
def raw_input(*args):
    """Coconut uses Python 3 "input" instead of Python 2 "raw_input"."""
    raise _coconut.NameError('Coconut uses Python 3 "input" instead of Python 2 "raw_input"')
def xrange(*args):
    """Coconut uses Python 3 "range" instead of Python 2 "xrange"."""
    raise _coconut.NameError('Coconut uses Python 3 "range" instead of Python 2 "xrange"')
'''
PY2_HEADER = PY27_HEADER + '''if _coconut_sys.version_info < (2, 7):
    import functools as _coconut_functools, copy_reg as _coconut_copy_reg
    def _coconut_new_partial(func, args, keywords):
        return _coconut_functools.partial(func, *(args if args is not None else ()), **(keywords if keywords is not None else {}))
    _coconut_copy_reg.constructor(_coconut_new_partial)
    def _coconut_reduce_partial(self):
        return (_coconut_new_partial, (self.func, self.args, self.keywords))
    _coconut_copy_reg.pickle(_coconut_functools.partial, _coconut_reduce_partial)
'''
PYCHECK_HEADER = r'''if _coconut_sys.version_info < (3,):
''' + "".join(
    ("    " if _line else "") + _line for _line in PY2_HEADER.splitlines(True)
) + '''else:
''' + "".join(
    ("    " if _line else "") + _line for _line in PY3_HEADER.splitlines(True)
)

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if PY2:
    if PY26:
        exec(PY2_HEADER)
    else:
        exec(PY27_HEADER)
    import __builtin__ as _coconut  # NOQA
    import pickle
    _coconut.pickle = pickle
    _coconut_map = map
else:
    exec(PY3_HEADER)
