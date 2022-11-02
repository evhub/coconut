# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: MyPy stub file for __coconut__._coconut.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

import sys
import typing as _t

import collections as _collections
import copy as _copy
import functools as _functools
import types as _types
import itertools as _itertools
import operator as _operator
import threading as _threading
import weakref as _weakref
import os as _os
import warnings as _warnings
import contextlib as _contextlib
import traceback as _traceback
import pickle as _pickle
import multiprocessing as _multiprocessing
from multiprocessing import dummy as _multiprocessing_dummy

if sys.version_info >= (3,):
    import copyreg as _copyreg
else:
    import copy_reg as _copyreg

if sys.version_info >= (3, 4):
    import asyncio as _asyncio
else:
    import trollius as _asyncio  # type: ignore

if sys.version_info < (3, 3):
    _abc = _collections
else:
    from collections import abc as _abc

if sys.version_info >= (3,):
    from itertools import zip_longest as _zip_longest
else:
    from itertools import izip_longest as _zip_longest

try:
    import numpy as _numpy  # type: ignore
    import numpy.typing as _npt  # type: ignore
except ImportError:
    _numpy = ...
    _npt = ...
else:
    _abc.Sequence.register(_numpy.ndarray)

if sys.version_info < (3, 10):
    try:
        from typing_extensions import TypeAlias, ParamSpec, Concatenate
    except ImportError:
        TypeAlias = ...
        ParamSpec = ...
    typing.TypeAlias = TypeAlias
    typing.ParamSpec = ParamSpec
    typing.Concatenate = Concatenate


if sys.version_info < (3, 11):
    try:
        from typing_extensions import TypeVarTuple, Unpack
    except ImportError:
        TypeVarTuple = ...
        Unpack = ...
    typing.TypeVarTuple = TypeVarTuple
    typing.Unpack = Unpack

# -----------------------------------------------------------------------------------------------------------------------
# STUB:
# -----------------------------------------------------------------------------------------------------------------------

typing = _t

collections = _collections
copy = _copy
copyreg = _copyreg
functools = _functools
types = _types
itertools = _itertools
operator = _operator
threading = _threading
weakref = _weakref
os = _os
warnings = _warnings
contextlib = _contextlib
traceback = _traceback
pickle = _pickle
asyncio = _asyncio
abc = _abc
multiprocessing = _multiprocessing
multiprocessing_dummy = _multiprocessing_dummy
numpy = _numpy
npt = _npt  # Fake, like typing
if sys.version_info >= (2, 7):
    OrderedDict = collections.OrderedDict
else:
    OrderedDict = dict
zip_longest = _zip_longest
Ellipsis = Ellipsis
NotImplemented = NotImplemented
NotImplementedError = NotImplementedError
Exception = Exception
AttributeError = AttributeError
ImportError = ImportError
IndexError = IndexError
NameError = NameError
TypeError = TypeError
ValueError = ValueError
StopIteration = StopIteration
RuntimeError = RuntimeError
classmethod = classmethod
all = all
any = any
bytes = bytes
dict = dict
enumerate = enumerate
filter = filter
float = float
frozenset = frozenset
getattr = getattr
hasattr = hasattr
hash = hash
id = id
int = int
isinstance = isinstance
issubclass = issubclass
iter = iter
len: _t.Callable[..., int] = ...  # pattern-matching needs an untyped _coconut.len to avoid type errors
list = list
locals = locals
map = map
min = min
max = max
next = next
object = object
print = print
property = property
range = range
reversed = reversed
set = set
slice = slice
str = str
sum = sum
super = super
tuple = tuple
type = type
zip = zip
vars = vars
repr = repr
if sys.version_info >= (3,):
    bytearray = bytearray
