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
    Dict,
    Tuple,
    Text,
)


_T = TypeVar('_T')
_S = TypeVar('_S')


if sys.version_info >= (3,):
    import builtins as _b
    ascii, filter, hex, map, oct, zip, open, chr, str, range = _b.ascii, _b.filter, _b.hex, _b.map, _b.oct, _b.zip, _b.open, _b.chr, _b.str, _b.range

else:
    import __builtin__ as _b
    from future_builtins import *  # type: ignore
    from io import open

    py_raw_input, py_xrange = _b.raw_input, _b.xrange
    chr, str = _b.unichr, _b.unicode

    class range:
        def __init__(self,
            start: Optional[int] = ...,
            stop: Optional[int] = ...,
            step: Optional[int] = ...
            ) -> None: ...
        def __iter__(self) -> Iterable[int]: ...
        def __reversed__(self) -> Iterable[int]: ...
        def __len__(self) -> int: ...
        def __contains__(self, elem: int) -> bool: ...
        def __getitem__(self, index: int) -> int: ...
        def __hash__(self) -> int: ...
        def count(self, elem: int) -> int: ...
        def index(self, elem: int) -> int: ...


py_chr, py_filter, py_hex, py_input, py_int, py_map, py_oct, py_open, py_print, py_range, py_str, py_zip, py_filter, py_reversed, py_enumerate = _b.chr, _b.filter, _b.hex, _b.input, _b.int, _b.map, _b.oct, _b.open, _b.print, _b.range, _b.str, _b.zip, _b.filter, _b.reversed, _b.enumerate


from functools import reduce
from itertools import takewhile, dropwhile, tee


_coconut_tee = tee
parallel_map = concurrent_map = _coconut_map = map


class _coconut:
    import collections, functools, imp, itertools, operator, types, copy, pickle
    IndexError, NameError, ValueError, map, zip, dict, frozenset, getattr, hasattr, hash, isinstance, iter, len, list, min, max, next, object, range, reversed, set, slice, str, sum, super, tuple, repr = IndexError, NameError, ValueError, map, zip, dict, frozenset, getattr, hasattr, hash, isinstance, iter, len, list, min, max, next, object, range, reversed, set, slice, str, sum, super, tuple, repr
    if sys.version_info < (3, 3):
        abc = collections
    else:
        bytearray, repr = bytearray, repr
        import collections.abc as abc  # type: ignore


class MatchError(Exception): ...
_coconut_MatchError = MatchError


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


def _coconut_compose(*funcs: Callable) -> Callable[..., Any]: ...


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


class _coconut_partial:
    args = ...  # type: Tuple
    keywords = ...  # type: Dict[Text, Any]
    def __init__(self, func: Callable, argdict: Dict[int, Any], arglen: int, *args, **kwargs) -> None: ...
    def __call__(self, *args, **kwargs) -> Any: ...
