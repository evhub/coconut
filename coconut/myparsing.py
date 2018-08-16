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

from coconut.constants import (
    packrat_cache,
    default_whitespace_chars,
    varchars,
    min_versions,
    ver_str_to_tuple,
    ver_tuple_to_str,
)

# warning: do not name this file cPyparsing or pyparsing or it might collide with the following imports
try:
    from cPyparsing import *  # NOQA
    from cPyparsing import (  # NOQA
        _trim_arity,
        _ParseResultsWithOffset,
        __version__,
    )
    PYPARSING = "Cython cPyparsing v" + __version__

except ImportError:
    try:

        from pyparsing import *  # NOQA
        from pyparsing import (  # NOQA
            _trim_arity,
            _ParseResultsWithOffset,
            __version__,
        )
        PYPARSING = "Python pyparsing v" + __version__

    except ImportError:
        traceback.print_exc()
        __version__ = None

# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------

if __version__ is None or ver_str_to_tuple(__version__) < min_versions["pyparsing"]:
    req_ver_str = ver_tuple_to_str(min_versions["pyparsing"])
    raise ImportError(
        "Coconut requires pyparsing version >= " + req_ver_str
        + ("; got version " + __version__ if __version__ is not None else "")
        + " (run 'pip install --upgrade pyparsing' or"
        + " 'pip install --upgrade cPyparsing' to fix)",
    )

if packrat_cache:
    ParserElement.enablePackrat(packrat_cache)

ParserElement.setDefaultWhitespaceChars(default_whitespace_chars)

Keyword.setDefaultKeywordChars(varchars)
