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
    import readline
except ImportError:
    pass

import sys

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

VERSION = "0.3.4"
VERSION_NAME = "Macapuno"
DEVELOP = True

ENCODING = "UTF-8"

if DEVELOP:
    VERSION += "-post_dev"
VERSION_STR = VERSION + " [" + VERSION_NAME + "]"

PY2 = sys.version_info < (3,)

PY2_HEADER = r'''py2_filter, py2_hex, py2_map, py2_oct, py2_zip = filter, hex, map, oct, zip
from future_builtins import *
py2_open = open
from io import open
py2_range, range = range, xrange
py2_int = int
_coconut_int, _coconut_long = py2_int, long
class _coconut_metaint(type):
    def __instancecheck__(cls, inst):
        return isinstance(inst, (_coconut_int, _coconut_long))
class int(_coconut_int):
    """Python 3 int."""
    __metaclass__ = _coconut_metaint
py2_chr, chr = chr, unichr
py2_str = str
_coconut_str, _coconut_unicode = py2_str, unicode
_coconut_new_int = int
bytes = _coconut_str
def _coconut_bytes_init(self, *args, **kwargs):
    """Python 3 bytes constructor."""
    if len(args) == 1 and isinstance(args[0], _coconut_new_int):
        _coconut_str.__init__(self, b"\x00" * args[0], **kwargs)
    else:
        _coconut_str.__init__(self, *args, **kwargs)
bytes.__init__ = _coconut_bytes_init
str = _coconut_unicode
def _coconut_str_init(self, *args, **kwargs):
    """Python 3 str constructor."""
    if len(args) == 1 and isinstance(args[0], _coconut_str):
        return _coconut_unicode.__init__(self, repr(args[0]), **kwargs)
    else:
        return _coconut_unicode.__init__(self, *args, **kwargs)
str.__init__ = _coconut_str_init
_coconut_encoding = "'''+ENCODING+r'''"
py2_print = print
_coconut_print = py2_print
_coconut_new_str = str
def print(*args, **kwargs):
    """Python 3 print."""
    return _coconut_print(*(_coconut_new_str(x) for x in args), **kwargs)
py2_input = input
_coconut_raw_input = raw_input
def input(*args, **kwargs):
    """Python 3 input."""
    return _coconut_raw_input(*args, **kwargs).decode(_coconut_encoding)'''

#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if PY2:
    exec(PY2_HEADER)
