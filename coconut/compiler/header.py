#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Header utilities for the compiler.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from coconut.constants import (
    hash_prefix,
    tabideal,
    default_encoding,
)
from coconut.exceptions import CoconutInternalException
from coconut.compiler.util import get_target_info

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------


def gethash(compiled):
    """Retrieves a hash from a header."""
    lines = compiled.splitlines()
    if len(lines) < 3 or not lines[2].startswith(hash_prefix):
        return None
    else:
        return lines[2][len(hash_prefix):]


def minify(compiled):
    """Performs basic minifications (fails with strings or non-tabideal indentation)."""
    compiled = compiled.strip()
    if compiled:
        out = []
        for line in compiled.splitlines():
            line = line.split("#", 1)[0].rstrip()
            if line:
                ind = 0
                while line.startswith(" "):
                    line = line[1:]
                    ind += 1
                if ind % tabideal != 0:
                    raise CoconutInternalException("invalid indentation in", line)
                out.append(" " * (ind // tabideal) + line)
        compiled = "\n".join(out) + "\n"
    return compiled


def getheader(which, target="", usehash=None):
    """Generates the specified header."""
    if which == "none":
        return ""
    elif which == "initial" or which == "__coconut__":
        if target.startswith("2"):
            header = '#!/usr/bin/env python2'
        elif target.startswith('3'):
            header = '#!/usr/bin/env python3'
        else:
            header = '#!/usr/bin/env python'
        header += '''
# -*- coding: ''' + default_encoding + ''' -*-
'''
        if usehash is not None:
            header += hash_prefix + usehash + '\n'
        if which == "__coconut__":
            header += '# type: ignore\n'
        header += '''
# Compiled with Coconut version ''' + VERSION_STR + '''

'''
        if which == "__coconut__":
            header += r'''"""Built-in Coconut utilities."""

'''
    elif usehash is not None:
        raise CoconutInternalException("can only add a hash to an initial or __coconut__ header, not", which)
    else:
        header = ""
    if which != "initial":
        header += r'''# Coconut Header: --------------------------------------------------------

'''
        if not target.startswith("3"):
            header += r'''from __future__ import print_function, absolute_import, unicode_literals, division
'''
        elif get_target_info(target) >= (3, 5):
            header += r'''from __future__ import generator_stop
'''
        if which == "package":
            header += r'''
import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_tee, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)
'''
        elif which == "sys":
            header += r'''
import sys as _coconut_sys
from coconut.__coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_tee, _coconut_map, _coconut_partial
from coconut.__coconut__ import *
'''
        elif which == "__coconut__" or which == "code" or which == "file":
            header += r'''import sys as _coconut_sys
'''
            if target.startswith("3"):
                header += PY3_HEADER
            elif get_target_info(target) >= (2, 7):
                header += PY27_HEADER
            elif target.startswith("2"):
                header += PY2_HEADER
            else:
                header += PYCHECK_HEADER
            if target.startswith("3"):
                header += r'''
class _coconut:'''
            else:
                header += r'''
class _coconut(object):'''
            header += r'''
    import collections, functools, imp, itertools, operator, types, copy, pickle
'''
            if target.startswith("2"):
                header += r'''    abc = collections'''
            else:
                header += r'''    if _coconut_sys.version_info < (3, 3):
        abc = collections
    else:
        import collections.abc as abc'''
            if target.startswith("3"):
                header += r'''
    IndexError, NameError, ValueError, dict, enumerate, filter, frozenset, getattr, hasattr, hash, isinstance, iter, len, list, map, min, max, next, object, range, reversed, set, slice, str, sum, super, tuple, zip, repr = IndexError, NameError, ValueError, dict, enumerate, filter, frozenset, getattr, hasattr, hash, isinstance, iter, len, list, map, min, max, next, object, range, reversed, set, slice, str, sum, super, tuple, zip, repr'''
            else:
                header += r'''
    IndexError, NameError, ValueError, dict, enumerate, filter, frozenset, getattr, hasattr, hash, isinstance, iter, len, list, map, min, max, next, object, range, reversed, set, slice, str, sum, super, tuple, zip, repr, bytearray = IndexError, NameError, ValueError, dict, enumerate, filter, frozenset, getattr, hasattr, hash, isinstance, iter, len, list, map, min, max, next, object, range, reversed, set, slice, str, sum, super, tuple, zip, staticmethod(repr), bytearray'''
            header += r'''
class MatchError(Exception):
    """Pattern-matching error."""
    __slots__ = ("pattern", "value")
class _coconut_tail_call(Exception):
    __slots__ = ("func", "args", "kwargs")
    def __init__(self, func, *args, **kwargs):
        self.func, self.args, self.kwargs = func, args, kwargs
def _coconut_tco(func):
    @_coconut.functools.wraps(func)
    def tail_call_optimized_func(*args, **kwargs):
        call_func = func
        while True:
            if "_coconut_inside_tco" in kwargs:
                del kwargs["_coconut_inside_tco"]
                return call_func(*args, **kwargs)
            if hasattr(call_func, "_coconut_is_tco"):
                kwargs["_coconut_inside_tco"] = call_func._coconut_is_tco
            try:
                return call_func(*args, **kwargs)
            except _coconut_tail_call as tail_call:
                call_func, args, kwargs = tail_call.func, tail_call.args, tail_call.kwargs
    tail_call_optimized_func._coconut_is_tco = True
    return tail_call_optimized_func
def _coconut_igetitem(iterable, index):
    if isinstance(iterable, (_coconut_reversed, _coconut_map, _coconut.filter, _coconut.zip, _coconut_enumerate, _coconut.abc.Sequence)):
        return iterable[index]
    elif not _coconut.isinstance(index, _coconut.slice):
        if index < 0:
            return _coconut.collections.deque(iterable, maxlen=-index)[0]
        else:
            return _coconut.next(_coconut.itertools.islice(iterable, index, index + 1))
    elif index.start is not None and index.start < 0 and (index.stop is None or index.stop < 0) and index.step is None:
        queue = _coconut.collections.deque(iterable, maxlen=-index.start)
        if index.stop is not None:
            queue = _coconut.tuple(queue)[:index.stop - index.start]
        return queue
    elif (index.start is not None and index.start < 0) or (index.stop is not None and index.stop < 0) or (index.step is not None and index.step < 0):
        return _coconut.tuple(iterable)[index]
    else:
        return _coconut.itertools.islice(iterable, index.start, index.stop, index.step)'''
            if target.startswith("3"):
                header += r'''
class _coconut_compose:'''
            else:
                header += r'''
class _coconut_compose(object):'''
            header += r'''
    __slots__ = ("funcs")
    def __init__(self, *funcs):
        self.funcs = funcs
    def __call__(self, *args, **kwargs):
        arg = self.funcs[-1](*args, **kwargs)
        for f in self.funcs[-2::-1]:
            arg = f(arg)
        return arg
    def __repr__(self):
        return "..".join(_coconut.repr(f) for f in self.funcs)
    def __reduce__(self):
        return (_coconut_compose, self.funcs)
def _coconut_pipe(x, f): return f(x)
def _coconut_starpipe(xs, f): return f(*xs)
def _coconut_backpipe(f, x): return f(x)
def _coconut_backstarpipe(f, xs): return f(*xs)
def _coconut_bool_and(a, b): return a and b
def _coconut_bool_or(a, b): return a or b
def _coconut_minus(*args): return _coconut.operator.neg(*args) if len(args) < 2 else _coconut.operator.sub(*args)
@_coconut.functools.wraps(_coconut.itertools.tee)
def _coconut_tee(iterable, n=2):
    if n >= 0 and _coconut.isinstance(iterable, (_coconut.tuple, _coconut.frozenset)):
        return (iterable,)*n
    elif n > 0 and (_coconut.hasattr(iterable, "__copy__") or _coconut.isinstance(iterable, _coconut.abc.Sequence)):
        return (iterable,) + _coconut.tuple(_coconut.copy.copy(iterable) for i in range(n - 1))
    else:
        return _coconut.itertools.tee(iterable, n)
class _coconut_reversed(object):
    __slots__ = ("_iter",)
    if hasattr(_coconut.map, "__doc__"):
        __doc__ = _coconut.reversed.__doc__
    def __new__(cls, iterable):
        if _coconut.isinstance(iterable, _coconut.range):
            return iterable[::-1]
        elif not _coconut.hasattr(iterable, "__reversed__") or _coconut.isinstance(iterable, (_coconut.list, _coconut.tuple)):
            new_reversed = _coconut.object.__new__(cls)
            new_reversed._iter = iterable
            return new_reversed
        else:
            return _coconut.reversed(iterable)
    def __iter__(self):
        return _coconut.reversed(self._iter)
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return _coconut_igetitem(self._iter, _coconut.slice(-(index.start + 1) if index.start is not None else None, -(index.stop + 1) if index.stop else None, -(index.step if index.step is not None else 1)))
        else:
            return _coconut_igetitem(self._iter, -(index + 1))
    def __reversed__(self):
        return self._iter
    def __len__(self):
        return _coconut.len(self._iter)
    def __repr__(self):
        return "reversed(" + _coconut.repr(self._iter) + ")"
    def __hash__(self):
        return -_coconut.hash(self._iter)
    def __reduce__(self):
        return (self.__class__, (self._iter,))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(_coconut.copy.copy(self._iter))
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._iter == other._iter
    def __contains__(self, elem):
        return elem in self._iter
    def count(self, elem):
        """Count the number of times elem appears in the reversed iterator."""
        return self._iter.count(elem)
    def index(self, elem):
        """Find the index of elem in the reversed iterator."""
        return _coconut.len(self._iter) - self._iter.index(elem) - 1
class _coconut_map(_coconut.map):
    __slots__ = ("_func", "_iters")
    if hasattr(_coconut.map, "__doc__"):
        __doc__ = _coconut.map.__doc__
    def __new__(cls, function, *iterables):
        new_map = _coconut.map.__new__(cls, function, *iterables)
        new_map._func, new_map._iters = function, iterables
        return new_map
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(self._func, *(_coconut_igetitem(i, index) for i in self._iters))
        else:
            return self._func(*(_coconut_igetitem(i, index) for i in self._iters))
    def __reversed__(self):
        return self.__class__(self._func, *(_coconut_reversed(i) for i in self._iters))
    def __len__(self):
        return _coconut.min(_coconut.len(i) for i in self._iters)
    def __repr__(self):
        return "map(" + _coconut.repr(self._func) + ", " + ", ".join((_coconut.repr(i) for i in self._iters)) + ")"
    def __reduce__(self):
        return (self.__class__, (self._func,) + self._iters)
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(self._func, *_coconut_map(_coconut.copy.copy, self._iters))
class parallel_map(_coconut_map):
    """Multiprocessing implementation of map using concurrent.futures.
    Requires arguments to be pickleable."""
    __slots__ = ()
    def __iter__(self):
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor() as executor:
            return _coconut.iter(_coconut.tuple(executor.map(self._func, *self._iters)))
    def __repr__(self):
        return "parallel_" + _coconut_map.__repr__(self)
class concurrent_map(_coconut_map):
    """Multithreading implementation of map using concurrent.futures."""
    __slots__ = ()
    def __iter__(self):
        from concurrent.futures import ThreadPoolExecutor'''
            if get_target_info(target) >= (3, 5):
                header += r'''
        with ThreadPoolExecutor() as executor:'''
            else:
                header += r'''
        from multiprocessing import cpu_count  # cpu_count() * 5 is the default Python 3 thread count
        with ThreadPoolExecutor(cpu_count() * 5) as executor:'''
            header += r'''
            return _coconut.iter(_coconut.tuple(executor.map(self._func, *self._iters)))
    def __repr__(self):
        return "concurrent_" + _coconut_map.__repr__(self)
class filter(_coconut.filter):
    __slots__ = ("_func", "_iter")
    if hasattr(_coconut.filter, "__doc__"):
        __doc__ = _coconut.filter.__doc__
    def __new__(cls, function, iterable):
        new_filter = _coconut.filter.__new__(cls, function, iterable)
        new_filter._func, new_filter._iter = function, iterable
        return new_filter
    def __reversed__(self):
        return self.__class__(self._func, _coconut_reversed(self._iter))
    def __repr__(self):
        return "filter(" + _coconut.repr(self._func) + ", " + _coconut.repr(self._iter) + ")"
    def __reduce__(self):
        return (self.__class__, (self._func, self._iter))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(self._func, _coconut.copy.copy(self._iter))
class zip(_coconut.zip):
    __slots__ = ("_iters",)
    if hasattr(_coconut.zip, "__doc__"):
        __doc__ = _coconut.zip.__doc__
    def __new__(cls, *iterables):
        new_zip = _coconut.zip.__new__(cls, *iterables)
        new_zip._iters = iterables
        return new_zip
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(*(_coconut_igetitem(i, index) for i in self._iters))
        else:
            return _coconut.tuple(_coconut_igetitem(i, index) for i in self._iters)
    def __reversed__(self):
        return self.__class__(*(_coconut_reversed(i) for i in self._iters))
    def __len__(self):
        return _coconut.min(_coconut.len(i) for i in self._iters)
    def __repr__(self):
        return "zip(" + ", ".join((_coconut.repr(i) for i in self._iters)) + ")"
    def __reduce__(self):
        return (self.__class__, self._iters)
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(*_coconut_map(_coconut.copy.copy, self._iters))
class _coconut_enumerate(_coconut.enumerate):
    __slots__ = ("_iter", "_start")
    if hasattr(_coconut.enumerate, "__doc__"):
        __doc__ = _coconut.enumerate.__doc__
    def __new__(cls, iterable, start=0):
        new_enumerate = _coconut.enumerate.__new__(cls, iterable, start)
        new_enumerate._iter, new_enumerate._start = iterable, start
        return new_enumerate
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(_coconut_igetitem(self._iter, index), self._start + (0 if index.start is None else index.start if index.start >= 0 else len(self._iter) + index.start))
        else:
            return (self._start + index, _coconut_igetitem(self._iter, index))
    def __len__(self):
        return _coconut.len(self._iter)
    def __repr__(self):
        return "enumerate(" + _coconut.repr(self._iter) + ", " + _coconut.repr(self._start) + ")"
    def __reduce__(self):
        return (self.__class__, (self._iter, self._start))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(_coconut.copy.copy(self._iter), self._start)'''
            if target.startswith("3"):
                header += r'''
class count:'''
            else:
                header += r'''
class count(object):'''
            header += r'''
    """count(start, step) returns an infinite iterator starting at start and increasing by step."""
    __slots__ = ("_start", "_step")
    def __init__(self, start=0, step=1):
        self._start, self._step = start, step
    def __iter__(self):
        while True:
            yield self._start
            self._start += self._step
    def __contains__(self, elem):
        return elem >= self._start and (elem - self._start) % self._step == 0
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice) and (index.start is None or index.start >= 0) and (index.stop is None or index.stop >= 0):
            if index.stop is None:
                return self.__class__(self._start + (index.start if index.start is not None else 0), self._step * (index.step if index.step is not None else 1))
            else:
                return _coconut.range(self._start + (index.start if index.start is not None else 0), index.stop, self._step * (index.step if index.step is not None else 1))
        elif index >= 0:
            return self._start + index * self._step
        else:
            raise _coconut.IndexError("count indices must be positive")
    def count(self, elem):
        """Count the number of times elem appears in the count."""
        return int(elem in self)
    def index(self, elem):
        """Find the index of elem in the count."""
        if elem not in self:
            raise _coconut.ValueError(_coconut.repr(elem) + " is not in count")
        return (elem - self._start) // self._step
    def __repr__(self):
        return "count(" + _coconut.str(self._start) + ", " + _coconut.str(self._step) + ")"
    def __hash__(self):
        return _coconut.hash((self._start, self._step))
    def __reduce__(self):
        return (self.__class__, (self._start, self._step))
    def __copy__(self):
        return self.__class__(self._start, self._step)
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._start == other._start and self._step == other._step
_coconut.abc.Sequence.register(count)
def recursive_iterator(func):
    """Decorates a function by optimizing it for iterator recursion.
    Requires function arguments to be pickleable."""
    tee_store = {}
    @_coconut.functools.wraps(func)
    def recursive_iterator_func(*args, **kwargs):
        hashable_args_kwargs = _coconut.pickle.dumps((args, kwargs), _coconut.pickle.HIGHEST_PROTOCOL)
        if hashable_args_kwargs in tee_store:
            to_tee = tee_store[hashable_args_kwargs]
        else:
            to_tee = func(*args, **kwargs)
        tee_store[hashable_args_kwargs], to_return = _coconut_tee(to_tee)
        return to_return
    return recursive_iterator_func
def addpattern(base_func):
    """Decorator to add a new case to a pattern-matching function, where the new case is checked last."""
    def pattern_adder(func):
        @_coconut.functools.wraps(func)
        @_coconut_tco
        def add_pattern_func(*args, **kwargs):
            try:
                return base_func(*args, **kwargs)
            except _coconut_MatchError:
                raise _coconut_tail_call(func, *args, **kwargs)
        return add_pattern_func
    return pattern_adder
def prepattern(base_func):
    """Decorator to add a new case to a pattern-matching function, where the new case is checked first."""
    def pattern_prepender(func):
        return addpattern(func)(base_func)
    return pattern_prepender'''
            if target.startswith("3"):
                header += r'''
class _coconut_partial:'''
            else:
                header += r'''
class _coconut_partial(object):'''
            header += r'''
    __slots__ = ("func", "_argdict", "_arglen", "_stargs", "keywords")
    if hasattr(_coconut.functools.partial, "__doc__"):
        __doc__ = _coconut.functools.partial.__doc__
    def __init__(self, func, argdict, arglen, *args, **kwargs):
        self.func, self._argdict, self._arglen, self._stargs, self.keywords = func, argdict, arglen, args, kwargs
    def __reduce__(self):
        return (self.__class__, (self.func, self._argdict, self._arglen) + self._stargs, self.keywords)
    def __setstate__(self, keywords):
        self.keywords = keywords
    @property
    def args(self):
        return _coconut.tuple(self._argdict.get(i) for i in _coconut.range(self._arglen)) + self._stargs
    def __call__(self, *args, **kwargs):
        callargs = []
        argind = 0
        for i in _coconut.range(self._arglen):
            if i in self._argdict:
                callargs.append(self._argdict[i])
            elif argind >= _coconut.len(args):
                raise TypeError("expected at least " + _coconut.str(self._arglen - _coconut.len(self._argdict)) + " argument(s) to " + _coconut.repr(self))
            else:
                callargs.append(args[argind])
                argind += 1
        callargs += self._stargs
        callargs += args[argind:]
        kwargs.update(self.keywords)
        return self.func(*callargs, **kwargs)
    def __repr__(self):
        args = []
        for i in _coconut.range(self._arglen):
            if i in self._argdict:
                args.append(_coconut.repr(self._argdict[i]))
            else:
                args.append("?")
        for arg in self._stargs:
            args.append(_coconut.repr(arg))
        return _coconut.repr(self.func) + "$(" + ", ".join(args) + ")"
def datamaker(data_type):
    """Returns base data constructor of passed data type."""
    return _coconut.functools.partial(_coconut.super(data_type, data_type).__new__, data_type)
def consume(iterable, keep_last=0):
    """Fully exhaust iterable and return the last keep_last elements."""
    return _coconut.collections.deque(iterable, maxlen=keep_last)  # fastest way to exhaust an iterator
_coconut_MatchError, enumerate, reversed, map, reduce, takewhile, dropwhile, tee = MatchError, _coconut_enumerate, _coconut_reversed, _coconut_map, _coconut.functools.reduce, _coconut.itertools.takewhile, _coconut.itertools.dropwhile, _coconut_tee
'''
        else:
            raise CoconutInternalException("invalid header type", which)
        if which == "file" or which == "package":
            header += r'''
# Compiled Coconut: ------------------------------------------------------

'''
    return header
