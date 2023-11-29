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
        """
        range(stop) -> range object
        range(start, stop[, step]) -> range object

        Return an object that produces a sequence of integers from start (inclusive)
        to stop (exclusive) by step.  range(i, j) produces i, i+1, i+2, ..., j-1.
        start defaults to 0, and stop is omitted!  range(4) produces 0, 1, 2, 3.
        These are exactly the valid indices for a list of 4 elements.
        When step is given, it specifies the increment (or decrement).
        """
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
    def breakpoint(*args: _t.Any, **kwargs: _t.Any) -> _t.Any:
        """
        breakpoint(*args, **kws)

        Call sys.breakpointhook(*args, **kws).  sys.breakpointhook() must accept
        whatever arguments are passed.

        By default, this drops you into the pdb debugger.
        """
        ...


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

_coconut_partial = _coconut.functools.partial
_coconut_tee = tee
_coconut_starmap = starmap
_coconut_cartesian_product = cartesian_product


process_map = thread_map = parallel_map = concurrent_map = _coconut_map = map


TYPE_CHECKING = _t.TYPE_CHECKING


_coconut_sentinel: _t.Any = ...


def scan(
    func: _t.Callable[[_T, _U], _T],
    iterable: _t.Iterable[_U],
    initial: _T = ...,
) -> _t.Iterable[_T]:
    """Reduce func over iterable, yielding intermediate results,
    optionally starting from initial."""
    ...
_coconut_scan = scan


class MatchError(Exception):
    """Pattern-matching error. Has attributes .pattern, .value, and .message."""
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
    _func: _t.Callable[[], _U],
) -> _U: ...
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
# @_t.overload
# def call(
#     _func: _t.Callable[_t.Concatenate[_T, _P], _U],
#     _x: _T,
#     *args: _t.Any,
#     **kwargs: _t.Any,
# ) -> _U: ...
# @_t.overload
# def call(
#     _func: _t.Callable[_t.Concatenate[_T, _U, _P], _V],
#     _x: _T,
#     _y: _U,
#     *args: _t.Any,
#     **kwargs: _t.Any,
# ) -> _V: ...
# @_t.overload
# def call(
#     _func: _t.Callable[_t.Concatenate[_T, _U, _V, _P], _W],
#     _x: _T,
#     _y: _U,
#     _z: _V,
#     *args: _t.Any,
#     **kwargs: _t.Any,
# ) -> _W: ...
@_t.overload
def call(
    _func: _t.Callable[..., _T],
    *args: _t.Any,
    **kwargs: _t.Any,
) -> _T:
    """Function application operator function.

    Equivalent to:
        def call(f, /, *args, **kwargs) = f(*args, **kwargs).
    """
    ...

_coconut_tail_call = call
of = _deprecated("use call instead")(call)


@_dataclass(frozen=True, slots=True)
class _BaseExpected(_t.Generic[_T], _t.Tuple):
    result: _t.Optional[_T]
    error: _t.Optional[BaseException]
class Expected(_BaseExpected[_T]):
    '''Coconut's Expected built-in is a Coconut data that represents a value
    that may or may not be an error, similar to Haskell's Either.

    Effectively equivalent to:
        data Expected[T](result: T? = None, error: BaseException? = None):
            def __bool__(self) -> bool:
                return self.error is None
            def __fmap__[U](self, func: T -> U) -> Expected[U]:
                """Maps func over the result if it exists.

                __fmap__ should be used directly only when fmap is not available (e.g. when consuming an Expected in vanilla Python).
                """
                return self.__class__(func(self.result)) if self else self
            def and_then[U](self, func: T -> Expected[U]) -> Expected[U]:
                """Maps a T -> Expected[U] over an Expected[T] to produce an Expected[U].
                Implements a monadic bind. Equivalent to fmap ..> .join()."""
                return self |> fmap$(func) |> .join()
            def join(self: Expected[Expected[T]]) -> Expected[T]:
                """Monadic join. Converts Expected[Expected[T]] to Expected[T]."""
                if not self:
                    return self
                if not self.result `isinstance` Expected:
                    raise TypeError("Expected.join() requires an Expected[Expected[_]]")
                return self.result
            def map_error(self, func: BaseException -> BaseException) -> Expected[T]:
                """Maps func over the error if it exists."""
                return self if self else self.__class__(error=func(self.error))
            def handle(self, err_type, handler: BaseException -> T) -> Expected[T]:
                """Recover from the given err_type by calling handler on the error to determine the result."""
                if not self and isinstance(self.error, err_type):
                    return self.__class__(handler(self.error))
                return self
            def expect_error(self, *err_types: BaseException) -> Expected[T]:
                """Raise any errors that do not match the given error types."""
                if not self and not isinstance(self.error, err_types):
                    raise self.error
                return self
            def unwrap(self) -> T:
                """Unwrap the result or raise the error."""
                if not self:
                    raise self.error
                return self.result
            def or_else[U](self, func: BaseException -> Expected[U]) -> Expected[T | U]:
                """Return self if no error, otherwise return the result of evaluating func on the error."""
                return self if self else func(self.error)
            def result_or_else[U](self, func: BaseException -> U) -> T | U:
                """Return the result if it exists, otherwise return the result of evaluating func on the error."""
                return self.result if self else func(self.error)
            def result_or[U](self, default: U) -> T | U:
                """Return the result if it exists, otherwise return the default.

                Since .result_or() completely silences errors, it is highly recommended that you
                call .expect_error() first to explicitly declare what errors you are okay silencing.
                """
                return self.result if self else default
    '''
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
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> Expected[_U]:
        """Maps func over the result if it exists.

        __fmap__ should be used directly only when fmap is not available (e.g. when consuming an Expected in vanilla Python).
        """
        ...
    def __iter__(self) -> _t.Iterator[_T | BaseException | None]: ...
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _T | BaseException | None: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Tuple[_T | BaseException | None, ...]: ...
    def and_then(self, func: _t.Callable[[_T], Expected[_U]]) -> Expected[_U]:
        """Maps a T -> Expected[U] over an Expected[T] to produce an Expected[U].
        Implements a monadic bind. Equivalent to fmap ..> .join()."""
        ...
    def join(self: Expected[Expected[_T]]) -> Expected[_T]:
        """Monadic join. Converts Expected[Expected[T]] to Expected[T]."""
        ...
    def map_error(self, func: _t.Callable[[BaseException], BaseException]) -> Expected[_T]:
        """Maps func over the error if it exists."""
        ...
    def handle(self, err_type: _t.Type[BaseException], handler: _t.Callable[[BaseException], _T]) -> Expected[_T]:
        """Recover from the given err_type by calling handler on the error to determine the result."""
        ...
    def expect_error(self, *err_types: BaseException) -> Expected[_T]:
        """Raise any errors that do not match the given error types."""
        ...
    def unwrap(self) -> _T:
        """Unwrap the result or raise the error."""
        ...
    def or_else(self, func: _t.Callable[[BaseException], Expected[_U]]) -> Expected[_T | _U]:
        """Return self if no error, otherwise return the result of evaluating func on the error."""
        ...
    def result_or_else(self, func: _t.Callable[[BaseException], _U]) -> _T | _U:
        """Return the result if it exists, otherwise return the result of evaluating func on the error."""
        ...
    def result_or(self, default: _U) -> _T | _U:
        """Return the result if it exists, otherwise return the default.

        Since .result_or() completely silences errors, it is highly recommended that you
        call .expect_error() first to explicitly declare what errors you are okay silencing.
        """
        ...

_coconut_Expected = Expected


# should match call above but with Expected
@_t.overload
def safe_call(
    _func: _t.Callable[[], _U],
) -> Expected[_U]: ...
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
# @_t.overload
# def safe_call(
#     _func: _t.Callable[_t.Concatenate[_T, _P], _U],
#     _x: _T,
#     *args: _t.Any,
#     **kwargs: _t.Any,
# ) -> Expected[_U]: ...
# @_t.overload
# def safe_call(
#     _func: _t.Callable[_t.Concatenate[_T, _U, _P], _V],
#     _x: _T,
#     _y: _U,
#     *args: _t.Any,
#     **kwargs: _t.Any,
# ) -> Expected[_V]: ...
# @_t.overload
# def safe_call(
#     _func: _t.Callable[_t.Concatenate[_T, _U, _V, _P], _W],
#     _x: _T,
#     _y: _U,
#     _z: _V,
#     *args: _t.Any,
#     **kwargs: _t.Any,
# ) -> Expected[_W]: ...
@_t.overload
def safe_call(
    _func: _t.Callable[..., _T],
    *args: _t.Any,
    **kwargs: _t.Any,
) -> Expected[_T]:
    """safe_call is a version of call that catches any Exceptions and
    returns an Expected containing either the result or the error.

    Equivalent to:
        def safe_call(f, /, *args, **kwargs):
            try:
                return Expected(f(*args, **kwargs))
            except Exception as err:
                return Expected(error=err)
    """
    ...


# based on call above@_t.overload
@_t.overload
def _coconut_call_or_coefficient(
    _func: _t.Callable[[], _U],
) -> _U: ...
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
# @_t.overload
# def _coconut_call_or_coefficient(
#     _func: _t.Callable[_t.Concatenate[_T, _P], _U],
#     _x: _T,
#     *args: _t.Any,
# ) -> _U: ...
# @_t.overload
# def _coconut_call_or_coefficient(
#     _func: _t.Callable[_t.Concatenate[_T, _U, _P], _V],
#     _x: _T,
#     _y: _U,
#     *args: _t.Any,
# ) -> _V: ...
# @_t.overload
# def _coconut_call_or_coefficient(
#     _func: _t.Callable[_t.Concatenate[_T, _U, _V, _P], _W],
#     _x: _T,
#     _y: _U,
#     _z: _V,
#     *args: _t.Any,
# ) -> _W: ...
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


def recursive_generator(func: _T_iter_func) -> _T_iter_func:
    """Decorator that memoizes a recursive function that returns an iterator (e.g. a recursive generator)."""
    return func
recursive_iterator = recursive_generator


# if sys.version_info >= (3, 12):
#     from typing import override
# else:
try:
    from typing_extensions import override as _override  # type: ignore
    override = _override
except ImportError:
    def override(func: _Tfunc) -> _Tfunc:
        """Declare a method in a subclass as an override of a parent class method.
        Enforces at runtime that the parent class has such a method to be overwritten."""
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
) -> _t.Callable[..., _t.Any]:
    """Decorator to add new cases to a pattern-matching function (where the new case is checked last).

    Pass allow_any_func=True to allow any object as the base_func rather than just pattern-matching functions.
    If add_funcs are passed, addpattern(base_func, add_func) is equivalent to addpattern(base_func)(add_func).
    """
    ...

_coconut_addpattern = addpattern
prepattern = _deprecated("use addpattern instead")(addpattern)


def _coconut_mark_as_match(func: _Tfunc) -> _Tfunc:
    return func


class _coconut_complex_partial(_t.Generic[_T]):
    func: _t.Callable[..., _T] = ...
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
    __name__: str | None = ...


@_t.overload
def _coconut_iter_getitem(
    iterable: _t.Iterable[_T],
    index: _SupportsIndex,
    ) -> _T: ...
@_t.overload
def _coconut_iter_getitem(
    iterable: _t.Iterable[_T],
    index: slice,
    ) -> _t.Iterable[_T]:
    """Iterator slicing works just like sequence slicing, including support for negative indices and slices, and support for `slice` objects in the same way as can be done with normal slicing.

    Coconut's iterator slicing is very similar to Python's `itertools.islice`, but unlike `itertools.islice`, Coconut's iterator slicing supports negative indices, and will preferentially call an object's `__iter_getitem__` (always used if available) or `__getitem__` (only used if the object is a collections.abc.Sequence). Coconut's iterator slicing is also optimized to work well with all of Coconut's built-in objects, only computing the elements of each that are actually necessary to extract the desired slice.

    Some code taken from more_itertools under the terms of its MIT license.
    """
    ...


def _coconut_attritemgetter(
    attr: _t.Optional[_t.Text],
    *is_iter_and_items: _t.Tuple[_t.Tuple[bool, _t.Any], ...],
) -> _t.Callable[[_t.Any], _t.Any]: ...


def _coconut_base_compose(
    func: _t.Callable[[_T], _t.Any],
    *func_infos: _t.Tuple[_Callable, int, bool],
) -> _t.Callable[[_T], _t.Any]: ...


def and_then(
    first_async_func: _t.Callable[_P, _t.Awaitable[_U]],
    second_func: _t.Callable[[_U], _V],
) -> _t.Callable[_P, _t.Awaitable[_V]]:
    """Compose an async function with a normal function.

    Effectively equivalent to:
        def and_then[**T, U, V](
            first_async_func: async (**T) -> U,
            second_func: U -> V,
        ) -> async (**T) -> V =
            async def (*args, **kwargs) -> (
                first_async_func(*args, **kwargs)
                |> await
                |> second_func
            )
    """
    ...

def and_then_await(
    first_async_func: _t.Callable[_P, _t.Awaitable[_U]],
    second_async_func: _t.Callable[[_U], _t.Awaitable[_V]],
) -> _t.Callable[_P, _t.Awaitable[_V]]:
    """Compose two async functions.

    Effectively equivalent to:
        def and_then_await[**T, U, V](
            first_async_func: async (**T) -> U,
            second_async_func: async U -> V,
        ) -> async (**T) -> V =
            async def (*args, **kwargs) -> (
                first_async_func(*args, **kwargs)
                |> await
                |> second_async_func
                |> await
            )
    """
    ...


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
def _coconut_forward_compose(*funcs: _Callable) -> _Callable:
    """Forward composition operator (..>).

    (..>)(f, g) is effectively equivalent to (*args, **kwargs) -> g(f(*args, **kwargs))."""
    ...

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
def _coconut_back_compose(*funcs: _Callable) -> _Callable:
    """Backward composition operator (<..).

    (<..)(f, g) is effectively equivalent to (*args, **kwargs) -> f(g(*args, **kwargs))."""
    ...


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
def _coconut_forward_none_compose(*funcs: _Callable) -> _Callable:
    """Forward none-aware composition operator (..?>).

    (..?>)(f, g) is effectively equivalent to (*args, **kwargs) -> g?(f(*args, **kwargs))."""
    ...

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
def _coconut_back_none_compose(*funcs: _Callable) -> _Callable:
    """Backward none-aware composition operator (<..?).

    (<..?)(f, g) is effectively equivalent to (*args, **kwargs) -> f?(g(*args, **kwargs))."""
    ...


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
def _coconut_forward_star_compose(*funcs: _Callable) -> _Callable:
    """Forward star composition operator (..*>).

    (..*>)(f, g) is effectively equivalent to (*args, **kwargs) -> g(*f(*args, **kwargs))."""
    ...

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
def _coconut_back_star_compose(*funcs: _Callable) -> _Callable:
    """Backward star composition operator (<*..).

    (<*..)(f, g) is effectively equivalent to (*args, **kwargs) -> f(*g(*args, **kwargs))."""
    ...


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
def _coconut_forward_none_star_compose(*funcs: _Callable) -> _Callable:
    """Forward none-aware star composition operator (..?*>).

    (..?*>)(f, g) is effectively equivalent to (*args, **kwargs) -> g?(*f(*args, **kwargs))."""
    ...

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
def _coconut_back_none_star_compose(*funcs: _Callable) -> _Callable:
    """Backward none-aware star composition operator (<*?..).

    (<*?..)(f, g) is effectively equivalent to (*args, **kwargs) -> f?(*g(*args, **kwargs))."""
    ...


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
def _coconut_forward_dubstar_compose(*funcs: _Callable) -> _Callable:
    """Forward double star composition operator (..**>).

    (..**>)(f, g) is effectively equivalent to (*args, **kwargs) -> g(**f(*args, **kwargs))."""
    ...

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
def _coconut_back_dubstar_compose(*funcs: _Callable) -> _Callable:
    """Backward double star composition operator (<**..).

    (<**..)(f, g) is effectively equivalent to (*args, **kwargs) -> f(**g(*args, **kwargs))."""
    ...


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
def _coconut_forward_none_dubstar_compose(*funcs: _Callable) -> _Callable:
    """Forward none-aware double star composition operator (..?**>).

    (..?**>)(f, g) is effectively equivalent to (*args, **kwargs) -> g?(**f(*args, **kwargs))."""
    ...

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
def _coconut_back_none_dubstar_compose(*funcs: _Callable) -> _Callable:
    """Backward none-aware double star composition operator (<**?..).

    (<**?..)(f, g) is effectively equivalent to (*args, **kwargs) -> f?(**g(*args, **kwargs))."""
    ...


def _coconut_pipe(
    x: _T,
    f: _t.Callable[[_T], _U],
) -> _U:
    """Pipe operator (|>). Equivalent to (x, f) -> f(x)."""
    ...
def _coconut_star_pipe(
    xs: _Iterable,
    f: _t.Callable[..., _T],
) -> _T:
    """Star pipe operator (*|>). Equivalent to (xs, f) -> f(*xs)."""
    ...
def _coconut_dubstar_pipe(
    kws: _t.Dict[_t.Text, _t.Any],
    f: _t.Callable[..., _T],
) -> _T:
    """Double star pipe operator (**|>). Equivalent to (kws, f) -> f(**kws)."""
    ...

def _coconut_back_pipe(
    f: _t.Callable[[_T], _U],
    x: _T,
) -> _U:
    """Backward pipe operator (<|). Equivalent to (f, x) -> f(x)."""
    ...
def _coconut_back_star_pipe(
    f: _t.Callable[..., _T],
    xs: _Iterable,
) -> _T:
    """Backward star pipe operator (<*|). Equivalent to (f, xs) -> f(*xs)."""
    ...
def _coconut_back_dubstar_pipe(
    f: _t.Callable[..., _T],
    kws: _t.Dict[_t.Text, _t.Any],
) -> _T:
    """Backward double star pipe operator (<**|). Equivalent to (f, kws) -> f(**kws)."""
    ...

def _coconut_none_pipe(
    x: _t.Optional[_T],
    f: _t.Callable[[_T], _U],
) -> _t.Optional[_U]:
    """Nullable pipe operator (|?>). Equivalent to (x, f) -> f(x) if x is not None else None."""
    ...
def _coconut_none_star_pipe(
    xs: _t.Optional[_Iterable],
    f: _t.Callable[..., _T],
) -> _t.Optional[_T]:
    """Nullable star pipe operator (|?*>). Equivalent to (xs, f) -> f(*xs) if xs is not None else None."""
    ...
def _coconut_none_dubstar_pipe(
    kws: _t.Optional[_t.Dict[_t.Text, _t.Any]],
    f: _t.Callable[..., _T],
) -> _t.Optional[_T]:
    """Nullable double star pipe operator (|?**>). Equivalent to (kws, f) -> f(**kws) if kws is not None else None."""
    ...

def _coconut_back_none_pipe(
    f: _t.Callable[[_T], _U],
    x: _t.Optional[_T],
) -> _t.Optional[_U]:
    """Nullable backward pipe operator (<?|). Equivalent to (f, x) -> f(x) if x is not None else None."""
    ...
def _coconut_back_none_star_pipe(
    f: _t.Callable[..., _T],
    xs: _t.Optional[_Iterable],
) -> _t.Optional[_T]:
    """Nullable backward star pipe operator (<*?|). Equivalent to (f, xs) -> f(*xs) if xs is not None else None."""
    ...
def _coconut_back_none_dubstar_pipe(
    f: _t.Callable[..., _T],
    kws: _t.Optional[_t.Dict[_t.Text, _t.Any]],
) -> _t.Optional[_T]:
    """Nullable backward double star pipe operator (<**?|). Equivalent to (kws, f) -> f(**kws) if kws is not None else None."""
    ...


def _coconut_assert(cond: _t.Any, msg: _t.Optional[_t.Text] = None) -> None:
    """Assert operator (assert). Asserts condition with optional message."""
    assert cond, msg


def _coconut_raise(exc: _t.Optional[Exception] = None, from_exc: _t.Optional[Exception] = None) -> None:
    """Raise operator (raise). Raises exception with optional cause."""
    ...


@_t.overload
def _coconut_bool_and(a: _t.Literal[True], b: _T) -> _T: ...
@_t.overload
def _coconut_bool_and(a: _T, b: _U) -> _t.Union[_T, _U]:
    """Boolean and operator (and). Equivalent to (a, b) -> a and b."""
    ...

@_t.overload
def _coconut_bool_or(a: None, b: _T) -> _T: ...
@_t.overload
def _coconut_bool_or(a: _t.Literal[False], b: _T) -> _T: ...
@_t.overload
def _coconut_bool_or(a: _T, b: _U) -> _t.Union[_T, _U]:
    """Boolean or operator (or). Equivalent to (a, b) -> a or b."""
    ...


def _coconut_in(a: _T, b: _t.Sequence[_T]) -> bool:
    """Containment operator (in). Equivalent to (a, b) -> a in b."""
    ...
def _coconut_not_in(a: _T, b: _t.Sequence[_T]) -> bool:
    """Negative containment operator (not in). Equivalent to (a, b) -> a not in b."""
    ...


@_t.overload
def _coconut_none_coalesce(a: _T, b: None) -> _T: ...
@_t.overload
def _coconut_none_coalesce(a: None, b: _T) -> _T: ...
@_t.overload
def _coconut_none_coalesce(a: _T, b: _U) -> _t.Union[_T, _U]:
    """None coalescing operator (??). Equivalent to (a, b) -> a if a is not None else b."""
    ...


@_t.overload
def _coconut_minus(a: _T) -> _T: ...
@_t.overload
def _coconut_minus(a: int, b: float) -> float: ...
@_t.overload
def _coconut_minus(a: float, b: int) -> float: ...
@_t.overload
def _coconut_minus(a: _T, _b: _T) -> _T:
    """Minus operator (-). Effectively equivalent to (a, b=None) -> a - b if b is not None else -a."""
    ...


@_t.overload
def _coconut_comma_op(_x: _T) -> _t.Tuple[_T]: ...
@_t.overload
def _coconut_comma_op(_x: _T, _y: _U) -> _t.Tuple[_T, _U]: ...
@_t.overload
def _coconut_comma_op(_x: _T, _y: _U, _z: _V) -> _t.Tuple[_T, _U, _V]: ...
@_t.overload
def _coconut_comma_op(*args: _T) -> _t.Tuple[_T, ...]: ...
@_t.overload
def _coconut_comma_op(*args: _t.Any) -> _Tuple:
    """Comma operator (,). Equivalent to (*args) -> args."""
    ...


if sys.version_info < (3, 5):
    @_t.overload
    def _coconut_matmul(a: _T, b: _T) -> _T: ...
    @_t.overload
    def _coconut_matmul(a: _t.Any, b: _t.Any) -> _t.Any:
        """Matrix multiplication operator (@). Implements operator.matmul on any Python version."""
        ...
else:
    _coconut_matmul = _coconut.operator.matmul


def reiterable(iterable: _t.Iterable[_T]) -> _t.Iterable[_T]:
    """Allow an iterator to be iterated over multiple times with the same results."""
    ...
_coconut_reiterable = reiterable


@_t.overload
def async_map(
    async_func: _t.Callable[[_T], _t.Awaitable[_U]],
    iter: _t.Iterable[_T],
    strict: bool = False,
) -> _t.Awaitable[_t.List[_U]]: ...
@_t.overload
def async_map(
    async_func: _t.Callable[..., _t.Awaitable[_U]],
    *iters: _t.Iterable,
    strict: bool = False,
) -> _t.Awaitable[_t.List[_U]]:
    """Map async_func over iters asynchronously using anyio."""
    ...


def multi_enumerate(iterable: _Iterable) -> _t.Iterable[_t.Tuple[_t.Tuple[int, ...], _t.Any]]:
    """Enumerate an iterable of iterables. Works like enumerate, but indexes
    through inner iterables and produces a tuple index representing the index
    in each inner iterable. Supports indexing.

    For numpy arrays, effectively equivalent to:
        it = np.nditer(iterable, flags=["multi_index", "refs_ok"])
        for x in it:
            yield it.multi_index, x

    Also supports len for numpy arrays.
    """
    ...


class _count(_t.Iterable[_T]):
    """count(start, step) returns an infinite iterator starting at start and increasing by step."""
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
    def count(self, elem: _T) -> int | float:
        """Count the number of times elem appears in the count."""
        ...
    def index(self, elem: _T) -> int:
        """Find the index of elem in the count."""
        ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> _count[_U]: ...
    def __copy__(self) -> _count[_T]: ...
count = _coconut_count = _count  # necessary since we define .count()


class cycle(_t.Iterable[_T]):
    """cycle is a modified version of itertools.cycle with a times parameter
    that controls the number of times to cycle through the given iterable
    before stopping."""
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
    def count(self, elem: _T) -> int | float:
        """Count the number of times elem appears in the cycle."""
        ...
    def index(self, elem: _T) -> int:
        """Find the index of elem in the cycle."""
        ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> _t.Iterable[_U]: ...
    def __copy__(self) -> cycle[_T]: ...
    def __len__(self) -> int: ...
_coconut_cycle = cycle


class groupsof(_t.Generic[_T]):
    """groupsof(n, iterable) splits iterable into groups of size n.

    If the length of the iterable is not divisible by n, the last group will be of size < n.
    """
    def __new__(
        cls,
        n: _SupportsIndex,
        iterable: _t.Iterable[_T],
        fillvalue: _T = ...,
    ) -> groupsof[_T]: ...
    def __iter__(self) -> _t.Iterator[_t.Tuple[_T, ...]]: ...
    def __hash__(self) -> int: ...
    def __copy__(self) -> groupsof[_T]: ...
    def __len__(self) -> int: ...
    def __fmap__(self, func: _t.Callable[[_t.Tuple[_T, ...]], _U]) -> _t.Iterable[_U]: ...
_coconut_groupsof = groupsof


class windowsof(_t.Generic[_T]):
    """Produces an iterable that effectively mimics a sliding window over iterable of the given size.
    The step determines the spacing between windowsof.

    If the size is larger than the iterable, windowsof will produce an empty iterable.
    If that is not the desired behavior, fillvalue can be passed and will be used in place of missing values."""
    def __new__(
        cls,
        size: _SupportsIndex,
        iterable: _t.Iterable[_T],
        fillvalue: _T = ...,
        step: _SupportsIndex = 1,
    ) -> windowsof[_T]: ...
    def __iter__(self) -> _t.Iterator[_t.Tuple[_T, ...]]: ...
    def __hash__(self) -> int: ...
    def __copy__(self) -> windowsof[_T]: ...
    def __len__(self) -> int: ...
    def __fmap__(self, func: _t.Callable[[_t.Tuple[_T, ...]], _U]) -> _t.Iterable[_U]: ...
_coconut_windowsof = windowsof


class flatten(_t.Iterable[_T]):
    """Flatten an iterable of iterables into a single iterable.
    Only flattens the top level of the iterable."""
    def __new__(
        cls,
        iterable: _t.Iterable[_t.Iterable[_T]],
        levels: _t.Optional[_SupportsIndex] = 1,
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

    def count(self, elem: _T) -> int:
        """Count the number of times elem appears in the flattened iterable."""
        ...
    def index(self, elem: _T) -> int:
        """Find the index of elem in the flattened iterable."""
        ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> flatten[_U]: ...
_coconut_flatten = flatten


def makedata(data_type: _t.Type[_T], *args: _t.Any) -> _T:
    """Construct an object of the given data_type containing the given arguments."""
    ...
@_deprecated("use makedata instead")
def datamaker(data_type: _t.Type[_T]) -> _t.Callable[..., _T]:
    """DEPRECATED: use makedata instead."""
    return _coconut.functools.partial(makedata, data_type)


def consume(
    iterable: _t.Iterable[_T],
    keep_last: _t.Optional[int] = ...,
    ) -> _t.Sequence[_T]:
    """consume(iterable, keep_last) fully exhausts iterable and returns the last keep_last elements."""
    ...


class multiset(_t.Generic[_T], _coconut.collections.Counter[_T]):
    def add(self, item: _T) -> None: ...
    def discard(self, item: _T) -> None: ...
    def remove(self, item: _T) -> None: ...
    def isdisjoint(self, other: _coconut.collections.Counter[_T]) -> bool: ...
    def __xor__(self, other: _coconut.collections.Counter[_T]) -> multiset[_T]: ...
    def count(self, item: _T) -> int: ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> multiset[_U]: ...
_coconut_multiset = multiset


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
def fmap(func: _t.Callable[[_T, _U], _t.Tuple[_V, _W]], obj: _t.Mapping[_T, _U], starmap_over_mappings: _t.Literal[True]) -> _t.Mapping[_V, _W]:
    """fmap(func, obj) creates a copy of obj with func applied to its contents.

    Supports:
    * Coconut data types
    * `str`, `dict`, `list`, `tuple`, `set`, `frozenset`
    * `dict` (maps over .items())
    * asynchronous iterables
    * numpy arrays (uses np.vectorize)
    * pandas objects (uses .apply)

    Override by defining obj.__fmap__(func).
    """
    ...


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
def flip(func: _t.Callable[..., _T], nargs: _t.Optional[_SupportsIndex]) -> _t.Callable[..., _T]:
    """Given a function, return a new function with inverse argument order.
    If nargs is passed, only the first nargs arguments are reversed."""
    ...


def ident(x: _T, *, side_effect: _t.Optional[_t.Callable[[_T], _t.Any]] = None) -> _T:
    """The identity function. Generally equivalent to x -> x. Useful in point-free programming.
    Accepts one keyword-only argument, side_effect, which specifies a function to call on the argument before it is returned."""
    ...
_coconut_ident = ident


def const(value: _T) -> _t.Callable[..., _T]:
    """Create a function that, whatever its arguments, just returns the given value."""
    ...


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
def lift(func: _t.Callable[..., _W]) -> _t.Callable[..., _t.Callable[..., _W]]:
    """Lift a function up so that all of its arguments are functions.

    For a binary function f(x, y) and two unary functions g(z) and h(z), lift works as the S' combinator:
        lift(f)(g, h)(z) == f(g(z), h(z))

    In general, lift is equivalent to:
        def lift(f) = ((*func_args, **func_kwargs) -> (*args, **kwargs) ->
            f(*(g(*args, **kwargs) for g in func_args), **{lbrace}k: h(*args, **kwargs) for k, h in func_kwargs.items(){rbrace}))

    lift also supports a shortcut form such that lift(f, *func_args, **func_kwargs) is equivalent to lift(f)(*func_args, **func_kwargs).
    """
    ...
_coconut_lift = lift


def all_equal(iterable: _Iterable) -> bool:
    """For a given iterable, check whether all elements in that iterable are equal to each other.

    Supports numpy arrays. Assumes transitivity and 'x != y' being equivalent to 'not (x == y)'.
    """
    ...


@_t.overload
def collectby(
    key_func: _t.Callable[[_T], _U],
    iterable: _t.Iterable[_T],
    *,
    map_using: _t.Callable | None = None,
) -> _t.DefaultDict[_U, _t.List[_T]]: ...
@_t.overload
def collectby(
    key_func: _t.Callable[[_T], _U],
    iterable: _t.Iterable[_T],
    *,
    reduce_func: _t.Callable[[_T, _T], _V],
    reduce_func_init: _T = ...,
    map_using: _t.Callable | None = None,
) -> _t.Dict[_U, _V]: ...
@_t.overload
def collectby(
    key_func: _t.Callable[[_T], _U],
    iterable: _t.Iterable[_T],
    value_func: _t.Callable[[_T], _W],
    *,
    map_using: _t.Callable | None = None,
) -> _t.DefaultDict[_U, _t.List[_W]]: ...
@_t.overload
def collectby(
    key_func: _t.Callable[[_T], _U],
    iterable: _t.Iterable[_T],
    value_func: _t.Callable[[_T], _W],
    *,
    reduce_func: _t.Callable[[_W, _W], _V],
    reduce_func_init: _W = ...,
    map_using: _t.Callable | None = None,
) -> _t.Dict[_U, _V]: ...
@_t.overload
def collectby(
    key_func: _t.Callable[[_T], _U],
    iterable: _t.Iterable[_T],
    *,
    reduce_func: _t.Callable[[_T, _T], _V],
    reduce_func_init: _T = ...,
    map_using: _t.Callable | None = None,
) -> _t.Dict[_U, _V]: ...
@_t.overload
def collectby(
    key_func: _t.Callable[[_U], _t.Any],
    iterable: _t.Iterable[_U],
    value_func: _t.Callable[[_U], _t.Any] | None = None,
    *,
    collect_in: _T,
    reduce_func: _t.Callable | None | _t.Literal[False] = None,
    reduce_func_init: _t.Any = ...,
    map_using: _t.Callable | None = None,
) -> _T:
    """Collect the items in iterable into a dictionary of lists keyed by key_func(item).

    If value_func is passed, collect value_func(item) into each list instead of item.

    If reduce_func is passed, instead of collecting the items into lists, reduce over
    the items for each key with reduce_func, effectively implementing a MapReduce operation.

    If map_using is passed, calculate key_func and value_func by mapping them over
    the iterable using map_using as map. Useful with process_map/thread_map.
    """
    ...

collectby.using_processes = collectby.using_threads = collectby  # type: ignore


@_t.overload
def mapreduce(
    key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
    iterable: _t.Iterable[_T],
    *,
    map_using: _t.Callable | None = None,
) -> _t.DefaultDict[_U, _t.List[_W]]: ...
@_t.overload
def mapreduce(
    key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
    iterable: _t.Iterable[_T],
    *,
    reduce_func: _t.Callable[[_W, _W], _V],
    reduce_func_init: _W = ...,
    map_using: _t.Callable | None = None,
) -> _t.Dict[_U, _V]: ...
@_t.overload
def mapreduce(
    key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
    iterable: _t.Iterable[_T],
    *,
    reduce_func: _t.Callable[[_X, _W], _V],
    reduce_func_init: _X = ...,
    map_using: _t.Callable | None = None,
) -> _t.Dict[_U, _V]: ...
@_t.overload
def mapreduce(
    key_value_func: _t.Callable[[_U], _t.Tuple[_t.Any, _t.Any]],
    iterable: _t.Iterable[_U],
    *,
    collect_in: _T,
    reduce_func: _t.Callable | None | _t.Literal[False] = None,
    reduce_func_init: _t.Any = ...,
    map_using: _t.Callable | None = None,
) -> _T:
    """Map key_value_func over iterable, then collect the values into a dictionary of lists keyed by the keys.

    If reduce_func is passed, instead of collecting the values into lists, reduce over
    the values for each key with reduce_func, effectively implementing a MapReduce operation.

    If map_using is passed, calculate key_value_func by mapping them over
    the iterable using map_using as map. Useful with process_map/thread_map.
    """
    ...

mapreduce.using_processes = mapreduce.using_threads = mapreduce  # type: ignore
_coconut_mapreduce = mapreduce


@_t.overload
def _namedtuple_of(**kwargs: _t.Dict[_t.Text, _T]) -> _t.Tuple[_T, ...]: ...
@_t.overload
def _namedtuple_of(**kwargs: _t.Dict[_t.Text, _t.Any]) -> _Tuple:
    """Construct an anonymous namedtuple of the given keyword arguments."""
    ...


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
# def _coconut_arr_concat_op(
#     dim: int,
#     *arrs: _coconut.npt.NDArray[_DType],
# ) -> _coconut.npt.NDArray[_DType]: ...
# @_t.overload
# def _coconut_arr_concat_op(
#     dim: int,
#     *arrs: _DType,
# ) -> _coconut.npt.NDArray[_DType]: ...
@_t.overload
def _coconut_arr_concat_op(
    dim: _t.Literal[1],
    *arrs: _t.Sequence[_T],
) -> _t.Sequence[_T]: ...
@_t.overload
def _coconut_arr_concat_op(
    dim: _t.Literal[1],
    *arrs: _T,
) -> _t.Sequence[_T]: ...

@_t.overload
def _coconut_arr_concat_op(
    dim: _t.Literal[2],
    *arrs: _t.Sequence[_t.Sequence[_T]],
) -> _t.Sequence[_t.Sequence[_T]]: ...
@_t.overload
def _coconut_arr_concat_op(
    dim: _t.Literal[2],
    *arrs: _t.Sequence[_T],
) -> _t.Sequence[_t.Sequence[_T]]: ...
@_t.overload
def _coconut_arr_concat_op(
    dim: _t.Literal[2],
    *arrs: _T,
) -> _t.Sequence[_t.Sequence[_T]]: ...

@_t.overload
def _coconut_arr_concat_op(dim: int, *arrs: _t.Any) -> _Sequence: ...


class _coconut_SupportsAdd(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (+) Protocol. Equivalent to:

        class SupportsAdd[T, U, V](Protocol):
            def __add__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __add__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsMinus(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (-) Protocol. Equivalent to:

        class SupportsMinus[T, U, V](Protocol):
            def __sub__(self: T, other: U) -> V:
                raise NotImplementedError
            def __neg__(self: T) -> V:
                raise NotImplementedError
    """
    def __sub__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError
    def __neg__(self: _Tco) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsMul(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (*) Protocol. Equivalent to:

        class SupportsMul[T, U, V](Protocol):
            def __mul__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __mul__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsPow(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (**) Protocol. Equivalent to:

        class SupportsPow[T, U, V](Protocol):
            def __pow__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __pow__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsTruediv(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (/) Protocol. Equivalent to:

        class SupportsTruediv[T, U, V](Protocol):
            def __truediv__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __truediv__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsFloordiv(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (//) Protocol. Equivalent to:

        class SupportsFloordiv[T, U, V](Protocol):
            def __floordiv__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __floordiv__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsMod(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (%) Protocol. Equivalent to:

        class SupportsMod[T, U, V](Protocol):
            def __mod__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __mod__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsAnd(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (&) Protocol. Equivalent to:

        class SupportsAnd[T, U, V](Protocol):
            def __and__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __and__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsXor(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (^) Protocol. Equivalent to:

        class SupportsXor[T, U, V](Protocol):
            def __xor__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __xor__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsOr(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (|) Protocol. Equivalent to:

        class SupportsOr[T, U, V](Protocol):
            def __or__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __or__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsLshift(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (<<) Protocol. Equivalent to:

        class SupportsLshift[T, U, V](Protocol):
            def __lshift__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __lshift__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsRshift(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (>>) Protocol. Equivalent to:

        class SupportsRshift[T, U, V](Protocol):
            def __rshift__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __rshift__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsMatmul(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (@) Protocol. Equivalent to:

        class SupportsMatmul[T, U, V](Protocol):
            def __matmul__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __matmul__(self: _Tco, other: _Ucontra) -> _Vco:
        raise NotImplementedError

class _coconut_SupportsInv(_t.Protocol, _t.Generic[_Tco, _Vco]):
    """Coconut (~) Protocol. Equivalent to:

        class SupportsInv[T, V](Protocol):
            def __invert__(self: T) -> V:
                raise NotImplementedError(...)
    """
    def __invert__(self: _Tco) -> _Vco:
        raise NotImplementedError
