import sys
from typing import (
    TypeVar,
    Callable,
    overload,
    Iterable,
    Text,
    Any,
    Optional,
    Union,
)


_T = TypeVar('_T')
_S = TypeVar('_S')


if sys.version_info < (3,):
    from future_builtins import *  # type: ignore
from functools import reduce
from itertools import takewhile, dropwhile, tee


_coconut_tee = tee
parallel_map = concurrent_map = _coconut_map = map


class _coconut:
    import collections, functools, imp, itertools, operator, types, copy, pickle
    if sys.version_info < (3, 3):
        abc = collections
    else:
        import collections.abc as abc  # type: ignore
    IndexError, NameError, ValueError, map, zip, dict, frozenset, getattr, hasattr, hash, isinstance, iter, len, list, min, next, object, range, reversed, set, slice, super, tuple, repr = IndexError, NameError, ValueError, map, zip, dict, frozenset, getattr, hasattr, hash, isinstance, iter, len, list, min, next, object, range, reversed, set, slice, super, tuple, repr


class _coconut_MatchError(Exception): ...
MatchError = _coconut_MatchError


class _coconut_tail_call(Exception): ...


def recursive_iterator(func: Callable[..., Iterable[_S]]) -> Callable[..., Iterable[_S]]: ...
def _coconut_tco(func: Callable[..., _T]) -> Callable[..., _T]: ...
addpattern = prepattern = _coconut_tco


@overload
def _coconut_igetitem(
    iterable: Iterable[_T],
    index: int
    ) -> _T: ...
@overload
def _coconut_igetitem(
    iterable: Iterable[_T],
    index: slice
    ) -> Iterable[_T]: ...


class _coconut_compose:
    def __init__(self, *funcs: Callable) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


def _coconut_pipe(x: _T, f: Callable[[_T], _S]) -> _S: ...
def _coconut_backpipe(f: Callable[[_T], _S], x: _T) -> _S: ...


def _coconut_starpipe(xs: Iterable, f: Callable[..., _T]) -> _T: ...
def _coconut_backstarpipe(f: Callable[..., _T], xs: Iterable) -> _T: ...


def _coconut_bool_and(a: Any, b: Any) -> bool: ...
def _coconut_bool_or(a: Any, b: Any) -> bool: ...


@overload
def _coconut_minus(a: _T) -> _T: ...
@overload
def _coconut_minus(a: _T, b: _S) -> Union[_T, _S]: ...


class count:
    def __init__(self, start: int = ..., step: int = ...) -> None: ...
    def __iter__(self) -> Iterable[int]: ...
    def __contains__(self, elem: int) -> bool: ...
    def __getitem__(self, index: int) -> int: ...
    def __hash__(self) -> int: ...
    def count(self, elem: int) -> int: ...
    def index(self, elem: int) -> int: ...


def datamaker(data_type: Any) -> Callable: ...


def consume(
    iterable: Iterable[_T],
    keep_last: Optional[int] = ...
    ) -> Iterable[_T]: ...
