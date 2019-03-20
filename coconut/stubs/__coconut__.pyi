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


py_chr, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_zip, py_filter, py_reversed, py_enumerate = chr, hex, input, int, map, object, oct, open, print, range, str, zip, filter, reversed, enumerate


def scan(
    func: _t.Callable[[_T, _U], _T],
    iterable: _t.Iterable[_U],
    initializer: _T = ...,
    ) -> _t.Iterable[_T]: ...


class _coconut:
    typing = _t  # The real _coconut doesn't import typing, but we want type-checkers to treat it as if it does
    import collections, copy, functools, types, itertools, operator, types, weakref
    import pickle
    Ellipsis, Exception, ImportError, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, float, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip, repr = Ellipsis, Exception, ImportError, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, float, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip, repr
    if sys.version_info >= (3, 4):
        import asyncio
    else:
        import trollius as asyncio  # type: ignore
    if sys.version_info < (3, 3):
        abc = collections
    else:
        abc = collections.abc
    if sys.version_info >= (3,):
        bytearray = bytearray
    if sys.version_info >= (2, 7):
        OrderedDict = collections.OrderedDict
    else:
        OrderedDict = dict


reduce = _coconut.functools.reduce
takewhile = _coconut.itertools.takewhile
dropwhile = _coconut.itertools.dropwhile
tee = _coconut.itertools.tee
starmap = _coconut.itertools.starmap


if sys.version_info >= (3, 2):
    memoize = _coconut.functools.lru_cache
else:
    from backports.functools_lru_cache import lru_cache as memoize  # type: ignore
    _coconut.functools.lru_cache = memoize  # type: ignore


_coconut_tee = tee
_coconut_starmap = starmap
parallel_map = concurrent_map = _coconut_map = map


_coconut_sentinel = object()


TYPE_CHECKING = _t.TYPE_CHECKING


class MatchError(Exception): ...
_coconut_MatchError = MatchError


def _coconut_get_function_match_error() -> _t.Type[MatchError]: ...


def _coconut_tco(func: _FUNC) -> _FUNC: ...
def _coconut_tail_call(func, *args, **kwargs):
    return func(*args, **kwargs)


def recursive_iterator(func: _ITER_FUNC) -> _ITER_FUNC: ...


def addpattern(func: _FUNC) -> _t.Callable[[_FUNC2], _t.Union[_FUNC, _FUNC2]]: ...
_coconut_addpattern = prepattern = addpattern


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
def _coconut_back_pipe(f: _t.Callable[[_T], _U], x: _T) -> _U: ...


def _coconut_star_pipe(xs: _t.Iterable, f: _t.Callable[..., _T]) -> _T: ...
def _coconut_back_star_pipe(f: _t.Callable[..., _T], xs: _t.Iterable) -> _T: ...


def _coconut_dubstar_pipe(kws: _t.Dict[_t.Text, _t.Any], f: _t.Callable[..., _T]) -> _T: ...
def _coconut_back_dubstar_pipe(f: _t.Callable[..., _T], kws: _t.Dict[_t.Text, _t.Any]) -> _T: ...


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


def fmap(func: _t.Callable, obj: _t.Iterable) -> _t.Iterable: ...
