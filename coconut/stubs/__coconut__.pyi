import sys
from typing import *


_T = TypeVar('_T')
_S = TypeVar('_S')


if sys.version_info < (3,):
    import io as _io
    import future_builtins as _fb
    import __builtin__ as _b

    str = unicode
    open = _io.open
    ascii = _fb.ascii
    filter = _fb.filter
    hex = _fb.hex
    map = _fb.map
    oct = _fb.oct
    zip = _fb.zip

    py_raw_input, py_xrange = _b.raw_input, _b.xrange

    class range(Iterable[int]):
        def __init__(self,
            start: Optional[int] = ...,
            stop: Optional[int] = ...,
            step: Optional[int] = ...
            ) -> None: ...
        def __iter__(self) -> Iterator[int]: ...
        def __reversed__(self) -> Iterable[int]: ...
        def __len__(self) -> int: ...
        def __contains__(self, elem: int) -> bool: ...
        def __getitem__(self, index: int) -> int: ...
        def __hash__(self) -> int: ...
        def count(self, elem: int) -> int: ...
        def index(self, elem: int) -> int: ...

else:
    import builtins as _b


py_chr, py_filter, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_zip, py_filter, py_reversed, py_enumerate = _b.chr, _b.filter, _b.hex, _b.input, _b.int, _b.map, _b.object, _b.oct, _b.open, _b.print, _b.range, _b.str, _b.zip, _b.filter, _b.reversed, _b.enumerate


def scan(func: Callable[[_T, _T], _T], iterable: Iterable[_T]) -> Iterable[_T]: ...


class _coconut:
    # The real _coconut doesn't import typing, but we want type-checkers to treat it as if it does
    import typing

    import collections, copy, functools, imp, itertools, operator, types, weakref, pickle
    Exception, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip = Exception, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip
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


_coconut_tee = tee
_coconut_starmap = starmap
parallel_map = concurrent_map = _coconut_map = map


_coconut_NamedTuple = _coconut.typing.NamedTuple


class MatchError(Exception): ...
_coconut_MatchError = MatchError


class _coconut_tail_call(Exception): ...


def recursive_iterator(func: Callable[..., Iterable[_S]]) -> Callable[..., Iterable[_S]]: ...
def addpattern(func: Callable[..., _T]) -> Callable[..., _T]: ...
_coconut_tco = prepattern = addpattern


@overload
def _coconut_igetitem(
    iterable: Iterable[_T],
    index: int,
    ) -> _T: ...
@overload
def _coconut_igetitem(
    iterable: Iterable[_T],
    index: slice,
    ) -> Iterable[_T]: ...


class _coconut_base_compose:
    def __init__(self, func: Callable, *funcstars: Tuple[Callable, bool]) -> None: ...
    def __call__(self, *args, **kwargs) -> Any: ...


@overload
def _coconut_forward_compose(g: Callable[..., _T], f: Callable[[_T], _S]) -> Callable[..., _S]: ...
@overload
def _coconut_forward_compose(*funcs: Callable) -> Callable: ...
_coconut_forward_star_compose = _coconut_forward_compose


@overload
def _coconut_back_compose(f: Callable[[_T], _S], g: Callable[..., _T]) -> Callable[..., _S]: ...
@overload
def _coconut_back_compose(*funcs: Callable) -> Callable: ...
_coconut_back_star_compose = _coconut_back_compose


def _coconut_pipe(x: _T, f: Callable[[_T], _S]) -> _S: ...
def _coconut_back_pipe(f: Callable[[_T], _S], x: _T) -> _S: ...


def _coconut_star_pipe(xs: Iterable, f: Callable[..., _T]) -> _T: ...
def _coconut_back_star_pipe(f: Callable[..., _T], xs: Iterable) -> _T: ...


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


def reiterable(iterable: Iterable[_T]) -> Iterable[_T]: ...


class count(Iterable[int]):
    def __init__(self, start: int = ..., step: int = ...) -> None: ...
    def __iter__(self) -> Iterator[int]: ...
    def __contains__(self, elem: int) -> bool: ...
    def __getitem__(self, index: int) -> int: ...
    def __hash__(self) -> int: ...
    def count(self, elem: int) -> int: ...
    def index(self, elem: int) -> int: ...


def groupsof(n: int, iterable: Iterable[_T]) -> Iterable[Tuple[_T, ...]]: ...


def makedata(data_type, *args, **kwargs): ...
def datamaker(data_type) -> Callable: ...


def consume(
    iterable: Iterable[_T],
    keep_last: Optional[int] = ...,
    ) -> Iterable[_T]: ...


class _coconut_partial:
    args: Tuple = ...
    keywords: Dict[Text, Any] = ...
    def __init__(
        self,
        func: Callable,
        argdict: Dict[int, Any],
        arglen: int,
        *args,
        **kwargs,
        ) -> None: ...
    def __call__(self, *args, **kwargs) -> Any: ...


def fmap(func: Callable, obj: _T) -> _T: ...
