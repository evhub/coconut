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

from coconut.root import _indent
from coconut.constants import (
    get_target_info,
    hash_prefix,
    tabideal,
    default_encoding,
    template_ext,
    justify_len,
)
from coconut.exceptions import internal_assert

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


def minify(compiled):
    """Perform basic minifications.

    Fails on non-tabideal indentation or a string with a #.
    """
    compiled = compiled.strip()
    if compiled:
        out = []
        for line in compiled.splitlines():
            line = line.split("#", 1)[0].rstrip()
            if line:
                ind = 0
                while line.startswith(" "):
                    line = line[1:]
                    ind += 1
                internal_assert(ind % tabideal == 0, "invalid indentation in", line)
                out.append(" " * (ind // tabideal) + line)
        compiled = "\n".join(out) + "\n"
    return compiled


template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def get_template(template):
    """Read the given template file."""
    with open(os.path.join(template_dir, template) + template_ext, "r") as template_file:
        return template_file.read()


def one_num_ver(target):
    """Return the first number of the target version, if it has one."""
    return target[:1]  # "2", "3", or ""


def section(name):
    """Generate a section break."""
    line = "# " + name + ": "
    return line + "-" * (justify_len - len(line)) + "\n\n"


# -----------------------------------------------------------------------------------------------------------------------
# FORMAT DICTIONARY:
# -----------------------------------------------------------------------------------------------------------------------


class comment(object):
    """When passed to str.format, allows {comment.<>} to serve as a comment."""

    def __getattr__(self, attr):
        """Return an empty string for all comment attributes."""
        return ""


def process_header_args(which, target, use_hash, no_tco, strict):
    """Create the dictionary passed to str.format in the header, target_startswith, and target_info."""
    target_startswith = one_num_ver(target)
    target_info = get_target_info(target)

    try_backport_lru_cache = r'''try:
    from backports.functools_lru_cache import lru_cache
    functools.lru_cache = lru_cache
except ImportError: pass
'''
    try_import_trollius = r'''try:
    import trollius as asyncio
except ImportError:
    class you_need_to_install_trollius: pass
    asyncio = you_need_to_install_trollius()
'''

    format_dict = dict(
        comment=comment(),
        empty_dict="{}",
        target_startswith=target_startswith,
        default_encoding=default_encoding,
        hash_line=hash_prefix + use_hash + "\n" if use_hash is not None else "",
        typing_line="# type: ignore\n" if which == "__coconut__" else "",
        VERSION_STR=VERSION_STR,
        module_docstring='"""Built-in Coconut utilities."""\n\n' if which == "__coconut__" else "",
        object="(object)" if target_startswith != "3" else "",
        import_asyncio=_indent(
            "" if not target or target_info >= (3, 5)
            else "import asyncio\n" if target_info >= (3, 4)
            else r'''if _coconut_sys.version_info >= (3, 4):
    import asyncio
else:
''' + _indent(try_import_trollius) if target_info >= (3,)
            else try_import_trollius,
        ),
        import_pickle=_indent(
            r'''if _coconut_sys.version_info < (3,):
    import cPickle as pickle
else:
    import pickle''' if not target
            else "import cPickle as pickle" if target_info < (3,)
            else "import pickle"
        ),
        import_OrderedDict=_indent(
            r'''if _coconut_sys.version_info >= (2, 7):
    OrderedDict = collections.OrderedDict
else:
    OrderedDict = dict'''
            if not target
            else "OrderedDict = collections.OrderedDict" if target_info >= (2, 7)
            else "OrderedDict = dict"
        ),
        import_collections_abc=_indent(
            r'''if _coconut_sys.version_info < (3, 3):
    abc = collections
else:
    import collections.abc as abc'''
            if target_startswith != "2"
            else "abc = collections"
        ),
        bind_lru_cache=_indent(
            r'''if _coconut_sys.version_info < (3, 2):
''' + _indent(try_backport_lru_cache)
            if not target
            else try_backport_lru_cache if target_startswith == "2"
            else ""
        ),
        comma_bytearray=", bytearray" if target_startswith != "3" else "",
        static_repr="staticmethod(repr)" if target_startswith != "3" else "repr",
        with_ThreadPoolExecutor=(
            r'''from multiprocessing import cpu_count  # cpu_count() * 5 is the default Python 3.5 thread count
        with ThreadPoolExecutor(cpu_count() * 5)''' if target_info < (3, 5)
            else '''with ThreadPoolExecutor()'''
        ),
        tco_decorator="@_coconut_tco\n" + " " * 8 if not no_tco else "",
        tail_call_func_args_kwargs="func(*args, **kwargs)" if no_tco else "_coconut_tail_call(func, *args, **kwargs)",
        comma_tco=", _coconut_tail_call, _coconut_tco" if not no_tco else "",
        def_prepattern=(
            r'''def prepattern(base_func):
    """DEPRECATED: Use addpattern instead."""
    def pattern_prepender(func):
        return addpattern(func)(base_func)
    return pattern_prepender
''' if not strict else ""
        ),
        def_datamaker=(
            r'''def datamaker(data_type):
    """DEPRECATED: Use makedata instead."""
    return _coconut.functools.partial(makedata, data_type)
''' if not strict else ""
        ),
    )

    format_dict["import_typing_NamedTuple"] = _indent(
        "import typing" if target_info >= (3, 6)
        else '''class typing{object}:
    @staticmethod
    def NamedTuple(name, fields):
        return _coconut.collections.namedtuple(name, [x for x, t in fields])'''.format(**format_dict),
    )

    format_dict["underscore_imports"] = "_coconut, _coconut_MatchError{comma_tco}, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_back_pipe, _coconut_star_pipe, _coconut_back_star_pipe, _coconut_dubstar_pipe, _coconut_back_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_get_function_match_error, _coconut_addpattern, _coconut_sentinel, _coconut_assert".format(**format_dict)

    # ._coconut_tco_func is used in main.coco, so don't remove it
    #  here without replacing its usage there
    format_dict["def_tco"] = "" if no_tco else '''class _coconut_tail_call{object}:
    __slots__ = ("func", "args", "kwargs")
    def __init__(self, func, *args, **kwargs):
        self.func, self.args, self.kwargs = func, args, kwargs
_coconut_tco_func_dict = {empty_dict}
def _coconut_tco(func):
    @_coconut.functools.wraps(func)
    def tail_call_optimized_func(*args, **kwargs):
        call_func = func
        while True:
            wkref = _coconut_tco_func_dict.get(_coconut.id(call_func))
            if wkref is not None and wkref() is call_func:
                call_func = call_func._coconut_tco_func
            result = call_func(*args, **kwargs)  # pass --no-tco to clean up your traceback
            if not isinstance(result, _coconut_tail_call):
                return result
            call_func, args, kwargs = result.func, result.args, result.kwargs
    tail_call_optimized_func._coconut_tco_func = func
    _coconut_tco_func_dict[_coconut.id(tail_call_optimized_func)] = _coconut.weakref.ref(tail_call_optimized_func)
    return tail_call_optimized_func
'''.format(**format_dict)

    return format_dict, target_startswith, target_info


# -----------------------------------------------------------------------------------------------------------------------
# HEADER GENERATION:
# -----------------------------------------------------------------------------------------------------------------------


def getheader(which, target="", use_hash=None, no_tco=False, strict=False):
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

    # initial, __coconut__, package, sys, code, file

    format_dict, target_startswith, target_info = process_header_args(which, target, use_hash, no_tco, strict)

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

    # __coconut__, package, sys, code, file

    header += section("Coconut Header")

    if target_startswith != "3":
        header += "from __future__ import print_function, absolute_import, unicode_literals, division\n"
    elif target_info >= (3, 7):
        header += "from __future__ import generator_stop, annotations\n"
    elif target_info >= (3, 5):
        header += "from __future__ import generator_stop\n"

    if which.startswith("package"):
        levels_up = int(which[len("package:"):])
        coconut_file_path = "_coconut_os_path.dirname(_coconut_os_path.abspath(__file__))"
        for _ in range(levels_up):
            coconut_file_path = "_coconut_os_path.dirname(" + coconut_file_path + ")"
        return header + '''import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = {coconut_file_path}
_coconut_cached_module = _coconut_sys.modules.get({__coconut__})
if _coconut_cached_module is not None and _coconut_os_path.dirname(_coconut_cached_module.__file__) != _coconut_file_path:
    del _coconut_sys.modules[{__coconut__}]
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import {underscore_imports}
from __coconut__ import *
{sys_path_pop}

'''.format(
            coconut_file_path=coconut_file_path,
            __coconut__=(
                '"__coconut__"' if target_startswith == "3"
                else 'b"__coconut__"' if target_startswith == "2"
                else 'str("__coconut__")'
            ),
            sys_path_pop=(
                # we can't pop on Python 2 if we want __coconut__ objects to be pickleable
                "_coconut_sys.path.pop(0)" if target_startswith == "3"
                else "" if target_startswith == "2"
                else '''if _coconut_sys.version_info >= (3,):
    _coconut_sys.path.pop(0)'''
            ),
            **format_dict
        ) + section("Compiled Coconut")

    if which == "sys":
        return header + '''import sys as _coconut_sys
from coconut.__coconut__ import {underscore_imports}
from coconut.__coconut__ import *
'''.format(**format_dict)

    # __coconut__, code, file

    header += "import sys as _coconut_sys\n"

    if target_startswith == "3":
        header += PY3_HEADER
    elif target_info >= (2, 7):
        header += PY27_HEADER
    elif target_startswith == "2":
        header += PY2_HEADER
    else:
        header += PYCHECK_HEADER

    header += get_template("header").format(**format_dict)

    if which == "file":
        header += "\n" + section("Compiled Coconut")

    return header
