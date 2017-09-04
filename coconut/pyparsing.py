#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Wrapper around PyParsing that selects the best available implementation.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from coconut.requirements import (
    ver_str_to_tuple,
    ver_tuple_to_str,
)
from coconut.constants import (
    use_packrat,
    packrat_cache_size,
    default_whitespace_chars,
    varchars,
    min_versions,
)

try:
    from cPyparsing import *  # NOQA
    from cPyparsing import __version__
    if DEVELOP:
        from cPyparsing import _trim_arity  # NOQA
    PYPARSING = "Cython cPyparsing v" + __version__

except ImportError:
    from pyparsing import *  # NOQA
    from pyparsing import __version__
    if DEVELOP:
        from pyparsing import _trim_arity  # NOQA
    PYPARSING = "Python pyparsing v" + __version__

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if ver_str_to_tuple(__version__) < min_versions["pyparsing"]:
    req_ver_str = ver_tuple_to_str(min_versions["pyparsing"])
    raise ImportError(
        "Coconut requires pyparsing version >= " + req_ver_str
        + "; got version " + __version__
        + " (run 'pip install --upgrade pyparsing' or"
        + " 'pip install --upgrade cPyparsing' to fix)",
    )

if use_packrat:
    ParserElement.enablePackrat(packrat_cache_size)

ParserElement.setDefaultWhitespaceChars(default_whitespace_chars)

Keyword.setDefaultKeywordChars(varchars)
