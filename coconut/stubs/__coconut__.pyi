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

# -----------------------------------------------------------------------------------------------------------------------
# STUB:
# -----------------------------------------------------------------------------------------------------------------------


_T = _t.TypeVar("_T")
_U = _t.TypeVar("_U")
_V = _t.TypeVar("_V")
_W = _t.TypeVar("_W")
_FUNC = _t.TypeVar("_FUNC", bound=_t.Callable)
_FUNC2 = _t.TypeVar("_FUNC2", bound=_t.Callable)
_ITER_FUNC = _t.TypeVar("_ITER_FUNC", bound=_t.Callable[..., _t.Iterable])


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
        def __getitem__(self, index: int) -> int: ...
        def __hash__(self) -> int: ...
        def count(self, elem: int) -> int: ...
        def index(self, elem: int) -> int: ...


if sys.version_info < (3, 7):
    def breakpoint(*args, **kwargs) -> _t.Any: ...


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


def scan(
    func: _t.Callable[[_T, _U], _T],
    iterable: _t.Iterable[_U],
    initializer: _T = ...,
    ) -> _t.Iterable[_T]: ...


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
    if sys.version_info >= (3,):
        zip_longest = itertools.zip_longest
    else:
        zip_longest = itertools.izip_longest
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
    classmethod = classmethod
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
    len = len
    list = staticmethod(list)
    locals = locals
    map = map
    min = min
    max = max
    next = next
    object = _t.Union[object]
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
    repr = staticmethod(repr)
    if sys.version_info >= (3,):
        bytearray = bytearray


reduce = _coconut.functools.reduce
takewhile = _coconut.itertools.takewhile
dropwhile = _coconut.itertools.dropwhile
tee = _coconut.itertools.tee
starmap = _coconut.itertools.starmap


if sys.version_info >= (3, 2):
    from functools import lru_cache
else:
    from backports.functools_lru_cache import lru_cache  # type: ignore
    _coconut.functools.lru_cache = memoize  # type: ignore
memoize = lru_cache


_coconut_tee = tee
_coconut_starmap = starmap
parallel_map = concurrent_map = _coconut_map = map


TYPE_CHECKING = _t.TYPE_CHECKING


_coconut_sentinel = object()


class MatchError(Exception):
    pattern: _t.Text
    value: _t.Any
    _message: _t.Optional[_t.Text]
    def __init__(self, pattern: _t.Text, value: _t.Any): ...
    @property
    def message(self) -> _t.Text: ...
_coconut_MatchError = MatchError


def _coconut_get_function_match_error() -> _t.Type[MatchError]: ...


def _coconut_tco(func: _FUNC) -> _FUNC:
    return func
def _coconut_tail_call(func, *args, **kwargs):
    return func(*args, **kwargs)


def recursive_iterator(func: _ITER_FUNC) -> _ITER_FUNC:
    return func


def override(func: _FUNC) -> _FUNC:
    return func

def _coconut_call_set_names(cls: object): ...


class _coconut_base_pattern_func:
    def __init__(self, *funcs: _t.Callable): ...
    def add(self, func: _t.Callable) -> None: ...
    def __call__(self, *args, **kwargs) -> _t.Any: ...

def addpattern(
    func: _FUNC,
    *,
    allow_any_func: bool=False,
    ) -> _t.Callable[[_FUNC2], _t.Union[_FUNC, _FUNC2]]: ...
_coconut_addpattern = prepattern = addpattern


def _coconut_mark_as_match(func: _FUNC) -> _FUNC:
    return func


class _coconut_partial:
    args: _t.Tuple = ...
    keywords: _t.Dict[_t.Text, _t.Any] = ...
    def __init__(
        self,
        func: _t.Callable[..., _T],
        argdict: _t.Dict[int, _t.Any],
        arglen: int,
        *args,
        **kwargs,
        ) -> None: ...
    def __call__(self, *args, **kwargs) -> _T: ...


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
    *funcstars: _t.Tuple[_t.Callable, int],
    ) -> _t.Callable[[_T], _t.Any]: ...


@_t.overload
def _coconut_forward_compose(
    g: _t.Callable[..., _T],
    f: _t.Callable[[_T], _U],
    ) -> _t.Callable[..., _U]: ...
@_t.overload
def _coconut_forward_compose(
    h: _t.Callable[..., _T],
    g: _t.Callable[[_T], _U],
    f: _t.Callable[[_U], _V],
    ) -> _t.Callable[..., _V]: ...
@_t.overload
def _coconut_forward_compose(
    h: _t.Callable[..., _T],
    g: _t.Callable[[_T], _U],
    f: _t.Callable[[_U], _V],
    e: _t.Callable[[_V], _W],
    ) -> _t.Callable[..., _W]: ...
@_t.overload
def _coconut_forward_compose(*funcs: _t.Callable) -> _t.Callable: ...

_coconut_forward_star_compose = _coconut_forward_compose
_coconut_forward_dubstar_compose = _coconut_forward_compose


@_t.overload
def _coconut_back_compose(
    f: _t.Callable[[_T], _U],
    g: _t.Callable[..., _T],
    ) -> _t.Callable[..., _U]: ...
@_t.overload
def _coconut_back_compose(
    f: _t.Callable[[_U], _V],
    g: _t.Callable[[_T], _U],
    h: _t.Callable[..., _T],
    ) -> _t.Callable[..., _V]: ...
@_t.overload
def _coconut_back_compose(
    e: _t.Callable[[_V], _W],
    f: _t.Callable[[_U], _V],
    g: _t.Callable[[_T], _U],
    h: _t.Callable[..., _T],
    ) -> _t.Callable[..., _W]: ...
@_t.overload
def _coconut_back_compose(*funcs: _t.Callable) -> _t.Callable: ...

_coconut_back_star_compose = _coconut_back_compose
_coconut_back_dubstar_compose = _coconut_back_compose


def _coconut_pipe(x: _T, f: _t.Callable[[_T], _U]) -> _U: ...
def _coconut_star_pipe(xs: _t.Iterable, f: _t.Callable[..., _T]) -> _T: ...
def _coconut_dubstar_pipe(kws: _t.Dict[_t.Text, _t.Any], f: _t.Callable[..., _T]) -> _T: ...


def _coconut_back_pipe(f: _t.Callable[[_T], _U], x: _T) -> _U: ...
def _coconut_back_star_pipe(f: _t.Callable[..., _T], xs: _t.Iterable) -> _T: ...
def _coconut_back_dubstar_pipe(f: _t.Callable[..., _T], kws: _t.Dict[_t.Text, _t.Any]) -> _T: ...


def _coconut_none_pipe(x: _t.Optional[_T], f: _t.Callable[[_T], _U]) -> _t.Optional[_U]: ...
def _coconut_none_star_pipe(xs: _t.Optional[_t.Iterable], f: _t.Callable[..., _T]) -> _t.Optional[_T]: ...
def _coconut_none_dubstar_pipe(kws: _t.Optional[_t.Dict[_t.Text, _t.Any]], f: _t.Callable[..., _T]) -> _t.Optional[_T]: ...


def _coconut_assert(cond, msg: _t.Optional[_t.Text]=None):
    assert cond, msg


def _coconut_bool_and(a, b):
    return a and b
def _coconut_bool_or(a, b):
    return a or b


def _coconut_none_coalesce(a, b):
    return a if a is not None else b


def _coconut_minus(a, *rest):
    if not rest:
        return -a
    for b in rest:
        a -= b
    return a


def reiterable(iterable: _t.Iterable[_T]) -> _t.Iterable[_T]: ...
_coconut_reiterable = reiterable


class count(_t.Iterable[int]):
    def __init__(self, start: int = ..., step: int = ...) -> None: ...
    def __iter__(self) -> _t.Iterator[int]: ...
    def __contains__(self, elem: int) -> bool: ...
    def __getitem__(self, index: int) -> int: ...
    def __hash__(self) -> int: ...
    def count(self, elem: int) -> int: ...
    def index(self, elem: int) -> int: ...


def groupsof(n: int, iterable: _t.Iterable[_T]) -> _t.Iterable[_t.Tuple[_T, ...]]: ...


def makedata(data_type: _t.Type[_T], *args) -> _T: ...
def datamaker(data_type):
    return _coconut.functools.partial(makedata, data_type)


def consume(
    iterable: _t.Iterable[_T],
    keep_last: _t.Optional[int] = ...,
    ) -> _t.Iterable[_T]: ...


def fmap(func: _t.Callable, obj: _t.Iterable) -> _t.Iterable: ...
