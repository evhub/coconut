#!/usr/bin/python

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
    from future_builtins import map, filter
except ImportError:
    pass

try:
    import readline
except ImportError:
    pass

import codecs
import os.path

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SETUP:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

try:
    xrange
except NameError:
    xrange = range
else:
    range = xrange

try:
    long
except NameError:
    long = int

try:
    ascii
except NameError:
    ascii = repr

try:
    unichr
except NameError:
    unichr = chr

encoding = "UTF"

old_print = print
def_str = str
try:
    unicode
except NameError:
    old_str = bytes
    unicode = str
else:
    old_str = str
    str = unicode
    def print(*args):
        return old_print(*(str(x).encode(encoding) for x in args))

try:
    raw_input
except NameError:
    raw_input = input
    def old_input(*args, **kwargs):
        return eval(raw_input(*args, **kwargs))
else:
    old_input = raw_input
    def raw_input(*args, **kwargs):
        return old_input(*args, **kwargs).decode(encoding)
    input = raw_input
