#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: This file contains all the global constants used across Coconut.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os
import string

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


def fixpath(path):
    """Uniformly formats a path."""
    return os.path.normpath(os.path.realpath(path))


def get_target_info(target):
    """Returns target information as a version tuple."""
    return tuple(int(x) for x in target)


#-----------------------------------------------------------------------------------------------------------------------
# VERSION CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

version_long = "Version " + VERSION_STR + " running on Python " + sys.version.split()[0]
version_banner = "Coconut " + VERSION_STR

if DEVELOP:
    version_tag = "develop"
else:
    version_tag = "v" + VERSION
version_str_tag = "v" + VERSION_STR

version_tuple = VERSION.split(".")

#-----------------------------------------------------------------------------------------------------------------------
# INSTALLATION CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

package_name = "coconut" + ("-develop" if DEVELOP else "")

author = "Evan Hubinger"
author_email = "evanjhub@gmail.com"

description = "Simple, elegant, Pythonic functional programming."
website_url = "http://coconut-lang.org"

all_reqs = {
    "main": [
        "pyparsing",
    ],
    "non-py26": [
        "pygments",
        "prompt_toolkit",
    ],
    "py2": [
        "futures",
    ],
    "py26": [
        "argparse",
    ],
    "jobs": [
        "psutil",
    ],
    "jupyter": [
        "jupyter",
        "ipython",
        "ipykernel",
        "jupyter-console",
    ],
    "mypy": [
        "mypy",
    ],
    "watch": [
        "watchdog",
    ],
    "dev": [
        "pre-commit",
        "requests",
    ],
    "docs": [
        "sphinx",
        "pygments",
        "recommonmark",
        "sphinx_bootstrap_theme",
    ],
    "tests": [
        "pytest",
    ],
}

min_versions = {
    "pyparsing": (2, 2, 0),
    "pre-commit": (0, 13),
    "sphinx": (1, 5),
    "pygments": (2, 2),
    "recommonmark": (0, 4),
    "sphinx_bootstrap_theme": (0, 4),
    "psutil": (5, 2),
    "jupyter": (1, 0),
    "jupyter-console": (5, 1),
    "ipython": (5, 3),
    "ipykernel": (4, 6),
    "mypy": (0, 511),
    "prompt_toolkit": (1, 0),
    "futures": (3, 1),
    "argparse": (1, 4),
    "pytest": (3, 0),
    "watchdog": (0, 8),
    "requests": (2,),
}

version_strictly = [
    "pyparsing",
    "sphinx",
    "sphinx_bootstrap_theme",
    "ipython",
    "ipykernel",
]

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: Apache Software License",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Topic :: Software Development",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Compilers",
    "Topic :: Software Development :: Interpreters",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
    "Environment :: Console",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Other",
    "Programming Language :: Other Scripting Engines",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Framework :: IPython",
]

search_terms = [
    "functional",
    "programming",
    "language",
    "compiler",
    "match",
    "pattern",
    "pattern-matching",
    "algebraic",
    "data",
    "type",
    "types",
    "lambda",
    "lambdas",
    "lazy",
    "evaluation",
    "lazy list",
    "lazy lists",
    "tail",
    "recursion",
    "call",
    "recursive",
    "infix",
    "function",
    "composition",
    "partial",
    "application",
    "currying",
    "curry",
    "pipeline",
    "pipe",
    "unicode",
    "operator",
    "operators",
    "frozenset literal",
    "destructuring",
    "assignment",
    "reduce",
    "takewhile",
    "dropwhile",
    "tee",
    "consume",
    "count",
    "parallel_map",
    "concurrent_map",
    "MatchError",
    "datamaker",
    "addpattern",
    "prepattern",
    "recursive_iterator",
    "iterator",
    "fmap",
    "case",
    "keyword",
]

script_names = [
    "coconut",
    ("coconut-py2" if PY2 else "coconut-py3"),
    "coconut-py" + str(sys.version_info[0]) + str(sys.version_info[1]),
    ("coconut-develop" if DEVELOP else "coconut-release"),
] + [
    "coconut-v" + ".".join(version_tuple[:i]) for i in range(1, len(version_tuple) + 1)
]

document_names = {
    "description": "README.rst",
    "license": "LICENSE.txt",
}

#-----------------------------------------------------------------------------------------------------------------------
# COMPILER CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

template_ext = ".py_template"

default_encoding = "utf-8"

packrat_cache_size = 512
use_packrat = packrat_cache_size != 0

default_recursion_limit = 2000
minimum_recursion_limit = 100

# used for generating __coconut_hash__
from zlib import crc32 as checksum  # NOQA

hash_prefix = "# __coconut_hash__ = "
hash_sep = "\x00"

specific_targets = ("2", "27", "3", "33", "35", "36")
pseudo_targets = {
    "26": "2",
    "32": "3",
    "34": "33",
}

targets = ("",) + specific_targets
_sys_target = str(sys.version_info[0]) + str(sys.version_info[1])
if _sys_target in pseudo_targets:
    pseudo_targets["sys"] = pseudo_targets[_sys_target]
elif sys.version_info > get_target_info(specific_targets[-1]):
    pseudo_targets["sys"] = specific_targets[-1]
else:
    pseudo_targets["sys"] = _sys_target

default_whitespace_chars = " \t\f\v\xa0"
varchars = string.ascii_letters + string.digits + "_"

openindent = "\u204b"  # reverse pilcrow
closeindent = "\xb6"  # pilcrow
strwrapper = "\u25b6"  # right-pointing triangle
lnwrapper = "\u23f4"  # left-pointing triangle
unwrapper = "\u23f9"  # stop square

opens = "([{"  # opens parenthetical
closes = ")]}"  # closes parenthetical
holds = "'\""  # string open/close chars

taberrfmt = 2  # spaces to indent exceptions
tabideal = 4  # spaces to indent code for displaying
tabworth = 8  # worth of \t in spaces for parsing (8 = Python standard)

reserved_prefix = "_coconut"
decorator_var = reserved_prefix + "_decorator"
match_to_var = reserved_prefix + "_match_to"
match_to_args_var = match_to_var + "_args"
match_to_kwargs_var = match_to_var + "_kwargs"
match_check_var = reserved_prefix + "_match_check"
match_temp_var = reserved_prefix + "_match_temp"
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

py3_to_py2_stdlib = {
    # new_name: (old_name, before_version_info)
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

default_style = "default"
default_multiline = False
default_vi_mode = False
default_mouse_support = True

mypy_path_env_var = "MYPYPATH"
style_env_var = "COCONUT_STYLE"

watch_interval = .1  # seconds

info_tabulation = 18  # offset for tabulated info messages

base_url = "http://coconut.readthedocs.io/en/" + version_tag
tutorial_url = base_url + "/HELP.html"
documentation_url = base_url + "/DOCS.html"

base_dir = os.path.dirname(os.path.abspath(fixpath(__file__)))

icoconut_dir = os.path.join(base_dir, "icoconut")
icoconut_kernel_dirs = [
    os.path.join(icoconut_dir, "coconut"),
    os.path.join(icoconut_dir, "coconut2"),
    os.path.join(icoconut_dir, "coconut3"),
]

stub_dir = os.path.join(base_dir, "stubs")

exit_chars = (
    "\x04",  # Ctrl-D
    "\x1a",  # Ctrl-Z
)

coconut_run_args = ["--run", "--quiet", "--target", "sys"]

#-----------------------------------------------------------------------------------------------------------------------
# HIGHLIGHTER CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

shebang_regex = r'coconut(?:-run)?'

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
    "fmap",
    "py_chr",
    "py_filter",
    "py_hex",
    "py_input",
    "py_input",
    "py_int",
    "py_object",
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
    main_prompt.strip(),
    r"@",
    r"\$",
    r"`",
    r"::",
    r"(?!\.\.\.)\.\.",
    r"\|>",
    r"<\|",
    r"\|\*>",
    r"<\*\|",
    r"->",
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

all_keywords = keywords + const_vars + reserved_vars

conda_build_env_var = "CONDA_BUILD"

#-----------------------------------------------------------------------------------------------------------------------
# DOCUMENTATION CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

without_toc = """
=======
"""

with_toc = """
=======

.. toctree::
   :maxdepth: 3

   FAQ
   HELP
   DOCS
   CONTRIBUTING
"""

project = "Coconut"
copyright = "2015-2017, Evan Hubinger, licensed under Apache 2.0"

highlight_language = "coconut"
