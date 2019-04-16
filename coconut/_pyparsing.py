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

import traceback
import functools

from coconut.constants import (
    packrat_cache,
    default_whitespace_chars,
    varchars,
    min_versions,
    ver_str_to_tuple,
    ver_tuple_to_str,
    get_next_version,
)

# warning: do not name this file cPyparsing or pyparsing or it might collide with the following imports
try:

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
        PYPARSING_PACKAGE = "pyparsing"
        PYPARSING_INFO = None

# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------

min_ver = min(min_versions["pyparsing"], min_versions["cPyparsing"][:3])
max_ver = get_next_version(max(min_versions["pyparsing"], min_versions["cPyparsing"][:3]))

if __version__ is None or not min_ver <= ver_str_to_tuple(__version__) < max_ver:
    min_ver_str = ver_tuple_to_str(min_ver)
    max_ver_str = ver_tuple_to_str(max_ver)
    raise ImportError(
        "Coconut requires pyparsing/cPyparsing version >= " + min_ver_str + " and < " + max_ver_str
        + ("; got " + PYPARSING_INFO if PYPARSING_INFO is not None else "")
        + " (run 'pip install --upgrade " + PYPARSING_PACKAGE + "' to fix)",
    )


def fast_str(cls):
    """A very simple __str__ implementation."""
    return "<" + cls.__name__ + ">"


def fast_repr(cls):
    """A very simple __repr__ implementation."""
    return "<" + cls.__name__ + ">"


# makes pyparsing much faster if it doesn't have to compute expensive
#  nested string representations
for obj in vars(_pyparsing).values():
    try:
        if issubclass(obj, ParserElement):
            obj.__str__ = functools.partial(fast_str, obj)
            obj.__repr__ = functools.partial(fast_repr, obj)
    except TypeError:
        pass

if packrat_cache:
    ParserElement.enablePackrat(packrat_cache)

ParserElement.setDefaultWhitespaceChars(default_whitespace_chars)

Keyword.setDefaultKeywordChars(varchars)
