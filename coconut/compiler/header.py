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

from coconut.root import _indent
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
    jax_numpy_modules,
    self_match_types,
)
from coconut.util import (
    univ_open,
    get_target_info,
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
        return lines[2][len(hash_prefix):]


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


def base_pycondition(target, ver, if_lt=None, if_ge=None, indent=None, newline=False, fallback=""):
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
    if newline:
        out += "\n"
    return out


# -----------------------------------------------------------------------------------------------------------------------
# FORMAT DICTIONARY:
# -----------------------------------------------------------------------------------------------------------------------


class Comment(object):
    """When passed to str.format, allows {COMMENT.<>} to serve as a comment."""

    def __getattr__(self, attr):
        """Return an empty string for all comment attributes."""
        return ""


COMMENT = Comment()


def process_header_args(which, target, use_hash, no_tco, strict, no_wrap):
    """Create the dictionary passed to str.format in the header."""
    target_startswith = one_num_ver(target)
    target_info = get_target_info(target)
    pycondition = partial(base_pycondition, target)

    format_dict = dict(
        COMMENT=COMMENT,
        empty_dict="{}",
        lbrace="{",
        rbrace="}",
        target_startswith=target_startswith,
        default_encoding=default_encoding,
        hash_line=hash_prefix + use_hash + "\n" if use_hash is not None else "",
        typing_line="# type: ignore\n" if which == "__coconut__" else "",
        VERSION_STR=VERSION_STR,
        module_docstring='"""Built-in Coconut utilities."""\n\n' if which == "__coconut__" else "",
        object="" if target_startswith == "3" else "(object)",
        report_this_text=report_this_text,
        numpy_modules=tuple_str_of(numpy_modules, add_quotes=True),
        jax_numpy_modules=tuple_str_of(jax_numpy_modules, add_quotes=True),
        self_match_types=tuple_str_of(self_match_types),
        set_super=(
            # we have to use _coconut_super even on the universal target, since once we set __class__ it becomes a local variable
            "super = _coconut_super\n" if target_startswith != 3 else ""
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
        import_OrderedDict=_indent(
            r'''OrderedDict = collections.OrderedDict if _coconut_sys.version_info >= (2, 7) else dict'''
            if not target
            else "OrderedDict = collections.OrderedDict" if target_info >= (2, 7)
            else "OrderedDict = dict",
            by=1,
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
        set_zip_longest=_indent(
            r'''zip_longest = itertools.zip_longest if _coconut_sys.version_info >= (3,) else itertools.izip_longest'''
            if not target
            else "zip_longest = itertools.zip_longest" if target_info >= (3,)
            else "zip_longest = itertools.izip_longest",
            by=1,
        ),
        comma_bytearray=", bytearray" if target_startswith != "3" else "",
        lstatic="staticmethod(" if target_startswith != "3" else "",
        rstatic=")" if target_startswith != "3" else "",
        zip_iter=_indent(
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
            by=2,
            strip=True,
        ),
        # disabled mocks must have different docstrings so the
        #  interpreter can tell them apart from the real thing
        def_prepattern=(
            r'''def prepattern(base_func, **kwargs):
    """DEPRECATED: use addpattern instead."""
    def pattern_prepender(func):
        return addpattern(func, **kwargs)(base_func)
    return pattern_prepender'''
            if not strict else
            r'''def prepattern(*args, **kwargs):
    """Deprecated feature 'prepattern' disabled by --strict compilation; use 'addpattern' instead."""
    raise _coconut.NameError("deprecated feature 'prepattern' disabled by --strict compilation; use 'addpattern' instead")'''
        ),
        def_datamaker=(
            r'''def datamaker(data_type):
    """DEPRECATED: use makedata instead."""
    return _coconut.functools.partial(makedata, data_type)'''
            if not strict else
            r'''def datamaker(*args, **kwargs):
    """Deprecated feature 'datamaker' disabled by --strict compilation; use 'makedata' instead."""
    raise _coconut.NameError("deprecated feature 'datamaker' disabled by --strict compilation; use 'makedata' instead")'''
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
            if target_startswith == "2" else
            r'''def _coconut_call_set_names(cls): pass'''
            if target_info >= (3, 6) else
            r'''def _coconut_call_set_names(cls):
    if _coconut_sys.version_info < (3, 6):
        for k, v in _coconut.vars(cls).items():
            set_name = _coconut.getattr(v, "__set_name__", None)
            if set_name is not None:
                set_name(cls, k)'''
        ),
        pattern_func_slots=pycondition(
            (3, 7),
            if_lt=r'''
__slots__ = ("FunctionMatchError", "patterns", "__doc__", "__name__")
            ''',
            if_ge=r'''
__slots__ = ("FunctionMatchError", "patterns", "__doc__", "__name__", "__qualname__")
            ''',
            indent=1,
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
    if "numpy" in (a.__class__.__module__, b.__class__.__module__):
        from numpy import matmul
        return matmul(a, b)
    raise _coconut.TypeError("unsupported operand type(s) for @: " + _coconut.repr(_coconut.type(a)) + " and " + _coconut.repr(_coconut.type(b)))
            ''',
        ),
        import_typing_NamedTuple=pycondition(
            (3, 6),
            if_lt='''
def NamedTuple(name, fields):
    return _coconut.collections.namedtuple(name, [x for x, t in fields])
typing.NamedTuple = NamedTuple
NamedTuple = staticmethod(NamedTuple)
            ''',
            indent=1,
            newline=True,
        ),
        # used in the second round
        tco_comma="_coconut_tail_call, _coconut_tco, " if not no_tco else "",
        call_set_names_comma="_coconut_call_set_names, " if target_info < (3, 6) else "",
        handle_cls_args_comma="_coconut_handle_cls_kwargs, _coconut_handle_cls_stargs, " if target_startswith != "3" else "",
        async_def_anext=_indent(
            r'''
async def __anext__(self):
    return self.func(await self.aiter.__anext__())
            ''' if target_info >= (3, 5) else
            pycondition(
                (3, 5),
                if_ge=r'''
_coconut_anext_ns = {}
_coconut_exec("""async def __anext__(self):
    return self.func(await self.aiter.__anext__())""", _coconut_anext_ns)
__anext__ = _coconut_anext_ns["__anext__"]
                ''',
                if_lt=r'''
_coconut_anext_ns = {}
_coconut_exec("""def __anext__(self):
    result = yield from self.aiter.__anext__()
    return self.func(result)""", _coconut_anext_ns)
__anext__ = _coconut.asyncio.coroutine(_coconut_anext_ns["__anext__"])
                ''',
            ),
            by=1,
            strip=True,
        ),
    )

    # second round for format dict elements that use the format dict
    extra_format_dict = dict(
        # when anything is added to this list it must also be added to *both* __coconut__ stub files
        underscore_imports="{tco_comma}{call_set_names_comma}{handle_cls_args_comma}_namedtuple_of, _coconut, _coconut_super, _coconut_MatchError, _coconut_iter_getitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_star_pipe, _coconut_dubstar_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_back_dubstar_pipe, _coconut_none_pipe, _coconut_none_star_pipe, _coconut_none_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_get_function_match_error, _coconut_base_pattern_func, _coconut_addpattern, _coconut_sentinel, _coconut_assert, _coconut_raise, _coconut_mark_as_match, _coconut_reiterable, _coconut_self_match_types, _coconut_dict_merge, _coconut_exec, _coconut_comma_op, _coconut_multi_dim_arr, _coconut_mk_anon_namedtuple, _coconut_matmul".format(**format_dict),
        import_typing=pycondition(
            (3, 5),
            if_ge="import typing",
            if_lt='''
class typing_mock{object}:
    """The typing module is not available at runtime in Python 3.4 or earlier; try hiding your typedefs behind an 'if TYPE_CHECKING:' block."""
    TYPE_CHECKING = False
    Any = Ellipsis
    def cast(self, t, x):
        """typing.cast[TT <: Type, T <: TT](t: TT, x: Any) -> T = x"""
        return x
    def __getattr__(self, name):
        raise _coconut.ImportError("the typing module is not available at runtime in Python 3.4 or earlier; try hiding your typedefs behind an 'if TYPE_CHECKING:' block")
typing = typing_mock()
            '''.format(**format_dict),
            indent=1,
        ),
        # all typing_extensions imports must be added to the _coconut stub file
        import_typing_TypeAlias_ParamSpec_Concatenate=pycondition(
            (3, 10),
            if_lt='''
try:
    from typing_extensions import TypeAlias, ParamSpec, Concatenate
except ImportError:
    class you_need_to_install_typing_extensions{object}:
        __slots__ = ()
    TypeAlias = ParamSpec = Concatenate = you_need_to_install_typing_extensions()
typing.TypeAlias = TypeAlias
typing.ParamSpec = ParamSpec
typing.Concatenate = Concatenate
            '''.format(**format_dict),
            indent=1,
            newline=True,
        ),
        import_typing_TypeVarTuple_Unpack=pycondition(
            (3, 11),
            if_lt='''
try:
    from typing_extensions import TypeVarTuple, Unpack
except ImportError:
    class you_need_to_install_typing_extensions{object}:
        __slots__ = ()
    TypeVarTuple = Unpack = you_need_to_install_typing_extensions()
typing.TypeVarTuple = TypeVarTuple
typing.Unpack = Unpack
            '''.format(**format_dict),
            indent=1,
            newline=True,
        ),
        import_asyncio=pycondition(
            (3, 4),
            if_lt='''
try:
    import trollius as asyncio
except ImportError:
    class you_need_to_install_trollius{object}:
        __slots__ = ()
    asyncio = you_need_to_install_trollius()
            '''.format(**format_dict),
            if_ge='''
import asyncio
            ''',
            indent=1,
        ),
        class_amap=pycondition(
            (3, 3),
            if_lt=r'''
_coconut_amap = None
            ''',
            if_ge=r'''
class _coconut_amap(_coconut_base_hashable):
    __slots__ = ("func", "aiter")
    def __init__(self, func, aiter):
        self.func = func
        self.aiter = aiter
    def __reduce__(self):
        return (self.__class__, (self.func, self.aiter))
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
except ImportError:
    class you_need_to_install_backports_functools_lru_cache{object}:
        __slots__ = ()
    functools.lru_cache = you_need_to_install_backports_functools_lru_cache()
            '''.format(**format_dict),
            if_ge=None,
            indent=1,
            newline=True,
        ),
    )
    format_dict.update(extra_format_dict)

    return format_dict


# -----------------------------------------------------------------------------------------------------------------------
# HEADER GENERATION:
# -----------------------------------------------------------------------------------------------------------------------


def getheader(which, target, use_hash, no_tco, strict, no_wrap):
    """Generate the specified header."""
    internal_assert(
        which.startswith("package") or which in (
            "none", "initial", "__coconut__", "sys", "code", "file",
        ),
        "invalid header type",
        which,
    )

    if which == "none":
        return ""

    target_startswith = one_num_ver(target)
    target_info = get_target_info(target)

    # initial, __coconut__, package:n, sys, code, file

    format_dict = process_header_args(which, target, use_hash, no_tco, strict, no_wrap)

    if which == "initial" or which == "__coconut__":
        header = '''#!/usr/bin/env python{target_startswith}
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

    if target_startswith != "3":
        header += "from __future__ import print_function, absolute_import, unicode_literals, division\n"
    # including generator_stop here is fine, even though to universalize
    #  generator returns we raise StopIteration errors, since we only do so
    #  when target_info < (3, 3)
    elif target_info >= (3, 7):
        if no_wrap:
            header += "from __future__ import generator_stop\n"
        else:
            header += "from __future__ import generator_stop, annotations\n"
    elif target_info >= (3, 5):
        header += "from __future__ import generator_stop\n"

    if which.startswith("package"):
        levels_up = int(which[len("package:"):])
        coconut_file_dir = "_coconut_os.path.dirname(_coconut_os.path.abspath(__file__))"
        for _ in range(levels_up):
            coconut_file_dir = "_coconut_os.path.dirname(" + coconut_file_dir + ")"
        return header + '''import sys as _coconut_sys, os as _coconut_os
_coconut_file_dir = {coconut_file_dir}
_coconut_cached_module = _coconut_sys.modules.get({__coconut__})
if _coconut_cached_module is not None and _coconut_os.path.dirname(_coconut_cached_module.__file__) != _coconut_file_dir:  # type: ignore
    del _coconut_sys.modules[{__coconut__}]
_coconut_sys.path.insert(0, _coconut_file_dir)
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
_coconut_sys.path.pop(0)
'''.format(
            coconut_file_dir=coconut_file_dir,
            __coconut__=(
                '"__coconut__"' if target_startswith == "3"
                else 'b"__coconut__"' if target_startswith == "2"
                else 'str("__coconut__")'
            ),
            **format_dict
        ) + section("Compiled Coconut")

    if which == "sys":
        return header + '''import sys as _coconut_sys
from coconut.__coconut__ import *
from coconut.__coconut__ import {underscore_imports}
'''.format(**format_dict)

    # __coconut__, code, file

    header += "import sys as _coconut_sys\n"

    if target_info >= (3, 7):
        header += PY37_HEADER
    elif target_startswith == "3":
        header += PY3_HEADER
    elif target_info >= (2, 7):
        header += PY27_HEADER
    elif target_startswith == "2":
        header += PY2_HEADER
    else:
        header += PYCHECK_HEADER

    header += get_template("header").format(**format_dict)

    if which == "file":
        header += section("Compiled Coconut")

    return header
