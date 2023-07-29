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
    import builtins as _builtins
else:
    import __builtin__ as _builtins

if sys.version_info >= (3,):
    import copyreg as _copyreg
else:
    import copy_reg as _copyreg

if sys.version_info >= (3,):
    from itertools import zip_longest as _zip_longest
else:
    from itertools import izip_longest as _zip_longest

if sys.version_info < (3, 3):
    _abc = _collections
else:
    from collections import abc as _abc

if sys.version_info >= (3, 4):
    import asyncio as _asyncio
else:
    import trollius as _asyncio  # type: ignore

if sys.version_info >= (3, 5):
    import async_generator as _async_generator  # type: ignore

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
asyncio_Return = StopIteration
async_generator = _async_generator
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
pandas_numpy_modules: _t.Any = ...
jax_numpy_modules: _t.Any = ...
tee_type: _t.Any = ...
reiterables: _t.Any = ...
fmappables: _t.Any = ...

Ellipsis = _builtins.Ellipsis
NotImplemented = _builtins.NotImplemented
NotImplementedError = _builtins.NotImplementedError
Exception = _builtins.Exception
AttributeError = _builtins.AttributeError
ImportError = _builtins.ImportError
IndexError = _builtins.IndexError
KeyError = _builtins.KeyError
NameError = _builtins.NameError
TypeError = _builtins.TypeError
ValueError = _builtins.ValueError
StopIteration = _builtins.StopIteration
RuntimeError = _builtins.RuntimeError
callable = _builtins.callable
classmethod = _builtins.classmethod
complex = _builtins.complex
all = _builtins.all
any = _builtins.any
bool = _builtins.bool
bytes = _builtins.bytes
dict = _builtins.dict
enumerate = _builtins.enumerate
filter = _builtins.filter
float = _builtins.float
frozenset = _builtins.frozenset
getattr = _builtins.getattr
hasattr = _builtins.hasattr
hash = _builtins.hash
id = _builtins.id
int = _builtins.int
isinstance = _builtins.isinstance
issubclass = _builtins.issubclass
iter = _builtins.iter
len: _t.Callable[..., int] = ...  # pattern-matching needs an untyped _coconut.len to avoid type errors
list = _builtins.list
locals = _builtins.locals
globals = _builtins.globals
map = _builtins.map
min = _builtins.min
max = _builtins.max
next = _builtins.next
object = _builtins.object
print = _builtins.print
property = _builtins.property
range = _builtins.range
reversed = _builtins.reversed
set = _builtins.set
setattr = _builtins.setattr
slice = _builtins.slice
str = _builtins.str
sum = _builtins.sum
super = _builtins.super
tuple = _builtins.tuple
type = _builtins.type
zip = _builtins.zip
vars = _builtins.vars
repr = _builtins.repr
if sys.version_info >= (3,):
    bytearray = _builtins.bytearray
