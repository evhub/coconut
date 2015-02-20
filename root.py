#!/usr/bin/python

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
Date Created: 2015
Description: The Rabbit/Coconut Root.
"""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

try:
    from future_builtins import map, filter
except ImportError:
    pass

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

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def openfile(filename, opentype="r+b"):
    """Returns An Open File Object."""
    return codecs.open(str(filename), str(opentype), encoding=encoding)

def writefile(openedfile, writer):
    """Sets The Contents Of A File."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(writer)

def readfile(openedfile):
    """Reads The Contents Of A File."""
    openedfile.seek(0)
    return openedfile.read()
