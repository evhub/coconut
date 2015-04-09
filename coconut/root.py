#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
Date Created: 2015
Description: The Coconut Root.
"""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

try:
    from future_builtins import *
except ImportError:
    pass

try:
    import readline
except ImportError:
    pass

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

VERSION = "0.2.0"
VERSION_NAME = "Eocene"

ENCODING = "UTF"

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SETUP:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

try:
    xrange
except NameError:
    pass
else:
    range = xrange
    def xrange(*args, **kwargs):
        raise NameError("name 'xrange' is not defined")

try:
    ascii
except NameError:
    ascii = repr

try:
    unichr
except NameError:
    unichr = chr

try:
    unicode
except NameError:
    pass
else:
    bytes = str
    str = unicode
    def unicode(*args, **kwargs):
        raise NameError("name 'unicode' is not defined")
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
