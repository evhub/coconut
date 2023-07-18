# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: MyPy stub file for __coconut__.py.
"""

# -----------------------------------------------------------------------------------------------------------------------
# TYPE VARS:
# -----------------------------------------------------------------------------------------------------------------------

import sys
import typing as _t

_Callable = _t.Callable[..., _t.Any]
_Iterable = _t.Iterable[_t.Any]
_Tuple = _t.Tuple[_t.Any, ...]
_Sequence = _t.Sequence[_t.Any]

_T = _t.TypeVar("_T")
_U = _t.TypeVar("_U")
_V = _t.TypeVar("_V")
_W = _t.TypeVar("_W")
_X = _t.TypeVar("_X")
_Y = _t.TypeVar("_Y")
_Z = _t.TypeVar("_Z")

_Tco = _t.TypeVar("_Tco", covariant=True)
_Uco = _t.TypeVar("_Uco", covariant=True)
_Vco = _t.TypeVar("_Vco", covariant=True)
_Wco = _t.TypeVar("_Wco", covariant=True)
_Xco = _t.TypeVar("_Xco", covariant=True)
_Yco = _t.TypeVar("_Yco", covariant=True)
_Zco = _t.TypeVar("_Zco", covariant=True)

_Tcontra = _t.TypeVar("_Tcontra", contravariant=True)
_Ucontra = _t.TypeVar("_Ucontra", contravariant=True)
_Vcontra = _t.TypeVar("_Vcontra", contravariant=True)
_Wcontra = _t.TypeVar("_Wcontra", contravariant=True)
_Xcontra = _t.TypeVar("_Xcontra", contravariant=True)
_Ycontra = _t.TypeVar("_Ycontra", contravariant=True)
_Zcontra = _t.TypeVar("_Zcontra", contravariant=True)

_Tfunc = _t.TypeVar("_Tfunc", bound=_Callable)
_Ufunc = _t.TypeVar("_Ufunc", bound=_Callable)
_Tfunc_contra = _t.TypeVar("_Tfunc_contra", bound=_Callable, contravariant=True)
_Titer = _t.TypeVar("_Titer", bound=_Iterable)
_T_iter_func = _t.TypeVar("_T_iter_func", bound=_t.Callable[..., _Iterable])

_P = _t.ParamSpec("_P")

class _SupportsIndex(_t.Protocol):
    def __index__(self) -> int: ...

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

if sys.version_info >= (3,):
    import builtins as _builtins
else:
    import __builtin__ as _builtins

if sys.version_info >= (3, 2):
    from functools import lru_cache as _lru_cache
else:
    from backports.functools_lru_cache import lru_cache as _lru_cache  # `pip install -U coconut[mypy]` to fix errors on this line
    _coconut.functools.lru_cache = _lru_cache  # type: ignore

if sys.version_info >= (3, 7):
    from dataclasses import dataclass as _dataclass
else:
    @_dataclass_transform()
    def _dataclass(cls: type[_T], **kwargs: _t.Any) -> type[_T]: ...

if sys.version_info >= (3, 11):
    from typing import dataclass_transform as _dataclass_transform
else:
    try:
        from typing_extensions import dataclass_transform as _dataclass_transform
    except ImportError:
        dataclass_transform = ...

try:
    from typing_extensions import deprecated as _deprecated  # type: ignore
except ImportError:
    def _deprecated(message: _t.Text) -> _t.Callable[[_T], _T]: ...  # type: ignore

import _coconut as __coconut  # we mock _coconut as a package since mypy doesn't handle namespace classes very well
_coconut = __coconut


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
        def __getitem__(self, index: _SupportsIndex) -> int: ...
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
py_dict = dict
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
chr = _builtins.chr
hex = _builtins.hex
input = _builtins.input
map = _builtins.map
oct = _builtins.oct
open = _builtins.open
print = _builtins.print
range = _builtins.range
zip = _builtins.zip
filter = _builtins.filter
reversed = _builtins.reversed
enumerate = _builtins.enumerate


_coconut_py_str = py_str
_coconut_super = super
_coconut_enumerate = enumerate
_coconut_filter = filter
_coconut_range = range
_coconut_reversed = reversed
_coconut_zip = zip


zip_longest = _coconut.zip_longest
memoize = _lru_cache
reduce = _coconut.functools.reduce
takewhile = _coconut.itertools.takewhile
dropwhile = _coconut.itertools.dropwhile
tee = _coconut.itertools.tee
starmap = _coconut.itertools.starmap
cartesian_product = _coconut.itertools.product
multiset = _coconut.collections.Counter

_coconut_tee = tee
_coconut_starmap = starmap
_coconut_cartesian_product = cartesian_product
_coconut_multiset = multiset


parallel_map = concurrent_map = _coconut_map = map


TYPE_CHECKING = _t.TYPE_CHECKING


_coconut_sentinel: _t.Any = ...


def scan(
    func: _t.Callable[[_T, _U], _T],
    iterable: _t.Iterable[_U],
    initial: _T = ...,
) -> _t.Iterable[_T]: ...
_coconut_scan = scan


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


# any changes here should also be made to safe_call and call_or_coefficient below
@_t.overload
def call(
    _func: _t.Callable[[_T], _U],
    _x: _T,
) -> _U: ...
@_t.overload
def call(
    _func: _t.Callable[[_T, _U], _V],
    _x: _T,
    _y: _U,
) -> _V: ...
@_t.overload
def call(
    _func: _t.Callable[[_T, _U, _V], _W],
    _x: _T,
    _y: _U,
    _z: _V,
) -> _W: ...
@_t.overload
def call(
    _func: _t.Callable[_t.Concatenate[_T, _P], _U],
    _x: _T,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _U: ...
@_t.overload
def call(
    _func: _t.Callable[_t.Concatenate[_T, _U, _P], _V],
    _x: _T,
    _y: _U,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _V: ...
@_t.overload
def call(
    _func: _t.Callable[_t.Concatenate[_T, _U, _V, _P], _W],
    _x: _T,
    _y: _U,
    _z: _V,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _W: ...
@_t.overload
def call(
    _func: _t.Callable[..., _T],
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _T: ...

_coconut_tail_call = call
of = _deprecated("use call instead")(call)


@_dataclass(frozen=True, slots=True)
class _BaseExpected(_t.Generic[_T], _t.Tuple):
    result: _t.Optional[_T]
    error: _t.Optional[BaseException]
class Expected(_BaseExpected[_T]):
    __slots__ = ()
    _coconut_is_data = True
    __match_args__ = ("result", "error")
    _coconut_data_defaults: _t.Mapping[int, None] = ...
    @_t.overload
    def __new__(
        cls,
        result: _T,
        error: None = None,
    ) -> Expected[_T]: ...
    @_t.overload
    def __new__(
        cls,
        result: None = None,
        *,
        error: BaseException,
    ) -> Expected[_t.Any]: ...
    @_t.overload
    def __new__(
        cls,
        result: None,
        error: BaseException,
    ) -> Expected[_t.Any]: ...
    def __init__(
        self,
        result: _t.Optional[_T] = None,
        error: _t.Optional[BaseException] = None,
    ): ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> Expected[_U]: ...
    def __iter__(self) -> _t.Iterator[_T | BaseException | None]: ...
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _T | BaseException | None: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Tuple[_T | BaseException | None, ...]: ...
    def and_then(self, func: _t.Callable[[_T], Expected[_U]]) -> Expected[_U]: ...
    def join(self: Expected[Expected[_T]]) -> Expected[_T]: ...
    def map_error(self, func: _t.Callable[[BaseException], BaseException]) -> Expected[_T]: ...
    def or_else(self, func: _t.Callable[[BaseException], Expected[_U]]) -> Expected[_T | _U]: ...
    def result_or(self, default: _U) -> _T | _U: ...
    def result_or_else(self, func: _t.Callable[[BaseException], _U]) -> _T | _U: ...
    def unwrap(self) -> _T: ...

_coconut_Expected = Expected


# should match call above but with Expected
@_t.overload
def safe_call(
    _func: _t.Callable[[_T], _U],
    _x: _T,
) -> Expected[_U]: ...
@_t.overload
def safe_call(
    _func: _t.Callable[[_T, _U], _V],
    _x: _T,
    _y: _U,
) -> Expected[_V]: ...
@_t.overload
def safe_call(
    _func: _t.Callable[[_T, _U, _V], _W],
    _x: _T,
    _y: _U,
    _z: _V,
) -> Expected[_W]: ...
@_t.overload
def safe_call(
    _func: _t.Callable[_t.Concatenate[_T, _P], _U],
    _x: _T,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> Expected[_U]: ...
@_t.overload
def safe_call(
    _func: _t.Callable[_t.Concatenate[_T, _U, _P], _V],
    _x: _T,
    _y: _U,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> Expected[_V]: ...
@_t.overload
def safe_call(
    _func: _t.Callable[_t.Concatenate[_T, _U, _V, _P], _W],
    _x: _T,
    _y: _U,
    _z: _V,
    *args: _t.Any,
    **kwargs: _t.Any,
) -> Expected[_W]: ...
@_t.overload
def safe_call(
    _func: _t.Callable[..., _T],
    *args: _t.Any,
    **kwargs: _t.Any,
) -> Expected[_T]: ...


# based on call above
@_t.overload
def _coconut_call_or_coefficient(
    _func: _t.Callable[[_T], _U],
    _x: _T,
) -> _U: ...
@_t.overload
def _coconut_call_or_coefficient(
    _func: _t.Callable[[_T, _U], _V],
    _x: _T,
    _y: _U,
) -> _V: ...
@_t.overload
def _coconut_call_or_coefficient(
    _func: _t.Callable[[_T, _U, _V], _W],
    _x: _T,
    _y: _U,
    _z: _V,
) -> _W: ...
@_t.overload
def _coconut_call_or_coefficient(
    _func: _t.Callable[_t.Concatenate[_T, _P], _U],
    _x: _T,
    *args: _t.Any,
) -> _U: ...
@_t.overload
def _coconut_call_or_coefficient(
    _func: _t.Callable[_t.Concatenate[_T, _U, _P], _V],
    _x: _T,
    _y: _U,
    *args: _t.Any,
) -> _V: ...
@_t.overload
def _coconut_call_or_coefficient(
    _func: _t.Callable[_t.Concatenate[_T, _U, _V, _P], _W],
    _x: _T,
    _y: _U,
    _z: _V,
    *args: _t.Any,
) -> _W: ...
@_t.overload
def _coconut_call_or_coefficient(
    _func: _t.Callable[..., _T],
    *args: _t.Any,
) -> _T: ...
@_t.overload
def _coconut_call_or_coefficient(
    _func: _T,
    *args: _T,
) -> _T: ...


def recursive_iterator(func: _T_iter_func) -> _T_iter_func:
    return func


# if sys.version_info >= (3, 12):
#     from typing import override
# else:
try:
    from typing_extensions import override as _override  # type: ignore
    override = _override
except ImportError:
    def override(func: _Tfunc) -> _Tfunc:
        return func


def _coconut_call_set_names(cls: object) -> None: ...


class _coconut_base_pattern_func:
    def __init__(self, *funcs: _Callable) -> None: ...
    def add_pattern(self, func: _Callable) -> None: ...
    def __call__(self, *args: _t.Any, **kwargs: _t.Any) -> _t.Any: ...

@_t.overload
def addpattern(
    base_func: _t.Callable[[_T], _U],
    allow_any_func: bool=False,
) -> _t.Callable[[_t.Callable[[_V], _W]], _t.Callable[[_T | _V], _U | _W]]: ...
@_t.overload
def addpattern(
    base_func: _t.Callable[..., _U],
    allow_any_func: bool=False,
) -> _t.Callable[[_t.Callable[..., _W]], _t.Callable[..., _U | _W]]: ...
@_t.overload
def addpattern(
    base_func: _t.Callable[[_T], _U],
    _add_func: _t.Callable[[_V], _W],
    *,
    allow_any_func: bool=False,
) -> _t.Callable[[_T | _V], _U | _W]: ...
@_t.overload
def addpattern(
    base_func: _t.Callable[..., _T],
    _add_func: _t.Callable[..., _U],
    *,
    allow_any_func: bool=False,
) -> _t.Callable[..., _T | _U]: ...
@_t.overload
def addpattern(
    base_func: _Callable,
    *add_funcs: _Callable,
    allow_any_func: bool=False,
) -> _t.Callable[..., _t.Any]: ...

_coconut_addpattern = addpattern
prepattern = _deprecated("use addpattern instead")(addpattern)


def _coconut_mark_as_match(func: _Tfunc) -> _Tfunc:
    return func


class _coconut_partial(_t.Generic[_T]):
    args: _Tuple = ...
    required_nargs: int = ...
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
    index: _SupportsIndex,
    ) -> _T: ...
@_t.overload
def _coconut_iter_getitem(
    iterable: _t.Iterable[_T],
    index: slice,
    ) -> _t.Iterable[_T]: ...


def _coconut_base_compose(
    func: _t.Callable[[_T], _t.Any],
    *func_infos: _t.Tuple[_Callable, int, bool],
    ) -> _t.Callable[[_T], _t.Any]: ...


def and_then(
    first_async_func: _t.Callable[_P, _t.Awaitable[_U]],
    second_func: _t.Callable[[_U], _V],
) -> _t.Callable[_P, _t.Awaitable[_V]]: ...

def and_then_await(
    first_async_func: _t.Callable[_P, _t.Awaitable[_U]],
    second_async_func: _t.Callable[[_U], _t.Awaitable[_V]],
) -> _t.Callable[_P, _t.Awaitable[_V]]: ...


# all forward/backward/none composition functions MUST be kept in sync:

# @_t.overload
# def _coconut_forward_compose(
#     _g: _t.Callable[[_T], _U],
#     _f: _t.Callable[[_U], _V],
#     ) -> _t.Callable[[_T], _V]: ...
# @_t.overload
# def _coconut_forward_compose(
#     _g: _t.Callable[[_T, _U], _V],
#     _f: _t.Callable[[_V], _W],
#     ) -> _t.Callable[[_T, _U], _W]: ...
# @_t.overload
# def _coconut_forward_compose(
#     _h: _t.Callable[[_T], _U],
#     _g: _t.Callable[[_U], _V],
#     _f: _t.Callable[[_V], _W],
#     ) -> _t.Callable[[_T], _W]: ...
# @_t.overload
# def _coconut_forward_compose(
#     _h: _t.Callable[_P, _T],
#     _g: _t.Callable[[_T], _U],
#     _f: _t.Callable[[_U], _V],
#     ) -> _t.Callable[_P, _V]: ...
# @_t.overload
# def _coconut_forward_compose(
#     _h: _t.Callable[_P, _T],
#     _g: _t.Callable[[_T], _U],
#     _f: _t.Callable[[_U], _V],
#     _e: _t.Callable[[_V], _W],
#     ) -> _t.Callable[_P, _W]: ...
# @_t.overload
# def _coconut_forward_compose(
#     _h: _t.Callable[..., _T],
#     _g: _t.Callable[[_T], _U],
#     _f: _t.Callable[[_U], _V],
#     ) -> _t.Callable[..., _V]: ...
# @_t.overload
# def _coconut_forward_compose(
#     _h: _t.Callable[..., _T],
#     _g: _t.Callable[[_T], _U],
#     _f: _t.Callable[[_U], _V],
#     _e: _t.Callable[[_V], _W],
#     ) -> _t.Callable[..., _W]: ...
@_t.overload
def _coconut_forward_compose(
    _g: _t.Callable[_P, _T],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[_P, _U]: ...
@_t.overload
def _coconut_forward_compose(
    _g: _t.Callable[..., _T],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[..., _U]: ...
@_t.overload
def _coconut_forward_compose(*funcs: _Callable) -> _Callable: ...

@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[_P, _T],
    ) -> _t.Callable[_P, _U]: ...
@_t.overload
def _coconut_back_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[..., _T],
    ) -> _t.Callable[..., _U]: ...
@_t.overload
def _coconut_back_compose(*funcs: _Callable) -> _Callable: ...


@_t.overload
def _coconut_forward_none_compose(
    _g: _t.Callable[_P, _t.Optional[_T]],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[_P, _t.Optional[_U]]: ...
@_t.overload
def _coconut_forward_none_compose(
    _g: _t.Callable[..., _t.Optional[_T]],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[..., _t.Optional[_U]]: ...
@_t.overload
def _coconut_forward_none_compose(*funcs: _Callable) -> _Callable: ...

@_t.overload
def _coconut_back_none_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[_P, _t.Optional[_T]],
    ) -> _t.Callable[_P, _t.Optional[_U]]: ...
@_t.overload
def _coconut_back_none_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[..., _t.Optional[_T]],
    ) -> _t.Callable[..., _t.Optional[_U]]: ...
@_t.overload
def _coconut_back_none_compose(*funcs: _Callable) -> _Callable: ...


@_t.overload
def _coconut_forward_star_compose(
    _g: _t.Callable[_P, _t.Tuple[_T]],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[_P, _U]: ...
@_t.overload
def _coconut_forward_star_compose(
    _g: _t.Callable[_P, _t.Tuple[_T, _U]],
    _f: _t.Callable[[_T, _U], _V],
    ) -> _t.Callable[_P, _V]: ...
@_t.overload
def _coconut_forward_star_compose(
    _g: _t.Callable[_P, _t.Tuple[_T, _U, _V]],
    _f: _t.Callable[[_T, _U, _V], _W],
    ) -> _t.Callable[_P, _W]: ...
@_t.overload
def _coconut_forward_star_compose(
    _g: _t.Callable[..., _t.Tuple[_T]],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[..., _U]: ...
@_t.overload
def _coconut_forward_star_compose(
    _g: _t.Callable[..., _t.Tuple[_T, _U]],
    _f: _t.Callable[[_T, _U], _V],
    ) -> _t.Callable[..., _V]: ...
@_t.overload
def _coconut_forward_star_compose(
    _g: _t.Callable[..., _t.Tuple[_T, _U, _V]],
    _f: _t.Callable[[_T, _U, _V], _W],
    ) -> _t.Callable[..., _W]: ...
@_t.overload
def _coconut_forward_star_compose(*funcs: _Callable) -> _Callable: ...

@_t.overload
def _coconut_back_star_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[_P, _t.Tuple[_T]],
    ) -> _t.Callable[_P, _U]: ...
@_t.overload
def _coconut_back_star_compose(
    _f: _t.Callable[[_T, _U], _V],
    _g: _t.Callable[_P, _t.Tuple[_T, _U]],
    ) -> _t.Callable[_P, _V]: ...
@_t.overload
def _coconut_back_star_compose(
    _f: _t.Callable[[_T, _U, _V], _W],
    _g: _t.Callable[_P, _t.Tuple[_T, _U, _V]],
    ) -> _t.Callable[_P, _W]: ...
@_t.overload
def _coconut_back_star_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[..., _t.Tuple[_T]],
    ) -> _t.Callable[..., _U]: ...
@_t.overload
def _coconut_back_star_compose(
    _f: _t.Callable[[_T, _U], _V],
    _g: _t.Callable[..., _t.Tuple[_T, _U]],
    ) -> _t.Callable[..., _V]: ...
@_t.overload
def _coconut_back_star_compose(
    _f: _t.Callable[[_T, _U, _V], _W],
    _g: _t.Callable[..., _t.Tuple[_T, _U, _V]],
    ) -> _t.Callable[..., _W]: ...
@_t.overload
def _coconut_back_star_compose(*funcs: _Callable) -> _Callable: ...


@_t.overload
def _coconut_forward_none_star_compose(
    _g: _t.Callable[_P, _t.Optional[_t.Tuple[_T]]],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[_P, _t.Optional[_U]]: ...
@_t.overload
def _coconut_forward_none_star_compose(
    _g: _t.Callable[_P, _t.Optional[_t.Tuple[_T, _U]]],
    _f: _t.Callable[[_T, _U], _V],
    ) -> _t.Callable[_P, _t.Optional[_V]]: ...
@_t.overload
def _coconut_forward_none_star_compose(
    _g: _t.Callable[_P, _t.Optional[_t.Tuple[_T, _U, _V]]],
    _f: _t.Callable[[_T, _U, _V], _W],
    ) -> _t.Callable[_P, _t.Optional[_W]]: ...
@_t.overload
def _coconut_forward_none_star_compose(
    _g: _t.Callable[..., _t.Optional[_t.Tuple[_T]]],
    _f: _t.Callable[[_T], _U],
    ) -> _t.Callable[..., _t.Optional[_U]]: ...
@_t.overload
def _coconut_forward_none_star_compose(
    _g: _t.Callable[..., _t.Optional[_t.Tuple[_T, _U]]],
    _f: _t.Callable[[_T, _U], _V],
    ) -> _t.Callable[..., _t.Optional[_V]]: ...
@_t.overload
def _coconut_forward_none_star_compose(
    _g: _t.Callable[..., _t.Optional[_t.Tuple[_T, _U, _V]]],
    _f: _t.Callable[[_T, _U, _V], _W],
    ) -> _t.Callable[..., _t.Optional[_W]]: ...
@_t.overload
def _coconut_forward_none_star_compose(*funcs: _Callable) -> _Callable: ...

@_t.overload
def _coconut_back_none_star_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[_P, _t.Optional[_t.Tuple[_T]]],
    ) -> _t.Callable[_P, _t.Optional[_U]]: ...
@_t.overload
def _coconut_back_none_star_compose(
    _f: _t.Callable[[_T, _U], _V],
    _g: _t.Callable[_P, _t.Optional[_t.Tuple[_T, _U]]],
    ) -> _t.Callable[_P, _t.Optional[_V]]: ...
@_t.overload
def _coconut_back_none_star_compose(
    _f: _t.Callable[[_T, _U, _V], _W],
    _g: _t.Callable[_P, _t.Optional[_t.Tuple[_T, _U, _V]]],
    ) -> _t.Callable[_P, _t.Optional[_W]]: ...
@_t.overload
def _coconut_back_none_star_compose(
    _f: _t.Callable[[_T], _U],
    _g: _t.Callable[..., _t.Optional[_t.Tuple[_T]]],
    ) -> _t.Callable[..., _t.Optional[_U]]: ...
@_t.overload
def _coconut_back_none_star_compose(
    _f: _t.Callable[[_T, _U], _V],
    _g: _t.Callable[..., _t.Optional[_t.Tuple[_T, _U]]],
    ) -> _t.Callable[..., _t.Optional[_V]]: ...
@_t.overload
def _coconut_back_none_star_compose(
    _f: _t.Callable[[_T, _U, _V], _W],
    _g: _t.Callable[..., _t.Optional[_t.Tuple[_T, _U, _V]]],
    ) -> _t.Callable[..., _t.Optional[_W]]: ...
@_t.overload
def _coconut_back_none_star_compose(*funcs: _Callable) -> _Callable: ...


@_t.overload
def _coconut_forward_dubstar_compose(
    _g: _t.Callable[_P, _t.Dict[_t.Text, _t.Any]],
    _f: _t.Callable[..., _T],
    ) -> _t.Callable[_P, _T]: ...
# @_t.overload
# def _coconut_forward_dubstar_compose(
#     _g: _t.Callable[..., _t.Dict[_t.Text, _t.Any]],
#     _f: _t.Callable[..., _T],
#     ) -> _t.Callable[..., _T]: ...
@_t.overload
def _coconut_forward_dubstar_compose(*funcs: _Callable) -> _Callable: ...

@_t.overload
def _coconut_back_dubstar_compose(
    _f: _t.Callable[..., _T],
    _g: _t.Callable[_P, _t.Dict[_t.Text, _t.Any]],
    ) -> _t.Callable[_P, _T]: ...
# @_t.overload
# def _coconut_back_dubstar_compose(
#     _f: _t.Callable[..., _T],
#     _g: _t.Callable[..., _t.Dict[_t.Text, _t.Any]],
#     ) -> _t.Callable[..., _T]: ...
@_t.overload
def _coconut_back_dubstar_compose(*funcs: _Callable) -> _Callable: ...


@_t.overload
def _coconut_forward_none_dubstar_compose(
    _g: _t.Callable[_P, _t.Optional[_t.Dict[_t.Text, _t.Any]]],
    _f: _t.Callable[..., _T],
    ) -> _t.Callable[_P, _t.Optional[_T]]: ...
# @_t.overload
# def _coconut_forward_none_dubstar_compose(
#     _g: _t.Callable[..., _t.Optional[_t.Dict[_t.Text, _t.Any]]],
#     _f: _t.Callable[..., _T],
#     ) -> _t.Callable[..., _t.Optional[_T]]: ...
@_t.overload
def _coconut_forward_none_dubstar_compose(*funcs: _Callable) -> _Callable: ...

@_t.overload
def _coconut_back_none_dubstar_compose(
    _f: _t.Callable[..., _T],
    _g: _t.Callable[_P, _t.Optional[_t.Dict[_t.Text, _t.Any]]],
    ) -> _t.Callable[_P, _t.Optional[_T]]: ...
# @_t.overload
# def _coconut_back_none_dubstar_compose(
#     _f: _t.Callable[..., _T],
#     _g: _t.Callable[..., _t.Optional[_t.Dict[_t.Text, _t.Any]]],
#     ) -> _t.Callable[..., _t.Optional[_T]]: ...
@_t.overload
def _coconut_back_none_dubstar_compose(*funcs: _Callable) -> _Callable: ...


def _coconut_pipe(
    x: _T,
    f: _t.Callable[[_T], _U],
) -> _U: ...
def _coconut_star_pipe(
    xs: _Iterable,
    f: _t.Callable[..., _T],
) -> _T: ...
def _coconut_dubstar_pipe(
    kws: _t.Dict[_t.Text, _t.Any],
    f: _t.Callable[..., _T],
) -> _T: ...

def _coconut_back_pipe(
    f: _t.Callable[[_T], _U],
    x: _T,
) -> _U: ...
def _coconut_back_star_pipe(
    f: _t.Callable[..., _T],
    xs: _Iterable,
) -> _T: ...
def _coconut_back_dubstar_pipe(
    f: _t.Callable[..., _T],
    kws: _t.Dict[_t.Text, _t.Any],
) -> _T: ...

def _coconut_none_pipe(
    x: _t.Optional[_T],
    f: _t.Callable[[_T], _U],
) -> _t.Optional[_U]: ...
def _coconut_none_star_pipe(
    xs: _t.Optional[_Iterable],
    f: _t.Callable[..., _T],
) -> _t.Optional[_T]: ...
def _coconut_none_dubstar_pipe(
    kws: _t.Optional[_t.Dict[_t.Text, _t.Any]],
    f: _t.Callable[..., _T],
) -> _t.Optional[_T]: ...

def _coconut_back_none_pipe(
    f: _t.Callable[[_T], _U],
    x: _t.Optional[_T],
) -> _t.Optional[_U]: ...
def _coconut_back_none_star_pipe(
    f: _t.Callable[..., _T],
    xs: _t.Optional[_Iterable],
) -> _t.Optional[_T]: ...
def _coconut_back_none_dubstar_pipe(
    f: _t.Callable[..., _T],
    kws: _t.Optional[_t.Dict[_t.Text, _t.Any]],
) -> _t.Optional[_T]: ...


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


def _coconut_in(a: _T, b: _t.Sequence[_T]) -> bool: ...
_coconut_not_in = _coconut_in


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
    def __new__(cls) -> _count[int]: ...
    @_t.overload
    def __new__(cls, start: _T) -> _count[_T]: ...
    @_t.overload
    def __new__(cls, start: _T, step: _t.Optional[_T]) -> _count[_T]: ...

    def __iter__(self) -> _t.Iterator[_T]: ...
    def __contains__(self, elem: _T) -> bool: ...

    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_T]: ...

    def __hash__(self) -> int: ...
    def count(self, elem: _T) -> int | float: ...
    def index(self, elem: _T) -> int: ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> _count[_U]: ...
    def __copy__(self) -> _count[_T]: ...
count = _coconut_count = _count  # necessary since we define .count()


class cycle(_t.Iterable[_T]):
    def __new__(
        cls,
        iterable: _t.Iterable[_T],
        times: _t.Optional[_SupportsIndex]=None,
    ) -> cycle[_T]: ...
    def __iter__(self) -> _t.Iterator[_T]: ...
    def __contains__(self, elem: _T) -> bool: ...

    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_T]: ...

    def __hash__(self) -> int: ...
    def count(self, elem: _T) -> int | float: ...
    def index(self, elem: _T) -> int: ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> _t.Iterable[_U]: ...
    def __copy__(self) -> cycle[_T]: ...
    def __len__(self) -> int: ...
_coconut_cycle = cycle


class groupsof(_t.Generic[_T]):
    def __new__(
        cls,
        n: _SupportsIndex,
        iterable: _t.Iterable[_T],
    ) -> groupsof[_T]: ...
    def __iter__(self) -> _t.Iterator[_t.Tuple[_T, ...]]: ...
    def __hash__(self) -> int: ...
    def __copy__(self) -> groupsof[_T]: ...
    def __len__(self) -> int: ...
    def __fmap__(self, func: _t.Callable[[_t.Tuple[_T, ...]], _U]) -> _t.Iterable[_U]: ...
_coconut_groupsof = groupsof


class windowsof(_t.Generic[_T]):
    def __new__(
        cls,
        size: _SupportsIndex,
        iterable: _t.Iterable[_T],
        fillvalue: _T=...,
        step: _SupportsIndex=1,
    ) -> windowsof[_T]: ...
    def __iter__(self) -> _t.Iterator[_t.Tuple[_T, ...]]: ...
    def __hash__(self) -> int: ...
    def __copy__(self) -> windowsof[_T]: ...
    def __len__(self) -> int: ...
    def __fmap__(self, func: _t.Callable[[_t.Tuple[_T, ...]], _U]) -> _t.Iterable[_U]: ...
_coconut_windowsof = windowsof


class flatten(_t.Iterable[_T]):
    def __new__(
        cls,
        iterable: _t.Iterable[_t.Iterable[_T]],
        levels: _t.Optional[_SupportsIndex]=1,
    ) -> flatten[_T]: ...

    def __iter__(self) -> _t.Iterator[_T]: ...
    def __reversed__(self) -> flatten[_T]: ...
    def __len__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __contains__(self, elem: _T) -> bool: ...

    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_T]: ...

    def count(self, elem: _T) -> int: ...
    def index(self, elem: _T) -> int: ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> flatten[_U]: ...
_coconut_flatten = flatten


def makedata(data_type: _t.Type[_T], *args: _t.Any) -> _T: ...
@_deprecated("use makedata instead")
def datamaker(data_type: _t.Type[_T]) -> _t.Callable[..., _T]:
    return _coconut.functools.partial(makedata, data_type)


def consume(
    iterable: _t.Iterable[_T],
    keep_last: _t.Optional[int] = ...,
    ) -> _t.Sequence[_T]: ...


class _FMappable(_t.Protocol[_Tfunc_contra, _Tco]):
    def __fmap__(self, func: _Tfunc_contra) -> _Tco: ...


@_t.overload
def fmap(func: _Tfunc, obj: _FMappable[_Tfunc, _T]) -> _T: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _T], obj: _Titer) -> _Titer: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.List[_T]) -> _t.List[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.Tuple[_T, ...]) -> _t.Tuple[_U, ...]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.Iterator[_T]) -> _t.Iterator[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.Set[_T]) -> _t.Set[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.AsyncIterable[_T]) -> _t.AsyncIterable[_U]: ...
# @_t.overload
# def fmap(func: _t.Callable[[_t.Tuple[_T, _U]], _t.Tuple[_V, _W]], obj: _t.Dict[_T, _U]) -> _t.Dict[_V, _W]: ...
# @_t.overload
# def fmap(func: _t.Callable[[_t.Tuple[_T, _U]], _t.Tuple[_V, _W]], obj: _t.Mapping[_T, _U]) -> _t.Mapping[_V, _W]: ...
@_t.overload
def fmap(func: _t.Callable[[_T, _U], _t.Tuple[_V, _W]], obj: _t.Dict[_T, _U], starmap_over_mappings: _t.Literal[True]) -> _t.Dict[_V, _W]: ...
@_t.overload
def fmap(func: _t.Callable[[_T, _U], _t.Tuple[_V, _W]], obj: _t.Mapping[_T, _U], starmap_over_mappings: _t.Literal[True]) -> _t.Mapping[_V, _W]: ...


def _coconut_handle_cls_kwargs(**kwargs: _t.Dict[_t.Text, _t.Any]) -> _t.Callable[[_T], _T]: ...


def _coconut_handle_cls_stargs(*args: _t.Any) -> _t.Any: ...


_coconut_self_match_types: _t.Tuple[_t.Type, ...] = (bool, bytearray, bytes, dict, float, frozenset, int, py_int, list, set, str, py_str, tuple)


@_t.overload
def _coconut_dict_merge(*dicts: _t.Dict[_T, _U]) -> _t.Dict[_T, _U]: ...
@_t.overload
def _coconut_dict_merge(*dicts: _t.Dict[_T, _t.Any]) -> _t.Dict[_T, _t.Any]: ...
@_t.overload
def _coconut_dict_merge(*dicts: _t.Dict[_t.Any, _t.Any]) -> _t.Dict[_t.Any, _t.Any]: ...


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
def flip(func: _t.Callable[..., _T], nargs: _t.Optional[_SupportsIndex]) -> _t.Callable[..., _T]: ...


def ident(x: _T, *, side_effect: _t.Optional[_t.Callable[[_T], _t.Any]] = None) -> _T: ...
_coconut_ident = ident


def const(value: _T) -> _t.Callable[..., _T]: ...


# lift(_T -> _W)
class _coconut_lifted_1(_t.Generic[_T, _W]):
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_X], _T],
    # ) -> _t.Callable[[_X], _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_X, _Y], _T],
    # ) -> _t.Callable[[_X, _Y], _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_X, _Y, _Z], _T],
    # ) -> _t.Callable[[_X, _Y, _Z], _W]: ...
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
    #     _g: _t.Callable[[_X], _T],
    #     _h: _t.Callable[[_X], _U],
    # ) -> _t.Callable[[_X], _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_X, _Y], _T],
    #     _h: _t.Callable[[_X, _Y], _U],
    # ) -> _t.Callable[[_X, _Y], _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_X, _Y, _Z], _T],
    #     _h: _t.Callable[[_X, _Y, _Z], _U],
    # ) -> _t.Callable[[_X, _Y, _Z], _W]: ...
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
    #     _g: _t.Callable[[_X], _T],
    #     _h: _t.Callable[[_X], _U],
    #     _i: _t.Callable[[_X], _V],
    # ) -> _t.Callable[[_X], _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_X, _Y], _T],
    #     _h: _t.Callable[[_X, _Y], _U],
    #     _i: _t.Callable[[_X, _Y], _V],
    # ) -> _t.Callable[[_X, _Y], _W]: ...
    # @_t.overload
    # def __call__(
    #     self,
    #     _g: _t.Callable[[_X, _Y, _Z], _T],
    #     _h: _t.Callable[[_X, _Y, _Z], _U],
    #     _i: _t.Callable[[_X, _Y, _Z], _V],
    # ) -> _t.Callable[[_X, _Y, _Z], _W]: ...
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
_coconut_lift = lift


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
    types: None = None,
) -> _t.Callable[[_T], _t.Tuple[_T]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, _t.Text],
    types: None = None,
) -> _t.Callable[[_T, _U], _t.Tuple[_T, _U]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, _t.Text, _t.Text],
    types: None = None,
) -> _t.Callable[[_T, _U, _V], _t.Tuple[_T, _U, _V]]: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, ...],
    types: _t.Optional[_t.Tuple[_t.Any, ...]] = None,
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


class _coconut_SupportsAdd(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __add__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsMinus(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __sub__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError
    def __neg__(self: _Tco) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsMul(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __mul__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsPow(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __pow__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsTruediv(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __truediv__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsFloordiv(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __floordiv__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsMod(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __mod__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsAnd(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __and__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsXor(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __xor__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsOr(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __or__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsLshift(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __lshift__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsRshift(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __rshift__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsMatmul(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    def __matmul__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsInv(_t.Protocol, _t.Generic[_Tco, _Vco]):
    def __invert__(self: _Tco) -> _Vco:
        raise NotImplementedError
