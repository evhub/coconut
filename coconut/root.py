#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: The Coconut root.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

try:
    from future_builtins import *
except ImportError:
    pass

try:
    import readline
except ImportError:
    pass

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

VERSION = "0.3.1"
VERSION_NAME = "Jawz"

VERSION_STR = VERSION + " [" + VERSION_NAME + "]"

ENCODING = "UTF-8"

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

try:
    xrange
except NameError:
    pass
else:
    range = xrange

try:
    ascii
except NameError:
    ascii = repr

try:
    unichr
except NameError:
    pass
else:
    chr = unichr

try:
    unicode
except NameError:
    pass
else:
    bytes, str = str, unicode
    __print = print
    def print(*args, **kwargs):
        return __print(*(str(x).encode(ENCODING) for x in args), **kwargs)

try:
    raw_input
except NameError:
    pass
else:
    __input = raw_input
    def input(*args, **kwargs):
        return __input(*args, **kwargs).decode(ENCODING)
