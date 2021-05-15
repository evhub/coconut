# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: MyPy stub file for __coconut__.py.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

import sys
import typing as _t

if sys.version_info >= (3,):
    from itertools import zip_longest as _zip_longest
else:
    from itertools import izip_longest as _zip_longest

# -----------------------------------------------------------------------------------------------------------------------
# STUB:
# -----------------------------------------------------------------------------------------------------------------------

_Callable = _t.Callable[..., _t.Any]
_Iterable = _t.Iterable[_t.Any]

_T = _t.TypeVar("_T")
_U = _t.TypeVar("_U")
_V = _t.TypeVar("_V")
_W = _t.TypeVar("_W")
_FUNC = _t.TypeVar("_FUNC", bound=_Callable)
_FUNC2 = _t.TypeVar("_FUNC2", bound=_Callable)
_ITER_FUNC = _t.TypeVar("_ITER_FUNC", bound=_t.Callable[..., _Iterable])


if sys.version_info < (3,):
    from future_builtins import *
    from io import open

    str = unicode

    py_raw_input = raw_input
    py_xrange = xrange

    class range(_t.Iterable[int]):
        def __init__(self,
            start: _t.Optional[int] = ...,
            stop: _t.Optional[int] = ...,
            step: _t.Optional[int] = ...,
            ) -> None: ...
        def __iter__(self) -> _t.Iterator[int]: ...
        def __reversed__(self) -> _t.Iterable[int]: ...
        def __len__(self) -> int: ...
        def __contains__(self, elem: int) -> bool: ...

        @_t.overload
        def __getitem__(self, index: int) -> int: ...
        @_t.overload
        def __getitem__(self, index: slice) -> _t.Iterable[int]: ...

        def __hash__(self) -> int: ...
        def count(self, elem: int) -> int: ...
        def index(self, elem: int) -> int: ...
        def __copy__(self) -> range: ...


if sys.version_info < (3, 7):
    def breakpoint(*args: _t.Any, **kwargs: _t.Any) -> _t.Any: ...


py_chr = chr
py_hex = hex
py_input = input
py_int = int
py_map = map
py_object = object
py_oct = oct
py_open = open
py_print = print
py_range = range
py_str = str
py_zip = zip
py_filter = filter
py_reversed = reversed
py_enumerate = enumerate
py_repr = repr
py_breakpoint = breakpoint

# all py_ functions, but not py_ types, go here
chr = chr
hex = hex
input = input
map = map
oct = oct
open = open
print = print
range = range
zip = zip
filter = filter
reversed = reversed
enumerate = enumerate


class _coconut:
    import collections, copy, functools, types, itertools, operator, threading, weakref, os, warnings, contextlib, traceback
    if sys.version_info >= (3, 4):
        import asyncio
    else:
        import trollius as asyncio  # type: ignore
    import pickle
    if sys.version_info >= (2, 7):
        OrderedDict = collections.OrderedDict
    else:
        OrderedDict = dict
    if sys.version_info < (3, 3):
        abc = collections
    else:
        from collections import abc
    typing = _t  # The real _coconut doesn't import typing, but we want type-checkers to treat it as if it does
    zip_longest = staticmethod(_zip_longest)
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
    classmethod = staticmethod(classmethod)
    any = staticmethod(any)
    bytes = bytes
    dict = staticmethod(dict)
    enumerate = staticmethod(enumerate)
    filter = staticmethod(filter)
    float = float
    frozenset = staticmethod(frozenset)
    getattr = staticmethod(getattr)
    hasattr = staticmethod(hasattr)
    hash = staticmethod(hash)
    id = staticmethod(id)
    int = int
    isinstance = staticmethod(isinstance)
    issubclass = staticmethod(issubclass)
    iter = staticmethod(iter)
    len = staticmethod(len)
    list = staticmethod(list)
    locals = staticmethod(locals)
    map = staticmethod(map)
    min = staticmethod(min)
    max = staticmethod(max)
    next = staticmethod(next)
    object = _t.Union[object]
    print = staticmethod(print)
    property = staticmethod(property)
    range = staticmethod(range)
    reversed = staticmethod(reversed)
    set = staticmethod(set)
    slice = slice
    str = str
    sum = staticmethod(sum)
    super = staticmethod(super)
    tuple = staticmethod(tuple)
    type = staticmethod(type)
    zip = staticmethod(zip)
    vars = staticmethod(vars)
    repr = staticmethod(repr)
    if sys.version_info >= (3,):
        bytearray = bytearray


if sys.version_info >= (3, 2):
    from functools import lru_cache as _lru_cache
else:
    from backports.functools_lru_cache import lru_cache as _lru_cache
    _coconut.functools.lru_cache = _lru_cache

zip_longest = _zip_longest
memoize = _lru_cache


reduce = _coconut.functools.reduce
takewhile = _coconut.itertools.takewhile
dropwhile = _coconut.itertools.dropwhile
tee = _coconut.itertools.tee
starmap = _coconut.itertools.starmap


_coconut_tee = tee
_coconut_starmap = starmap
parallel_map = concurrent_map = _coconut_map = map


TYPE_CHECKING = _t.TYPE_CHECKING


_coconut_sentinel = object()


def scan(
    func: _t.Callable[[_T, _U], _T],
    iterable: _t.Iterable[_U],
    initializer: _T = ...,
) -> _t.Iterable[_T]: ...


class MatchError(Exception):
    pattern: _t.Text
    value: _t.Any
    _message: _t.Optional[_t.Text]
    def __init__(self, pattern: _t.Text, value: _t.Any) -> None: ...
    @property
    def message(self) -> _t.Text: ...
_coconut_MatchError = MatchError


def _coconut_get_function_match_error() -> _t.Type[MatchError]: ...


def _coconut_tco(func: _FUNC) -> _FUNC:
    return func


@_t.overload
def _coconut_tail_call(func: _t.Callable[[_T], _U], _x: _T) -> _U: ...
@_t.overload
def _coconut_tail_call(func: _t.Callable[[_T, _U], _V], _x: _T, _y: _U) -> _V: ...
@_t.overload
def _coconut_tail_call(func: _t.Callable[[_T, _U, _V], _W], _x: _T, _y: _U, _z: _V) -> _W: ...
@_t.overload
def _coconut_tail_call(func: _t.Callable[..., _T], *args: _t.Any, **kwargs: _t.Any) -> _T: ...


def recursive_iterator(func: _ITER_FUNC) -> _ITER_FUNC:
    return func


def override(func: _FUNC) -> _FUNC:
    return func

def _coconut_call_set_names(cls: object) -> None: ...


class _coconut_base_pattern_func:
    def __init__(self, *funcs: _Callable) -> None: ...
    def add(self, func: _Callable) -> None: ...
    def __call__(self, *args: _t.Any, **kwargs: _t.Any) -> _t.Any: ...

def addpattern(
    func: _Callable,
    *,
    allow_any_func: bool=False,
    ) -> _t.Callable[[_Callable], _Callable]: ...
_coconut_addpattern = prepattern = addpattern


def _coconut_mark_as_match(func: _FUNC) -> _FUNC:
    return func


class _coconut_partial(_t.Generic[_T]):
    args: _t.Tuple[_t.Any, ...] = ...
    keywords: _t.Dict[_t.Text, _t.Any] = ...
    def __init__(
        self,
        func: _t.Callable[..., _T],
        argdict: _t.Dict[int, _t.Any],
        arglen: int,
        *args: _t.Any,
        **kwargs: _t.Any,
        ) -> None: ...
    def __call__(self, *args: _t.Any, **kwargs: _t.Any) -> _T: ...


@_t.overload
def _coconut_igetitem(
    iterable: _t.Iterable[_T],
    index: int,
    ) -> _T: ...
@_t.overload
def _coconut_igetitem(
    iterable: _t.Iterable[_T],
    index: slice,
    ) -> _t.Iterable[_T]: ...


def _coconut_base_compose(
    func: _t.Callable[[_T], _t.Any],
    *funcstars: _t.Tuple[_Callable, int],
    ) -> _t.Callable[[_T], _t.Any]: ...


@_t.overload
def _coconut_forward_compose(
    _g: _t.Callable[[_T], _U],
    _f: _t.Callable[[_U], _V],
    ) -> _t.Callable[[_T], _V]: ...
@_t.overload
def _coconut_forward_compose(
    _h: _t.Callable[[_T], _U],
    _g: _t.Callable[[_U], _V],
    _f: _t.Callable[[_V], _W],
    ) -> _t.Callable[[_T], _W]: ...
@_t.overload
def _coconut_forward_compose(
    _g: _t.Callable[..., _T],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[..., _U]: ...
@_t.overload
def _coconut_forward_compose(
    _h: _t.Callable[..., _T],
    _g: _t.Callable[[_T], _U],
    _f: _t.Callable[[_U], _V],
    ) -> _t.Callable[..., _V]: ...
@_t.overload
def _coconut_forward_compose(
    _h: _t.Callable[..., _T],
    _g: _t.Callable[[_T], _U],
    _f: _t.Callable[[_U], _V],
    _e: _t.Callable[[_V], _W],
    ) -> _t.Callable[..., _W]: ...
@_t.overload
def _coconut_forward_compose(*funcs: _Callable) -> _Callable: ...

_coconut_forward_star_compose = _coconut_forward_compose
_coconut_forward_dubstar_compose = _coconut_forward_compose


@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_U], _V],
    _g: _t.Callable[[_T], _U],
    ) -> _t.Callable[[_T], _V]: ...
@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_V], _W],
    _g: _t.Callable[[_U], _V],
    _h: _t.Callable[[_T], _U],
    ) -> _t.Callable[[_T], _W]: ...
@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[..., _T],
    ) -> _t.Callable[..., _U]: ...
@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_U], _V],
    _g: _t.Callable[[_T], _U],
    _h: _t.Callable[..., _T],
    ) -> _t.Callable[..., _V]: ...
@_t.overload
def _coconut_back_compose(
    _e: _t.Callable[[_V], _W],
    _f: _t.Callable[[_U], _V],
    _g: _t.Callable[[_T], _U],
    _h: _t.Callable[..., _T],
    ) -> _t.Callable[..., _W]: ...
@_t.overload
def _coconut_back_compose(*funcs: _Callable) -> _Callable: ...

_coconut_back_star_compose = _coconut_back_compose
_coconut_back_dubstar_compose = _coconut_back_compose


def _coconut_pipe(x: _T, f: _t.Callable[[_T], _U]) -> _U: ...
def _coconut_star_pipe(xs: _Iterable, f: _t.Callable[..., _T]) -> _T: ...
def _coconut_dubstar_pipe(kws: _t.Dict[_t.Text, _t.Any], f: _t.Callable[..., _T]) -> _T: ...


def _coconut_back_pipe(f: _t.Callable[[_T], _U], x: _T) -> _U: ...
def _coconut_back_star_pipe(f: _t.Callable[..., _T], xs: _Iterable) -> _T: ...
def _coconut_back_dubstar_pipe(f: _t.Callable[..., _T], kws: _t.Dict[_t.Text, _t.Any]) -> _T: ...


def _coconut_none_pipe(x: _t.Optional[_T], f: _t.Callable[[_T], _U]) -> _t.Optional[_U]: ...
def _coconut_none_star_pipe(xs: _t.Optional[_Iterable], f: _t.Callable[..., _T]) -> _t.Optional[_T]: ...
def _coconut_none_dubstar_pipe(kws: _t.Optional[_t.Dict[_t.Text, _t.Any]], f: _t.Callable[..., _T]) -> _t.Optional[_T]: ...


def _coconut_assert(cond: _t.Any, msg: _t.Optional[_t.Text]=None) -> None:
    assert cond, msg


@_t.overload
def _coconut_bool_and(a: _t.Literal[True], b: _T) -> _T: ...
@_t.overload
def _coconut_bool_and(a: _T, b: _U) -> _t.Union[_T, _U]: ...

@_t.overload
def _coconut_bool_or(a: None, b: _T) -> _T: ...
@_t.overload
def _coconut_bool_or(a: _t.Literal[False], b: _T) -> _T: ...
@_t.overload
def _coconut_bool_or(a: _T, b: _U) -> _t.Union[_T, _U]: ...


@_t.overload
def _coconut_none_coalesce(a: _T, b: None) -> _T: ...
@_t.overload
def _coconut_none_coalesce(a: None, b: _T) -> _T: ...
@_t.overload
def _coconut_none_coalesce(a: _T, b: _U) -> _t.Union[_T, _U]: ...


@_t.overload
def _coconut_minus(a: _T) -> _T: ...
@_t.overload
def _coconut_minus(a: int, b: float) -> float: ...
@_t.overload
def _coconut_minus(a: float, b: int) -> float: ...
@_t.overload
def _coconut_minus(a: _T, _b: _T) -> _T: ...


def reiterable(iterable: _t.Iterable[_T]) -> _t.Iterable[_T]: ...
_coconut_reiterable = reiterable


class _count(_t.Iterable[_T]):
    def __init__(self, start: _T = ..., step: _T = ...) -> None: ...
    def __iter__(self) -> _t.Iterator[_T]: ...
    def __contains__(self, elem: _T) -> bool: ...

    @_t.overload
    def __getitem__(self, index: int) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_T]: ...

    def __hash__(self) -> int: ...
    def count(self, elem: _T) -> int: ...
    def index(self, elem: _T) -> int: ...
    def __copy__(self) -> _count[_T]: ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> _count[_U]: ...
count = _count


def groupsof(n: int, iterable: _t.Iterable[_T]) -> _t.Iterable[_t.Tuple[_T, ...]]: ...


def makedata(data_type: _t.Type[_T], *args: _t.Any) -> _T: ...
def datamaker(data_type: _t.Type[_T]) -> _t.Callable[..., _T]:
    return _coconut.functools.partial(makedata, data_type)


def consume(
    iterable: _t.Iterable[_T],
    keep_last: _t.Optional[int] = ...,
    ) -> _t.Iterable[_T]: ...


def fmap(func: _t.Callable[[_T], _U], obj: _t.Iterable[_T]) -> _t.Iterable[_U]: ...
