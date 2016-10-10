#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from coconut.root import *  # NOQA

import sys
import os
from pyparsing import alphanums

#-----------------------------------------------------------------------------------------------------------------------
# COMPILER CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

default_recursion_limit = 2000
minimum_recursion_limit = 100

# used for generating __coconut_hash__
from zlib import crc32 as checksum  # NOQA

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

default_encoding = "utf-8"
default_whitespace_chars = " \t\f\v"

openindent = "\u204b"  # reverse pilcrow
closeindent = "\xb6"  # pilcrow
strwrapper = "\u25b6"  # right-pointing triangle
lnwrapper = "\u23f4"  # left-pointing triangle
unwrapper = "\u23f9"  # stop square

downs = "([{"  # opens parenthetical
ups = ")]}"  # closes parenthetical
holds = "'\""  # string open/close chars

taberrfmt = 2  # spaces to indent exceptions
tabideal = 4  # spaces to indent code for displaying
tabworth = 8  # worth of \t in spaces for parsing (8 = Python standard)

reserved_prefix = "_coconut"
decorator_var = reserved_prefix + "_decorator"
match_to_var = reserved_prefix + "_match_to"
match_check_var = reserved_prefix + "_match_check"
match_iter_var = reserved_prefix + "_match_iter"
match_err_var = reserved_prefix + "_match_err"
lazy_item_var = reserved_prefix + "_lazy_item"
lazy_chain_var = reserved_prefix + "_lazy_chain"
import_as_var = reserved_prefix + "_import"
yield_from_var = reserved_prefix + "_yield_from"
yield_item_var = reserved_prefix + "_yield_item"
raise_from_var = reserved_prefix + "_raise_from"
stmt_lambda_var = reserved_prefix + "_lambda"
tre_mock_var = reserved_prefix + "_mock_func"
tre_store_var = reserved_prefix + "_recursive_func"

wildcard = "_"  # for pattern-matching

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

reserved_vars = (  # can be backslash-escaped
    "data",
    "match",
    "case",
    "async",
    "await",
)

new_to_old_stdlib = {  # new_name: (old_name, new_version_info)
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

code_exts = [".coco", ".coc", ".coconut"]  # in order of preference
comp_ext = ".py"

main_sig = "Coconut: "

main_prompt = ">>> "
more_prompt = "    "

default_style = "monokai"
default_multiline = False
default_vi_mode = False
default_mouse_support = True

ensure_elapsed_time = .001  # seconds
watch_interval = .1  # seconds

info_tabulation = 18  # offset for tabulated info messages

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
    "datamaker",
    "consume",
    "parallel_map",
    "addpattern",
    "prepattern",
    "recursive_iterator",
    "concurrent_map",
    "py_chr",
    "py_filter",
    "py_hex",
    "py_input",
    "py_input",
    "py_int",
    "py_oct",
    "py_open",
    "py_print",
    "py_range",
    "py_xrange",
    "py_str",
    "py_map",
    "py_zip",
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
