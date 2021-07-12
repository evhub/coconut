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
import sys
import traceback
import functools
from warnings import warn

from coconut.constants import (
    use_fast_pyparsing_reprs,
    packrat_cache,
    default_whitespace_chars,
    varchars,
    min_versions,
    pure_python_env_var,
    PURE_PYTHON,
)
from coconut.util import (
    ver_str_to_tuple,
    ver_tuple_to_str,
    get_next_version,
)

# warning: do not name this file cPyparsing or pyparsing or it might collide with the following imports
try:

    if PURE_PYTHON:
        raise ImportError("skipping cPyparsing check due to " + pure_python_env_var + " = " + os.environ.get(pure_python_env_var, ""))

    import cPyparsing as _pyparsing
    from cPyparsing import *  # NOQA
    from cPyparsing import (  # NOQA
        _trim_arity,
        _ParseResultsWithOffset,
        __version__,
    )
    PYPARSING_PACKAGE = "cPyparsing"
    PYPARSING_INFO = "Cython cPyparsing v" + __version__

except ImportError:
    try:

        import pyparsing as _pyparsing
        from pyparsing import *  # NOQA
        from pyparsing import (  # NOQA
            _trim_arity,
            _ParseResultsWithOffset,
            __version__,
        )
        PYPARSING_PACKAGE = "pyparsing"
        PYPARSING_INFO = "Python pyparsing v" + __version__

    except ImportError:
        traceback.print_exc()
        __version__ = None
        PYPARSING_PACKAGE = "cPyparsing"
        PYPARSING_INFO = None

# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------

min_ver = min(min_versions["pyparsing"], min_versions["cPyparsing"][:3])  # inclusive
max_ver = get_next_version(max(min_versions["pyparsing"], min_versions["cPyparsing"][:3]))  # exclusive
cur_ver = None if __version__ is None else ver_str_to_tuple(__version__)

if cur_ver is None or cur_ver < min_ver:
    min_ver_str = ver_tuple_to_str(min_ver)
    raise ImportError(
        "Coconut requires pyparsing/cPyparsing version >= " + min_ver_str
        + ("; got " + PYPARSING_INFO if PYPARSING_INFO is not None else "")
        + " (run '{python} -m pip install --upgrade {package}' to fix)".format(python=sys.executable, package=PYPARSING_PACKAGE),
    )
elif cur_ver >= max_ver:
    max_ver_str = ver_tuple_to_str(max_ver)
    warn(
        "This version of Coconut was built for pyparsing/cPyparsing versions < " + max_ver_str
        + ("; got " + PYPARSING_INFO if PYPARSING_INFO is not None else "")
        + " (run '{python} -m pip install {package}<{max_ver}' to fix)".format(python=sys.executable, package=PYPARSING_PACKAGE, max_ver=max_ver_str),
    )


if PY2:
    def fast_repr(cls):
        """A very simple, fast __repr__/__str__ implementation."""
        return "<" + cls.__name__ + ">"
else:
    fast_repr = object.__repr__


# makes pyparsing much faster if it doesn't have to compute expensive
#  nested string representations
if use_fast_pyparsing_reprs:
    for obj in vars(_pyparsing).values():
        try:
            if issubclass(obj, ParserElement):
                obj.__repr__ = functools.partial(fast_repr, obj)
                obj.__str__ = functools.partial(fast_repr, obj)
        except TypeError:
            pass


if packrat_cache:
    ParserElement.enablePackrat(packrat_cache)

ParserElement.setDefaultWhitespaceChars(default_whitespace_chars)

Keyword.setDefaultKeywordChars(varchars)
