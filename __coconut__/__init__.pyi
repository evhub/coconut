# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: MyPy stub file for __coconut__.py.

Conventions used throughout this stub:
- Every name here should match what the generated header (coconut/compiler/templates/header.py_template)
  defines at runtime, with argument names and positional/keyword-ness matching the runtime signatures.
- Coconut's lazy iterator types (map, zip, reiterable, scan, ...) are typed as covariant generics in the
  type of the elements they produce, and are only declared to support the operations (len, indexing,
  reversed, in, .count(), .index(), ...) that they actually implement at runtime.
- Places where `_t.Any` remains are either genuinely dynamic (e.g. the heterogeneous fields of a data type
  being fmapped over) or not expressible in the type system (e.g. the leaves of an arbitrarily nested iterable).
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

_S = _t.TypeVar("_S")
_K = _t.TypeVar("_K")
_K2 = _t.TypeVar("_K2")
_V2 = _t.TypeVar("_V2")

_T1 = _t.TypeVar("_T1")
_T2 = _t.TypeVar("_T2")
_T3 = _t.TypeVar("_T3")
_T4 = _t.TypeVar("_T4")
_T5 = _t.TypeVar("_T5")

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
_Tfunc_co = _t.TypeVar("_Tfunc_co", bound=_Callable, covariant=True)
_Tfunc_contra = _t.TypeVar("_Tfunc_contra", bound=_Callable, contravariant=True)
_Titer = _t.TypeVar("_Titer", bound=_Iterable)
_T_iter_func = _t.TypeVar("_T_iter_func", bound=_t.Callable[..., _Iterable])
_Texc = _t.TypeVar("_Texc", bound=BaseException)

# things that reiterable/tee always consider reiterable and so return unchanged
_Treiterable = _t.TypeVar(
    "_Treiterable",
    bound=_t.Union[
        _t.Sequence[_t.Any],
        _t.Mapping[_t.Any, _t.Any],
        _t.AbstractSet[_t.Any],
        "reiterable[_t.Any]",
        "iterate[_t.Any]",
        "unfold[_t.Any]",
        "_coconut_lazy_slice[_t.Any]",
    ],
)

_P = _t.ParamSpec("_P")
_Q = _t.ParamSpec("_Q")

class _SupportsIndex(_t.Protocol):
    def __index__(self) -> int: ...

class _SupportsReversed(_t.Protocol[_Tco]):
    """Anything with a __reversed__ method (whatever __reversed__ returns is what reversed() gives back)."""
    def __reversed__(self) -> _Tco: ...

class _coconut_SupportsData(_t.Protocol):
    """Protocol satisfied by all Coconut data types."""
    _coconut_is_data: bool

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

if sys.version_info >= (3,):
    import builtins as _builtins
else:
    import __builtin__ as _builtins

import functools as _functools
import itertools as _itertools
import collections as _collections

# typing_extensions always ships with the type checker's copy of typeshed
from typing_extensions import Self as _Self
from typing_extensions import deprecated as _deprecated
from typing_extensions import TypeGuard as _TypeGuard
from typing_extensions import TypeIs as _TypeIs

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


# the py_ versions always refer to the original Python built-ins (map, zip, filter,
#  reversed, and enumerate are redefined below as Coconut's enhanced versions)
py_bytes = _builtins.bytes
py_chr = _builtins.chr
py_dict = _builtins.dict
py_hex = _builtins.hex
py_input = _builtins.input
py_int = _builtins.int
py_map = _builtins.map
py_object = _builtins.object
py_oct = _builtins.oct
py_open = _builtins.open
py_print = _builtins.print
py_range = _builtins.range
py_str = _builtins.str
py_super = _builtins.super
py_zip = _builtins.zip
py_filter = _builtins.filter
py_reversed = _builtins.reversed
py_enumerate = _builtins.enumerate
py_repr = _builtins.repr
py_breakpoint = breakpoint
py_min = _builtins.min
py_max = _builtins.max

# all py_ functions, but not py_ types, go here
chr = _builtins.chr
hex = _builtins.hex
input = _builtins.input
oct = _builtins.oct
open = _builtins.open
print = _builtins.print
range = _builtins.range
min = _builtins.min
max = _builtins.max


_coconut_py_str = py_str
_coconut_super = super
_coconut_range = range
_coconut_type = type


TYPE_CHECKING = _t.TYPE_CHECKING


_coconut_sentinel: _t.Any = ...


@_t.overload
def _coconut_lazy_module(name: str) -> _coconut.types.ModuleType: ...
@_t.overload
def _coconut_lazy_module(name: str, *, attr: str) -> _t.Any: ...


def _coconut_lazy_get(obj: _T) -> _T: ...


class CoconutWarning(Warning):
    """Exception class used for all Coconut warnings."""
_coconut_CoconutWarning = CoconutWarning


class MatchError(Exception):
    """Pattern-matching error. Has attributes .pattern, .value, and .message."""
    max_val_repr_len: int
    pattern: _t.Optional[_t.Text]
    value: _t.Any
    def __init__(self, pattern: _t.Optional[_t.Text] = None, value: _t.Any = None) -> None: ...
    @property
    def message(self) -> _t.Text: ...
_coconut_MatchError = MatchError


def _coconut_get_function_match_error() -> _t.Type[MatchError]: ...


def _coconut_tco(func: _Tfunc) -> _Tfunc:
    return func


# -----------------------------------------------------------------------------------------------------------------------
# ITERATOR BUILT-INS:
# -----------------------------------------------------------------------------------------------------------------------

class _coconut_has_iter(_t.Iterable[_Tco]):
    """Base class for Coconut's lazy iterables that wrap a single underlying iterable."""
    iter: _t.Iterable[_t.Any]
    def get_new_iter(self) -> _t.Iterable[_t.Any]:
        """Tee the underlying iterator."""
        ...
    def __iter__(self) -> _t.Iterator[_Tco]: ...
    def __fmap__(self, func: _t.Callable[[_Tco], _U]) -> map[_U]: ...


class reiterable(_coconut_has_iter[_Tco]):
    """Allow an iterator to be iterated over multiple times with the same results.

    Note that, if the given iterable is already reiterable (a Sequence, Mapping,
    Set, reiterable, or iterate/unfold object), reiterable just returns it unchanged."""
    @_t.overload
    def __new__(cls, iterable: _Treiterable) -> _Treiterable: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, iterable: _t.Iterable[_Tco]) -> reiterable[_Tco]: ...
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _Tco: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_Tco]: ...
    def __reversed__(self) -> _t.Iterable[_Tco]: ...
    def __len__(self) -> int: ...
    def __contains__(self, elem: object) -> bool: ...
    def __copy__(self) -> reiterable[_Tco]: ...
    def count(self, elem: object) -> int:
        """Count the number of times elem appears in the iterable."""
        ...
    def index(self, elem: object) -> int:
        """Find the index of elem in the iterable."""
        ...
_coconut_reiterable = reiterable


# map.using_processes is process_map and map.using_threads is thread_map
class _coconut_map_using_processes(_t.Protocol):
    """The type of map.using_processes, which is process_map."""
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1], _T], iter1: _t.Iterable[_T1], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2, _T3], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2, _T3, _T4], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[..., _T], iter1: _t.Iterable[_t.Any], /, *iterables: _t.Iterable[_t.Any], chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...

class _coconut_map_using_threads(_t.Protocol):
    """The type of map.using_threads, which is thread_map."""
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1], _T], iter1: _t.Iterable[_T1], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2, _T3], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2, _T3, _T4], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[..., _T], iter1: _t.Iterable[_t.Any], /, *iterables: _t.Iterable[_t.Any], chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...


class map(_builtins.map[_T]):
    """Coconut's enhanced map. Supports len, indexing, slicing, reversed, fmap, repr,
    multiple iteration (when the underlying iterables can be iterated over multiple times),
    the strict=True keyword argument, the func/iters attributes, and the
    using_processes/using_threads attributes (which are process_map/thread_map)."""
    func: _t.Callable[..., _T]
    iters: _t.Tuple[_t.Iterable[_t.Any], ...]
    using_processes: _t.ClassVar[_coconut_map_using_processes]
    using_threads: _t.ClassVar[_coconut_map_using_threads]
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1], _T], iter1: _t.Iterable[_T1], /, *, strict: bool = False) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /, *, strict: _t.Literal[False] = False) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /, *, strict: _t.Literal[False] = False) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3, _T4], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], /, *, strict: _t.Literal[False] = False) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3, _T4, _T5], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], iter5: _t.Iterable[_T5], /, *, strict: _t.Literal[False] = False) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[..., _T], iter1: _t.Iterable[_t.Any], iter2: _t.Iterable[_t.Any], iter3: _t.Iterable[_t.Any], iter4: _t.Iterable[_t.Any], iter5: _t.Iterable[_t.Any], iter6: _t.Iterable[_t.Any], /, *iterables: _t.Iterable[_t.Any], strict: _t.Literal[False] = False) -> _Self: ...
    # with multiple iterables, map(..., strict=True) is implemented as (and returns) a starmap over a zip(..., strict=True)
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2], _S], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /, *, strict: _t.Literal[True]) -> starmap[_S]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3], _S], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /, *, strict: _t.Literal[True]) -> starmap[_S]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, function: _t.Callable[..., _S], iter1: _t.Iterable[_t.Any], iter2: _t.Iterable[_t.Any], /, *iterables: _t.Iterable[_t.Any], strict: _t.Literal[True]) -> starmap[_S]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, function: _t.Callable[..., _S], iter1: _t.Iterable[_t.Any], iter2: _t.Iterable[_t.Any], /, *iterables: _t.Iterable[_t.Any], strict: bool) -> _t.Union[map[_S], starmap[_S]]: ...  # type: ignore[misc]
    def __iter__(self) -> _t.Iterator[_T]: ...  # type: ignore[override]
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _Self: ...
    def __reversed__(self) -> _Self: ...
    def __len__(self) -> int: ...
    def __copy__(self) -> _Self: ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> map[_U]: ...
_coconut_map = map


class _coconut_base_parallel_map(map[_T]):
    """Base class for process_map and thread_map."""
    result: _t.Optional[_t.Tuple[_T, ...]]
    chunksize: int
    strict: bool
    stream: bool
    ordered: bool
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1], _T], iter1: _t.Iterable[_T1], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3, _T4], _T], iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], /, *, chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[..., _T], iter1: _t.Iterable[_t.Any], /, *iterables: _t.Iterable[_t.Any], chunksize: int = 1, strict: bool = False, stream: bool = False, ordered: bool = True) -> _Self: ...
    @classmethod
    def multiple_sequential_calls(cls, max_workers: _t.Optional[int] = None) -> _t.ContextManager[None]:
        """Context manager that causes nested calls to use the same pool."""
        ...
    def to_tuple(self) -> _t.Tuple[_T, ...]:
        """Execute the map operation and return the results as a tuple."""
        ...
    def to_stream(self) -> _t.Iterator[_T]:
        """Stream the map operation, yielding results one at a time."""
        ...

class process_map(_coconut_base_parallel_map[_T]):
    """Multi-process implementation of map. Requires arguments to be pickleable.

    For multiple sequential calls, use:
        with process_map.multiple_sequential_calls():
            ...
    """

class thread_map(_coconut_base_parallel_map[_T]):
    """Multi-thread implementation of map.

    For multiple sequential calls, use:
        with thread_map.multiple_sequential_calls():
            ...
    """

parallel_map = process_map
concurrent_map = thread_map


class zip(_builtins.zip[_Tco]):
    """Coconut's enhanced zip. Supports len, indexing, slicing, reversed, fmap, repr,
    multiple iteration (when the underlying iterables can be iterated over multiple times),
    strict=True on all Python versions, and the iters attribute."""
    iters: _t.Tuple[_t.Iterable[_t.Any], ...]
    strict: bool
    @_t.overload
    def __new__(cls, *, strict: bool = False) -> zip[_t.Any]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], /, *, strict: bool = False) -> zip[_t.Tuple[_T1]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /, *, strict: bool = False) -> zip[_t.Tuple[_T1, _T2]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /, *, strict: bool = False) -> zip[_t.Tuple[_T1, _T2, _T3]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], /, *, strict: bool = False) -> zip[_t.Tuple[_T1, _T2, _T3, _T4]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], iter5: _t.Iterable[_T5], /, *, strict: bool = False) -> zip[_t.Tuple[_T1, _T2, _T3, _T4, _T5]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_t.Any], iter2: _t.Iterable[_t.Any], iter3: _t.Iterable[_t.Any], iter4: _t.Iterable[_t.Any], iter5: _t.Iterable[_t.Any], iter6: _t.Iterable[_t.Any], /, *iterables: _t.Iterable[_t.Any], strict: bool = False) -> zip[_t.Tuple[_t.Any, ...]]: ...
    def __iter__(self) -> _t.Iterator[_Tco]: ...  # type: ignore[override]
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _Tco: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _Self: ...
    def __reversed__(self) -> _Self: ...
    def __len__(self) -> int: ...
    def __copy__(self) -> _Self: ...
    def __fmap__(self, func: _t.Callable[[_Tco], _U]) -> map[_U]: ...
_coconut_zip = zip


class zip_longest(zip[_Tco]):
    """Coconut's enhanced version of itertools.zip_longest. Supports all the same features
    as Coconut's enhanced zip, as well as the fillvalue attribute."""
    fillvalue: _t.Any
    @_t.overload
    def __new__(cls, *, fillvalue: object = None) -> zip_longest[_t.Any]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], /, *, fillvalue: object = None) -> zip_longest[_t.Tuple[_T1]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /) -> zip_longest[_t.Tuple[_t.Optional[_T1], _t.Optional[_T2]]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /, *, fillvalue: _S) -> zip_longest[_t.Tuple[_t.Union[_T1, _S], _t.Union[_T2, _S]]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /) -> zip_longest[_t.Tuple[_t.Optional[_T1], _t.Optional[_T2], _t.Optional[_T3]]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /, *, fillvalue: _S) -> zip_longest[_t.Tuple[_t.Union[_T1, _S], _t.Union[_T2, _S], _t.Union[_T3, _S]]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], /) -> zip_longest[_t.Tuple[_t.Optional[_T1], _t.Optional[_T2], _t.Optional[_T3], _t.Optional[_T4]]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], /, *, fillvalue: _S) -> zip_longest[_t.Tuple[_t.Union[_T1, _S], _t.Union[_T2, _S], _t.Union[_T3, _S], _t.Union[_T4, _S]]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], /, *iterables: _t.Iterable[_T1]) -> zip_longest[_t.Tuple[_t.Optional[_T1], ...]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], /, *iterables: _t.Iterable[_T1], fillvalue: _S) -> zip_longest[_t.Tuple[_t.Union[_T1, _S], ...]]: ...
_coconut_zip_longest = zip_longest


class filter(_builtins.filter[_T]):
    """Coconut's enhanced filter. Supports reversed, fmap, repr, multiple iteration
    (when the underlying iterable can be iterated over multiple times), and the func/iter attributes."""
    func: _t.Optional[_t.Callable[[_t.Any], _t.Any]]
    iter: _t.Iterable[_t.Any]
    @_t.overload
    def __new__(cls, function: None, iterable: _t.Iterable[_t.Optional[_T]]) -> filter[_T]: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_S], _TypeGuard[_T]], iterable: _t.Iterable[_S]) -> filter[_T]: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_S], _TypeIs[_T]], iterable: _t.Iterable[_S]) -> filter[_T]: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T], object], iterable: _t.Iterable[_T]) -> filter[_T]: ...
    def __iter__(self) -> _t.Iterator[_T]: ...  # type: ignore[override]
    def __reversed__(self) -> filter[_T]: ...
    def __copy__(self) -> filter[_T]: ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> map[_U]: ...
_coconut_filter = filter


class enumerate(_builtins.enumerate[_T]):
    """Coconut's enhanced enumerate. Supports len, indexing, slicing, fmap, repr,
    multiple iteration (when the underlying iterable can be iterated over multiple times),
    and the iter/start attributes."""
    iter: _t.Iterable[_T]
    start: int
    def __new__(cls, iterable: _t.Iterable[_T], start: _SupportsIndex = 0) -> enumerate[_T]: ...
    def __iter__(self) -> _t.Iterator[_t.Tuple[int, _T]]: ...  # type: ignore[override]
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _t.Tuple[int, _T]: ...
    @_t.overload
    def __getitem__(self, index: slice) -> enumerate[_T]: ...
    def __len__(self) -> int: ...
    def __copy__(self) -> enumerate[_T]: ...
    def __fmap__(self, func: _t.Callable[[_t.Tuple[int, _T]], _U]) -> map[_U]: ...
_coconut_enumerate = enumerate


class reversed(_coconut_has_iter[_Tco]):
    """Coconut's enhanced reversed. Supports len, indexing, slicing, in, .count(), .index(),
    fmap, repr, multiple iteration (when the underlying iterable can be iterated over
    multiple times), and the iter attribute.

    Note that a Coconut reversed object is not itself an iterator; use iter() to get one.
    Additionally, reversed(range(...)) returns a range, and reversing anything other than a
    list or a tuple that defines __reversed__ just calls its __reversed__ method (e.g. reversing
    a Coconut map gives back a map). Sequences are always typed as producing a reversed object."""
    @_t.overload
    def __new__(cls, iterable: range) -> range: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, iterable: _t.Sequence[_Tco]) -> reversed[_Tco]: ...
    @_t.overload
    def __new__(cls, iterable: _SupportsReversed[_S]) -> _S: ...  # type: ignore[misc]
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _Tco: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_Tco]: ...
    def __reversed__(self) -> _t.Iterable[_Tco]: ...
    def __len__(self) -> int: ...
    def __contains__(self, elem: object) -> bool: ...
    def __copy__(self) -> reversed[_Tco]: ...
    def count(self, elem: object) -> int:
        """Count the number of times elem appears in the reversed iterable."""
        ...
    def index(self, elem: object) -> int:
        """Find the index of elem in the reversed iterable."""
        ...
_coconut_reversed = reversed


# starmap.using_processes/using_threads return process_map/thread_map objects
class _coconut_starmap_using_processes(_t.Protocol):
    """starmap.using_processes(function, iterable, **kwargs) is starmap(function, iterable, map_using=process_map$(**kwargs))."""
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1], _T], iterable: _t.Iterable[_t.Tuple[_T1]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2], _T], iterable: _t.Iterable[_t.Tuple[_T1, _T2]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2, _T3], _T], iterable: _t.Iterable[_t.Tuple[_T1, _T2, _T3]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2, _T3, _T4], _T], iterable: _t.Iterable[_t.Tuple[_T1, _T2, _T3, _T4]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[..., _T], iterable: _t.Iterable[_t.Iterable[_t.Any]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> process_map[_T]: ...

class _coconut_starmap_using_threads(_t.Protocol):
    """starmap.using_threads(function, iterable, **kwargs) is starmap(function, iterable, map_using=thread_map$(**kwargs))."""
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1], _T], iterable: _t.Iterable[_t.Tuple[_T1]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2], _T], iterable: _t.Iterable[_t.Tuple[_T1, _T2]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2, _T3], _T], iterable: _t.Iterable[_t.Tuple[_T1, _T2, _T3]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[[_T1, _T2, _T3, _T4], _T], iterable: _t.Iterable[_t.Tuple[_T1, _T2, _T3, _T4]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...
    @_t.overload
    def __call__(self, function: _t.Callable[..., _T], iterable: _t.Iterable[_t.Iterable[_t.Any]], *, chunksize: int = 1, stream: bool = False, ordered: bool = True) -> thread_map[_T]: ...


class starmap(_itertools.starmap[_Tco]):
    """Coconut's enhanced version of itertools.starmap. Supports len, indexing, slicing,
    reversed, fmap, repr, keyword arguments, and the func/iter attributes.

    If map_using is passed, instead returns map_using(args => function(*args), iterable)
    (e.g. map_using=process_map), using a function that can be pickled if function can be.
    starmap.using_processes/starmap.using_threads do that with process_map/thread_map."""
    func: _t.Callable[..., _Tco]
    iter: _t.Iterable[_t.Iterable[_t.Any]]
    using_processes: _t.ClassVar[_coconut_starmap_using_processes]
    using_threads: _t.ClassVar[_coconut_starmap_using_threads]
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1], _Tco], iterable: _t.Iterable[_t.Tuple[_T1]], *, map_using: None = None) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2], _Tco], iterable: _t.Iterable[_t.Tuple[_T1, _T2]], *, map_using: None = None) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3], _Tco], iterable: _t.Iterable[_t.Tuple[_T1, _T2, _T3]], *, map_using: None = None) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3, _T4], _Tco], iterable: _t.Iterable[_t.Tuple[_T1, _T2, _T3, _T4]], *, map_using: None = None) -> _Self: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[..., _Tco], iterable: _t.Iterable[_t.Iterable[_t.Any]], *, map_using: None = None) -> _Self: ...
    # with map_using, starmap returns whatever map_using does
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1], _S], iterable: _t.Iterable[_t.Tuple[_T1]], *, map_using: _t.Callable[..., _t.Iterable[_t.Any]]) -> _t.Iterable[_S]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2], _S], iterable: _t.Iterable[_t.Tuple[_T1, _T2]], *, map_using: _t.Callable[..., _t.Iterable[_t.Any]]) -> _t.Iterable[_S]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3], _S], iterable: _t.Iterable[_t.Tuple[_T1, _T2, _T3]], *, map_using: _t.Callable[..., _t.Iterable[_t.Any]]) -> _t.Iterable[_S]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, function: _t.Callable[[_T1, _T2, _T3, _T4], _S], iterable: _t.Iterable[_t.Tuple[_T1, _T2, _T3, _T4]], *, map_using: _t.Callable[..., _t.Iterable[_t.Any]]) -> _t.Iterable[_S]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, function: _t.Callable[..., _S], iterable: _t.Iterable[_t.Iterable[_t.Any]], *, map_using: _t.Callable[..., _t.Iterable[_t.Any]]) -> _t.Iterable[_S]: ...  # type: ignore[misc]
    def __iter__(self) -> _t.Iterator[_Tco]: ...  # type: ignore[override]
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _Tco: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _Self: ...
    def __reversed__(self) -> _Self: ...
    def __len__(self) -> int: ...
    def __copy__(self) -> _Self: ...
    def __fmap__(self, func: _t.Callable[[_Tco], _U]) -> starmap[_U]: ...
_coconut_starmap = starmap


class takewhile(_itertools.takewhile[_T]):
    """Coconut's version of itertools.takewhile, which additionally supports keyword arguments."""
    def __new__(cls, predicate: _t.Callable[[_T], object], iterable: _t.Iterable[_T]) -> takewhile[_T]: ...


class dropwhile(_itertools.dropwhile[_T]):
    """Coconut's version of itertools.dropwhile, which additionally supports keyword arguments."""
    def __new__(cls, predicate: _t.Callable[[_T], object], iterable: _t.Iterable[_T]) -> dropwhile[_T]: ...


@_t.overload
def tee(iterable: _Treiterable, n: int = 2) -> _t.Tuple[_Treiterable, ...]: ...
@_t.overload
def tee(iterable: _t.Iterator[_T], n: int = 2) -> _t.Tuple[_t.Iterator[_T], ...]: ...
@_t.overload
def tee(iterable: _t.Iterable[_T], n: int = 2) -> _t.Tuple[_t.Iterable[_T], ...]:
    """Coconut's optimized version of itertools.tee.

    Reiterable objects (Sequences, Mappings, Sets, reiterables, and iterate/unfold objects) are returned unchanged
    (n times), copyable iterators are copied, and everything else uses itertools.tee."""
    ...
_coconut_tee = tee


@_t.overload
def reduce(function: _t.Callable[[_T, _S], _T], iterable: _t.Iterable[_S], initial: _T) -> _T: ...
@_t.overload
def reduce(function: _t.Callable[[_T, _T], _T], iterable: _t.Iterable[_T]) -> _T:
    """Coconut's version of functools.reduce, which additionally supports keyword arguments."""
    ...


class scan(_coconut_has_iter[_Tco]):
    """Reduce func over iterable, yielding intermediate results,
    optionally starting from initial."""
    func: _t.Callable[[_t.Any, _t.Any], _Tco]
    initial: _t.Any
    @_t.overload
    def __new__(cls, function: _t.Callable[[_Tco, _Tco], _Tco], iterable: _t.Iterable[_Tco]) -> scan[_Tco]: ...
    @_t.overload
    def __new__(cls, function: _t.Callable[[_Tco, _T], _Tco], iterable: _t.Iterable[_T], initial: _Tco) -> scan[_Tco]: ...
    def __len__(self) -> int: ...
    def __copy__(self) -> scan[_Tco]: ...
_coconut_scan = scan


class _count(_t.Iterable[_T]):
    """count(start, step) returns an infinite iterator starting at start and increasing by step.

    If step is None or 0, count behaves like itertools.repeat."""
    start: _T
    step: _t.Optional[_T]
    @_t.overload
    def __new__(cls, start: int = 0, step: _t.Optional[int] = 1) -> _count[int]: ...
    @_t.overload
    def __new__(cls, start: _T, step: _t.Optional[_T] = ...) -> _count[_T]: ...
    def __iter__(self) -> _t.Iterator[_T]: ...
    def __contains__(self, elem: object) -> bool: ...
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_T]: ...
    def __reversed__(self) -> _count[_T]: ...
    def __hash__(self) -> int: ...
    def count(self, elem: object) -> int | float:
        """Count the number of times elem appears in the count."""
        ...
    def index(self, elem: object) -> int:
        """Find the index of elem in the count."""
        ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> map[_U]: ...
# necessary since we define .count()
count = _count
_coconut_count = _count


class cycle(_coconut_has_iter[_Tco]):
    """cycle is a modified version of itertools.cycle with a times parameter
    that controls the number of times to cycle through the given iterable
    before stopping."""
    times: _t.Optional[int]
    def __new__(
        cls,
        iterable: _t.Iterable[_Tco],
        times: _t.Optional[_SupportsIndex] = None,
    ) -> cycle[_Tco]: ...
    def __contains__(self, elem: object) -> bool: ...
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _Tco: ...
    @_t.overload
    def __getitem__(self, index: slice) -> map[_Tco]: ...
    def __hash__(self) -> int: ...
    def count(self, elem: object) -> int | float:
        """Count the number of times elem appears in the cycle."""
        ...
    def index(self, elem: object) -> int:
        """Find the index of elem in the cycle."""
        ...
    def __copy__(self) -> cycle[_Tco]: ...
    def __len__(self) -> int: ...
    def __reversed__(self) -> cycle[_Tco]: ...
_coconut_cycle = cycle


class _coconut_lazy_slice(_t.Iterable[_Tco]):
    """A lazy slice of an iterate or unfold object, which can be iterated over multiple times.

    Gives the elements of iter at indices start, start + step, start + 2*step, ...,
    either exactly length of them or, if length is None, those before index stop (if not None)."""
    iter: _t.Iterable[_Tco]
    start: int
    stop: _t.Optional[int]
    step: int
    length: _t.Optional[int]
    def __iter__(self) -> _t.Iterator[_Tco]: ...
    def __len__(self) -> int: ...
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _Tco: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_Tco]: ...
    def __reversed__(self) -> _coconut_lazy_slice[_Tco]: ...
    def __copy__(self) -> _coconut_lazy_slice[_Tco]: ...
    def __hash__(self) -> int: ...
    def __fmap__(self, func: _t.Callable[[_Tco], _U]) -> map[_U]: ...


class iterate(_t.Iterable[_T]):
    """iterate(func, x) returns the infinite iterator x, func(x), func(func(x)), ...

    If times is passed, only the first times elements are produced (so func is called times - 1 times),
    which additionally enables len, reversed, and negative indices.

    Iterating over an iterate object again starts over from x, so func should be pure.
    Indexing and slicing are efficient: iterate(func, x)$[n] just applies func n times."""
    func: _t.Callable[[_T], _T]
    x: _T
    times: _t.Optional[int]
    def __new__(
        cls,
        func: _t.Callable[[_T], _T],
        x: _T,
        times: _t.Optional[_SupportsIndex] = None,
    ) -> iterate[_T]: ...
    def __iter__(self) -> _t.Iterator[_T]: ...
    def __len__(self) -> int: ...
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _T: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _coconut_lazy_slice[_T]: ...
    def __reversed__(self) -> _coconut_lazy_slice[_T]: ...
    def __copy__(self) -> iterate[_T]: ...
    def __hash__(self) -> int: ...
    def index(self, elem: object) -> int:
        """Find the index of the first occurrence of elem in the iterate (if times isn't passed, never returns when elem never appears)."""
        ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> map[_U]: ...


class unfold(_t.Iterable[_Tco]):
    """unfold(func, seed) builds an iterator from a state, starting from seed (or None if no seed is passed).

    func(state) should return (value, next_state) to yield value and continue from next_state,
    or None to stop. For example, the digits of 1234 from the right are
        unfold(n => None if n == 0 else (n % 10, n // 10), 1234)

    Iterating over an unfold object again starts over from seed, so func should be pure."""
    func: _t.Callable[[_t.Any], _t.Optional[_t.Tuple[_Tco, _t.Any]]]
    seed: _t.Any
    @_t.overload
    def __new__(
        cls,
        func: _t.Callable[[_S], _t.Optional[_t.Tuple[_Tco, _S]]],
        seed: _S,
    ) -> unfold[_Tco]: ...
    @_t.overload
    def __new__(
        cls,
        func: _t.Callable[[_t.Optional[_S]], _t.Optional[_t.Tuple[_Tco, _S]]],
        seed: None = None,
    ) -> unfold[_Tco]: ...
    def __iter__(self) -> _t.Iterator[_Tco]: ...
    @_t.overload
    def __iter_getitem__(self, index: _SupportsIndex) -> _Tco: ...
    @_t.overload
    def __iter_getitem__(self, index: slice) -> _t.Iterable[_Tco]: ...
    def __copy__(self) -> unfold[_Tco]: ...
    def __hash__(self) -> int: ...
    def index(self, elem: object) -> int:
        """Find the index of the first occurrence of elem in the unfold."""
        ...
    def __fmap__(self, func: _t.Callable[[_Tco], _U]) -> map[_U]: ...


class groupsof(_coconut_has_iter[_t.Tuple[_Tco, ...]]):
    """groupsof(n, iterable) splits iterable into groups of size n.

    If the length of the iterable is not divisible by n, the last group will be of size < n.
    """
    group_size: int
    fillvalue: _t.Any
    @_t.overload
    def __new__(
        cls,
        n: _SupportsIndex,
        iterable: _t.Iterable[_Tco],
    ) -> groupsof[_Tco]: ...
    @_t.overload
    def __new__(
        cls,
        n: _SupportsIndex,
        iterable: _t.Iterable[_T],
        fillvalue: _S,
    ) -> groupsof[_t.Union[_T, _S]]: ...
    def __hash__(self) -> int: ...
    def __copy__(self) -> groupsof[_Tco]: ...
    def __len__(self) -> int: ...
_coconut_groupsof = groupsof


class windowsof(_coconut_has_iter[_t.Tuple[_Tco, ...]]):
    """Produces an iterable that effectively mimics a sliding window over iterable of the given size.
    The step determines the spacing between windowsof.

    If the size is larger than the iterable, windowsof will produce an empty iterable.
    If that is not the desired behavior, fillvalue can be passed and will be used in place of missing values."""
    size: int
    fillvalue: _t.Any
    step: int
    @_t.overload
    def __new__(
        cls,
        size: _SupportsIndex,
        iterable: _t.Iterable[_Tco],
        *,
        step: _SupportsIndex = 1,
    ) -> windowsof[_Tco]: ...
    @_t.overload
    def __new__(
        cls,
        size: _SupportsIndex,
        iterable: _t.Iterable[_T],
        fillvalue: _S,
        step: _SupportsIndex = 1,
    ) -> windowsof[_t.Union[_T, _S]]: ...
    def __hash__(self) -> int: ...
    def __copy__(self) -> windowsof[_Tco]: ...
    def __len__(self) -> int: ...
_coconut_windowsof = windowsof


class flatten(_coconut_has_iter[_Tco]):
    """Flatten an iterable of iterables into a single iterable.
    Only flattens the top level of the iterable unless levels is passed
    (levels=0 returns the iterable unchanged and levels=None flattens all levels).

    Note that flatten does not support len or indexing (use iterator slicing instead)."""
    levels: _t.Optional[int]
    @_t.overload
    def __new__(
        cls,
        iterable: _t.Iterable[_t.Iterable[_Tco]],
        levels: _t.Literal[1] = 1,
    ) -> flatten[_Tco]: ...
    @_t.overload
    def __new__(  # type: ignore[misc]
        cls,
        iterable: _Titer,
        levels: _t.Literal[0],
    ) -> _Titer: ...
    @_t.overload
    def __new__(
        cls,
        iterable: _t.Iterable[_t.Iterable[_t.Iterable[_Tco]]],
        levels: _t.Literal[2],
    ) -> flatten[_Tco]: ...
    @_t.overload
    def __new__(
        cls,
        iterable: _t.Iterable[_t.Any],
        levels: _t.Optional[_SupportsIndex],
    ) -> flatten[_t.Any]: ...
    def __reversed__(self) -> _t.Iterable[_Tco]: ...
    def __hash__(self) -> int: ...
    def __copy__(self) -> flatten[_Tco]: ...
    # in, .count(), and .index() are only supported when levels=1
    def __contains__(self, elem: object) -> bool: ...
    def count(self, elem: object) -> int:
        """Count the number of times elem appears in the flattened iterable."""
        ...
    def index(self, elem: object) -> int:
        """Find the index of elem in the flattened iterable."""
        ...
    def __fmap__(self, func: _t.Callable[[_Tco], _U]) -> _t.Union[flatten[_U], map[_U]]: ...  # type: ignore[override]
_coconut_flatten = flatten


class cartesian_product(_t.Iterable[_Tco]):
    """Coconut's enhanced version of itertools.product. Supports len, in, .count(), fmap,
    repr, and the iters/repeat attributes.

    Additionally supports Cartesian products of numpy arrays (in which case a numpy
    array is returned instead)."""
    iters: _t.Tuple[_t.Iterable[_t.Any], ...]
    repeat: int
    @_t.overload
    def __new__(cls) -> cartesian_product[_t.Tuple[()]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], /) -> cartesian_product[_t.Tuple[_T1]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], /) -> cartesian_product[_t.Tuple[_T1, _T2]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], /) -> cartesian_product[_t.Tuple[_T1, _T2, _T3]]: ...
    @_t.overload
    def __new__(cls, iter1: _t.Iterable[_T1], iter2: _t.Iterable[_T2], iter3: _t.Iterable[_T3], iter4: _t.Iterable[_T4], /) -> cartesian_product[_t.Tuple[_T1, _T2, _T3, _T4]]: ...
    @_t.overload
    def __new__(cls, *iterables: _t.Iterable[_T1], repeat: _SupportsIndex = 1) -> cartesian_product[_t.Tuple[_T1, ...]]: ...
    def __iter__(self) -> _t.Iterator[_Tco]: ...
    def __len__(self) -> int: ...
    def __contains__(self, elem: object) -> bool: ...
    def __copy__(self) -> cartesian_product[_Tco]: ...
    def count(self, elem: object) -> int:
        """Count the number of times elem appears in the product."""
        ...
    @property
    def all_iters(self) -> _t.Iterator[_t.Iterable[_t.Any]]: ...
    def __fmap__(self, func: _t.Callable[[_Tco], _U]) -> map[_U]: ...
_coconut_cartesian_product = cartesian_product


class multi_enumerate(_coconut_has_iter[_t.Tuple[_t.Tuple[int, ...], _t.Any]]):
    """Enumerate an iterable of iterables. Works like enumerate, but indexes
    through inner iterables and produces a tuple index representing the index
    in each inner iterable. Supports indexing.

    For numpy arrays, effectively equivalent to:
        it = np.nditer(iterable, flags=["multi_index", "refs_ok"])
        for x in it:
            yield it.multi_index, x

    Also supports len for numpy arrays.
    """
    def __new__(cls, iterable: _t.Iterable[_t.Any]) -> multi_enumerate: ...
    @property
    def is_numpy(self) -> bool: ...
    @_t.overload
    def __getitem__(self, index: _SupportsIndex) -> _t.Tuple[_t.Tuple[int, ...], _t.Any]: ...
    @_t.overload
    def __getitem__(self, index: slice) -> _t.Iterable[_t.Tuple[_t.Tuple[int, ...], _t.Any]]: ...
    def __len__(self) -> int: ...
    def __copy__(self) -> multi_enumerate: ...


def consume(
    iterable: _t.Iterable[_T],
    keep_last: _t.Optional[int] = 0,
) -> _t.Deque[_T]:
    """consume(iterable, keep_last) fully exhausts iterable and returns the last keep_last elements."""
    ...


# -----------------------------------------------------------------------------------------------------------------------
# FUNCTION BUILT-INS:
# -----------------------------------------------------------------------------------------------------------------------

def call(_func: _t.Callable[_P, _T], /, *args: _P.args, **kwargs: _P.kwargs) -> _T:
    """Function application operator function.

    Equivalent to:
        def call(f, /, *args, **kwargs) = f(*args, **kwargs).
    """
    ...

_coconut_tail_call = call
of = _deprecated("use call instead")(call)


class _coconut_SupportsResult(_t.Protocol[_Tco]):
    @property
    def result(self) -> _t.Optional[_Tco]: ...

class Expected(_t.Tuple[_t.Optional[_Tco], _t.Optional[BaseException]], _t.Generic[_Tco]):
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
            def expect_error(self, *err_types: type[BaseException]) -> Expected[T]:
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

    In this stub, an Expected constructed with an error is typed as Expected[NoReturn],
    which (since Expected is covariant) is compatible with Expected[T] for any T.
    '''
    __slots__ = ()
    _coconut_is_data: bool
    __match_args__ = ("result", "error")
    _coconut_data_defaults: _t.Mapping[int, None] = ...
    @_t.overload
    def __new__(  # type: ignore[misc]
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
    ) -> Expected[_t.NoReturn]: ...
    @_t.overload
    def __new__(
        cls,
        result: None,
        error: BaseException,
    ) -> Expected[_t.NoReturn]: ...
    @property
    def result(self) -> _t.Optional[_Tco]: ...
    @property
    def error(self) -> _t.Optional[BaseException]: ...
    def __bool__(self) -> bool: ...
    def __fmap__(self, func: _t.Callable[[_Tco], _U]) -> Expected[_U]:
        """Maps func over the result if it exists.

        __fmap__ should be used directly only when fmap is not available (e.g. when consuming an Expected in vanilla Python).
        """
        ...
    def and_then(self, func: _t.Callable[[_Tco], Expected[_U]]) -> Expected[_U]:
        """Maps a T -> Expected[U] over an Expected[T] to produce an Expected[U].
        Implements a monadic bind. Equivalent to fmap ..> .join()."""
        ...
    def join(self: _coconut_SupportsResult[Expected[_T]]) -> Expected[_T]:
        """Monadic join. Converts Expected[Expected[T]] to Expected[T]."""
        ...
    def map_error(self, func: _t.Callable[[BaseException], BaseException]) -> Expected[_Tco]:
        """Maps func over the error if it exists."""
        ...
    def handle(
        self,
        err_type: _t.Union[_t.Type[_Texc], _t.Tuple[_t.Type[_Texc], ...]],
        handler: _t.Callable[[_Texc], _U],
    ) -> Expected[_t.Union[_Tco, _U]]:
        """Recover from the given err_type by calling handler on the error to determine the result."""
        ...
    def expect_error(self, *err_types: _t.Type[BaseException]) -> Expected[_Tco]:
        """Raise any errors that do not match the given error types."""
        ...
    def unwrap(self) -> _Tco:
        """Unwrap the result or raise the error."""
        ...
    def or_else(self, func: _t.Callable[[BaseException], Expected[_U]]) -> Expected[_t.Union[_Tco, _U]]:
        """Return self if no error, otherwise return the result of evaluating func on the error."""
        ...
    def result_or_else(self, func: _t.Callable[[BaseException], _U]) -> _t.Union[_Tco, _U]:
        """Return the result if it exists, otherwise return the result of evaluating func on the error."""
        ...
    def result_or(self, default: _U) -> _t.Union[_Tco, _U]:
        """Return the result if it exists, otherwise return the default.

        Since .result_or() completely silences errors, it is highly recommended that you
        call .expect_error() first to explicitly declare what errors you are okay silencing.
        """
        ...

_coconut_Expected = Expected


def safe_call(_func: _t.Callable[_P, _T], /, *args: _P.args, **kwargs: _P.kwargs) -> Expected[_T]:
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


# based on call above, but only supports positional arguments (and allows coefficients)
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


@_t.overload
def recursive_generator(func: _t.Callable[_P, _Treiterable]) -> _t.Callable[_P, _Treiterable]: ...  # type: ignore[overload-overlap]
@_t.overload
def recursive_generator(func: _t.Callable[_P, _t.Iterable[_T]]) -> _t.Callable[_P, reiterable[_T]]:
    """Decorator that memoizes a generator (or any function that returns an iterator).
    Particularly useful for recursive generators, which may require recursive_generator to function properly.

    Calls with equal arguments return the same reiterable."""
    ...
recursive_iterator = recursive_generator


# Coconut's override is presented to type checkers as typing_extensions.override (as documented),
#  which is what makes MyPy/Pyright check that an overridden method actually exists. Note that
#  both MyPy and Pyright special-case override by its fully-qualified name (discarding its declared
#  return type), so no stub can additionally make the __override__ attribute it sets visible.
from typing_extensions import override as override


class _coconut_lru_cache_wrapper(_t.Generic[_P, _Tco]):
    """The memoized function returned by memoize. Has the same signature as the
    wrapped function, plus the functools.lru_cache methods."""
    __wrapped__: _t.Callable[_P, _Tco]
    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _Tco: ...
    def cache_info(self) -> _functools._CacheInfo: ...
    def cache_clear(self) -> None: ...
    def cache_parameters(self) -> _functools._CacheParameters: ...
    def __copy__(self) -> _Self: ...
    def __deepcopy__(self, memo: _t.Any, /) -> _Self: ...
    @_t.overload
    def __get__(self, obj: None, objtype: _t.Optional[type] = None) -> _Self: ...
    @_t.overload
    def __get__(self: _coconut_lru_cache_wrapper[_t.Concatenate[_T, _Q], _U], obj: _T, objtype: _t.Optional[type] = None) -> _coconut_lru_cache_wrapper[_Q, _U]: ...

class _coconut_memoize_recursive_sentinel:
    """The type of memoize.RECURSIVE."""

class _coconut_memoize_func:
    """Decorator that memoizes a function, preventing it from being recomputed
    if it is called multiple times with the same arguments.

    memoize(maxsize=None, typed=False) works like functools.lru_cache (but with maxsize
    defaulting to None), memoize(func) is the same as memoize()(func), and
    memoize(maxsize=memoize.RECURSIVE) produces a memoized function whose cache is
    cleared after each top-level call returns."""
    RECURSIVE: _coconut_memoize_recursive_sentinel
    @_t.overload
    def __call__(self, user_function: _t.Callable[_P, _T], /) -> _coconut_lru_cache_wrapper[_P, _T]: ...
    @_t.overload
    def __call__(self, *, user_function: _t.Callable[_P, _T]) -> _coconut_lru_cache_wrapper[_P, _T]: ...
    @_t.overload
    def __call__(self, maxsize: _coconut_memoize_recursive_sentinel, typed: bool = False) -> _t.Callable[[_t.Callable[_P, _T]], _t.Callable[_P, _T]]: ...
    @_t.overload
    def __call__(self, maxsize: _t.Optional[int] = None, typed: bool = False) -> _t.Callable[[_t.Callable[_P, _T]], _coconut_lru_cache_wrapper[_P, _T]]: ...

memoize: _coconut_memoize_func


def _coconut_call_set_names(cls: object) -> None: ...


class _coconut_base_pattern_func:
    FunctionMatchError: _t.Type[MatchError]
    patterns: _t.List[_Callable]
    def __init__(self, *funcs: _Callable) -> None: ...
    def add_pattern(self, func: _Callable) -> None: ...
    def __call__(self, *args: _t.Any, **kwargs: _t.Any) -> _t.Any: ...

@_t.overload
def addpattern(
    base_func: _t.Callable[[_T], _U],
    *,
    allow_any_func: bool = False,
) -> _t.Callable[[_t.Callable[[_V], _W]], _t.Callable[[_t.Union[_T, _V]], _t.Union[_U, _W]]]: ...
@_t.overload
def addpattern(
    base_func: _t.Callable[..., _U],
    *,
    allow_any_func: bool = False,
) -> _t.Callable[[_t.Callable[..., _W]], _t.Callable[..., _t.Union[_U, _W]]]: ...
@_t.overload
def addpattern(
    base_func: _t.Callable[[_T], _U],
    _add_func: _t.Callable[[_V], _W],
    *,
    allow_any_func: bool = False,
) -> _t.Callable[[_t.Union[_T, _V]], _t.Union[_U, _W]]: ...
@_t.overload
def addpattern(
    base_func: _t.Callable[..., _T],
    _add_func: _t.Callable[..., _U],
    *,
    allow_any_func: bool = False,
) -> _t.Callable[..., _t.Union[_T, _U]]: ...
@_t.overload
def addpattern(
    base_func: _Callable,
    *add_funcs: _Callable,
    allow_any_func: bool = False,
) -> _t.Callable[..., _t.Any]:
    """Decorator to add new cases to a pattern-matching function (where the new case is checked last).

    Pass allow_any_func=True to allow any object as the base_func rather than just pattern-matching functions.
    If add_funcs are passed, addpattern(base_func, add_func) is equivalent to addpattern(base_func)(add_func).
    """
    ...

# what addpattern def uses: the combined function keeps base_func's signature
#  (all pattern-matching functions share the same signature) and returns what either function returns
def _coconut_addpattern(
    base_func: _t.Callable[_P, _T],
    *,
    allow_any_func: bool = False,
) -> _t.Callable[[_t.Callable[..., _U]], _t.Callable[_P, _t.Union[_T, _U]]]: ...

@_deprecated("use addpattern instead")
def prepattern(
    base_func: _t.Callable[..., _T],
    *,
    allow_any_func: bool = False,
) -> _t.Callable[[_t.Callable[..., _U]], _t.Callable[..., _t.Union[_T, _U]]]:
    """DEPRECATED: use addpattern instead."""
    ...


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


_coconut_partial = _coconut.functools.partial


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
    *is_iter_and_items: _t.Tuple[bool, _t.Any],
) -> _t.Callable[[_t.Any], _t.Any]: ...


# update sections, (.<path> <op> <value>), where each update is (path, op, value)
#  and each step of a path is either an attribute name or a one-element list of an index
_coconut_update_t = _t.Tuple[_t.Tuple[_t.Any, ...], _t.Text, _t.Any]
def _coconut_update(obj: _T, *updates: _coconut_update_t) -> _T:
    """Return a copy of obj with each update applied in turn, without mutating obj."""
    ...
class _coconut_updater:
    """Update section (.<path> <op> <value>). Calling it on an object returns an updated copy without mutating the original."""
    updates: _t.Tuple[_coconut_update_t, ...]
    def __init__(self, *updates: _coconut_update_t) -> None: ...
    def __call__(self, obj: _T) -> _T: ...


# function composition (f ..> g, g <.. f, etc.) compiles directly to _coconut_base_compose,
#  where each func_info is (func, number of stars, whether none-aware); the single-argument
#  overloads come first since matching an overloaded function against a ParamSpec can pick
#  an overload with required keyword-only arguments
@_t.overload
def _coconut_base_compose(  # type: ignore[overload-overlap]
    func: _t.Callable[[_S], _T],
    func_info1: _t.Tuple[_t.Callable[[_T], _U], _t.Literal[0], _t.Literal[False]],
    /,
) -> _t.Callable[[_S], _U]: ...
@_t.overload
def _coconut_base_compose(  # type: ignore[overload-overlap]
    func: _t.Callable[[_S], _T],
    func_info1: _t.Tuple[_t.Callable[[_T], _U], _t.Literal[0], _t.Literal[False]],
    func_info2: _t.Tuple[_t.Callable[[_U], _V], _t.Literal[0], _t.Literal[False]],
    /,
) -> _t.Callable[[_S], _V]: ...
@_t.overload
def _coconut_base_compose(  # type: ignore[overload-overlap]
    func: _t.Callable[[_S], _T],
    func_info1: _t.Tuple[_t.Callable[[_T], _U], _t.Literal[0], _t.Literal[False]],
    func_info2: _t.Tuple[_t.Callable[[_U], _V], _t.Literal[0], _t.Literal[False]],
    func_info3: _t.Tuple[_t.Callable[[_V], _W], _t.Literal[0], _t.Literal[False]],
    /,
) -> _t.Callable[[_S], _W]: ...
@_t.overload
def _coconut_base_compose(
    func: _t.Callable[_P, _T],
    func_info1: _t.Tuple[_t.Callable[[_T], _U], _t.Literal[0], _t.Literal[False]],
    /,
) -> _t.Callable[_P, _U]: ...
@_t.overload
def _coconut_base_compose(
    func: _t.Callable[_P, _T],
    func_info1: _t.Tuple[_t.Callable[[_T], _U], _t.Literal[0], _t.Literal[False]],
    func_info2: _t.Tuple[_t.Callable[[_U], _V], _t.Literal[0], _t.Literal[False]],
    /,
) -> _t.Callable[_P, _V]: ...
@_t.overload
def _coconut_base_compose(
    func: _t.Callable[_P, _T],
    func_info1: _t.Tuple[_t.Callable[[_T], _U], _t.Literal[0], _t.Literal[False]],
    func_info2: _t.Tuple[_t.Callable[[_U], _V], _t.Literal[0], _t.Literal[False]],
    func_info3: _t.Tuple[_t.Callable[[_V], _W], _t.Literal[0], _t.Literal[False]],
    /,
) -> _t.Callable[_P, _W]: ...
@_t.overload
def _coconut_base_compose(
    func: _t.Callable[_P, _t.Optional[_T]],
    func_info1: _t.Tuple[_t.Callable[[_T], _U], _t.Literal[0], _t.Literal[True]],
    /,
) -> _t.Callable[_P, _t.Optional[_U]]: ...
@_t.overload
def _coconut_base_compose(
    func: _t.Callable[_P, _t.Tuple[_T1, _T2]],
    func_info1: _t.Tuple[_t.Callable[[_T1, _T2], _U], _t.Literal[1], _t.Literal[False]],
    /,
) -> _t.Callable[_P, _U]: ...
@_t.overload
def _coconut_base_compose(
    func: _t.Callable[[_S], _t.Any],
    *func_infos: _t.Tuple[_Callable, int, bool],
) -> _t.Callable[[_S], _t.Any]: ...
@_t.overload
def _coconut_base_compose(
    func: _t.Callable[_P, _t.Any],
    *func_infos: _t.Tuple[_Callable, int, bool],
) -> _t.Callable[_P, _t.Any]: ...


def and_then(
    first_async_func: _t.Callable[_P, _t.Awaitable[_U]],
    second_func: _t.Callable[[_U], _V],
) -> _t.Callable[_P, _t.Coroutine[_t.Any, _t.Any, _V]]:
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
) -> _t.Callable[_P, _t.Coroutine[_t.Any, _t.Any, _V]]:
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
@_t.overload
def _coconut_star_pipe(
    xs: _t.Tuple[()],
    f: _t.Callable[[], _T],
) -> _T: ...
@_t.overload
def _coconut_star_pipe(
    xs: _t.Tuple[_T1],
    f: _t.Callable[[_T1], _T],
) -> _T: ...
@_t.overload
def _coconut_star_pipe(
    xs: _t.Tuple[_T1, _T2],
    f: _t.Callable[[_T1, _T2], _T],
) -> _T: ...
@_t.overload
def _coconut_star_pipe(
    xs: _t.Tuple[_T1, _T2, _T3],
    f: _t.Callable[[_T1, _T2, _T3], _T],
) -> _T: ...
@_t.overload
def _coconut_star_pipe(
    xs: _Iterable,
    f: _t.Callable[..., _T],
) -> _T:
    """Star pipe operator (*|>). Equivalent to (xs, f) -> f(*xs)."""
    ...
def _coconut_dubstar_pipe(
    kws: _t.Mapping[_t.Text, _t.Any],
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
@_t.overload
def _coconut_back_star_pipe(
    f: _t.Callable[[], _T],
    xs: _t.Tuple[()],
) -> _T: ...
@_t.overload
def _coconut_back_star_pipe(
    f: _t.Callable[[_T1], _T],
    xs: _t.Tuple[_T1],
) -> _T: ...
@_t.overload
def _coconut_back_star_pipe(
    f: _t.Callable[[_T1, _T2], _T],
    xs: _t.Tuple[_T1, _T2],
) -> _T: ...
@_t.overload
def _coconut_back_star_pipe(
    f: _t.Callable[[_T1, _T2, _T3], _T],
    xs: _t.Tuple[_T1, _T2, _T3],
) -> _T: ...
@_t.overload
def _coconut_back_star_pipe(
    f: _t.Callable[..., _T],
    xs: _Iterable,
) -> _T:
    """Backward star pipe operator (<*|). Equivalent to (f, xs) -> f(*xs)."""
    ...
def _coconut_back_dubstar_pipe(
    f: _t.Callable[..., _T],
    kws: _t.Mapping[_t.Text, _t.Any],
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
    kws: _t.Optional[_t.Mapping[_t.Text, _t.Any]],
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
    kws: _t.Optional[_t.Mapping[_t.Text, _t.Any]],
) -> _t.Optional[_T]:
    """Nullable backward double star pipe operator (<**?|). Equivalent to (kws, f) -> f(**kws) if kws is not None else None."""
    ...


def _coconut_assert_msg(expr: _t.Text, *names_and_values: _t.Any) -> _t.Text: ...
def _coconut_eager_thunk(thunk: _t.Callable[[], _T]) -> _t.Callable[[], _T]: ...
def _coconut_assert(cond: _t.Any, msg: _t.Optional[_t.Text] = None) -> None:
    """Assert operator (assert). Asserts condition with optional message."""
    assert cond, msg


def _coconut_raise(
    exc: _t.Optional[_t.Union[BaseException, _t.Type[BaseException]]] = None,
    from_exc: _t.Optional[BaseException] = None,
) -> _t.NoReturn:
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


def _coconut_in(a: object, b: _t.Union[_t.Container[_t.Any], _t.Iterable[_t.Any]]) -> bool:
    """Containment operator (in). Equivalent to (a, b) -> a in b."""
    ...
def _coconut_not_in(a: object, b: _t.Union[_t.Container[_t.Any], _t.Iterable[_t.Any]]) -> bool:
    """Negative containment operator (not in). Equivalent to (a, b) -> a not in b."""
    ...


@_t.overload
def _coconut_none_coalesce(a: _T, b: None) -> _T: ...
@_t.overload
def _coconut_none_coalesce(a: None, b: _T) -> _T: ...
@_t.overload
def _coconut_none_coalesce(a: _t.Optional[_T], b: _U) -> _t.Union[_T, _U]:
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


def _coconut_if_op(cond: _t.Any, if_true: _T, if_false: _U) -> _t.Union[_T, _U]:
    """If operator (if). Equivalent to (cond, if_true, if_false) => if_true if cond else if_false."""
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



def makedata(data_type: _t.Type[_T], *args: _t.Any, fallback_to_init: bool = False) -> _T:
    """Construct an object of the given data_type containing the given arguments."""
    ...
@_deprecated("use makedata instead")
def datamaker(data_type: _t.Type[_T]) -> _t.Callable[..., _T]:
    """DEPRECATED: use makedata instead."""
    ...


class multiset(_collections.Counter[_T]):
    """multiset is a version of set that counts the number of times each element is added.

    Subclass of collections.Counter that additionally implements the full Set and MutableSet
    interfaces (and is registered as a collections.abc.MutableSet)."""
    def add(self, item: _T) -> None:
        """Add an element to a multiset."""
        ...
    def discard(self, item: _T) -> None:
        """Remove an element from a multiset if it is a member."""
        ...
    def remove(self, item: _T, *, allow_missing: bool = False) -> None:
        """Remove an element from a multiset; it must be a member."""
        ...
    def isdisjoint(self, other: _t.Mapping[_t.Any, int]) -> bool:
        """Return True if two multisets have a null intersection."""
        ...
    def __xor__(self, other: _collections.Counter[_U]) -> multiset[_t.Union[_T, _U]]: ...
    def __add__(self, other: _collections.Counter[_U]) -> multiset[_t.Union[_T, _U]]: ...
    def __sub__(self, other: _collections.Counter[_U]) -> multiset[_T]: ...
    def __and__(self, other: _collections.Counter[_U]) -> multiset[_T]: ...
    def __or__(self, other: _collections.Counter[_U]) -> multiset[_t.Union[_T, _U]]: ...  # type: ignore[override]
    def __pos__(self) -> multiset[_T]: ...
    def __neg__(self) -> multiset[_T]: ...
    def count(self, item: _T) -> int:
        """Return the number of times an element occurs in a multiset.
        Equivalent to multiset[item], but additionally verifies the count is non-negative."""
        ...
    def total(self) -> int:
        """Compute the sum of the counts in a multiset.
        Note that total is different from len(multiset), which only counts the unique elements."""
        ...
    def __fmap__(self, func: _t.Callable[[_T], _U]) -> multiset[_U]: ...
_coconut_multiset = multiset


class _coconut_SupportsFmap(_t.Protocol[_Tfunc_contra, _Tco]):
    """Anything with an __fmap__ method."""
    def __fmap__(self, func: _Tfunc_contra) -> _Tco: ...

_Tdata = _t.TypeVar("_Tdata", bound=_coconut_SupportsData)

# the overloads for Coconut's own types come first so that lambdas get the right argument types
#  (these use nominal types rather than Protocols since objects with a __getattr__, like
#  xarray objects, would otherwise match any Protocol)
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: multiset[_T]) -> multiset[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: starmap[_T]) -> starmap[_U]: ...  # type: ignore[overload-overlap]
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: flatten[_T]) -> _t.Union[flatten[_U], map[_U]]: ...  # type: ignore[overload-overlap]
@_t.overload
def fmap(func: _t.Callable[[_t.Tuple[int, _T]], _U], obj: enumerate[_T]) -> map[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.Union[map[_T], zip[_T], filter[_T], _coconut_has_iter[_T], _count[_T], iterate[_T], unfold[_T], _coconut_lazy_slice[_T], cartesian_product[_T]]) -> map[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _coconut_SupportsFmap[_t.Callable[[_T], _U], _V]) -> _V: ...
@_t.overload
def fmap(func: _t.Callable[[_t.Any], _t.Any], obj: _Tdata) -> _Tdata: ...
@_t.overload
def fmap(func: _t.Callable[[str], str], obj: str) -> str: ...
# (bytearray has to come before bytes, since older type checkers treat bytearray as a subtype of bytes)
@_t.overload
def fmap(func: _t.Callable[[int], int], obj: bytearray) -> bytearray: ...
@_t.overload
def fmap(func: _t.Callable[[int], int], obj: bytes) -> bytes: ...
@_t.overload
def fmap(func: _t.Callable[[int], _U], obj: range) -> map[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_t.Tuple[_K, _V]], _t.Tuple[_K2, _V2]], obj: _t.Dict[_K, _V], *, starmap_over_mappings: _t.Literal[False] = False) -> _t.Dict[_K2, _V2]: ...
@_t.overload
def fmap(func: _t.Callable[[_K, _V], _t.Tuple[_K2, _V2]], obj: _t.Dict[_K, _V], *, starmap_over_mappings: _t.Literal[True]) -> _t.Dict[_K2, _V2]: ...
@_t.overload
def fmap(func: _t.Callable[[_t.Tuple[_K, _V]], _t.Tuple[_K2, _V2]], obj: _t.Mapping[_K, _V], *, starmap_over_mappings: _t.Literal[False] = False) -> _t.Mapping[_K2, _V2]: ...
@_t.overload
def fmap(func: _t.Callable[[_K, _V], _t.Tuple[_K2, _V2]], obj: _t.Mapping[_K, _V], *, starmap_over_mappings: _t.Literal[True]) -> _t.Mapping[_K2, _V2]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.AsyncIterable[_T]) -> _t.AsyncIterator[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.Iterator[_T]) -> map[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.List[_T]) -> _t.List[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.Tuple[_T, ...]) -> _t.Tuple[_U, ...]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.Set[_T]) -> _t.Set[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.FrozenSet[_T]) -> _t.FrozenSet[_U]: ...
@_t.overload
def fmap(func: _t.Callable[[_T], _U], obj: _t.Iterable[_T], *, fallback_to_init: bool = False) -> _t.Iterable[_U]:
    """fmap(func, obj) creates a copy of obj with func applied to its contents.

    Supports:
    * Coconut data types
    * `str`, `dict`, `list`, `tuple`, `set`, `frozenset`, `bytes`, `bytearray`
    * `dict` (maps over .items())
    * asynchronous iterables
    * numpy arrays (uses np.vectorize)
    * pandas objects (uses .apply)

    Override by defining obj.__fmap__(func).
    """
    ...

_coconut_fmap = fmap


def _coconut_handle_cls_kwargs(**kwargs: _t.Any) -> _t.Callable[[_T], _T]: ...


def _coconut_handle_cls_stargs(*args: _t.Any) -> _t.Any: ...


_coconut_self_match_types: _t.Tuple[_t.Type[_t.Any], ...] = (bool, bytearray, bytes, dict, float, frozenset, int, py_int, list, set, str, py_str, tuple)


@_t.overload
def _coconut_dict_merge(*dicts: _t.Mapping[_T, _U], for_func: bool = False) -> _t.Dict[_T, _U]: ...
@_t.overload
def _coconut_dict_merge(*dicts: _t.Mapping[_T, _t.Any], for_func: bool = False) -> _t.Dict[_T, _t.Any]: ...
@_t.overload
def _coconut_dict_merge(*dicts: _t.Mapping[_t.Any, _t.Any], for_func: bool = False) -> _t.Dict[_t.Any, _t.Any]: ...


@_t.overload
def flip(func: _t.Callable[[_T], _V], nargs: None = None) -> _t.Callable[[_T], _V]: ...
@_t.overload
def flip(func: _t.Callable[[_T, _U], _V], nargs: None = None) -> _t.Callable[[_U, _T], _V]: ...
@_t.overload
def flip(func: _t.Callable[[_T, _U, _V], _W], nargs: None = None) -> _t.Callable[[_V, _U, _T], _W]: ...
@_t.overload
def flip(func: _t.Callable[[_T, _U, _V, _W], _X], nargs: None = None) -> _t.Callable[[_W, _V, _U, _T], _X]: ...
@_t.overload
def flip(func: _t.Callable[_P, _T], nargs: _t.Literal[0, 1]) -> _t.Callable[_P, _T]: ...
@_t.overload
def flip(func: _t.Callable[_t.Concatenate[_T, _U, _P], _V], nargs: _t.Literal[2]) -> _t.Callable[_t.Concatenate[_U, _T, _P], _V]: ...
@_t.overload
def flip(func: _t.Callable[_t.Concatenate[_T, _U, _V, _P], _W], nargs: _t.Literal[3]) -> _t.Callable[_t.Concatenate[_V, _U, _T, _P], _W]: ...
@_t.overload
def flip(func: _t.Callable[..., _T], nargs: _t.Optional[_SupportsIndex] = None) -> _t.Callable[..., _T]:
    """Given a function, return a new function with inverse argument order.
    If nargs is passed, only the first nargs arguments are reversed."""
    ...


def ident(x: _T, *, side_effect: _t.Optional[_t.Callable[[_T], _t.Any]] = None) -> _T:
    """The identity function. Generally equivalent to x -> x. Useful in point-free programming.
    Accepts one keyword-only argument, side_effect, which specifies a function to call on the argument before it is returned."""
    ...
_coconut_ident = ident


class const(_t.Generic[_Tco]):
    """Create a function that, whatever its arguments, just returns the given value."""
    def __init__(self, value: _Tco) -> None: ...
    @property
    def value(self) -> _Tco: ...
    def __call__(self, *args: _t.Any, **kwargs: _t.Any) -> _Tco: ...


class lift(_t.Generic[_Tfunc_co]):
    """Lift a function up so that all of its arguments are functions that all take the same arguments.

    For a binary function f(x, y) and two unary functions g(z) and h(z), lift works as the S' combinator:
        lift(f)(g, h)(z) == f(g(z), h(z))

    In general, lift is equivalent to:
        def lift(f) = ((*func_args, **func_kwargs) => (*args, **kwargs) => (
            f(*(g(*args, **kwargs) for g in func_args), **{k: h(*args, **kwargs) for k, h in func_kwargs.items()}))
        )

    lift also supports a shortcut form such that lift(f, *func_args, **func_kwargs) is equivalent to lift(f)(*func_args, **func_kwargs).
    """
    @property
    def func(self) -> _Tfunc_co: ...
    @_t.overload
    def __new__(cls, func: _Tfunc_co) -> lift[_Tfunc_co]: ...
    @_t.overload
    def __new__(cls, func: _t.Callable[[_T], _W], _g: _t.Callable[_P, _T], /) -> _t.Callable[_P, _W]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, func: _t.Callable[[_T, _U], _W], _g: _t.Callable[_P, _T], _h: _t.Callable[_P, _U], /) -> _t.Callable[_P, _W]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, func: _t.Callable[[_T, _U, _V], _W], _g: _t.Callable[_P, _T], _h: _t.Callable[_P, _U], _i: _t.Callable[_P, _V], /) -> _t.Callable[_P, _W]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, func: _t.Callable[..., _W], *func_args: _Callable, **func_kwargs: _Callable) -> _t.Callable[..., _W]: ...  # type: ignore[misc]
    @_t.overload
    def __call__(self: lift[_t.Callable[[_T], _W]], _g: _t.Callable[_P, _T], /) -> _t.Callable[_P, _W]: ...
    @_t.overload
    def __call__(self: lift[_t.Callable[[_T, _U], _W]], _g: _t.Callable[_P, _T], _h: _t.Callable[_P, _U], /) -> _t.Callable[_P, _W]: ...
    @_t.overload
    def __call__(self: lift[_t.Callable[[_T, _U, _V], _W]], _g: _t.Callable[_P, _T], _h: _t.Callable[_P, _U], _i: _t.Callable[_P, _V], /) -> _t.Callable[_P, _W]: ...
    @_t.overload
    def __call__(self, *func_args: _Callable, **func_kwargs: _Callable) -> _Callable: ...
_coconut_lift = lift

class lift_apart(lift[_Tfunc_co]):
    """Lift a function up so that all of its arguments are functions that each take separate arguments.

    For a binary function f(x, y) and two unary functions g(z) and h(z), lift_apart works as the D2 combinator:
        lift_apart(f)(g, h)(z, w) == f(g(z), h(w))

    In general, lift_apart is equivalent to:
        def lift_apart(func) = (*func_args, **func_kwargs) => (*args, **kwargs) => func(
            *(f(x) for f, x in zip(func_args, args, strict=True)),
            **{k: func_kwargs[k](kwargs[k]) for k in func_kwargs.keys() | kwargs.keys()},
        )

    lift_apart also supports a shortcut form such that lift_apart(f, *func_args, **func_kwargs) is equivalent to lift_apart(f)(*func_args, **func_kwargs).
    """
    @_t.overload
    def __new__(cls, func: _Tfunc_co) -> lift_apart[_Tfunc_co]: ...
    @_t.overload
    def __new__(cls, func: _t.Callable[[_T], _W], _g: _t.Callable[[_X], _T], /) -> _t.Callable[[_X], _W]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, func: _t.Callable[[_T, _U], _W], _g: _t.Callable[[_X], _T], _h: _t.Callable[[_Y], _U], /) -> _t.Callable[[_X, _Y], _W]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, func: _t.Callable[[_T, _U, _V], _W], _g: _t.Callable[[_X], _T], _h: _t.Callable[[_Y], _U], _i: _t.Callable[[_Z], _V], /) -> _t.Callable[[_X, _Y, _Z], _W]: ...  # type: ignore[misc]
    @_t.overload
    def __new__(cls, func: _t.Callable[..., _W], *func_args: _Callable, **func_kwargs: _Callable) -> _t.Callable[..., _W]: ...  # type: ignore[misc]
    @_t.overload  # type: ignore[override]
    def __call__(self: lift_apart[_t.Callable[[_T], _W]], _g: _t.Callable[[_X], _T], /) -> _t.Callable[[_X], _W]: ...
    @_t.overload
    def __call__(self: lift_apart[_t.Callable[[_T, _U], _W]], _g: _t.Callable[[_X], _T], _h: _t.Callable[[_Y], _U], /) -> _t.Callable[[_X, _Y], _W]: ...
    @_t.overload
    def __call__(self: lift_apart[_t.Callable[[_T, _U, _V], _W]], _g: _t.Callable[[_X], _T], _h: _t.Callable[[_Y], _U], _i: _t.Callable[[_Z], _V], /) -> _t.Callable[[_X, _Y, _Z], _W]: ...
    @_t.overload
    def __call__(self, *func_args: _Callable, **func_kwargs: _Callable) -> _Callable: ...  # pyright: ignore[reportIncompatibleMethodOverride]


def all_equal(iterable: _t.Iterable[_t.Any], to: object = ...) -> bool:
    """For a given iterable, check whether all elements in that iterable are equal to each other.
    If 'to' is passed, check that all the elements are equal to that value.

    Supports numpy arrays. Assumes transitivity and 'x != y' being equivalent to 'not (x == y)'.
    """
    ...


# the type of map_using: anything that works like map(func, iterable)
_coconut_MapUsing = _t.Callable[..., _t.Iterable[_t.Any]]

class _coconut_collectby_func(_t.Protocol):
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: None = None,
        *,
        reduce_func: None = None,
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.DefaultDict[_U, _t.List[_T]]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: _t.Callable[[_T], _W],
        *,
        reduce_func: None = None,
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.DefaultDict[_U, _t.List[_W]]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: None = None,
        *,
        reduce_func: _t.Union[_t.Callable[[_T, _T], _T], _t.Literal[False]],
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.Dict[_U, _T]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: _t.Callable[[_T], _W],
        *,
        reduce_func: _t.Union[_t.Callable[[_W, _W], _W], _t.Literal[False]],
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.Dict[_U, _W]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: None = None,
        *,
        reduce_func: _t.Callable[[_X, _T], _X],
        reduce_func_init: _X,
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.Dict[_U, _X]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: _t.Callable[[_T], _W],
        *,
        reduce_func: _t.Callable[[_X, _W], _X],
        reduce_func_init: _X,
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.Dict[_U, _X]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _t.Any],
        iterable: _t.Iterable[_T],
        value_func: _t.Optional[_t.Callable[[_T], _t.Any]] = None,
        *,
        collect_in: _V,
        reduce_func: _t.Union[_t.Callable[[_t.Any, _t.Any], _t.Any], None, _t.Literal[False]] = False,
        reduce_func_init: _t.Any = ...,
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _V: ...

class _coconut_parallel_collectby_func(_t.Protocol):
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: None = None,
        *,
        reduce_func: None = None,
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.DefaultDict[_U, _t.List[_T]]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: _t.Callable[[_T], _W],
        *,
        reduce_func: None = None,
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.DefaultDict[_U, _t.List[_W]]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: None = None,
        *,
        reduce_func: _t.Union[_t.Callable[[_T, _T], _T], _t.Literal[False]],
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.Dict[_U, _T]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: _t.Callable[[_T], _W],
        *,
        reduce_func: _t.Union[_t.Callable[[_W, _W], _W], _t.Literal[False]],
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.Dict[_U, _W]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: None = None,
        *,
        reduce_func: _t.Callable[[_X, _T], _X],
        reduce_func_init: _X,
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.Dict[_U, _X]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _U],
        iterable: _t.Iterable[_T],
        value_func: _t.Callable[[_T], _W],
        *,
        reduce_func: _t.Callable[[_X, _W], _X],
        reduce_func_init: _X,
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.Dict[_U, _X]: ...
    @_t.overload
    def __call__(
        self,
        key_func: _t.Callable[[_T], _t.Any],
        iterable: _t.Iterable[_T],
        value_func: _t.Optional[_t.Callable[[_T], _t.Any]] = None,
        *,
        collect_in: _V,
        reduce_func: _t.Union[_t.Callable[[_t.Any, _t.Any], _t.Any], None, _t.Literal[False]] = False,
        reduce_func_init: _t.Any = ...,
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _V: ...

class _coconut_collectby_type(_coconut_collectby_func, _t.Protocol):
    """Collect the items in iterable into a dictionary of lists keyed by key_func(item).

    If value_func is passed, collect value_func(item) into each list instead of item.

    If reduce_func is passed, instead of collecting the items into lists, reduce over
    the items for each key with reduce_func, effectively implementing a MapReduce operation.

    If map_using is passed, calculate key_func and value_func by mapping them over
    the iterable using map_using as map. Useful with process_map/thread_map.
    """
    using_processes: _coconut_parallel_collectby_func
    using_threads: _coconut_parallel_collectby_func

collectby: _coconut_collectby_type


class _coconut_mapreduce_func(_t.Protocol):
    @_t.overload
    def __call__(
        self,
        key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
        iterable: _t.Iterable[_T],
        *,
        reduce_func: None = None,
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.DefaultDict[_U, _t.List[_W]]: ...
    @_t.overload
    def __call__(
        self,
        key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
        iterable: _t.Iterable[_T],
        *,
        reduce_func: _t.Union[_t.Callable[[_W, _W], _W], _t.Literal[False]],
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.Dict[_U, _W]: ...
    @_t.overload
    def __call__(
        self,
        key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
        iterable: _t.Iterable[_T],
        *,
        reduce_func: _t.Callable[[_X, _W], _X],
        reduce_func_init: _X,
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _t.Dict[_U, _X]: ...
    @_t.overload
    def __call__(
        self,
        key_value_func: _t.Callable[[_T], _t.Tuple[_t.Any, _t.Any]],
        iterable: _t.Iterable[_T],
        *,
        collect_in: _V,
        reduce_func: _t.Union[_t.Callable[[_t.Any, _t.Any], _t.Any], None, _t.Literal[False]] = False,
        reduce_func_init: _t.Any = ...,
        map_using: _t.Optional[_coconut_MapUsing] = None,
    ) -> _V: ...

class _coconut_parallel_mapreduce_func(_t.Protocol):
    @_t.overload
    def __call__(
        self,
        key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
        iterable: _t.Iterable[_T],
        *,
        reduce_func: None = None,
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.DefaultDict[_U, _t.List[_W]]: ...
    @_t.overload
    def __call__(
        self,
        key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
        iterable: _t.Iterable[_T],
        *,
        reduce_func: _t.Union[_t.Callable[[_W, _W], _W], _t.Literal[False]],
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.Dict[_U, _W]: ...
    @_t.overload
    def __call__(
        self,
        key_value_func: _t.Callable[[_T], _t.Tuple[_U, _W]],
        iterable: _t.Iterable[_T],
        *,
        reduce_func: _t.Callable[[_X, _W], _X],
        reduce_func_init: _X,
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _t.Dict[_U, _X]: ...
    @_t.overload
    def __call__(
        self,
        key_value_func: _t.Callable[[_T], _t.Tuple[_t.Any, _t.Any]],
        iterable: _t.Iterable[_T],
        *,
        collect_in: _V,
        reduce_func: _t.Union[_t.Callable[[_t.Any, _t.Any], _t.Any], None, _t.Literal[False]] = False,
        reduce_func_init: _t.Any = ...,
        ordered: bool = False,
        chunksize: int = 1,
        max_workers: _t.Optional[int] = None,
    ) -> _V: ...

class _coconut_mapreduce_type(_coconut_mapreduce_func, _t.Protocol):
    """Map key_value_func over iterable, then collect the values into a dictionary of lists keyed by the keys.

    If reduce_func is passed, instead of collecting the values into lists, reduce over
    the values for each key with reduce_func, effectively implementing a MapReduce operation.

    If collect_in is passed, initialize the collection from collect_in rather than as a
    collections.defaultdict (if reduce_func=None) or an empty dict (otherwise).

    If map_using is passed, calculate key_value_func by mapping them over
    the iterable using map_using as map. Useful with process_map/thread_map.
    """
    using_processes: _coconut_parallel_mapreduce_func
    using_threads: _coconut_parallel_mapreduce_func

mapreduce: _coconut_mapreduce_type
_coconut_mapreduce = mapreduce


def _namedtuple_of(**kwargs: _T) -> _t.Tuple[_T, ...]:
    """Construct an anonymous namedtuple of the given keyword arguments."""
    ...



@_t.overload
def async_map(
    async_func: _t.Callable[[_T1], _t.Awaitable[_U]],
    iter1: _t.Iterable[_T1],
    /,
    *,
    strict: bool = False,
) -> _t.Coroutine[_t.Any, _t.Any, _t.List[_U]]: ...
@_t.overload
def async_map(
    async_func: _t.Callable[[_T1, _T2], _t.Awaitable[_U]],
    iter1: _t.Iterable[_T1],
    iter2: _t.Iterable[_T2],
    /,
    *,
    strict: bool = False,
) -> _t.Coroutine[_t.Any, _t.Any, _t.List[_U]]: ...
@_t.overload
def async_map(
    async_func: _t.Callable[[_T1, _T2, _T3], _t.Awaitable[_U]],
    iter1: _t.Iterable[_T1],
    iter2: _t.Iterable[_T2],
    iter3: _t.Iterable[_T3],
    /,
    *,
    strict: bool = False,
) -> _t.Coroutine[_t.Any, _t.Any, _t.List[_U]]: ...
@_t.overload
def async_map(
    async_func: _t.Callable[..., _t.Awaitable[_U]],
    *iters: _Iterable,
    strict: bool = False,
) -> _t.Coroutine[_t.Any, _t.Any, _t.List[_U]]:
    """Map async_func over iters asynchronously using anyio."""
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
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, ...],
    types: _t.Optional[_t.Tuple[_t.Any, ...]],
    of_args: _T,
) -> _T: ...
@_t.overload
def _coconut_mk_anon_namedtuple(
    fields: _t.Tuple[_t.Text, ...],
    *,
    of_args: _T,
) -> _T: ...


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
    def __add__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsMinus(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (-) Protocol. Equivalent to:

        class SupportsMinus[T, U, V](Protocol):
            def __sub__(self: T, other: U) -> V:
                raise NotImplementedError
            def __neg__(self: T) -> V:
                raise NotImplementedError
    """
    def __sub__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError
    def __neg__(self: _Tco) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsMul(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (*) Protocol. Equivalent to:

        class SupportsMul[T, U, V](Protocol):
            def __mul__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __mul__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsPow(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (**) Protocol. Equivalent to:

        class SupportsPow[T, U, V](Protocol):
            def __pow__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __pow__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsTruediv(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (/) Protocol. Equivalent to:

        class SupportsTruediv[T, U, V](Protocol):
            def __truediv__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __truediv__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsFloordiv(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (//) Protocol. Equivalent to:

        class SupportsFloordiv[T, U, V](Protocol):
            def __floordiv__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __floordiv__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsMod(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (%) Protocol. Equivalent to:

        class SupportsMod[T, U, V](Protocol):
            def __mod__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __mod__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsAnd(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (&) Protocol. Equivalent to:

        class SupportsAnd[T, U, V](Protocol):
            def __and__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __and__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsXor(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (^) Protocol. Equivalent to:

        class SupportsXor[T, U, V](Protocol):
            def __xor__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __xor__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsOr(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (|) Protocol. Equivalent to:

        class SupportsOr[T, U, V](Protocol):
            def __or__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __or__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsLshift(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (<<) Protocol. Equivalent to:

        class SupportsLshift[T, U, V](Protocol):
            def __lshift__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __lshift__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsRshift(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (>>) Protocol. Equivalent to:

        class SupportsRshift[T, U, V](Protocol):
            def __rshift__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __rshift__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsMatmul(_t.Protocol, _t.Generic[_Tco, _Ucontra, _Vco]):
    """Coconut (@) Protocol. Equivalent to:

        class SupportsMatmul[T, U, V](Protocol):
            def __matmul__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __matmul__(self: _Tco, other: _Ucontra, /) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError

class _coconut_SupportsInv(_t.Protocol, _t.Generic[_Tco, _Vco]):
    """Coconut (~) Protocol. Equivalent to:

        class SupportsInv[T, V](Protocol):
            def __invert__(self: T) -> V:
                raise NotImplementedError(...)
    """
    def __invert__(self: _Tco) -> _Vco:  # pyright: ignore[reportGeneralTypeIssues]
        raise NotImplementedError
