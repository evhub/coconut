#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: This file contains all the global constants used accross Coconut.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

import sys
import os
from pyparsing import alphanums

#-----------------------------------------------------------------------------------------------------------------------
# COMPILER CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

minimum_recursion_limit = 400

from zlib import crc32 as checksum # used for generating __coconut_hash__
hash_prefix = "# __coconut_hash__ = "
hash_sep = "\x00"

specific_targets = ("2", "27", "3", "33", "35", "36")
targets = ("",) + specific_targets
pseudo_targets = {
    "26": "2",
    "32": "3",
    "34": "33",
}
sys_target = str(sys.version_info[0]) + str(sys.version_info[1])
if sys_target in pseudo_targets:
    pseudo_targets["sys"] = pseudo_targets[sys_target]
else:
    pseudo_targets["sys"] = sys_target

default_encoding = "UTF-8"
default_whitespace_chars = " \t\f\v"

openindent = "\u204b" # reverse pilcrow
closeindent = "\xb6" # pilcrow
strwrapper = "\u25b6" # right-pointing triangle
lnwrapper = "\u23f4" # left-pointing triangle
unwrapper = "\u23f9" # stop square

downs = "([{" # opens parenthetical
ups = ")]}" # closes parenthetical
holds = "'\"" # string open/close chars

taberrfmt = 2 # spaces to indent exceptions
tabideal = 4 # spaces to indent code for displaying
tabworth = 8 # worth of \t in spaces for parsing (8 = Python standard)

reserved_prefix = "_coconut"
decorator_var = "_coconut_decorator"
match_to_var = "_coconut_match_to"
match_check_var = "_coconut_match_check"
match_iter_var = "_coconut_match_iter"
match_err_var = "_coconut_match_err"
lazy_item_var = "_coconut_lazy_item"
lazy_chain_var = "_coconut_lazy_chain"
import_as_var = "_coconut_import"
yield_from_var = "_coconut_yield_from"
yield_item_var = "_coconut_yield_item"
raise_from_var = "_coconut_raise_from"
stmt_lambda_var = "_coconut_lambda"

wildcard = "_" # for pattern-matching

keywords = (
    "and",
    "as",
    "assert",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
    "nonlocal",
    )

const_vars = (
    "True",
    "False",
    "None",
    )

reserved_vars = ( # can be backslash-escaped
    "data",
    "match",
    "case",
    "async",
    "await",
    )

new_to_old_stdlib = { # new_name: (old_name, new_version_info)
    "builtins": ("__builtin__", (3,)),
    "configparser": ("ConfigParser", (3,)),
    "copyreg": ("copy_reg", (3,)),
    "dbm.gnu": ("gdbm", (3,)),
    "_dummy_thread": ("dummy_thread", (3,)),
    "queue": ("Queue", (3,)),
    "reprlib": ("repr", (3,)),
    "socketserver": ("SocketServer", (3,)),
    "_thread": ("thread", (3,)),
    "tkinter": ("Tkinter", (3,)),
    "http.cookiejar": ("cookielib", (3,)),
    "http.cookies": ("Cookie", (3,)),
    "html.entites": ("htmlentitydefs", (3,)),
    "html.parser": ("HTMLParser", (3,)),
    "http.client": ("httplib", (3,)),
    "email.mime.multipart": ("email.MIMEMultipart", (3,)),
    "email.mime.nonmultipart": ("email.MIMENonMultipart", (3,)),
    "email.mime.text": ("email.MIMEText", (3,)),
    "email.mime.base": ("email.MIMEBase", (3,)),
    "tkinter.tix": ("Tix", (3,)),
    "tkinter.ttk": ("ttk", (3,)),
    "tkinter.constants": ("Tkconstants", (3,)),
    "tkinter.dnd": ("Tkdnd", (3,)),
    "tkinter.colorchooser": ("tkColorChooser", (3,)),
    "tkinter.commondialog": ("tkCommonDialog", (3,)),
    "tkinter.filedialog": ("tkFileDialog", (3,)),
    "tkinter.font": ("tkFont", (3,)),
    "tkinter.messagebox": ("tkMessageBox", (3,)),
    "tkinter.simpledialog": ("tkSimpleDialog", (3,)),
    "urllib.robotparser": ("robotparser", (3,)),
    "xmlrpc.client": ("xmlrpclib", (3,)),
    "xmlrpc.server": ("SimpleXMLRPCServer", (3,)),
    "urllib.request": ("urllib2", (3,)),
    "urllib.parse": ("urllib2", (3,)),
    "urllib.error": ("urllib2", (3,)),
    "io.StringIO": ("StringIO.StringIO", (3,)),
    "io.BytesIO": ("BytesIO.BytesIO", (3,)),
    "collections.abc": ("collections", (3, 3)),
}

#-----------------------------------------------------------------------------------------------------------------------
# COMMAND CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

code_exts = [".coco", ".coc", ".coconut"] # in order of preference
comp_ext = ".py"

main_sig = "Coconut: "
debug_sig = ""

default_prompt = ">>> "
default_moreprompt = "    "

watch_interval = .1 # seconds

info_tabulation = 18 # offset for tabulated info messages

end_color_code = 0
color_codes = { # unix/ansii color codes, underscores in names removed
    "bold": 1,
    "dim": 2,
    "underlined": 4,
    "blink": 5,
    "reverse": 7,
    "default": 39,
    "black": 30,
    "red": 31,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "lightgray": 37,
    "darkgray": 90,
    "lightred": 91,
    "lightgreen": 92,
    "lightyellow": 93,
    "lightblue": 94,
    "lightmagenta": 95,
    "lightcyan": 96,
    "white": 97,
    "defaultbackground": 49,
    "blackbackground": 40,
    "redbackground": 41,
    "greenbackground": 42,
    "yellowbackground": 43,
    "bluebackground": 44,
    "magentabackground": 45,
    "cyanbackground": 46,
    "lightgraybackground": 47,
    "darkgraybackground": 100,
    "lightredbackground": 101,
    "lightgreenbackground": 102,
    "lightyellowbackground": 103,
    "lightbluebackground": 104,
    "lightmagentabackground": 105,
    "lightcyanbackground": 106,
    "whitebackground": 107,
    }

version_long = "Version " + VERSION_STR + " running on Python " + " ".join(sys.version.splitlines())
version_banner = "Coconut " + VERSION_STR
if DEVELOP:
    version_tag = "develop"
else:
    version_tag = VERSION_TAG
tutorial_url = "http://coconut.readthedocs.io/en/" + version_tag + "/HELP.html"
documentation_url = "http://coconut.readthedocs.io/en/" + version_tag + "/DOCS.html"

icoconut_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icoconut")
icoconut_kernel_dirs = [
    os.path.join(icoconut_dir, "coconut"),
    os.path.join(icoconut_dir, "coconut2"),
    os.path.join(icoconut_dir, "coconut3"),
]

#-----------------------------------------------------------------------------------------------------------------------
# HIGHLIGHTER CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

builtins = (
    "reduce",
    "takewhile",
    "dropwhile",
    "tee",
    "count",
    "recursive",
    "datamaker",
    "consume",
    "parallel_map",
    "addpattern",
    "prepattern",
    "recursive_iterator",
    "concurrent_map",
    )

new_operators = (
    r">>>",
    r"@",
    r"\$",
    r"`",
    r"::",
    r"(?!\.\.\.)\.\.",
    r"\u2192",
    r"\u21a6",
    r"\u21a4",
    r"\u22c5",
    r"\u2191",
    r"\xf7",
    r"\u2212",
    r"\u207b",
    r"\xac",
    r"\u2260",
    r"\u2264",
    r"\u2265",
    r"\u2227",
    r"\u2229",
    r"\u2228",
    r"\u222a",
    r"\u22bb",
    r"\u2295",
    r"\xab",
    r"\xbb",
    r"\xd7",
    r"\u2026",
    r"\u2218",
    )

#-----------------------------------------------------------------------------------------------------------------------
# ICOCONUT CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

py_syntax_version = 3.6
mimetype = "text/x-python3"

varchars = alphanums + "_"
all_keywords = keywords + const_vars + reserved_vars
