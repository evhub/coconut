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

VERSION = "3.1.1"
VERSION_NAME = None
# False for release, int >= 1 for develop
DEVELOP = 1
ALPHA = False  # for pre releases rather than post releases

assert DEVELOP is False or DEVELOP >= 1, "DEVELOP must be False or an int >= 1"
assert DEVELOP or not ALPHA, "alpha releases are only for develop"

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def _indent(code, by=1, tabsize=4, strip=False, newline=False, initial_newline=False):
    """Indents every nonempty line of the given code."""
    return ("\n" if initial_newline else "") + "".join(
        (" " * (tabsize * by) if line.strip() else "") + line
        for line in (code.strip() if strip else code).splitlines(True)
    ) + ("\n" if newline else "")


def _get_target_info(target):
    """Return target information as a version tuple."""
    if not target or target == "universal":
        return ()
    elif len(target) == 1:
        return (int(target),)
    else:
        return (int(target[0]), int(target[1:]))


# -----------------------------------------------------------------------------------------------------------------------
# HEADER:
# -----------------------------------------------------------------------------------------------------------------------

# if a new assignment is added below, a new builtins import should be added alongside it
_base_py3_header = r'''from builtins import chr, dict, hex, input, int, map, object, oct, open, print, range, str, super, zip, filter, reversed, enumerate, repr
py_bytes, py_chr, py_dict, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_super, py_zip, py_filter, py_reversed, py_enumerate, py_repr, py_min, py_max = bytes, chr, dict, hex, input, int, map, object, oct, open, print, range, str, super, zip, filter, reversed, enumerate, repr, min, max
_coconut_py_str, _coconut_py_super, _coconut_py_dict, _coconut_py_min, _coconut_py_max = str, super, dict, min, max
from functools import wraps as _coconut_wraps
exec("_coconut_exec = exec")
'''

# if a new assignment is added below, a new builtins import should be added alongside it
_base_py2_header = r'''from __builtin__ import chr, dict, hex, input, int, map, object, oct, open, print, range, str, super, zip, filter, reversed, enumerate, raw_input, xrange, repr, long
py_bytes, py_chr, py_dict, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_super, py_zip, py_filter, py_reversed, py_enumerate, py_raw_input, py_xrange, py_repr, py_min, py_max = bytes, chr, dict, hex, input, int, map, object, oct, open, print, range, str, super, zip, filter, reversed, enumerate, raw_input, xrange, repr, min, max
_coconut_py_raw_input, _coconut_py_xrange, _coconut_py_int, _coconut_py_long, _coconut_py_print, _coconut_py_str, _coconut_py_super, _coconut_py_unicode, _coconut_py_repr, _coconut_py_dict, _coconut_py_bytes, _coconut_py_min, _coconut_py_max = raw_input, xrange, int, long, print, str, super, unicode, repr, dict, bytes, min, max
from functools import wraps as _coconut_wraps
from collections import Sequence as _coconut_Sequence
from future_builtins import *
chr, str = unichr, unicode
from io import open
class object(object):
    __slots__ = ()
    def __ne__(self, other):
        eq = self == other
        return _coconut.NotImplemented if eq is _coconut.NotImplemented else not eq
    def __nonzero__(self):
        if _coconut.hasattr(self, "__bool__"):
            got = self.__bool__()
            if not _coconut.isinstance(got, _coconut.bool):
                raise _coconut.TypeError("__bool__ should return bool, returned " + _coconut.type(got).__name__)
            return got
        return True
class int(_coconut_py_int):
    __slots__ = ()
    __doc__ = getattr(_coconut_py_int, "__doc__", "<see help(py_int)>")
    class __metaclass__(type):
        def __instancecheck__(cls, inst):
            return _coconut.isinstance(inst, (_coconut_py_int, _coconut_py_long))
        def __subclasscheck__(cls, subcls):
            return _coconut.issubclass(subcls, (_coconut_py_int, _coconut_py_long))
class bytes(_coconut_py_bytes):
    __slots__ = ()
    __doc__ = getattr(_coconut_py_bytes, "__doc__", "<see help(py_bytes)>")
    class __metaclass__(type):
        def __instancecheck__(cls, inst):
            return _coconut.isinstance(inst, _coconut_py_bytes)
        def __subclasscheck__(cls, subcls):
            return _coconut.issubclass(subcls, _coconut_py_bytes)
    def __new__(self, *args):
        if not args:
            return b""
        elif _coconut.len(args) == 1:
            if _coconut.isinstance(args[0], _coconut.int):
                return b"\x00" * args[0]
            elif _coconut.isinstance(args[0], _coconut.bytes):
                return _coconut_py_bytes(args[0])
            else:
                return b"".join(_coconut.chr(x) for x in args[0])
        else:
            return args[0].encode(*args[1:])
class range(object):
    __slots__ = ("_xrange",)
    __doc__ = getattr(_coconut_py_xrange, "__doc__", "<see help(py_xrange)>")
    def __init__(self, *args):
        self._xrange = _coconut_py_xrange(*args)
    def __iter__(self):
        return _coconut.iter(self._xrange)
    def __reversed__(self):
        return _coconut.reversed(self._xrange)
    def __len__(self):
        return _coconut.len(self._xrange)
    def __bool__(self):
        return _coconut.bool(self._xrange)
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
_coconut_Sequence.register(range)
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
import operator as _coconut_operator
class _coconut_attrgetter(object):
    __slots__ = ("attrs",)
    def __init__(self, *attrs):
        self.attrs = attrs
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __reduce__(self):
        return (self.__class__, self.attrs)
    @staticmethod
    def _getattr(obj, attr):
        for name in attr.split("."):
            obj = _coconut.getattr(obj, name)
        return obj
    def __call__(self, obj):
        if len(self.attrs) == 1:
            return self._getattr(obj, self.attrs[0])
        return _coconut.tuple(self._getattr(obj, attr) for attr in self.attrs)
_coconut_operator.attrgetter = _coconut_attrgetter
class _coconut_itemgetter(object):
    __slots__ = ("items",)
    def __init__(self, *items):
        self.items = items
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __reduce__(self):
        return (self.__class__, self.items)
    def __call__(self, obj):
        if len(self.items) == 1:
            return obj[self.items[0]]
        return _coconut.tuple(obj[item] for item in self.items)
_coconut_operator.itemgetter = _coconut_itemgetter
class _coconut_methodcaller(object):
    __slots__ = ("name", "args", "kwargs")
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __reduce__(self):
        return (self.__class__, (self.name,) + self.args, {"kwargs": self.kwargs})
    def __setstate__(self, setvars):
        for k, v in setvars.items():
            _coconut.setattr(self, k, v)
    def __call__(self, obj):
        return _coconut.getattr(obj, self.name)(*self.args, **self.kwargs)
_coconut_operator.methodcaller = _coconut_methodcaller
'''

_below_py34_extras = '''def min(*args, **kwargs):
    if len(args) == 1 and "default" in kwargs:
        obj = tuple(args[0])
        default = kwargs.pop("default")
        if len(obj):
            return _coconut_py_min(obj, **kwargs)
        else:
            return default
    else:
        return _coconut_py_min(*args, **kwargs)
def max(*args, **kwargs):
    if len(args) == 1 and "default" in kwargs:
        obj = tuple(args[0])
        default = kwargs.pop("default")
        if len(obj):
            return _coconut_py_max(obj, **kwargs)
        else:
            return default
    else:
        return _coconut_py_max(*args, **kwargs)
'''

_finish_dict_def = '''
    def __or__(self, other):
        out = self.copy()
        out.update(other)
        return out
    def __ror__(self, other):
        out = self.__class__(other)
        out.update(self)
        return out
    def __ior__(self, other):
        self.update(other)
        return self
class _coconut_dict_meta(type):
    def __instancecheck__(cls, inst):
        return _coconut.isinstance(inst, _coconut_py_dict)
    def __subclasscheck__(cls, subcls):
        return _coconut.issubclass(subcls, _coconut_py_dict)
dict = _coconut_dict_meta(py_str("dict"), _coconut_dict_base.__bases__, _coconut_dict_base.__dict__.copy())
'''

_below_py37_extras = '''from collections import OrderedDict as _coconut_OrderedDict
def _coconut_default_breakpointhook(*args, **kwargs):
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
class _coconut_dict_base(_coconut_OrderedDict):
    __slots__ = ()
    __doc__ = getattr(_coconut_OrderedDict, "__doc__", "<see help(py_dict)>")
    __eq__ = _coconut_py_dict.__eq__
    def __repr__(self):
        return "{" + ", ".join("{k!r}: {v!r}".format(k=k, v=v) for k, v in self.items()) + "}"''' + _finish_dict_def

_py37_py38_extras = '''class _coconut_dict_base(_coconut_py_dict):
    __slots__ = ()
    __doc__ = getattr(_coconut_py_dict, "__doc__", "<see help(py_dict)>")''' + _finish_dict_def

_py26_extras = '''if _coconut_sys.version_info < (2, 7):
    import functools as _coconut_functools, copy_reg as _coconut_copy_reg
    def _coconut_new_partial(func, args, keywords):
        return _coconut_functools.partial(func, *(args if args is not None else ()), **(keywords if keywords is not None else {}))
    _coconut_copy_reg.constructor(_coconut_new_partial)
    def _coconut_reduce_partial(self):
        return (_coconut_new_partial, (self.func, self.args, self.keywords))
    _coconut_copy_reg.pickle(_coconut_functools.partial, _coconut_reduce_partial)
'''

_py3_before_py311_extras = '''try:
    from exceptiongroup import ExceptionGroup, BaseExceptionGroup
except ImportError:
    class you_need_to_install_exceptiongroup(object):
        __slots__ = ()
    ExceptionGroup = BaseExceptionGroup = you_need_to_install_exceptiongroup()
'''


# whenever new versions are added here, header.py must be updated to use them
ROOT_HEADER_VERSIONS = (
    "universal",
    "2",
    "27",
    "3",
    "37",
    "39",
    "311",
)


def _get_root_header(version="universal"):
    assert version in ROOT_HEADER_VERSIONS, version

    if version == "universal":
        return r'''if _coconut_sys.version_info < (3,):
''' + _indent(_get_root_header("2")) + '''else:
''' + _indent(_get_root_header("3"))

    version_info = _get_target_info(version)
    header = ""

    if version.startswith("3"):
        header += _base_py3_header
    else:
        assert version.startswith("2"), version
        # if a new assignment is added below, a new builtins import should be added alongside it
        header += _base_py2_header

    if version_info >= (3, 7):
        header += r'''py_breakpoint = breakpoint
'''
    elif version == "3":
        header += r'''if _coconut_sys.version_info >= (3, 7):
    py_breakpoint = breakpoint
'''
    elif version == "2":
        header += _py26_extras

    if version.startswith("2"):
        header += _below_py34_extras
    elif version_info < (3, 4):
        header += r'''if _coconut_sys.version_info < (3, 4):
''' + _indent(_below_py34_extras)

    if version == "3":
        header += r'''if _coconut_sys.version_info < (3, 7):
''' + _indent(_below_py37_extras) + r'''elif _coconut_sys.version_info < (3, 9):
''' + _indent(_py37_py38_extras)
    elif (3, 7) <= version_info < (3, 9):
        header += r'''if _coconut_sys.version_info < (3, 9):
''' + _indent(_py37_py38_extras)
    elif version.startswith("2"):
        header += _below_py37_extras + '''dict.keys = _coconut_OrderedDict.viewkeys
dict.values = _coconut_OrderedDict.viewvalues
dict.items = _coconut_OrderedDict.viewitems
'''
    else:
        assert version_info >= (3, 9), version

    if (3,) <= version_info < (3, 11):
        header += r'''if _coconut_sys.version_info < (3, 11):
''' + _indent(_py3_before_py311_extras)

    return header


# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

if DEVELOP:
    VERSION += "-" + ("a" if ALPHA else "post") + "_dev" + str(int(DEVELOP))
VERSION_STR = VERSION + (" [" + VERSION_NAME + "]" if VERSION_NAME else "")

PY2 = _coconut_sys.version_info < (3,)

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

exec(_get_root_header())
