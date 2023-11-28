#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Wrapper around PyParsing that selects the best available implementation.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os
import re
import sys
import traceback
from warnings import warn
from collections import defaultdict
from itertools import permutations
from functools import wraps
from pprint import pprint

from coconut.constants import (
    PURE_PYTHON,
    use_fast_pyparsing_reprs,
    use_packrat_parser,
    packrat_cache_size,
    default_whitespace_chars,
    varchars,
    min_versions,
    max_versions,
    pure_python_env_var,
    enable_pyparsing_warnings,
    use_left_recursion_if_available,
    get_bool_env_var,
    use_computation_graph_env_var,
    use_incremental_if_available,
    default_incremental_cache_size,
    never_clear_incremental_cache,
    warn_on_multiline_regex,
    num_displayed_timing_items,
    use_cache_file,
)
from coconut.util import get_clock_time  # NOQA
from coconut.util import (
    ver_str_to_tuple,
    ver_tuple_to_str,
    get_next_version,
)

# warning: do not name this file cPyparsing or pyparsing or it might collide with the following imports
try:

    if PURE_PYTHON:
        raise ImportError("skipping cPyparsing check due to " + pure_python_env_var + " = " + os.getenv(pure_python_env_var, ""))

    import cPyparsing as _pyparsing
    from cPyparsing import *  # NOQA
    from cPyparsing import __version__

    CPYPARSING = True
    PYPARSING_INFO = "Cython cPyparsing v" + __version__

except ImportError:
    try:

        import pyparsing as _pyparsing
        from pyparsing import *  # NOQA
        from pyparsing import __version__

        CPYPARSING = False
        PYPARSING_INFO = "Python pyparsing v" + __version__

    except ImportError:
        traceback.print_exc()
        __version__ = None
        CPYPARSING = True
        PYPARSING_INFO = None


# -----------------------------------------------------------------------------------------------------------------------
# VERSIONING:
# -----------------------------------------------------------------------------------------------------------------------

PYPARSING_PACKAGE = "cPyparsing" if CPYPARSING else "pyparsing"

if CPYPARSING:
    min_ver = min_versions["cPyparsing"]  # inclusive
    max_ver = get_next_version(
        min_versions["cPyparsing"],
        point_to_increment=len(max_versions["cPyparsing"]) - 1,
    )  # exclusive
else:
    min_ver = min_versions["pyparsing"]  # inclusive
    max_ver = get_next_version(min_versions["pyparsing"])  # exclusive

cur_ver = None if __version__ is None else ver_str_to_tuple(__version__)

if cur_ver is None or cur_ver < min_ver:
    raise ImportError(
        (
            "This version of Coconut requires {package} version >= {min_ver}"
            + ("; got " + PYPARSING_INFO if PYPARSING_INFO is not None else "")
            + " (run '{python} -m pip install --upgrade {package}' to fix)"
        ).format(
            python=sys.executable,
            package=PYPARSING_PACKAGE,
            min_ver=ver_tuple_to_str(min_ver),
        )
    )
elif cur_ver >= max_ver:
    warn(
        (
            "This version of Coconut was built for {package} versions < {max_ver}"
            + ("; got " + PYPARSING_INFO if PYPARSING_INFO is not None else "")
            + " (run '{python} -m pip install {package}<{max_ver}' to fix)"
        ).format(
            python=sys.executable,
            package=PYPARSING_PACKAGE,
            max_ver=ver_tuple_to_str(max_ver),
        )
    )

MODERN_PYPARSING = cur_ver >= (3,)

if MODERN_PYPARSING:
    warn(
        "This version of Coconut is not built for pyparsing v3; some syntax features WILL NOT WORK (run either '{python} -m pip install cPyparsing<{max_ver}' or '{python} -m pip install pyparsing<{max_ver}' to fix)".format(
            python=sys.executable,
            max_ver=ver_tuple_to_str(max_ver),
        )
    )


# -----------------------------------------------------------------------------------------------------------------------
# OVERRIDES:
# -----------------------------------------------------------------------------------------------------------------------

if MODERN_PYPARSING:
    SUPPORTS_PACKRAT_CONTEXT = False

elif CPYPARSING:
    assert hasattr(ParserElement, "packrat_context"), (
        "This version of Coconut requires cPyparsing>=" + ver_tuple_to_str(min_versions["cPyparsing"])
        + "; got cPyparsing==" + __version__
        + " (run '{python} -m pip install --upgrade cPyparsing' to fix)".format(python=sys.executable),
    )
    SUPPORTS_PACKRAT_CONTEXT = True

else:
    SUPPORTS_PACKRAT_CONTEXT = True
    HIT, MISS = 0, 1

    def _parseCache(self, instring, loc, doActions=True, callPreParse=True):
        # [CPYPARSING] HIT, MISS are constants
        # [CPYPARSING] include packrat_context, merge callPreParse and doActions
        lookup = (self, instring, loc, callPreParse | doActions << 1, ParserElement.packrat_context)
        with ParserElement.packrat_cache_lock:
            cache = ParserElement.packrat_cache
            value = cache.get(lookup)
            if value is cache.not_in_cache:
                ParserElement.packrat_cache_stats[MISS] += 1
                try:
                    value = self._parseNoCache(instring, loc, doActions, callPreParse)
                except ParseBaseException as pe:
                    # cache a copy of the exception, without the traceback
                    cache.set(lookup, pe.__class__(*pe.args))
                    raise
                else:
                    cache.set(lookup, (value[0], value[1].copy()))
                    return value
            else:
                ParserElement.packrat_cache_stats[HIT] += 1
                if isinstance(value, Exception):
                    raise value
                return value[0], value[1].copy()

    ParserElement._parseCache = _parseCache

    # [CPYPARSING] fix append
    def append(self, other):
        if (self.parseAction
                or self.resultsName is not None
                or self.debug):
            return self.__class__([self, other])
        elif (other.__class__ == self.__class__
                and not other.parseAction
                and other.resultsName is None
                and not other.debug):
            self.exprs += other.exprs
            self.strRepr = None
            self.saveAsList |= other.saveAsList
            if isinstance(self, And):
                self.mayReturnEmpty &= other.mayReturnEmpty
            else:
                self.mayReturnEmpty |= other.mayReturnEmpty
            self.mayIndexError |= other.mayIndexError
        else:
            self.exprs.append(other)
            self.strRepr = None
            if isinstance(self, And):
                self.mayReturnEmpty &= other.mayReturnEmpty
            else:
                self.mayReturnEmpty |= other.mayReturnEmpty
            self.mayIndexError |= other.mayIndexError
            self.saveAsList |= other.saveAsList
        return self
    ParseExpression.append = append

if SUPPORTS_PACKRAT_CONTEXT:
    ParserElement.packrat_context = frozenset()

if hasattr(ParserElement, "enableIncremental"):
    SUPPORTS_INCREMENTAL = sys.version_info >= (3, 8)  # avoids stack overflows on py<=37
else:
    SUPPORTS_INCREMENTAL = False
    ParserElement._incrementalEnabled = False
    ParserElement._incrementalWithResets = False

    def enableIncremental(*args, **kwargs):
        """Dummy version of enableIncremental that just raises an error."""
        raise ImportError(
            "incremental parsing only supported on cPyparsing>="
            + ver_tuple_to_str(min_versions["cPyparsing"])
            + " (run '{python} -m pip install --upgrade cPyparsing' to fix)".format(python=sys.executable)
        )


# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------

USE_COMPUTATION_GRAPH = get_bool_env_var(
    use_computation_graph_env_var,
    default=(
        not MODERN_PYPARSING  # not yet supported
        # commented out to minimize memory footprint when running tests:
        # and not PYPY  # experimentally determined
    ),
)

SUPPORTS_ADAPTIVE = (
    hasattr(MatchFirst, "setAdaptiveMode")
    and USE_COMPUTATION_GRAPH
)

USE_CACHE = SUPPORTS_INCREMENTAL and use_cache_file

if MODERN_PYPARSING:
    _trim_arity = _pyparsing.core._trim_arity
    _ParseResultsWithOffset = _pyparsing.core._ParseResultsWithOffset
else:
    _trim_arity = _pyparsing._trim_arity
    _ParseResultsWithOffset = _pyparsing._ParseResultsWithOffset

maybe_make_safe = getattr(_pyparsing, "maybe_make_safe", None)

if enable_pyparsing_warnings:
    if MODERN_PYPARSING:
        _pyparsing.enable_all_warnings()
    else:
        _pyparsing._enable_all_warnings()
    _pyparsing.__diag__.warn_name_set_on_empty_Forward = False
    _pyparsing.__diag__.warn_on_incremental_multiline_regex = warn_on_multiline_regex

if MODERN_PYPARSING and use_left_recursion_if_available:
    ParserElement.enable_left_recursion()
elif SUPPORTS_INCREMENTAL and use_incremental_if_available:
    ParserElement.enableIncremental(default_incremental_cache_size, still_reset_cache=not never_clear_incremental_cache)
elif use_packrat_parser:
    ParserElement.enablePackrat(packrat_cache_size)

ParserElement.setDefaultWhitespaceChars(default_whitespace_chars)

Keyword.setDefaultKeywordChars(varchars)

if SUPPORTS_INCREMENTAL:
    all_parse_elements = ParserElement.collectParseElements()
else:
    all_parse_elements = None


# -----------------------------------------------------------------------------------------------------------------------
# MISSING OBJECTS:
# -----------------------------------------------------------------------------------------------------------------------

python_quoted_string = getattr(_pyparsing, "python_quoted_string", None)
if python_quoted_string is None:
    python_quoted_string = _pyparsing.Combine(
        # multiline strings must come first
        (_pyparsing.Regex(r'"""(?:[^"\\]|""(?!")|"(?!"")|\\.)*', flags=re.MULTILINE) + '"""').setName("multiline double quoted string")
        | (_pyparsing.Regex(r"'''(?:[^'\\]|''(?!')|'(?!'')|\\.)*", flags=re.MULTILINE) + "'''").setName("multiline single quoted string")
        | (_pyparsing.Regex(r'"(?:[^"\n\r\\]|(?:\\")|(?:\\(?:[^x]|x[0-9a-fA-F]+)))*') + '"').setName("double quoted string")
        | (_pyparsing.Regex(r"'(?:[^'\n\r\\]|(?:\\')|(?:\\(?:[^x]|x[0-9a-fA-F]+)))*") + "'").setName("single quoted string")
    ).setName("Python quoted string")
    _pyparsing.python_quoted_string = python_quoted_string


# -----------------------------------------------------------------------------------------------------------------------
# FAST REPRS:
# -----------------------------------------------------------------------------------------------------------------------

if DEVELOP:
    def fast_repr(self):
        """A very simple, fast __repr__/__str__ implementation."""
        return getattr(self, "name", self.__class__.__name__)
elif PY2:
    def fast_repr(self):
        """A very simple, fast __repr__/__str__ implementation."""
        return "<" + self.__class__.__name__ + ">"
else:
    fast_repr = object.__repr__


_old_pyparsing_reprs = []


def set_fast_pyparsing_reprs():
    """Make pyparsing much faster by preventing it from computing expensive nested string representations."""
    for obj in vars(_pyparsing).values():
        try:
            if issubclass(obj, ParserElement):
                _old_pyparsing_reprs.append((obj, (obj.__repr__, obj.__str__)))
                obj.__repr__ = fast_repr
                obj.__str__ = fast_repr
        except TypeError:
            pass


def unset_fast_pyparsing_reprs():
    """Restore pyparsing's default string representations for ease of debugging."""
    for obj, (repr_method, str_method) in _old_pyparsing_reprs:
        obj.__repr__ = repr_method
        obj.__str__ = str_method
    _old_pyparsing_reprs[:] = []


if use_fast_pyparsing_reprs:
    set_fast_pyparsing_reprs()


# -----------------------------------------------------------------------------------------------------------------------
# PROFILING:
# -----------------------------------------------------------------------------------------------------------------------

_timing_info = [None]  # in list to allow reassignment


class _timing_sentinel(object):
    __slots__ = ()


def add_timing_to_method(cls, method_name, method):
    """Add timing collection to the given method.
    It's a monstrosity, but it's only used for profiling."""
    @wraps(method)
    def new_method(self, *args, **kwargs):
        start_time = get_clock_time()
        try:
            return method(self, *args, **kwargs)
        finally:
            _timing_info[0][ascii(self)] += get_clock_time() - start_time
    new_method._timed = True
    setattr(cls, method_name, new_method)
    return True


def collect_timing_info():
    """Modifies pyparsing elements to time how long they're executed for.
    It's a monstrosity, but it's only used for profiling."""
    from coconut.terminal import logger  # hide to avoid circular imports
    logger.log("adding timing to pyparsing elements:")
    _timing_info[0] = defaultdict(float)
    for obj in vars(_pyparsing).values():
        if isinstance(obj, type) and issubclass(obj, ParserElement):
            added_timing = False
            for attr_name in dir(obj):
                attr = getattr(obj, attr_name)
                if (
                    callable(attr)
                    and not isinstance(attr, ParserElement)
                    and not getattr(attr, "_timed", False)
                    and attr_name not in (
                        "__getattribute__",
                        "__setattribute__",
                        "__init_subclass__",
                        "__subclasshook__",
                        "__class__",
                        "__setattr__",
                        "__getattr__",
                        "__new__",
                        "__init__",
                        "__str__",
                        "__repr__",
                        "__hash__",
                        "__eq__",
                        "_trim_traceback",
                        "_ErrorStop",
                        "_UnboundedCache",
                        "enablePackrat",
                        "enableIncremental",
                        "inlineLiteralsUsing",
                        "setDefaultWhitespaceChars",
                        "setDefaultKeywordChars",
                        "resetCache",
                    )
                ):
                    added_timing |= add_timing_to_method(obj, attr_name, attr)
            if added_timing:
                logger.log("\tadded timing to", obj)
    return _timing_info


def print_timing_info():
    """Print timing_info collected by collect_timing_info()."""
    print(
        """
=====================================
Timing info:
(timed {num} total pyparsing objects)
=====================================
        """.rstrip().format(
            num=len(_timing_info[0]),
        ),
    )
    sorted_timing_info = sorted(_timing_info[0].items(), key=lambda kv: kv[1])[-num_displayed_timing_items:]
    for method_name, total_time in sorted_timing_info:
        print("{method_name}:\t{total_time}".format(method_name=method_name, total_time=total_time))


_profiled_MatchFirst_objs = {}


def add_profiling_to_MatchFirsts():
    """Add profiling to MatchFirst objects to look for possible reorderings."""

    @wraps(MatchFirst.parseImpl)
    def new_parseImpl(self, instring, loc, doActions=True):
        if id(self) not in _profiled_MatchFirst_objs:
            _profiled_MatchFirst_objs[id(self)] = self
            self.expr_usage_stats = []
            self.expr_timing_stats = []
        while len(self.expr_usage_stats) < len(self.exprs):
            self.expr_usage_stats.append(0)
            self.expr_timing_stats.append([])
        maxExcLoc = -1
        maxException = None
        for i, e in enumerate(self.exprs):
            try:
                start_time = get_clock_time()
                try:
                    ret = e._parse(instring, loc, doActions)
                finally:
                    self.expr_timing_stats[i].append(get_clock_time() - start_time)
                self.expr_usage_stats[i] += 1
                return ret
            except _pyparsing.ParseException as err:
                if err.loc > maxExcLoc:
                    maxException = err
                    maxExcLoc = err.loc
            except IndexError:
                if len(instring) > maxExcLoc:
                    maxException = _pyparsing.ParseException(instring, len(instring), e.errmsg, self)
                    maxExcLoc = len(instring)
        else:
            if maxException is not None:
                maxException.msg = self.errmsg
                raise maxException
            else:
                raise _pyparsing.ParseException(instring, loc, "no defined alternatives to match", self)

    _pyparsing.MatchFirst.parseImpl = new_parseImpl
    return _profiled_MatchFirst_objs


def time_for_ordering(expr_usage_stats, expr_timing_aves):
    """Get the total time for a given MatchFirst ordering."""
    total_time = 0
    for i, n in enumerate(expr_usage_stats):
        total_time += n * sum(expr_timing_aves[:i + 1])
    return total_time


def find_best_ordering(obj, num_perms_to_eval=None):
    """Get the best ordering of the MatchFirst."""
    if num_perms_to_eval is None:
        num_perms_to_eval = True if len(obj.exprs) <= 10 else 100000
    best_ordering = None
    best_time = float("inf")
    stats_zip = tuple(zip(obj.expr_usage_stats, obj.expr_timing_aves, obj.exprs))
    if num_perms_to_eval is True:
        perms_to_eval = permutations(stats_zip)
    else:
        perms_to_eval = [
            stats_zip,
            sorted(stats_zip, key=lambda u_t_e: (-u_t_e[0], u_t_e[1])),
            sorted(stats_zip, key=lambda u_t_e: (u_t_e[1], -u_t_e[0])),
        ]
        if num_perms_to_eval:
            max_usage = max(obj.expr_usage_stats)
            max_time = max(obj.expr_timing_aves)
            for i in range(1, num_perms_to_eval):
                a = i / num_perms_to_eval
                perms_to_eval.append(sorted(
                    stats_zip,
                    key=lambda u_t_e:
                        -a * u_t_e[0] / max_usage
                        + (1 - a) * u_t_e[1] / max_time,
                ))
    for perm in perms_to_eval:
        perm_expr_usage_stats, perm_expr_timing_aves = zip(*[(usage, timing) for usage, timing, expr in perm])
        perm_time = time_for_ordering(perm_expr_usage_stats, perm_expr_timing_aves)
        if perm_time < best_time:
            best_time = perm_time
            best_ordering = [(obj.exprs.index(expr), parse_expr_repr(expr)) for usage, timing, expr in perm]
    return best_ordering, best_time


def naive_timing_improvement(obj):
    """Get the expected timing improvement for a better MatchFirst ordering."""
    _, best_time = find_best_ordering(obj, num_perms_to_eval=False)
    return time_for_ordering(obj.expr_usage_stats, obj.expr_timing_aves) - best_time


def parse_expr_repr(obj):
    """Get a clean repr of a parse expression for displaying."""
    return ascii(getattr(obj, "name", None) or obj)


def print_poorly_ordered_MatchFirsts():
    """Print poorly ordered MatchFirsts."""
    for obj in _profiled_MatchFirst_objs.values():
        obj.expr_timing_aves = [sum(ts) / len(ts) if ts else 0 for ts in obj.expr_timing_stats]
        obj.naive_timing_improvement = naive_timing_improvement(obj)
    most_improveable = sorted(_profiled_MatchFirst_objs.values(), key=lambda obj: obj.naive_timing_improvement)[-num_displayed_timing_items:]
    for obj in most_improveable:
        print("\n" + parse_expr_repr(obj) + " (" + str(obj.naive_timing_improvement) + "):")
        pprint(list(zip(map(parse_expr_repr, obj.exprs), obj.expr_usage_stats, obj.expr_timing_aves)))
        best_ordering, best_time = find_best_ordering(obj)
        print("\tbest (" + str(best_time) + "):")
        pprint(best_ordering)


def start_profiling():
    """Do all the setup to begin profiling."""
    add_profiling_to_MatchFirsts()
    collect_timing_info()


def print_profiling_results():
    """Print all profiling results."""
    print_timing_info()
    print_poorly_ordered_MatchFirsts()
