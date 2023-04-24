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
import os as _os
import warnings as _warnings
import contextlib as _contextlib
import traceback as _traceback
import weakref as _weakref
import multiprocessing as _multiprocessing
import pickle as _pickle
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

# -----------------------------------------------------------------------------------------------------------------------
# TYPING:
# -----------------------------------------------------------------------------------------------------------------------

typing = _t

from typing_extensions import TypeVar
typing.TypeVar = TypeVar  # type: ignore

if sys.version_info < (3, 8):
    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = ...  # type: ignore
    typing.Protocol = Protocol  # type: ignore

if sys.version_info < (3, 10):
    try:
        from typing_extensions import TypeAlias, ParamSpec, Concatenate
    except ImportError:
        TypeAlias = ...  # type: ignore
        ParamSpec = ...  # type: ignore
        Concatenate = ...  # type: ignore
    typing.TypeAlias = TypeAlias  # type: ignore
    typing.ParamSpec = ParamSpec  # type: ignore
    typing.Concatenate = Concatenate  # type: ignore

if sys.version_info < (3, 11):
    try:
        from typing_extensions import TypeVarTuple, Unpack
    except ImportError:
        TypeVarTuple = ...  # type: ignore
        Unpack = ...  # type: ignore
    typing.TypeVarTuple = TypeVarTuple  # type: ignore
    typing.Unpack = Unpack  # type: ignore

# -----------------------------------------------------------------------------------------------------------------------
# STUB:
# -----------------------------------------------------------------------------------------------------------------------

collections = _collections
copy = _copy
functools = _functools
types = _types
itertools = _itertools
operator = _operator
threading = _threading
os = _os
warnings = _warnings
contextlib = _contextlib
traceback = _traceback
weakref = _weakref
multiprocessing = _multiprocessing
multiprocessing_dummy = _multiprocessing_dummy

copyreg = _copyreg
asyncio = _asyncio
pickle = _pickle
if sys.version_info >= (2, 7):
    OrderedDict = collections.OrderedDict
else:
    OrderedDict = dict

abc = _abc
abc.Sequence.register(collections.deque)

numpy = _numpy
npt = _npt  # Fake, like typing
zip_longest = _zip_longest

numpy_modules: _t.Any = ...
jax_numpy_modules: _t.Any = ...
tee_type: _t.Any = ...
reiterables: _t.Any = ...

Ellipsis = Ellipsis
NotImplemented = NotImplemented
NotImplementedError = NotImplementedError
Exception = Exception
AttributeError = AttributeError
ImportError = ImportError
IndexError = IndexError
KeyError = KeyError
NameError = NameError
TypeError = TypeError
ValueError = ValueError
StopIteration = StopIteration
RuntimeError = RuntimeError
callable = callable
classmethod = classmethod
complex = complex
all = all
any = any
bool = bool
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
globals = globals
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
setattr = setattr
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
