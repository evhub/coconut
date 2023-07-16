#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Header utilities for the compiler.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os.path
from functools import partial

from coconut.root import _indent, _get_root_header
from coconut.exceptions import CoconutInternalException
from coconut.terminal import internal_assert
from coconut.constants import (
    hash_prefix,
    tabideal,
    default_encoding,
    template_ext,
    justify_len,
    report_this_text,
    numpy_modules,
    pandas_numpy_modules,
    jax_numpy_modules,
    self_match_types,
    is_data_var,
    data_defaults_var,
    coconut_cache_dir,
)
from coconut.util import (
    univ_open,
    get_target_info,
    assert_remove_prefix,
)
from coconut.compiler.util import (
    split_comment,
    get_vers_for_target,
    tuple_str_of,
)

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def gethash(compiled):
    """Retrieve a hash from a header."""
    lines = compiled.splitlines()
    if len(lines) < 3 or not lines[2].startswith(hash_prefix):
        return None
    else:
        return assert_remove_prefix(lines[2], hash_prefix)


def minify_header(compiled):
    """Perform basic minification of the header.

    Fails on non-tabideal indentation, strings with #s, or multi-line strings.
    (So don't do those things in the header.)
    """
    compiled = compiled.strip()
    if compiled:
        out = []
        for line in compiled.splitlines():
            new_line, comment = split_comment(line)
            new_line = new_line.rstrip()
            if new_line:
                ind = 0
                while new_line.startswith(" "):
                    new_line = new_line[1:]
                    ind += 1
                internal_assert(ind % tabideal == 0, "invalid indentation in", line)
                new_line = " " * (ind // tabideal) + new_line
            comment = comment.strip()
            if comment:
                new_line += "#" + comment
            if new_line:
                out.append(new_line)
        compiled = "\n".join(out) + "\n"
    return compiled


template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def get_template(template):
    """Read the given template file."""
    with univ_open(os.path.join(template_dir, template) + template_ext, "r") as template_file:
        return template_file.read()


def one_num_ver(target):
    """Return the first number of the target version, if it has one."""
    return target[:1]  # "2", "3", or ""


def section(name, newline_before=True):
    """Generate a section break."""
    line = "# " + name + ": "
    return (
        "\n" * int(newline_before)
        + line
        + "-" * (justify_len - len(line))
        + "\n\n"
    )


def prepare(code, indent=0, **kwargs):
    """Prepare a piece of code for the header."""
    return _indent(code, by=indent, strip=True, **kwargs)


def base_pycondition(target, ver, if_lt=None, if_ge=None, indent=None, newline=False, initial_newline=False, fallback=""):
    """Produce code that depends on the Python version for the given target."""
    internal_assert(isinstance(ver, tuple), "invalid pycondition version")
    internal_assert(if_lt or if_ge, "either if_lt or if_ge must be specified")

    if if_lt:
        if_lt = if_lt.strip()
    if if_ge:
        if_ge = if_ge.strip()

    target_supported_vers = get_vers_for_target(target)

    if all(tar_ver < ver for tar_ver in target_supported_vers):
        if not if_lt:
            return fallback
        out = if_lt

    elif all(tar_ver >= ver for tar_ver in target_supported_vers):
        if not if_ge:
            return fallback
        out = if_ge

    else:
        if if_lt and if_ge:
            out = """if _coconut_sys.version_info < {ver}:
{lt_block}
else:
{ge_block}""".format(
                ver=repr(ver),
                lt_block=_indent(if_lt, by=1),
                ge_block=_indent(if_ge, by=1),
            )
        elif if_lt:
            out = """if _coconut_sys.version_info < {ver}:
{lt_block}""".format(
                ver=repr(ver),
                lt_block=_indent(if_lt, by=1),
            )
        else:
            out = """if _coconut_sys.version_info >= {ver}:
{ge_block}""".format(
                ver=repr(ver),
                ge_block=_indent(if_ge, by=1),
            )

    if indent is not None:
        out = _indent(out, by=indent)
    if initial_newline:
        out = "\n" + out
    if newline:
        out += "\n"
    return out


def make_py_str(str_contents, target, after_py_str_defined=False):
    """Get code that effectively wraps the given code in py_str."""
    return (
        repr(str_contents) if target.startswith("3")
        else "b" + repr(str_contents) if target.startswith("2")
        else "py_str(" + repr(str_contents) + ")" if after_py_str_defined
        else "str(" + repr(str_contents) + ")"
    )


# -----------------------------------------------------------------------------------------------------------------------
# FORMAT DICTIONARY:
# -----------------------------------------------------------------------------------------------------------------------


class Comment(object):
    """When passed to str.format, allows {COMMENT.<>} to serve as a comment."""

    def __getattr__(self, attr):
        """Return an empty string for all comment attributes."""
        return ""


COMMENT = Comment()


def process_header_args(which, use_hash, target, no_tco, strict, no_wrap):
    """Create the dictionary passed to str.format in the header."""
    target_info = get_target_info(target)
    pycondition = partial(base_pycondition, target)

    format_dict = dict(
        COMMENT=COMMENT,
        empty_dict="{}" if target_info >= (3, 7) else "_coconut.dict()",
        empty_py_dict="{}" if target_info >= (3, 7) else "_coconut_py_dict()",
        lbrace="{",
        rbrace="}",
        is_data_var=is_data_var,
        data_defaults_var=data_defaults_var,
        target_major=one_num_ver(target),
        default_encoding=default_encoding,
        hash_line=hash_prefix + use_hash + "\n" if use_hash is not None else "",
        typing_line="# type: ignore\n" if which == "__coconut__" else "",
        _coconut_="_coconut_" if which != "__coconut__" else "",  # only for aliases defined at the end of the header
        VERSION_STR=VERSION_STR,
        module_docstring='"""Built-in Coconut utilities."""\n\n' if which == "__coconut__" else "",
        __coconut__=make_py_str("__coconut__", target),
        _coconut_cached__coconut__=make_py_str("_coconut_cached__coconut__", target),
        coconut_cache_dir=make_py_str(coconut_cache_dir, target),
        object="" if target.startswith("3") else "(object)",
        comma_object="" if target.startswith("3") else ", object",
        comma_slash=", /" if target_info >= (3, 8) else "",
        report_this_text=report_this_text,
        numpy_modules=tuple_str_of(numpy_modules, add_quotes=True),
        pandas_numpy_modules=tuple_str_of(pandas_numpy_modules, add_quotes=True),
        jax_numpy_modules=tuple_str_of(jax_numpy_modules, add_quotes=True),
        self_match_types=tuple_str_of(self_match_types),
        set_super=(
            # we have to use _coconut_super even on the universal target, since once we set __class__ it becomes a local variable
            "super = py_super" if target.startswith("3") else "super = _coconut_super"
        ),
        import_pickle=pycondition(
            (3,),
            if_lt=r'''
import cPickle as pickle
            ''',
            if_ge=r'''
import pickle
            ''',
            indent=1,
        ),
        import_OrderedDict=prepare(
            r'''
OrderedDict = collections.OrderedDict if _coconut_sys.version_info >= (2, 7) else dict
            ''' if not target
            else "OrderedDict = collections.OrderedDict" if target_info >= (2, 7)
            else "OrderedDict = dict",
            indent=1,
        ),
        import_collections_abc=pycondition(
            (3, 3),
            if_lt=r'''
abc = collections
            ''',
            if_ge=r'''
import collections.abc as abc
            ''',
            indent=1,
        ),
        set_zip_longest=prepare(
            r'''
zip_longest = itertools.zip_longest if _coconut_sys.version_info >= (3,) else itertools.izip_longest
            ''' if not target
            else "zip_longest = itertools.zip_longest" if target_info >= (3,)
            else "zip_longest = itertools.izip_longest",
            indent=1,
        ),
        comma_bytearray=", bytearray" if not target.startswith("3") else "",
        lstatic="staticmethod(" if not target.startswith("3") else "",
        rstatic=")" if not target.startswith("3") else "",
        zip_iter=prepare(
            r'''
for items in _coconut.iter(_coconut.zip(*self.iters, strict=self.strict) if _coconut_sys.version_info >= (3, 10) else _coconut.zip_longest(*self.iters, fillvalue=_coconut_sentinel) if self.strict else _coconut.zip(*self.iters)):
    if self.strict and _coconut_sys.version_info < (3, 10) and _coconut.any(x is _coconut_sentinel for x in items):
        raise _coconut.ValueError("zip(..., strict=True) arguments have mismatched lengths")
    yield items
            '''
            if not target else
            r'''
for items in _coconut.iter(_coconut.zip(*self.iters, strict=self.strict)):
    yield items
            '''
            if target_info >= (3, 10) else
            r'''
for items in _coconut.iter(_coconut.zip_longest(*self.iters, fillvalue=_coconut_sentinel) if self.strict else _coconut.zip(*self.iters)):
    if self.strict and _coconut.any(x is _coconut_sentinel for x in items):
        raise _coconut.ValueError("zip(..., strict=True) arguments have mismatched lengths")
    yield items
            ''',
            indent=2,
        ),
        # disabled mocks must have different docstrings so the
        #  interpreter can tell them apart from the real thing
        def_prepattern=(
            r'''def prepattern(base_func, **kwargs):
    """DEPRECATED: use addpattern instead."""
    def pattern_prepender(func):
        return addpattern(func, base_func, **kwargs)
    return pattern_prepender'''
            if not strict else
            r'''def prepattern(*args, **kwargs):
    """Deprecated Coconut built-in 'prepattern' disabled by --strict compilation; use 'addpattern' instead."""
    raise _coconut.NameError("deprecated Coconut built-in 'prepattern' disabled by --strict compilation; use 'addpattern' instead")'''
        ),
        def_datamaker=(
            r'''def datamaker(data_type):
    """DEPRECATED: use makedata instead."""
    return _coconut.functools.partial(makedata, data_type)'''
            if not strict else
            r'''def datamaker(*args, **kwargs):
    """Deprecated Coconut built-in 'datamaker' disabled by --strict compilation; use 'makedata' instead."""
    raise _coconut.NameError("deprecated Coconut built-in 'datamaker' disabled by --strict compilation; use 'makedata' instead")'''
        ),
        of_is_call=(
            "of = call" if not strict else
            r'''def of(*args, **kwargs):
    """Deprecated Coconut built-in 'of' disabled by --strict compilation; use 'call' instead."""
    raise _coconut.NameError("deprecated Coconut built-in 'of' disabled by --strict compilation; use 'call' instead")'''
        ),
        return_method_of_self=pycondition(
            (3,),
            if_lt=r'''
return _coconut.types.MethodType(self, obj, objtype)
            ''',
            if_ge=r'''
return _coconut.types.MethodType(self, obj)
            ''',
            indent=2,
        ),
        return_method_of_self_func=pycondition(
            (3,),
            if_lt=r'''
return _coconut.types.MethodType(self.func, obj, objtype)
            ''',
            if_ge=r'''
return _coconut.types.MethodType(self.func, obj)
            ''',
            indent=2,
        ),
        def_call_set_names=(
            r'''def _coconut_call_set_names(cls):
    for k, v in _coconut.vars(cls).items():
        set_name = _coconut.getattr(v, "__set_name__", None)
        if set_name is not None:
            set_name(cls, k)'''
            if target.startswith("2") else
            r'''def _coconut_call_set_names(cls): pass'''
            if target_info >= (3, 6) else
            r'''def _coconut_call_set_names(cls):
    if _coconut_sys.version_info < (3, 6):
        for k, v in _coconut.vars(cls).items():
            set_name = _coconut.getattr(v, "__set_name__", None)
            if set_name is not None:
                set_name(cls, k)'''
        ),
        set_qualname_none=pycondition(
            (3, 7),
            if_ge=r'''
self.__qualname__ = None
            ''',
            indent=2,
        ),
        set_qualname_func=pycondition(
            (3, 7),
            if_ge=r'''
self.__qualname__ = _coconut.getattr(func, "__qualname__", self.__qualname__)
            ''',
            indent=2,
        ),
        namedtuple_of_implementation=pycondition(
            (3, 6),
            if_ge=r'''
return _coconut_mk_anon_namedtuple(kwargs.keys(), of_kwargs=kwargs)
            ''',
            if_lt=r'''
raise _coconut.RuntimeError("_namedtuple_of is not available on Python < 3.6 (use anonymous namedtuple literals instead)")
            ''',
            indent=1,
        ),
        import_copyreg=pycondition(
            (3,),
            if_lt="import copy_reg as copyreg",
            if_ge="import copyreg",
            indent=1,
        ),
        def_coconut_matmul=pycondition(
            (3, 5),
            if_ge=r'''_coconut_matmul = _coconut.operator.matmul''',
            if_lt=r'''
def _coconut_matmul(a, b, **kwargs):
    """Matrix multiplication operator (@). Implements operator.matmul on any Python version."""
    in_place = kwargs.pop("in_place", False)
    if kwargs:
        raise _coconut.TypeError("_coconut_matmul() got unexpected keyword arguments " + _coconut.repr(kwargs))
    if in_place and _coconut.hasattr(a, "__imatmul__"):
        try:
            result = a.__imatmul__(b)
        except _coconut.NotImplementedError:
            pass
        else:
            if result is not _coconut.NotImplemented:
                return result
    if _coconut.hasattr(a, "__matmul__"):
        try:
            result = a.__matmul__(b)
        except _coconut.NotImplementedError:
            pass
        else:
            if result is not _coconut.NotImplemented:
                return result
    if _coconut.hasattr(b, "__rmatmul__"):
        try:
            result = b.__rmatmul__(a)
        except _coconut.NotImplementedError:
            pass
        else:
            if result is not _coconut.NotImplemented:
                return result
    if "numpy" in (_coconut_get_base_module(a), _coconut_get_base_module(b)):
        from numpy import matmul
        return matmul(a, b)
    raise _coconut.TypeError("unsupported operand type(s) for @: " + _coconut.repr(_coconut.type(a)) + " and " + _coconut.repr(_coconut.type(b)))
            ''',
        ),
        def_total_and_comparisons=pycondition(
            (3, 10),
            if_lt='''
def total(self):
    """Compute the sum of the counts in a multiset.
    Note that total_size is different from len(multiset), which only counts the unique elements."""
    return _coconut.sum(self.values())
def __eq__(self, other):
    if not _coconut.isinstance(other, _coconut.dict):
        return False
    if not _coconut.isinstance(other, _coconut.collections.Counter):
        return _coconut.NotImplemented
    for k, v in self.items():
        if other[k] != v:
            return False
    for k, v in other.items():
        if self[k] != v:
            return False
    return True
__ne__ = _coconut.object.__ne__
def __le__(self, other):
    if not _coconut.isinstance(other, _coconut.collections.Counter):
        return _coconut.NotImplemented
    for k, v in self.items():
        if not (v <= other[k]):
            return False
    for k, v in other.items():
        if not (self[k] <= v):
            return False
    return True
def __lt__(self, other):
    if not _coconut.isinstance(other, _coconut.collections.Counter):
        return _coconut.NotImplemented
    found_diff = False
    for k, v in self.items():
        if not (v <= other[k]):
            return False
        found_diff = found_diff or v != other[k]
    for k, v in other.items():
        if not (self[k] <= v):
            return False
        found_diff = found_diff or self[k] != v
    return found_diff
            ''',
            indent=1,
            newline=True,
        ),
        def_py2_multiset_methods=pycondition(
            (3,),
            if_lt='''
def __bool__(self):
    return _coconut.bool(_coconut.len(self))
keys = _coconut.collections.Counter.viewkeys
values = _coconut.collections.Counter.viewvalues
items = _coconut.collections.Counter.viewitems
            ''',
            indent=1,
            newline=True,
        ),
        def_async_compose_call=prepare(
            r'''
async def __call__(self, *args, **kwargs):
    arg = await self._coconut_func(*args, **kwargs)
    for f, await_f in self._coconut_func_infos:
        arg = f(arg)
        if await_f:
            arg = await arg
    return arg
            ''' if target_info >= (3, 5) else
            pycondition(
                (3, 5),
                if_ge=r'''
_coconut_call_ns = {"_coconut": _coconut}
_coconut_exec("""async def __call__(self, *args, **kwargs):
    arg = await self._coconut_func(*args, **kwargs)
    for f, await_f in self._coconut_func_infos:
        arg = f(arg)
        if await_f:
            arg = await arg
    return arg""", _coconut_call_ns)
__call__ = _coconut_call_ns["__call__"]
                ''',
                if_lt=pycondition(
                    (3, 4),
                    if_ge=r'''
_coconut_call_ns = {"_coconut": _coconut}
_coconut_exec("""def __call__(self, *args, **kwargs):
    arg = yield from self._coconut_func(*args, **kwargs)
    for f, await_f in self._coconut_func_infos:
        arg = f(arg)
        if await_f:
            arg = yield from arg
    raise _coconut.StopIteration(arg)""", _coconut_call_ns)
__call__ = _coconut.asyncio.coroutine(_coconut_call_ns["__call__"])
                    ''',
                    if_lt='''
@_coconut.asyncio.coroutine
def __call__(self, *args, **kwargs):
    arg = yield _coconut.asyncio.From(self._coconut_func(*args, **kwargs))
    for f, await_f in self._coconut_func_infos:
        arg = f(arg)
        if await_f:
            arg = yield _coconut.asyncio.From(arg)
    raise _coconut.asyncio.Return(arg)
                    ''',
                ),
            ),
            indent=1
        ),

        # used in the second round
        tco_comma="_coconut_tail_call, _coconut_tco, " if not no_tco else "",
        call_set_names_comma="_coconut_call_set_names, " if target_info < (3, 6) else "",
        handle_cls_args_comma="_coconut_handle_cls_kwargs, _coconut_handle_cls_stargs, " if not target.startswith("3") else "",
        async_def_anext=prepare(
            r'''
async def __anext__(self):
    return self.func(await self.aiter.__anext__())
            ''' if target_info >= (3, 5) else
            pycondition(
                (3, 5),
                if_ge=r'''
_coconut_anext_ns = {"_coconut": _coconut}
_coconut_exec("""async def __anext__(self):
    return self.func(await self.aiter.__anext__())""", _coconut_anext_ns)
__anext__ = _coconut_anext_ns["__anext__"]
                ''',
                if_lt=r'''
_coconut_anext_ns = {"_coconut": _coconut}
_coconut_exec("""def __anext__(self):
    result = yield from self.aiter.__anext__()
    return self.func(result)""", _coconut_anext_ns)
__anext__ = _coconut.asyncio.coroutine(_coconut_anext_ns["__anext__"])
                ''',
            ),
            indent=1,
        ),
        patch_cached_MatchError=pycondition(
            (3,),
            if_ge=r'''
for _coconut_varname in dir(MatchError):
    try:
        setattr(_coconut_cached_MatchError, _coconut_varname, getattr(MatchError, _coconut_varname))
    except (AttributeError, TypeError):
        pass
            ''',
            indent=1,
            initial_newline=True,
        ),
    )

    # second round for format dict elements that use the format dict
    #  (extra_format_dict is to keep indentation levels matching)
    extra_format_dict = dict(
        # when anything is added to this list it must also be added to *both* __coconut__ stub files
        underscore_imports="{tco_comma}{call_set_names_comma}{handle_cls_args_comma}_namedtuple_of, _coconut, _coconut_Expected, _coconut_MatchError, _coconut_SupportsAdd, _coconut_SupportsMinus, _coconut_SupportsMul, _coconut_SupportsPow, _coconut_SupportsTruediv, _coconut_SupportsFloordiv, _coconut_SupportsMod, _coconut_SupportsAnd, _coconut_SupportsXor, _coconut_SupportsOr, _coconut_SupportsLshift, _coconut_SupportsRshift, _coconut_SupportsMatmul, _coconut_SupportsInv, _coconut_iter_getitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_star_pipe, _coconut_dubstar_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_back_dubstar_pipe, _coconut_none_pipe, _coconut_none_star_pipe, _coconut_none_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_get_function_match_error, _coconut_base_pattern_func, _coconut_addpattern, _coconut_sentinel, _coconut_assert, _coconut_raise, _coconut_mark_as_match, _coconut_reiterable, _coconut_self_match_types, _coconut_dict_merge, _coconut_exec, _coconut_comma_op, _coconut_multi_dim_arr, _coconut_mk_anon_namedtuple, _coconut_matmul, _coconut_py_str, _coconut_flatten, _coconut_multiset, _coconut_back_none_pipe, _coconut_back_none_star_pipe, _coconut_back_none_dubstar_pipe, _coconut_forward_none_compose, _coconut_back_none_compose, _coconut_forward_none_star_compose, _coconut_back_none_star_compose, _coconut_forward_none_dubstar_compose, _coconut_back_none_dubstar_compose, _coconut_call_or_coefficient, _coconut_in, _coconut_not_in".format(**format_dict),
        import_typing=pycondition(
            (3, 5),
            if_ge='''
import typing as _typing
for _name in dir(_typing):
    if not hasattr(typing, _name):
        setattr(typing, _name, getattr(_typing, _name))
            ''',
            if_lt='''
if not hasattr(typing, "TYPE_CHECKING"):
    typing.TYPE_CHECKING = False
if not hasattr(typing, "Any"):
    typing.Any = Ellipsis
if not hasattr(typing, "cast"):
    def cast(t, x):
        """typing.cast[T](t: Type[T], x: Any) -> T = x"""
        return x
    typing.cast = cast
    cast = staticmethod(cast)
if not hasattr(typing, "TypeVar"):
    def TypeVar(name, *args, **kwargs):
        """Runtime mock of typing.TypeVar for Python 3.4 and earlier."""
        return name
    typing.TypeVar = TypeVar
    TypeVar = staticmethod(TypeVar)
if not hasattr(typing, "Generic"):
    class Generic_mock{object}:
        """Runtime mock of typing.Generic for Python 3.4 and earlier."""
        __slots__ = ()
        def __getitem__(self, vars):
            return _coconut.object
    typing.Generic = Generic_mock()
            '''.format(**format_dict),
            indent=1,
        ),
        # all typing_extensions imports must be added to the _coconut stub file
        import_typing_36=pycondition(
            (3, 6),
            if_lt='''
if not hasattr(typing, "NamedTuple"):
    def NamedTuple(name, fields):
        return _coconut.collections.namedtuple(name, [x for x, t in fields])
    typing.NamedTuple = NamedTuple
    NamedTuple = staticmethod(NamedTuple)
            ''',
            indent=1,
            newline=True,
        ),
        import_typing_38=pycondition(
            (3, 8),
            if_lt='''
if not hasattr(typing, "Protocol"):
    class YouNeedToInstallTypingExtensions{object}:
        __slots__ = ()
        def __init__(self):
            raise _coconut.TypeError('Protocols cannot be instantiated')
    typing.Protocol = YouNeedToInstallTypingExtensions
            '''.format(**format_dict),
            indent=1,
            newline=True,
        ),
        import_typing_310=pycondition(
            (3, 10),
            if_lt='''
if not hasattr(typing, "ParamSpec"):
    def ParamSpec(name, *args, **kwargs):
        """Runtime mock of typing.ParamSpec for Python 3.9 and earlier."""
        return _coconut.typing.TypeVar(name)
    typing.ParamSpec = ParamSpec
if not hasattr(typing, "TypeAlias") or not hasattr(typing, "Concatenate"):
    class you_need_to_install_typing_extensions{object}:
        __slots__ = ()
    typing.TypeAlias = typing.Concatenate = you_need_to_install_typing_extensions()
            '''.format(**format_dict),
            indent=1,
            newline=True,
        ),
        import_typing_311=pycondition(
            (3, 11),
            if_lt='''
if not hasattr(typing, "TypeVarTuple"):
    def TypeVarTuple(name, *args, **kwargs):
        """Runtime mock of typing.TypeVarTuple for Python 3.10 and earlier."""
        return _coconut.typing.TypeVar(name)
    typing.TypeVarTuple = TypeVarTuple
if not hasattr(typing, "Unpack"):
    class you_need_to_install_typing_extensions{object}:
        __slots__ = ()
    typing.Unpack = you_need_to_install_typing_extensions()
            '''.format(**format_dict),
            indent=1,
            newline=True,
        ),
        import_asyncio=pycondition(
            (3, 4),
            if_lt='''
try:
    import trollius as asyncio
except ImportError as trollius_import_err:
    class you_need_to_install_trollius(_coconut_missing_module):
        __slots__ = ()
        def coroutine(self, func):
            def raise_import_error(*args, **kwargs):
                raise self._import_err
            return raise_import_error
        def Return(self, obj):
            raise self._import_err
    asyncio = you_need_to_install_trollius(trollius_import_err)
asyncio_Return = asyncio.Return
            '''.format(**format_dict),
            if_ge='''
import asyncio
asyncio_Return = StopIteration
            ''',
            indent=1,
        ),
        class_amap=pycondition(
            (3, 3),
            if_lt=r'''
_coconut_amap = None
            ''',
            if_ge=r'''
class _coconut_amap(_coconut_baseclass):
    __slots__ = ("func", "aiter")
    def __init__(self, func, aiter):
        self.func = func
        self.aiter = aiter
    def __reduce__(self):
        return (self.__class__, (self.func, self.aiter))
    def __repr__(self):
        return "fmap(" + _coconut.repr(self.func) + ", " + _coconut.repr(self.aiter) + ")"
    def __aiter__(self):
        return self
{async_def_anext}
            '''.format(**format_dict),
        ),
        maybe_bind_lru_cache=pycondition(
            (3, 2),
            if_lt='''
try:
    from backports.functools_lru_cache import lru_cache
    functools.lru_cache = lru_cache
except ImportError as lru_cache_import_err:
    functools.lru_cache = _coconut_missing_module(lru_cache_import_err)
            '''.format(**format_dict),
            if_ge=None,
            indent=1,
            newline=True,
        ),
        def_multiset_ops=pycondition(
            (3,),
            if_ge='''
def __add__(self, other):
    out = self.copy()
    out += other
    return out
def __and__(self, other):
    out = self.copy()
    out &= other
    return out
def __or__(self, other):
    out = self.copy()
    out |= other
    return out
def __sub__(self, other):
    out = self.copy()
    out -= other
    return out
def __pos__(self):
    return self.__class__(_coconut.super({_coconut_}multiset, self).__pos__())
def __neg__(self):
    return self.__class__(_coconut.super({_coconut_}multiset, self).__neg__())
            '''.format(**format_dict),
            if_lt='''
def __add__(self, other):
    return self.__class__(_coconut.super({_coconut_}multiset, self).__add__(other))
def __and__(self, other):
    return self.__class__(_coconut.super({_coconut_}multiset, self).__and__(other))
def __or__(self, other):
    return self.__class__(_coconut.super({_coconut_}multiset, self).__or__(other))
def __sub__(self, other):
    return self.__class__(_coconut.super({_coconut_}multiset, self).__sub__(other))
def __pos__(self):
    return self + {_coconut_}multiset()
def __neg__(self):
    return {_coconut_}multiset() - self
            '''.format(**format_dict),
            indent=1,
        ),
    )
    format_dict.update(extra_format_dict)

    return format_dict


# -----------------------------------------------------------------------------------------------------------------------
# HEADER GENERATION:
# -----------------------------------------------------------------------------------------------------------------------


def getheader(which, use_hash, target, no_tco, strict, no_wrap):
    """Generate the specified header.

    IMPORTANT: Any new arguments to this function must be duplicated to
    header_info and process_header_args.
    """
    internal_assert(
        which.startswith("package") or which in (
            "none", "initial", "__coconut__", "sys", "code", "file",
        ),
        "invalid header type",
        which,
    )

    if which == "none":
        return ""

    # initial, __coconut__, package:n, sys, code, file

    target_info = get_target_info(target)
    # header_info only includes arguments that affect __coconut__.py compatibility
    header_info = tuple_str_of((VERSION, target, strict), add_quotes=True)
    format_dict = process_header_args(which, use_hash, target, no_tco, strict, no_wrap)

    if which == "initial" or which == "__coconut__":
        header = '''#!/usr/bin/env python{target_major}
# -*- coding: {default_encoding} -*-
{hash_line}{typing_line}
# Compiled with Coconut version {VERSION_STR}

{module_docstring}'''.format(**format_dict)
    elif use_hash is not None:
        raise CoconutInternalException("can only add a hash to an initial or __coconut__ header, not", which)
    else:
        header = ""

    if which == "initial":
        return header

    # __coconut__, package:n, sys, code, file

    header += section("Coconut Header", newline_before=False)

    if not target.startswith("3"):
        header += "from __future__ import print_function, absolute_import, unicode_literals, division\n"
    # including generator_stop here is fine, even though to universalize generator returns
    #  we raise StopIteration errors, since we only do so when target_info < (3, 3)
    elif target_info >= (3, 13):
        # 3.13 supports lazy annotations, so we should just use that instead of from __future__ import annotations
        header += "from __future__ import generator_stop\n"
    elif target_info >= (3, 7):
        if no_wrap:
            header += "from __future__ import generator_stop\n"
        else:
            header += "from __future__ import generator_stop, annotations\n"
    elif target_info >= (3, 5):
        header += "from __future__ import generator_stop\n"

    header += '''import sys as _coconut_sys
import os as _coconut_os
'''

    if which.startswith("package") or which == "__coconut__":
        header += "_coconut_header_info = " + header_info + "\n"

    levels_up = None
    if which.startswith("package"):
        levels_up = int(assert_remove_prefix(which, "package:"))
        coconut_file_dir = "_coconut_os.path.dirname(_coconut_os.path.abspath(__file__))"
        for _ in range(levels_up):
            coconut_file_dir = "_coconut_os.path.dirname(" + coconut_file_dir + ")"
        header += prepare(
            '''
_coconut_cached__coconut__ = _coconut_sys.modules.get({__coconut__})
_coconut_file_dir = {coconut_file_dir}
_coconut_pop_path = False
if _coconut_cached__coconut__ is None or getattr(_coconut_cached__coconut__, "_coconut_header_info", None) != _coconut_header_info and _coconut_os.path.dirname(_coconut_cached__coconut__.__file__ or "") != _coconut_file_dir:
    if _coconut_cached__coconut__ is not None:
        _coconut_sys.modules[{_coconut_cached__coconut__}] = _coconut_cached__coconut__
        del _coconut_sys.modules[{__coconut__}]
    _coconut_sys.path.insert(0, _coconut_file_dir)
    _coconut_pop_path = True
    _coconut_module_name = _coconut_os.path.splitext(_coconut_os.path.basename(_coconut_file_dir))[0]
    if _coconut_module_name and _coconut_module_name[0].isalpha() and all(c.isalpha() or c.isdigit() for c in _coconut_module_name) and "__init__.py" in _coconut_os.listdir(_coconut_file_dir):
        _coconut_full_module_name = str(_coconut_module_name + ".__coconut__")
        import __coconut__ as _coconut__coconut__
        _coconut__coconut__.__name__ = _coconut_full_module_name
        for _coconut_v in vars(_coconut__coconut__).values():
            if getattr(_coconut_v, "__module__", None) == {__coconut__}:
                try:
                    _coconut_v.__module__ = _coconut_full_module_name
                except AttributeError:
                    _coconut_v_type = type(_coconut_v)
                    if getattr(_coconut_v_type, "__module__", None) == {__coconut__}:
                        _coconut_v_type.__module__ = _coconut_full_module_name
        _coconut_sys.modules[_coconut_full_module_name] = _coconut__coconut__
from __coconut__ import *
from __coconut__ import {underscore_imports}
if _coconut_pop_path:
    _coconut_sys.path.pop(0)
            ''',
            newline=True,
        ).format(
            coconut_file_dir=coconut_file_dir,
            **format_dict
        )

    if which == "sys":
        header += '''from coconut.__coconut__ import *
from coconut.__coconut__ import {underscore_imports}
'''.format(**format_dict)

    # remove coconut_cache_dir from __file__ if it was put there by auto compilation
    header += prepare(
        '''
try:
    __file__ = _coconut_os.path.abspath(__file__) if __file__ else __file__
except NameError:
    pass
else:
    if __file__ and {coconut_cache_dir} in __file__:
        _coconut_file_comps = []
        while __file__:
            __file__, _coconut_file_comp = _coconut_os.path.split(__file__)
            if not _coconut_file_comp:
                _coconut_file_comps.append(__file__)
                break
            if _coconut_file_comp != {coconut_cache_dir}:
                _coconut_file_comps.append(_coconut_file_comp)
        __file__ = _coconut_os.path.join(*reversed(_coconut_file_comps))
        ''',
        newline=True,
    ).format(**format_dict)

    if which == "sys" or which.startswith("package"):
        return header + section("Compiled Coconut")

    # __coconut__, code, file
    internal_assert(which in ("__coconut__", "code", "file"), "wrong header type", which)

    header += prepare(
        '''
_coconut_cached__coconut__ = _coconut_sys.modules.get({_coconut_cached__coconut__}, _coconut_sys.modules.get({__coconut__}))
        ''',
        newline=True,
    ).format(**format_dict)

    if target_info >= (3, 9):
        header += _get_root_header("39")
    if target_info >= (3, 7):
        header += _get_root_header("37")
    elif target.startswith("3"):
        header += _get_root_header("3")
    elif target_info >= (2, 7):
        header += _get_root_header("27")
    elif target.startswith("2"):
        header += _get_root_header("2")
    else:
        header += _get_root_header("universal")

    header += get_template("header").format(**format_dict)

    if which == "file":
        header += section("Compiled Coconut")

    return header
