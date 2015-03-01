#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
Date Created: 2015
Description: Coconut Utilities.
"""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from .root import *
import codecs
import sys
import traceback

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def print_error():
    """Processes An Error."""
    err_type, err_value, err_trace = sys.exc_info()
    traceback.print_exception(err_type, err_value, err_trace)

def openfile(filename, opentype="r+b"):
    """Returns An Open File Object."""
    return codecs.open(str(filename), str(opentype), encoding=ENCODING)

def writefile(openedfile, writer):
    """Sets The Contents Of A File."""
    openedfile.seek(0)
    openedfile.truncate()
    openedfile.write(writer)

def readfile(openedfile):
    """Reads The Contents Of A File."""
    openedfile.seek(0)
    return str(openedfile.read())

class terminal(object):
    """Wraps Base Terminal Commands To Create A Fake Console."""
    colors = {
        "end" : "\033[0m",
        "bold" : "\033[1m",
        "blink" : "\033[5m",
        "black" : "\033[30m",
        "red" : "\033[31m",
        "green" : "\033[32m",
        "yellow" : "\033[33m",
        "blue" : "\033[34m",
        "magenta" : "\033[35m",
        "cyan" : "\033[36m",
        "white" : "\033[37m",
        "blackhighlight" : "\033[40m",
        "redhighlight" : "\033[41m",
        "greenhighlight" : "\033[42m",
        "yellowhighlight" : "\033[43m",
        "bluehighlight" : "\033[44m",
        "magentahighlight" : "\033[45m",
        "cyanhighlight" : "\033[46m",
        "whitehighlight" : "\033[47m",
        "pink" : "\033[95m",
        "purple" : "\033[94m",
        "lightgreen" : "\033[92m",
        "lightyellow" : "\033[93m",
        "lightred" : "\033[91m"
        }
    on = True

    def __init__(self, main_color=None, debug_color=None, main_sig="", debug_sig=None):
        """Creates The Terminal Wrapper."""
        self.main_color = main_color
        self.debug_color = debug_color
        self.main_sig = main_sig
        if debug_sig is None:
            self.debug_sig = self.main_sig
        else:
            self.debug_sig = debug_sig
    def addcolor(self, inputstring, color):
        """Adds The Specified Colors To The String."""
        if color is not None:
            return self.colors[str(color)] + inputstring + self.colors["end"]
        else:
            return inputstring
    def delcolor(self, inputstring):
        """Removes Recognized Colors From A String."""
        inputstring = str(inputstring)
        for x in self.colors:
            inputstring = inputstring.replace(x, "")
        return inputstring
    def display(self, *messages, color=None, sig=""):
        """Prints Messages."""
        if self.on:
            message = " ".join(str(msg) for msg in messages)
            for line in message.splitlines():
                print(self.addcolor(sig+line, color))
    def print(self, *messages):
        """Prints Messages With Main Color."""
        self.display(*messages, color=self.main_color, sig=self.main_sig)
    def debug(self, *messages):
        """Prints Messages With Debug Color."""
        self.display(*messages, color=self.debug_color, sig=self.debug_sig)
