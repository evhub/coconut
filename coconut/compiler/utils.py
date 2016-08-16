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


from pyparsing import replaceWith

from coconut.const import ups,downs
from .exceptions import printerr

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

class Tracer(object):
    """Debug tracer."""

    def __init__(self, show=printerr, on=False):
        """Creates the tracer."""
        self.show = show
        self.debug(on)

    def debug(self, on=True):
        """Changes the tracer's state."""
        self.on = on

    def show_trace(self, tag, original, location, tokens):
        """Formats and displays a trace."""
        original = str(original)
        location = int(location)
        out = "[" + tag + "] "
        if len(tokens) == 1 and isinstance(tokens[0], str):
            out += ascii(tokens[0])
        else:
            out += str(tokens)
        out += " (line "+str(lineno(location, original))+", col "+str(col(location, original))+")"
        self.show(out)

    def trace(self, item, tag):
        """Traces a parse element."""
        def callback(original, location, tokens):
            """Callback function constructed by tracer."""
            if self.on:
                self.show_trace(tag, original, location, tokens)
            return tokens
        bound = attach(item, callback)
        bound.setName(tag)
        return bound