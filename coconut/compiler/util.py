#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Utilites for use in the compiler.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

from pyparsing import (
    replaceWith,
    lineno,
    col,
    ZeroOrMore,
    Optional,
)

from coconut.constants import ups, downs
from coconut.exceptions import CoconutException

#-----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS:
#-----------------------------------------------------------------------------------------------------------------------

def target_info(target):
    """Returns target information as a version tuple."""
    return tuple(int(x) for x in target)

def addskip(skips, skip):
    """Adds a line skip to the skips."""
    if skip < 1:
        raise CoconutException("invalid skip of line " + str(skip))
    elif skip in skips:
        raise CoconutException("duplicate skip of line " + str(skip))
    else:
        skips.add(skip)
        return skips

def count_end(teststr, testchar):
    """Counts instances of testchar at end of teststr."""
    count = 0
    x = len(teststr) - 1
    while x >= 0 and teststr[x] == testchar:
        count += 1
        x -= 1
    return count

def change(inputstring):
    """Determines the parenthetical change of level."""
    count = 0
    for c in inputstring:
        if c in downs:
            count -= 1
        elif c in ups:
            count += 1
    return count

def attach(item, action, copy=False):
    """Attaches a parse action to an item."""
    if copy:
        item = item.copy()
    return item.addParseAction(action)

def fixto(item, output, copy=False):
    """Forces an item to result in a specific output."""
    return attach(item, replaceWith(output), copy)

def addspace(item, copy=False):
    """Condenses and adds space to the tokenized output."""
    return attach(item, " ".join, copy)

def condense(item, copy=False):
    """Condenses the tokenized output."""
    return attach(item, "".join, copy)

def parenwrap(lparen, item, rparen, tokens=False):
    """Wraps an item in optional parentheses."""
    wrap = lparen.suppress() + item + rparen.suppress() | item
    if not tokens:
        wrap = condense(wrap)
    return wrap

def tokenlist(item, sep, suppress=True):
    """Creates a list of tokens matching the item."""
    if suppress:
        sep = sep.suppress()
    return item + ZeroOrMore(sep + item) + Optional(sep)

def itemlist(item, sep):
    """Creates a list of an item."""
    return condense(item + ZeroOrMore(addspace(sep + item)) + Optional(sep))
