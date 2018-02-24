import sys
import typing as _t


_T = _t.TypeVar("_T")
_U = _t.TypeVar("_U")


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

    class range(_t.Iterable[int]):
        def __init__(self,
            start: _t.Optional[int] = ...,
            stop: _t.Optional[int] = ...,
            step: _t.Optional[int] = ...
            ) -> None: ...
        def __iter__(self) -> _t.Iterator[int]: ...
        def __reversed__(self) -> _t.Iterable[int]: ...
        def __len__(self) -> int: ...
        def __contains__(self, elem: int) -> bool: ...
        def __getitem__(self, index: int) -> int: ...
        def __hash__(self) -> int: ...
        def count(self, elem: int) -> int: ...
        def index(self, elem: int) -> int: ...

else:
    import builtins as _b


py_chr, py_filter, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_zip, py_filter, py_reversed, py_enumerate = _b.chr, _b.filter, _b.hex, _b.input, _b.int, _b.map, _b.object, _b.oct, _b.open, _b.print, _b.range, _b.str, _b.zip, _b.filter, _b.reversed, _b.enumerate


def scan(func: _t.Callable[[_T, _U], _T], iterable: _t.Iterable[_U], initializer: _T=None) -> _t.Iterable[_T]: ...


class _coconut:
    typing = _t  # The real _coconut doesn't import typing, but we want type-checkers to treat it as if it does
    import collections, copy, functools, imp, itertools, operator, types, weakref, pickle
    Exception, ImportError, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip = Exception, ImportError, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip
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


_coconut_NamedTuple = _t.NamedTuple
TYPE_CHECKING = _t.TYPE_CHECKING


class MatchError(Exception): ...
_coconut_MatchError = MatchError


class _coconut_tail_call(Exception): ...


def recursive_iterator(func: _T) -> _T: ...
_coconut_tco = recursive_iterator


def addpattern(func: _T) -> _t.Callable[[_U], _t.Union[_T, _U]]: ...
prepattern = addpattern


@overload
def _coconut_igetitem(
    iterable: _t.Iterable[_T],
    index: int,
    ) -> _T: ...
@overload
def _coconut_igetitem(
    iterable: _t.Iterable[_T],
    index: slice,
    ) -> _t.Iterable[_T]: ...


def _coconut_base_compose(func: _t.Callable[[_T], _t.Any], *funcstars: _t.Tuple[_t.Callable, bool]) -> _t.Callable[[_T], _t.Any]: ...


@overload
def _coconut_forward_compose(g: _t.Callable[..., _T], f: _t.Callable[[_T], _U]) -> _t.Callable[..., _U]: ...
@overload
def _coconut_forward_compose(*funcs: _t.Callable) -> _t.Callable: ...
_coconut_forward_star_compose = _coconut_forward_compose


@overload
def _coconut_back_compose(f: _t.Callable[[_T], _U], g: _t.Callable[..., _T]) -> _t.Callable[..., _U]: ...
@overload
def _coconut_back_compose(*funcs: _t.Callable) -> _t.Callable: ...
_coconut_back_star_compose = _coconut_back_compose


def _coconut_pipe(x: _T, f: _t.Callable[[_T], _U]) -> _U: ...
def _coconut_back_pipe(f: _t.Callable[[_T], _U], x: _T) -> _U: ...


def _coconut_star_pipe(xs: _t.Iterable, f: _t.Callable[..., _T]) -> _T: ...
def _coconut_back_star_pipe(f: _t.Callable[..., _T], xs: _t.Iterable) -> _T: ...


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


def makedata(data_type: Type[_T], *args, **kwargs) -> _T: ...
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
        func: _t.Callable,
        argdict: _t.Dict[int, _t.Any],
        arglen: int,
        *args,
        **kwargs,
        ) -> None: ...
    def __call__(self, *args, **kwargs) -> _t.Any: ...


def fmap(func: _t.Callable, obj: _T) -> _T: ...
