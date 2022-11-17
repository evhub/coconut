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

import _coconut as __coconut  # we mock _coconut as a package since mypy doesn't handle namespace classes very well
_coconut = __coconut

if sys.version_info >= (3, 2):
    from functools import lru_cache as _lru_cache
else:
    from backports.functools_lru_cache import lru_cache as _lru_cache  # `pip install -U coconut[mypy]` to fix errors on this line
    _coconut.functools.lru_cache = _lru_cache  # type: ignore

# -----------------------------------------------------------------------------------------------------------------------
# TYPE VARS:
# -----------------------------------------------------------------------------------------------------------------------

_Callable = _t.Callable[..., _t.Any]
_Iterable = _t.Iterable[_t.Any]
_Tuple = _t.Tuple[_t.Any, ...]
_Sequence = _t.Sequence[_t.Any]

_T = _t.TypeVar("_T")
_U = _t.TypeVar("_U")
_V = _t.TypeVar("_V")
_W = _t.TypeVar("_W")
_Xco = _t.TypeVar("_Xco", covariant=True)
_Yco = _t.TypeVar("_Yco", covariant=True)
_Zco = _t.TypeVar("_Zco", covariant=True)
_Tco = _t.TypeVar("_Tco", covariant=True)
_Uco = _t.TypeVar("_Uco", covariant=True)
_Vco = _t.TypeVar("_Vco", covariant=True)
_Wco = _t.TypeVar("_Wco", covariant=True)
_Tcontra = _t.TypeVar("_Tcontra", contravariant=True)
_Tfunc = _t.TypeVar("_Tfunc", bound=_Callable)
_Ufunc = _t.TypeVar("_Ufunc", bound=_Callable)
_Titer = _t.TypeVar("_Titer", bound=_Iterable)
_T_iter_func = _t.TypeVar("_T_iter_func", bound=_t.Callable[..., _Iterable])

_P = _t.ParamSpec("_P")

# -----------------------------------------------------------------------------------------------------------------------
# STUB:
# -----------------------------------------------------------------------------------------------------------------------

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

    def _coconut_exec(obj: _t.Any, globals: _t.Dict[_t.Text, _t.Any] = None, locals: _t.Dict[_t.Text, _t.Any] = None) -> None: ...

else:
    _coconut_exec = exec

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
py_super = super
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


_coconut_py_str = py_str
_coconut_super = super


zip_longest = _coconut.zip_longest
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


_coconut_sentinel: _t.Any = ...


def scan(
    func: _t.Callable[[_T, _Uco], _T],
    iterable: _t.Iterable[_Uco],
    initial: _T = ...,
) -> _t.Iterable[_T]: ...


class MatchError(Exception):
    pattern: _t.Optional[_t.Text]
    value: _t.Any
    def __init__(self, pattern: _t.Optional[_t.Text] = None, value: _t.Any = None) -> None: ...
    @property
    def message(self) -> _t.Text: ...
_coconut_MatchError = MatchError


def _coconut_get_function_match_error() -> _t.Type[MatchError]: ...


def _coconut_tco(func: _Tfunc) -> _Tfunc:
    return func


@_t.overload
def _coconut_tail_call(
    _func: _t.Callable[[_T], _Uco],
    _x: _T,
) -> _Uco: ...
@_t.overload
def _coconut_tail_call(
    _func: _t.Callable[[_T, _U], _Vco],
    _x: _T,
    _y: _U,
) -> _Vco: ...
@_t.overload
def _coconut_tail_call(
    _func: _t.Callable[[_T, _U, _V], _Wco],
    _x: _T,
    _y: _U,
    _z: _V,
) -> _Wco: ...
@_t.overload
def _coconut_tail_call(
    _func: _t.Callable[_t.Concatenate[_T, _P], _Uco],
    _x: _T,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _Uco: ...
@_t.overload
def _coconut_tail_call(
    _func: _t.Callable[_t.Concatenate[_T, _U, _P], _Vco],
    _x: _T,
    _y: _U,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _Vco: ...
@_t.overload
def _coconut_tail_call(
    _func: _t.Callable[_t.Concatenate[_T, _U, _V, _P], _Wco],
    _x: _T,
    _y: _U,
    _z: _V,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _Wco: ...
@_t.overload
def _coconut_tail_call(
    _func: _t.Callable[..., _Tco],
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _Tco: ...


of = _coconut_tail_call


def recursive_iterator(func: _T_iter_func) -> _T_iter_func:
    return func


try:
    from typing_extensions import override as _override  # type: ignore
    override = _override
except ImportError:
    def override(func: _Tfunc) -> _Tfunc:
        return func

def _coconut_call_set_names(cls: object) -> None: ...


class _coconut_base_pattern_func:
    def __init__(self, *funcs: _Callable) -> None: ...
    def add(self, func: _Callable) -> None: ...
    def __call__(self, *args: _t.Any, **kwargs: _t.Any) -> _t.Any: ...

@_t.overload
def addpattern(
    base_func: _Callable,
    new_pattern: None = None,
    *,
    allow_any_func: bool=False,
    ) -> _t.Callable[[_Callable], _Callable]: ...
@_t.overload
def addpattern(
    base_func: _Callable,
    new_pattern: _Callable,
    *,
    allow_any_func: bool=False,
    ) -> _Callable: ...
_coconut_addpattern = prepattern = addpattern


def _coconut_mark_as_match(func: _Tfunc) -> _Tfunc:
    return func


class _coconut_partial(_t.Generic[_T]):
    args: _Tuple = ...
    keywords: _t.Dict[_t.Text, _t.Any] = ...
    def __init__(
        self,
        _coconut_func: _t.Callable[..., _T],
        _coconut_argdict: _t.Dict[int, _t.Any],
        _coconut_arglen: int,
        _coconut_pos_kwargs: _t.Sequence[_t.Text],
        *args: _t.Any,
        **kwargs: _t.Any,
        ) -> None: ...
    def __call__(self, *args: _t.Any, **kwargs: _t.Any) -> _T: ...


@_t.overload
def _coconut_iter_getitem(
    iterable: _t.Iterable[_T],
    index: int,
    ) -> _T: ...
@_t.overload
def _coconut_iter_getitem(
    iterable: _t.Iterable[_T],
    index: slice,
    ) -> _t.Iterable[_T]: ...


def _coconut_base_compose(
    func: _t.Callable[[_T], _t.Any],
    *funcstars: _t.Tuple[_Callable, int],
    ) -> _t.Callable[[_T], _t.Any]: ...


# @_t.overload
# def _coconut_forward_compose(
#     _g: _t.Callable[[_T], _Uco],
#     _f: _t.Callable[[_Uco], _Vco],
#     ) -> _t.Callable[[_T], _Vco]: ...
# @_t.overload
# def _coconut_forward_compose(
#     _g: _t.Callable[[_T, _U], _Vco],
#     _f: _t.Callable[[_Vco], _Wco],
#     ) -> _t.Callable[[_T, _U], _Wco]: ...
# @_t.overload
# def _coconut_forward_compose(
#     _h: _t.Callable[[_T], _Uco],
#     _g: _t.Callable[[_Uco], _Vco],
#     _f: _t.Callable[[_Vco], _Wco],
#     ) -> _t.Callable[[_T], _Wco]: ...
@_t.overload
def _coconut_forward_compose(
    _g: _t.Callable[_P, _Tco],
    _f: _t.Callable[[_Tco], _Uco],
    ) -> _t.Callable[_P, _Uco]: ...
@_t.overload
def _coconut_forward_compose(
    _h: _t.Callable[_P, _Tco],
    _g: _t.Callable[[_Tco], _Uco],
    _f: _t.Callable[[_Uco], _Vco],
    ) -> _t.Callable[_P, _Vco]: ...
@_t.overload
def _coconut_forward_compose(
    _h: _t.Callable[_P, _Tco],
    _g: _t.Callable[[_Tco], _Uco],
    _f: _t.Callable[[_Uco], _Vco],
    _e: _t.Callable[[_Vco], _Wco],
    ) -> _t.Callable[_P, _Wco]: ...
@_t.overload
def _coconut_forward_compose(
    _g: _t.Callable[..., _Tco],
    _f: _t.Callable[[_Tco], _Uco],
    ) -> _t.Callable[..., _Uco]: ...
@_t.overload
def _coconut_forward_compose(
    _h: _t.Callable[..., _Tco],
    _g: _t.Callable[[_Tco], _Uco],
    _f: _t.Callable[[_Uco], _Vco],
    ) -> _t.Callable[..., _Vco]: ...
@_t.overload
def _coconut_forward_compose(
    _h: _t.Callable[..., _Tco],
    _g: _t.Callable[[_Tco], _Uco],
    _f: _t.Callable[[_Uco], _Vco],
    _e: _t.Callable[[_Vco], _Wco],
    ) -> _t.Callable[..., _Wco]: ...
@_t.overload
def _coconut_forward_compose(*funcs: _Callable) -> _Callable: ...

_coconut_forward_star_compose = _coconut_forward_compose
_coconut_forward_dubstar_compose = _coconut_forward_compose


@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_Uco], _Vco],
    _g: _t.Callable[[_Tco], _Uco],
    ) -> _t.Callable[[_Tco], _Vco]: ...
@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_Vco], _Wco],
    _g: _t.Callable[[_Uco], _Vco],
    _h: _t.Callable[[_Tco], _Uco],
    ) -> _t.Callable[[_Tco], _Wco]: ...
@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_Tco], _Uco],
    _g: _t.Callable[..., _Tco],
    ) -> _t.Callable[..., _Uco]: ...
@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_Uco], _Vco],
    _g: _t.Callable[[_Tco], _Uco],
    _h: _t.Callable[..., _Tco],
    ) -> _t.Callable[..., _Vco]: ...
@_t.overload
def _coconut_back_compose(
    _e: _t.Callable[[_Vco], _Wco],
    _f: _t.Callable[[_Uco], _Vco],
    _g: _t.Callable[[_Tco], _Uco],
    _h: _t.Callable[..., _Tco],
    ) -> _t.Callable[..., _Wco]: ...
@_t.overload
def _coconut_back_compose(*funcs: _Callable) -> _Callable: ...

_coconut_back_star_compose = _coconut_back_compose
_coconut_back_dubstar_compose = _coconut_back_compose


def _coconut_pipe(
    x: _T,
    f: _t.Callable[[_T], _Uco],
) -> _Uco: ...
def _coconut_star_pipe(
    xs: _Iterable,
    f: _t.Callable[..., _Tco],
) -> _Tco: ...
def _coconut_dubstar_pipe(
    kws: _t.Dict[_t.Text, _t.Any],
    f: _t.Callable[..., _Tco],
) -> _Tco: ...

def _coconut_back_pipe(
    f: _t.Callable[[_T], _Uco],
    x: _T,
) -> _Uco: ...
def _coconut_back_star_pipe(
    f: _t.Callable[..., _Tco],
    xs: _Iterable,
) -> _Tco: ...
def _coconut_back_dubstar_pipe(
    f: _t.Callable[..., _Tco],
    kws: _t.Dict[_t.Text, _t.Any],
) -> _Tco: ...

def _coconut_none_pipe(
    x: _t.Optional[_Tco],
    f: _t.Callable[[_Tco], _Uco],
) -> _t.Optional[_Uco]: ...
def _coconut_none_star_pipe(
    xs: _t.Optional[_Iterable],
    f: _t.Callable[..., _Tco],
) -> _t.Optional[_Tco]: ...
def _coconut_none_dubstar_pipe(
    kws: _t.Optional[_t.Dict[_t.Text, _t.Any]],
    f: _t.Callable[..., _Tco],
) -> _t.Optional[_Tco]: ...


def _coconut_assert(cond: _t.Any, msg: _t.Optional[_t.Text] = None) -> None:
    assert cond, msg


def _coconut_raise(exc: _t.Optional[Exception] = None, from_exc: _t.Optional[Exception] = None) -> None: ...


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


@_t.overload
def _coconut_comma_op(_x: _T) -> _t.Tuple[_T]: ...
@_t.overload
def _coconut_comma_op(_x: _T, _y: _U) -> _t.Tuple[_T, _U]: ...
@_t.overload
def _coconut_comma_op(_x: _T, _y: _U, _z: _V) -> _t.Tuple[_T, _U, _V]: ...
@_t.overload
def _coconut_comma_op(*args: _T) -> _t.Tuple[_T, ...]: ...
@_t.overload
def _coconut_comma_op(*args: _t.Any) -> _Tuple: ...


if sys.version_info < (3, 5):
    @_t.overload
    def _coconut_matmul(a: _T, b: _T) -> _T: ...
    @_t.overload
    def _coconut_matmul(a: _t.Any, b: _t.Any) -> _t.Any: ...
else:
    _coconut_matmul = _coconut.operator.matmul


def reiterable(iterable: _t.Iterable[_T]) -> _t.Iterable[_T]: ...
_coconut_reiterable = reiterable


def multi_enumerate(iterable: _Iterable) -> _t.Iterable[_t.Tuple[_t.Tuple[int, ...], _t.Any]]: ...


class _count(_t.Iterable[_T]):
    @_t.overload
    def __new__(self) -> _count[int]: ...
    @_t.overload
    def __new__(self, start: _T) -> _count[_T]: ...
    @_t.overload
    def __new__(self, start: _T, step: _t.Optional[_T]) -> _count[_T]: ...

    def __iter__(self) -> _t.Iterator[_T]: ...
    def __contains__(self, elem: _T) -> bool: ...

    @_t.overload
    def __getitem__(self, index: int) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_T]: ...

    def __hash__(self) -> int: ...
    def count(self, elem: _T) -> int: ...
    def index(self, elem: _T) -> int: ...
    def __fmap__(self, func: _t.Callable[[_T], _Uco]) -> _count[_Uco]: ...
    def __copy__(self) -> _count[_T]: ...
count = _count  # necessary since we define .count()


class flatten(_t.Iterable[_T]):
    def __new__(self, iterable: _t.Iterable[_t.Iterable[_T]]) -> flatten[_T]: ...

    def __iter__(self) -> _t.Iterator[_T]: ...
    def __reversed__(self) -> flatten[_T]: ...
    def __len__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __contains__(self, elem: _T) -> bool: ...

    @_t.overload
    def __getitem__(self, index: int) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_T]: ...

    def count(self, elem: _T) -> int: ...
    def index(self, elem: _T) -> int: ...
    def __fmap__(self, func: _t.Callable[[_T], _Uco]) -> flatten[_Uco]: ...


def groupsof(n: int, iterable: _t.Iterable[_T]) -> _t.Iterable[_t.Tuple[_T, ...]]: ...


def makedata(data_type: _t.Type[_T], *args: _t.Any) -> _T: ...
def datamaker(data_type: _t.Type[_T]) -> _t.Callable[..., _T]:
    return _coconut.functools.partial(makedata, data_type)


def consume(
    iterable: _t.Iterable[_T],
    keep_last: _t.Optional[int] = ...,
    ) -> _t.Sequence[_T]: ...


@_t.overload
def fmap(func: _t.Callable[[_Tco], _Tco], obj: _Titer) -> _Titer: ...
@_t.overload
def fmap(func: _t.Callable[[_Tco], _Uco], obj: _t.List[_Tco]) -> _t.List[_Uco]: ...
@_t.overload
def fmap(func: _t.Callable[[_Tco], _Uco], obj: _t.Tuple[_Tco, ...]) -> _t.Tuple[_Uco, ...]: ...
@_t.overload
def fmap(func: _t.Callable[[_Tco], _Uco], obj: _t.Iterator[_Tco]) -> _t.Iterator[_Uco]: ...
@_t.overload
def fmap(func: _t.Callable[[_Tco], _Uco], obj: _t.Set[_Tco]) -> _t.Set[_Uco]: ...
@_t.overload
def fmap(func: _t.Callable[[_Tco], _Uco], obj: _t.AsyncIterable[_Tco]) -> _t.AsyncIterable[_Uco]: ...
@_t.overload
def fmap(func: _t.Callable[[_t.Tuple[_Tco, _Uco]], _t.Tuple[_Vco, _Wco]], obj: _t.Dict[_Tco, _Uco]) -> _t.Dict[_Vco, _Wco]: ...
@_t.overload
def fmap(func: _t.Callable[[_t.Tuple[_Tco, _Uco]], _t.Tuple[_Vco, _Wco]], obj: _t.Mapping[_Tco, _Uco]) -> _t.Mapping[_Vco, _Wco]: ...
@_t.overload
def fmap(func: _t.Callable[[_Tco, _Uco], _t.Tuple[_Vco, _Wco]], obj: _t.Dict[_Tco, _Uco], starmap_over_mappings: _t.Literal[True]) -> _t.Dict[_Vco, _Wco]: ...
@_t.overload
def fmap(func: _t.Callable[[_Tco, _Uco], _t.Tuple[_Vco, _Wco]], obj: _t.Mapping[_Tco, _Uco], starmap_over_mappings: _t.Literal[True]) -> _t.Mapping[_Vco, _Wco]: ...


def _coconut_handle_cls_kwargs(**kwargs: _t.Dict[_t.Text, _t.Any]) -> _t.Callable[[_T], _T]: ...


def _coconut_handle_cls_stargs(*args: _t.Any) -> _t.Any: ...


_coconut_self_match_types: _t.Tuple[_t.Type, ...] = (bool, bytearray, bytes, dict, float, frozenset, int, py_int, list, set, str, py_str, tuple)


@_t.overload
def _coconut_dict_merge(*dicts: _t.Dict[_Tco, _Uco]) -> _t.Dict[_Tco, _Uco]: ...
@_t.overload
def _coconut_dict_merge(*dicts: _t.Dict[_Tco, _t.Any]) -> _t.Dict[_Tco, _t.Any]: ...


@_t.overload
def flip(func: _t.Callable[[_T], _V]) -> _t.Callable[[_T], _V]: ...
@_t.overload
def flip(func: _t.Callable[[_T, _U], _V]) -> _t.Callable[[_U, _T], _V]: ...
@_t.overload
def flip(func: _t.Callable[[_T, _U], _V], nargs: _t.Literal[2]) -> _t.Callable[[_U, _T], _V]: ...
@_t.overload
def flip(func: _t.Callable[[_T, _U, _V], _W]) -> _t.Callable[[_V, _U, _T], _W]: ...
@_t.overload
def flip(func: _t.Callable[[_T, _U, _V], _W], nargs: _t.Literal[3]) -> _t.Callable[[_V, _U, _T], _W]: ...
@_t.overload
def flip(func: _t.Callable[[_T, _U, _V], _W], nargs: _t.Literal[2]) -> _t.Callable[[_U, _T, _V], _W]: ...
@_t.overload
def flip(func: _t.Callable[..., _T], nargs: _t.Optional[int]) -> _t.Callable[..., _T]: ...


def ident(x: _T, *, side_effect: _t.Optional[_t.Callable[[_T], _t.Any]] = None) -> _T: ...


def const(value: _T) -> _t.Callable[..., _T]: ...


# lift(_T -> _W)
class _coconut_lifted_1(_t.Generic[_T, _W]):
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_Xco], _T],
    # ) -> _t.Callable[[_Xco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[[_Xco, _Yco], _T],
    ) -> _t.Callable[[_Xco, _Yco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[[_Xco, _Yco, _Zco], _T],
    ) -> _t.Callable[[_Xco, _Yco, _Zco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[_P, _T],
    ) -> _t.Callable[_P, _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[..., _T],
    # ) -> _t.Callable[..., _W]: ...
    @_t.overload
    def __call__(
        self,
        **kwargs: _t.Dict[_t.Text, _t.Callable[..., _T]],
    ) -> _t.Callable[..., _W]: ...

# lift((_T, _U) -> _W)
class _coconut_lifted_2(_t.Generic[_T, _U, _W]):
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_Xco], _T],
    #     _h: _t.Callable[[_Xco], _U],
    # ) -> _t.Callable[[_Xco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[[_Xco, _Yco], _T],
        _h: _t.Callable[[_Xco, _Yco], _U],
    ) -> _t.Callable[[_Xco, _Yco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[[_Xco, _Yco, _Zco], _T],
        _h: _t.Callable[[_Xco, _Yco, _Zco], _U],
    ) -> _t.Callable[[_Xco, _Yco, _Zco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[_P, _T],
        _h: _t.Callable[_P, _U],
    ) -> _t.Callable[_P, _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[..., _T],
    #     _h: _t.Callable[..., _U],
    # ) -> _t.Callable[..., _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[..., _T] = ...,
        **kwargs: _t.Dict[_t.Text, _t.Any],
    ) -> _t.Callable[..., _W]: ...

# lift((_T, _U, _V) -> _W)
class _coconut_lifted_3(_t.Generic[_T, _U, _V, _W]):
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_Xco], _T],
    #     _h: _t.Callable[[_Xco], _U],
    #     _i: _t.Callable[[_Xco], _V],
    # ) -> _t.Callable[[_Xco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[[_Xco, _Yco], _T],
        _h: _t.Callable[[_Xco, _Yco], _U],
        _i: _t.Callable[[_Xco, _Yco], _V],
    ) -> _t.Callable[[_Xco, _Yco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[[_Xco, _Yco, _Zco], _T],
        _h: _t.Callable[[_Xco, _Yco, _Zco], _U],
        _i: _t.Callable[[_Xco, _Yco, _Zco], _V],
    ) -> _t.Callable[[_Xco, _Yco, _Zco], _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[_P, _T],
        _h: _t.Callable[_P, _U],
        _i: _t.Callable[_P, _V],
    ) -> _t.Callable[_P, _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[..., _T],
    #     _h: _t.Callable[..., _U],
    #     _i: _t.Callable[..., _V],
    # ) -> _t.Callable[..., _W]: ...
    @_t.overload
    def __call__(
        self,
        _g: _t.Callable[..., _T] = ...,
        _h: _t.Callable[..., _U] = ...,
        **kwargs: _t.Dict[_t.Text, _t.Any],
    ) -> _t.Callable[..., _W]: ...


@_t.overload
def lift(func: _t.Callable[[_T], _W]) -> _coconut_lifted_1[_T, _W]: ...
@_t.overload
def lift(func: _t.Callable[[_T, _U], _W]) -> _coconut_lifted_2[_T, _U, _W]: ...
@_t.overload
def lift(func: _t.Callable[[_T, _U, _V], _W]) -> _coconut_lifted_3[_T, _U, _V, _W]: ...
@_t.overload
def lift(func: _t.Callable[..., _W]) -> _t.Callable[..., _t.Callable[..., _W]]: ...


def all_equal(iterable: _Iterable) -> bool: ...


@_t.overload
def collectby(
    key_func: _t.Callable[[_T], _U],
    iterable: _t.Iterable[_T],
) -> _t.DefaultDict[_U, _t.List[_T]]: ...
@_t.overload
def collectby(
    key_func: _t.Callable[[_T], _U],
    iterable: _t.Iterable[_T],
    reduce_func: _t.Callable[[_T, _T], _V],
) -> _t.DefaultDict[_U, _V]: ...


@_t.overload
def _namedtuple_of(**kwargs: _t.Dict[_t.Text, _T]) -> _t.Tuple[_T, ...]: ...
@_t.overload
def _namedtuple_of(**kwargs: _t.Dict[_t.Text, _t.Any]) -> _Tuple: ...


@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text],
    types: _t.Tuple[_t.Type[_T]],
) -> _t.Callable[[_T], _t.Tuple[_T]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, _t.Text],
    types: _t.Tuple[_t.Type[_T], _t.Type[_U]],
) -> _t.Callable[[_T, _U], _t.Tuple[_T, _U]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, _t.Text, _t.Text],
    types: _t.Tuple[_t.Type[_T], _t.Type[_U], _t.Type[_V]],
) -> _t.Callable[[_T, _U, _V], _t.Tuple[_T, _U, _V]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, ...],
    types: _t.Tuple[_t.Type[_T], ...],
) -> _t.Callable[..., _t.Tuple[_T, ...]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text],
    types: None,
) -> _t.Callable[[_T], _t.Tuple[_T]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, _t.Text],
    types: None,
) -> _t.Callable[[_T, _U], _t.Tuple[_T, _U]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, _t.Text, _t.Text],
    types: None,
) -> _t.Callable[[_T, _U, _V], _t.Tuple[_T, _U, _V]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, ...],
    types: _t.Optional[_t.Tuple[_t.Any, ...]],
) -> _t.Callable[..., _t.Tuple[_t.Any, ...]]: ...


# @_t.overload
# def _coconut_multi_dim_arr(
#     arrs: _t.Tuple[_coconut.npt.NDArray[_DType], ...],
#     dim: int,
# ) -> _coconut.npt.NDArray[_DType]: ...
# @_t.overload
# def _coconut_multi_dim_arr(
#     arrs: _t.Tuple[_DType, ...],
#     dim: int,
# ) -> _coconut.npt.NDArray[_DType]: ...

@_t.overload
def _coconut_multi_dim_arr(
    arrs: _t.Tuple[_t.Sequence[_T], ...],
    dim: _t.Literal[1],
) -> _t.Sequence[_T]: ...
@_t.overload
def _coconut_multi_dim_arr(
    arrs: _t.Tuple[_T, ...],
    dim: _t.Literal[1],
) -> _t.Sequence[_T]: ...

@_t.overload
def _coconut_multi_dim_arr(
    arrs: _t.Tuple[_t.Sequence[_t.Sequence[_T]], ...],
    dim: _t.Literal[2],
) -> _t.Sequence[_t.Sequence[_T]]: ...
@_t.overload
def _coconut_multi_dim_arr(
    arrs: _t.Tuple[_t.Sequence[_T], ...],
    dim: _t.Literal[2],
) -> _t.Sequence[_t.Sequence[_T]]: ...
@_t.overload
def _coconut_multi_dim_arr(
    arrs: _t.Tuple[_T, ...],
    dim: _t.Literal[2],
) -> _t.Sequence[_t.Sequence[_T]]: ...

@_t.overload
def _coconut_multi_dim_arr(arrs: _Tuple, dim: int) -> _Sequence: ...
