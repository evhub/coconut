#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Basic Coconut constants and compatibility handling.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys as _coconut_sys

# -----------------------------------------------------------------------------------------------------------------------
# VERSION:
# -----------------------------------------------------------------------------------------------------------------------

VERSION = "2.0.0"
VERSION_NAME = "How Not to Be Seen"
# False for release, int >= 1 for develop
DEVELOP = 34
ALPHA = True

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def _indent(code, by=1, tabsize=4, newline=False):
    """Indents every nonempty line of the given code."""
    return "".join(
        (" " * (tabsize * by) if line else "") + line
        for line in code.splitlines(True)
    ) + ("\n" if newline else "")


# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

assert DEVELOP or not ALPHA, "alpha releases are only for develop"
if DEVELOP:
    VERSION += "-" + ("a" if ALPHA else "post") + "_dev" + str(int(DEVELOP))
VERSION_STR = VERSION + " [" + VERSION_NAME + "]"

PY2 = _coconut_sys.version_info < (3,)
PY26 = _coconut_sys.version_info < (2, 7)
PY37 = _coconut_sys.version_info >= (3, 7)

_non_py37_extras = r'''def _coconut_default_breakpointhook(*args, **kwargs):
    hookname = _coconut.os.getenv("PYTHONBREAKPOINT")
    if hookname != "0":
        if not hookname:
            hookname = "pdb.set_trace"
        modname, dot, funcname = hookname.rpartition(".")
        if not dot:
            modname = "builtins" if _coconut_sys.version_info >= (3,) else "__builtin__"
        if _coconut_sys.version_info >= (2, 7):
            import importlib
            module = importlib.import_module(modname)
        else:
            import imp
            module = imp.load_module(modname, *imp.find_module(modname))
        hook = _coconut.getattr(module, funcname)
        return hook(*args, **kwargs)
if not hasattr(_coconut_sys, "__breakpointhook__"):
    _coconut_sys.__breakpointhook__ = _coconut_default_breakpointhook
def breakpoint(*args, **kwargs):
    return _coconut.getattr(_coconut_sys, "breakpointhook", _coconut_default_breakpointhook)(*args, **kwargs)
'''

_base_py3_header = r'''from builtins import chr, filter, hex, input, int, map, object, oct, open, print, range, str, zip, filter, reversed, enumerate
py_chr, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_zip, py_filter, py_reversed, py_enumerate, py_repr = chr, hex, input, int, map, object, oct, open, print, range, str, zip, filter, reversed, enumerate, repr
_coconut_py_str = str
exec("_coconut_exec = exec")
'''

PY37_HEADER = _base_py3_header + r'''py_breakpoint = breakpoint
'''

PY3_HEADER = _base_py3_header + r'''if _coconut_sys.version_info < (3, 7):
''' + _indent(_non_py37_extras) + r'''else:
    py_breakpoint = breakpoint
'''

PY27_HEADER = r'''from __builtin__ import chr, filter, hex, input, int, map, object, oct, open, print, range, str, zip, filter, reversed, enumerate, raw_input, xrange
py_chr, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_zip, py_filter, py_reversed, py_enumerate, py_raw_input, py_xrange, py_repr = chr, hex, input, int, map, object, oct, open, print, range, str, zip, filter, reversed, enumerate, raw_input, xrange, repr
_coconut_py_raw_input, _coconut_py_xrange, _coconut_py_int, _coconut_py_long, _coconut_py_print, _coconut_py_str, _coconut_py_unicode, _coconut_py_repr = raw_input, xrange, int, long, print, str, unicode, repr
from future_builtins import *
chr, str = unichr, unicode
from io import open
class object(object):
    __slots__ = ()
    def __ne__(self, other):
        eq = self == other
        return _coconut.NotImplemented if eq is _coconut.NotImplemented else not eq
class int(_coconut_py_int):
    __slots__ = ()
    if hasattr(_coconut_py_int, "__doc__"):
        __doc__ = _coconut_py_int.__doc__
    class __metaclass__(type):
        def __instancecheck__(cls, inst):
            return _coconut.isinstance(inst, (_coconut_py_int, _coconut_py_long))
        def __subclasscheck__(cls, subcls):
            return _coconut.issubclass(subcls, (_coconut_py_int, _coconut_py_long))
class range(object):
    __slots__ = ("_xrange",)
    if hasattr(_coconut_py_xrange, "__doc__"):
        __doc__ = _coconut_py_xrange.__doc__
    def __init__(self, *args):
        self._xrange = _coconut_py_xrange(*args)
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
            args = _coconut.slice(*self._args)
            start, stop, step = (args.start if args.start is not None else 0), args.stop, (args.step if args.step is not None else 1)
            if index.start is None:
                new_start = start if index.step is None or index.step >= 0 else stop - step
            elif index.start >= 0:
                new_start = start + step * index.start
                if (step >= 0 and new_start >= stop) or (step < 0 and new_start <= stop):
                    new_start = stop
            else:
                new_start = stop + step * index.start
                if (step >= 0 and new_start <= start) or (step < 0 and new_start >= start):
                    new_start = start
            if index.stop is None:
                new_stop = stop if index.step is None or index.step >= 0 else start - step
            elif index.stop >= 0:
                new_stop = start + step * index.stop
                if (step >= 0 and new_stop >= stop) or (step < 0 and new_stop <= stop):
                    new_stop = stop
            else:
                new_stop = stop + step * index.stop
                if (step >= 0 and new_stop <= start) or (step < 0 and new_stop >= start):
                    new_stop = start
            new_step = step if index.step is None else step * index.step
            return self.__class__(new_start, new_stop, new_step)
        else:
            return self._xrange[index]
    def count(self, elem):
        """Count the number of times elem appears in the range."""
        return _coconut_py_int(elem in self._xrange)
    def index(self, elem):
        """Find the index of elem in the range."""
        if elem not in self._xrange: raise _coconut.ValueError(_coconut.repr(elem) + " is not in range")
        start, _, step = self._xrange.__reduce_ex__(2)[1]
        return (elem - start) // step
    def __repr__(self):
        return _coconut.repr(self._xrange)[1:]
    @property
    def _args(self):
        return self._xrange.__reduce__()[1]
    def __reduce_ex__(self, protocol):
        return (self.__class__, self._xrange.__reduce_ex__(protocol)[1])
    def __reduce__(self):
        return self.__reduce_ex__(_coconut.pickle.DEFAULT_PROTOCOL)
    def __hash__(self):
        return _coconut.hash(self._args)
    def __copy__(self):
        return self.__class__(*self._args)
    def __eq__(self, other):
        return self.__class__ is other.__class__ and self._args == other._args
from collections import Sequence as _coconut_Sequence
_coconut_Sequence.register(range)
from functools import wraps as _coconut_wraps
@_coconut_wraps(_coconut_py_print)
def print(*args, **kwargs):
    file = kwargs.get("file", _coconut_sys.stdout)
    if "flush" in kwargs:
        flush = kwargs["flush"]
        del kwargs["flush"]
    else:
        flush = False
    if _coconut.getattr(file, "encoding", None) is not None:
        _coconut_py_print(*(_coconut_py_unicode(x).encode(file.encoding) for x in args), **kwargs)
    else:
        _coconut_py_print(*args, **kwargs)
    if flush:
        file.flush()
@_coconut_wraps(_coconut_py_raw_input)
def input(*args, **kwargs):
    if _coconut.getattr(_coconut_sys.stdout, "encoding", None) is not None:
        return _coconut_py_raw_input(*args, **kwargs).decode(_coconut_sys.stdout.encoding)
    return _coconut_py_raw_input(*args, **kwargs).decode()
@_coconut_wraps(_coconut_py_repr)
def repr(obj):
    import __builtin__
    try:
        __builtin__.repr = _coconut_repr
        if isinstance(obj, _coconut_py_unicode):
            return _coconut_py_unicode(_coconut_py_repr(obj)[1:])
        if isinstance(obj, _coconut_py_str):
            return "b" + _coconut_py_unicode(_coconut_py_repr(obj))
        return _coconut_py_unicode(_coconut_py_repr(obj))
    finally:
        __builtin__.repr = _coconut_py_repr
ascii = _coconut_repr = repr
def raw_input(*args):
    """Coconut uses Python 3 'input' instead of Python 2 'raw_input'."""
    raise _coconut.NameError("Coconut uses Python 3 'input' instead of Python 2 'raw_input'")
def xrange(*args):
    """Coconut uses Python 3 'range' instead of Python 2 'xrange'."""
    raise _coconut.NameError("Coconut uses Python 3 'range' instead of Python 2 'xrange'")
def _coconut_exec(obj, globals=None, locals=None):
    """Execute the given source in the context of globals and locals."""
    if locals is None:
        locals = _coconut_sys._getframe(1).f_locals if globals is None else globals
    if globals is None:
        globals = _coconut_sys._getframe(1).f_globals
    exec(obj, globals, locals)
''' + _non_py37_extras

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
''' + _indent(PY2_HEADER) + '''else:
''' + _indent(PY3_HEADER)

# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------

if PY2:
    import __builtin__ as _coconut  # NOQA
else:
    import builtins as _coconut  # NOQA

import pickle
_coconut.pickle = pickle

import os
_coconut.os = os

if PY26:
    exec(PY2_HEADER)
elif PY2:
    exec(PY27_HEADER)
elif PY37:
    exec(PY37_HEADER)
else:
    exec(PY3_HEADER)
