#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: This file contains all the global constants used across Coconut.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import os
import string
import platform
import re
import datetime as dt
from warnings import warn

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def fixpath(path):
    """Uniformly format a path."""
    return os.path.normpath(os.path.realpath(os.path.expanduser(path)))


def get_bool_env_var(env_var, default=False):
    """Get a boolean from an environment variable."""
    boolstr = os.getenv(env_var, "").lower()
    if boolstr in ("true", "yes", "on", "1"):
        return True
    elif boolstr in ("false", "no", "off", "0"):
        return False
    else:
        if boolstr not in ("", "none", "default"):
            warn("{env_var} has invalid value {value!r} (defaulting to {default})".format(env_var=env_var, value=os.getenv(env_var), default=default))
        return default


# -----------------------------------------------------------------------------------------------------------------------
# VERSION CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

version_banner = "Coconut " + VERSION_STR

if DEVELOP:
    version_tag = "develop"
else:
    version_tag = "v" + VERSION

version_tuple = tuple(VERSION.split("."))

WINDOWS = os.name == "nt"
PYPY = platform.python_implementation() == "PyPy"
CPYTHON = platform.python_implementation() == "CPython"
PY32 = sys.version_info >= (3, 2)
PY33 = sys.version_info >= (3, 3)
PY34 = sys.version_info >= (3, 4)
PY35 = sys.version_info >= (3, 5)
PY36 = sys.version_info >= (3, 6)
PY37 = sys.version_info >= (3, 7)
PY38 = sys.version_info >= (3, 8)
PY39 = sys.version_info >= (3, 9)
PY310 = sys.version_info >= (3, 10)
PY311 = sys.version_info >= (3, 11)
IPY = (
    ((PY2 and not PY26) or PY35)
    and not (PYPY and WINDOWS)
    and not (PY311 and not WINDOWS)
)
MYPY = (
    PY37
    and not WINDOWS
    and not PYPY
)
XONSH = (
    PY35
    and not (PYPY and PY39)
)

py_version_str = sys.version.split()[0]

# -----------------------------------------------------------------------------------------------------------------------
# PYPARSING CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

# set this to False only ever temporarily for ease of debugging
use_fast_pyparsing_reprs = True
assert use_fast_pyparsing_reprs or DEVELOP, "use_fast_pyparsing_reprs should never be disabled on non-develop build"

enable_pyparsing_warnings = DEVELOP

# experimentally determined to maximize performance
use_packrat_parser = True  # True also gives us better error messages
use_left_recursion_if_available = False
packrat_cache_size = None  # only works because final() clears the cache
streamline_grammar_for_len = 4000

default_whitespace_chars = " \t\f"  # the only non-newline whitespace Python allows

varchars = string.ascii_letters + string.digits + "_"

# -----------------------------------------------------------------------------------------------------------------------
# COMPILER CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

# set this to True only ever temporarily for ease of debugging
embed_on_internal_exc = False
assert not embed_on_internal_exc or DEVELOP, "embed_on_internal_exc should never be enabled on non-develop build"

# should be the minimal ref count observed by attach
temp_grammar_item_ref_count = 3 if PY311 else 5

minimum_recursion_limit = 128
default_recursion_limit = 2090

if sys.getrecursionlimit() < default_recursion_limit:
    sys.setrecursionlimit(default_recursion_limit)

# modules that numpy-like arrays can live in
jax_numpy_modules = (
    "jaxlib.xla_extension",
)
numpy_modules = (
    "numpy",
    "pandas",
) + jax_numpy_modules

legal_indent_chars = " \t"  # the only Python-legal indent chars

non_syntactic_newline = "\f"  # must be a single character

# both must be in ascending order and must be unbroken with no missing 2 num vers
supported_py2_vers = (
    (2, 6),
    (2, 7),
)
supported_py3_vers = (
    (3, 2),
    (3, 3),
    (3, 4),
    (3, 5),
    (3, 6),
    (3, 7),
    (3, 8),
    (3, 9),
    (3, 10),
    (3, 11),
    (3, 12),
)

# must match supported vers above and must be replicated in DOCS
specific_targets = (
    "2",
    "27",
    "3",
    "33",
    "34",
    "35",
    "36",
    "37",
    "38",
    "39",
    "310",
    "311",
    "312",
)
pseudo_targets = {
    "universal": "",
    "26": "2",
    "32": "3",
}

targets = ("",) + specific_targets

template_ext = ".py_template"

default_encoding = "utf-8"

hash_prefix = "# __coconut_hash__ = "
hash_sep = "\x00"

reserved_prefix = "_coconut"

# prefer Compiler.get_temp_var to proliferating more vars here
none_coalesce_var = reserved_prefix + "_x"
func_var = reserved_prefix + "_func"
format_var = reserved_prefix + "_format"
is_data_var = reserved_prefix + "_is_data"
custom_op_var = reserved_prefix + "_op"

# prefer Matcher.get_temp_var to proliferating more vars here
match_to_args_var = reserved_prefix + "_match_args"
match_to_kwargs_var = reserved_prefix + "_match_kwargs"
function_match_error_var = reserved_prefix + "_FunctionMatchError"
match_set_name_var = reserved_prefix + "_match_set_name"

# should match reserved_compiler_symbols below
openindent = "\u204b"  # reverse pilcrow
closeindent = "\xb6"  # pilcrow
strwrapper = "\u25b6"  # black right-pointing triangle
errwrapper = "\u24d8"  # circled letter i
early_passthrough_wrapper = "\u2038"  # caret
lnwrapper = "\u2021"  # double dagger
unwrapper = "\u23f9"  # stop square
funcwrapper = "def:"

# must be tuples for .startswith / .endswith purposes
indchars = (openindent, closeindent, "\n")
comment_chars = ("#", lnwrapper)

opens = "([{"  # opens parenthetical
closes = ")]}"  # closes parenthetical
holds = "'\""  # string open/close chars

# together should include all the constants defined above
delimiter_symbols = tuple(opens + closes + holds) + (
    strwrapper,
    errwrapper,
    early_passthrough_wrapper,
    unwrapper,
) + indchars + comment_chars
reserved_compiler_symbols = delimiter_symbols + (
    reserved_prefix,
    funcwrapper,
)

taberrfmt = 2  # spaces to indent exceptions
tabideal = 4  # spaces to indent code for displaying

justify_len = 79  # ideal line length

# for pattern-matching
default_matcher_style = "python warn"
wildcard = "_"

keyword_vars = (
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

# names that can be backslash-escaped
reserved_vars = (
    "async",
    "await",
    "data",
    "match",
    "case",
    "cases",
    "where",
    "addpattern",
    "then",
    "operator",
    "type",
    "\u03bb",  # lambda
)

# names that trigger __class__ to be bound to local vars
super_names = (
    # we would include py_super, but it's not helpful, since
    #  py_super is unsatisfied by a simple local __class__ var
    "super",
    "__class__",
)

# regexes that commonly refer to functions that can't be TCOd
untcoable_funcs = (
    r"locals",
    r"globals",
    r"(py_)?super",
    r"(typing\.)?cast",
    r"(sys\.)?exc_info",
    r"(sys\.)?_getframe",
    r"(sys\.)?_current_frames",
    r"(sys\.)?_current_exceptions",
)

py3_to_py2_stdlib = {
    # new_name: (old_name, before_version_info)
    "builtins": ("__builtin__", (3,)),
    "configparser": ("ConfigParser", (3,)),
    "copyreg": ("copy_reg", (3,)),
    "dbm.gnu": ("gdbm", (3,)),
    "queue": ("Queue", (3,)),
    "reprlib": ("repr", (3,)),
    "socketserver": ("SocketServer", (3,)),
    "_thread": ("thread", (3,)),
    "tkinter": ("Tkinter", (3,)),
    "http.cookiejar": ("cookielib", (3,)),
    "http.cookies": ("Cookie", (3,)),
    "html.entities": ("htmlentitydefs", (3,)),
    "html.parser": ("HTMLParser", (3,)),
    "http.client": ("httplib", (3,)),
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
    "urllib.error": ("urllib2", (3,)),
    "urllib.parse": ("urllib", (3,)),
    "pickle": ("cPickle", (3,)),
    "collections.abc": ("collections", (3, 3)),
    # ./ in old_name denotes from ... import ...
    "io.StringIO": ("StringIO./StringIO", (2, 7)),
    "io.BytesIO": ("cStringIO./StringIO", (2, 7)),
    "importlib.reload": ("imp./reload", (3, 4)),
    "itertools.filterfalse": ("itertools./ifilterfalse", (3,)),
    "itertools.zip_longest": ("itertools./izip_longest", (3,)),
    "math.gcd": ("fractions./gcd", (3, 5)),
    "time.process_time": ("time./clock", (3, 3)),
    # _dummy_thread was removed in Python 3.9, so this no longer works
    # "_dummy_thread": ("dummy_thread", (3,)),

    # third-party backports
    "asyncio": ("trollius", (3, 4)),
    "enum": ("aenum", (3, 4)),
    "typing.AsyncContextManager": ("typing_extensions./AsyncContextManager", (3, 6)),
    "typing.AsyncGenerator": ("typing_extensions./AsyncGenerator", (3, 6)),
    "typing.AsyncIterable": ("typing_extensions./AsyncIterable", (3, 6)),
    "typing.AsyncIterator": ("typing_extensions./AsyncIterator", (3, 6)),
    "typing.Awaitable": ("typing_extensions./Awaitable", (3, 6)),
    "typing.ChainMap": ("typing_extensions./ChainMap", (3, 6)),
    "typing.ClassVar": ("typing_extensions./ClassVar", (3, 6)),
    "typing.ContextManager": ("typing_extensions./ContextManager", (3, 6)),
    "typing.Coroutine": ("typing_extensions./Coroutine", (3, 6)),
    "typing.Counter": ("typing_extensions./Counter", (3, 6)),
    "typing.DefaultDict": ("typing_extensions./DefaultDict", (3, 6)),
    "typing.Deque": ("typing_extensions./Deque", (3, 6)),
    "typing.NamedTuple": ("typing_extensions./NamedTuple", (3, 6)),
    "typing.NewType": ("typing_extensions./NewType", (3, 6)),
    "typing.NoReturn": ("typing_extensions./NoReturn", (3, 6)),
    "typing.overload": ("typing_extensions./overload", (3, 6)),
    "typing.Text": ("typing_extensions./Text", (3, 6)),
    "typing.Type": ("typing_extensions./Type", (3, 6)),
    "typing.TYPE_CHECKING": ("typing_extensions./TYPE_CHECKING", (3, 6)),
    "typing.get_type_hints": ("typing_extensions./get_type_hints", (3, 6)),
    "typing.OrderedDict": ("typing_extensions./OrderedDict", (3, 7)),
    "typing.final": ("typing_extensions./final", (3, 8)),
    "typing.Final": ("typing_extensions./Final", (3, 8)),
    "typing.Literal": ("typing_extensions./Literal", (3, 8)),
    "typing.Protocol": ("typing_extensions./Protocol", (3, 8)),
    "typing.runtime_checkable": ("typing_extensions./runtime_checkable", (3, 8)),
    "typing.TypedDict": ("typing_extensions./TypedDict", (3, 8)),
    "typing.get_origin": ("typing_extensions./get_origin", (3, 8)),
    "typing.get_args": ("typing_extensions./get_args", (3, 8)),
    "typing.Annotated": ("typing_extensions./Annotated", (3, 9)),
    "typing.Concatenate": ("typing_extensions./Concatenate", (3, 10)),
    "typing.ParamSpec": ("typing_extensions./ParamSpec", (3, 10)),
    "typing.ParamSpecArgs": ("typing_extensions./ParamSpecArgs", (3, 10)),
    "typing.ParamSpecKwargs": ("typing_extensions./ParamSpecKwargs", (3, 10)),
    "typing.TypeAlias": ("typing_extensions./TypeAlias", (3, 10)),
    "typing.TypeGuard": ("typing_extensions./TypeGuard", (3, 10)),
    "typing.is_typeddict": ("typing_extensions./is_typeddict", (3, 10)),
    "typing.assert_never": ("typing_extensions./assert_never", (3, 11)),
    "typing.assert_type": ("typing_extensions./assert_type", (3, 11)),
    "typing.clear_overloads": ("typing_extensions./clear_overloads", (3, 11)),
    "typing.dataclass_transform": ("typing_extensions./dataclass_transform", (3, 11)),
    "typing.get_overloads": ("typing_extensions./get_overloads", (3, 11)),
    "typing.LiteralString": ("typing_extensions./LiteralString", (3, 11)),
    "typing.Never": ("typing_extensions./Never", (3, 11)),
    "typing.NotRequired": ("typing_extensions./NotRequired", (3, 11)),
    "typing.reveal_type": ("typing_extensions./reveal_type", (3, 11)),
    "typing.Required": ("typing_extensions./Required", (3, 11)),
    "typing.Self": ("typing_extensions./Self", (3, 11)),
    "typing.TypeVarTuple": ("typing_extensions./TypeVarTuple", (3, 11)),
    "typing.Unpack": ("typing_extensions./Unpack", (3, 11)),
}

self_match_types = (
    "bool",
    "bytearray",
    "bytes",
    "dict",
    "float",
    "frozenset",
    "int",
    "py_int",
    "list",
    "set",
    "str",
    "py_str",
    "tuple",
)

python_builtins = (
    '__import__', 'abs', 'all', 'any', 'bin', 'bool', 'bytearray',
    'breakpoint', 'bytes', 'chr', 'classmethod', 'compile', 'complex',
    'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'filter',
    'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
    'hash', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass',
    'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview',
    'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print',
    'property', 'range', 'repr', 'reversed', 'round', 'set', 'setattr',
    'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple',
    'type', 'vars', 'zip',
    'Ellipsis', 'NotImplemented',
    'ArithmeticError', 'AssertionError', 'AttributeError',
    'BaseException', 'BufferError', 'BytesWarning', 'DeprecationWarning',
    'EOFError', 'EnvironmentError', 'Exception', 'FloatingPointError',
    'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError',
    'ImportWarning', 'IndentationError', 'IndexError', 'KeyError',
    'KeyboardInterrupt', 'LookupError', 'MemoryError', 'NameError',
    'NotImplementedError', 'OSError', 'OverflowError',
    'PendingDeprecationWarning', 'ReferenceError', 'ResourceWarning',
    'RuntimeError', 'RuntimeWarning', 'StopIteration',
    'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit',
    'TabError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
    'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
    'UnicodeWarning', 'UserWarning', 'ValueError', 'VMSError',
    'Warning', 'WindowsError', 'ZeroDivisionError',
    '__name__',
    '__file__',
    '__annotations__',
    '__debug__',
    # don't include builtins that aren't always made available by Coconut:
    # 'BlockingIOError', 'ChildProcessError', 'ConnectionError',
    # 'BrokenPipeError', 'ConnectionAbortedError', 'ConnectionRefusedError',
    # 'ConnectionResetError', 'FileExistsError', 'FileNotFoundError',
    # 'InterruptedError', 'IsADirectoryError', 'NotADirectoryError',
    # 'PermissionError', 'ProcessLookupError', 'TimeoutError',
    # 'StopAsyncIteration', 'ModuleNotFoundError', 'RecursionError',
    # 'EncodingWarning',
)

# -----------------------------------------------------------------------------------------------------------------------
# COMMAND CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

code_exts = (".coco", ".coc", ".coconut")  # in order of preference
comp_ext = ".py"

main_sig = "Coconut: "

main_prompt = ">>> "
more_prompt = "    "

mypy_path_env_var = "MYPYPATH"
style_env_var = "COCONUT_STYLE"
vi_mode_env_var = "COCONUT_VI_MODE"
home_env_var = "COCONUT_HOME"
use_color_env_var = "COCONUT_USE_COLOR"

coconut_home = fixpath(os.getenv(home_env_var, "~"))

use_color = get_bool_env_var(use_color_env_var, default=None)
error_color_code = "31"
log_color_code = "93"

default_style = "default"
prompt_histfile = os.path.join(coconut_home, ".coconut_history")
prompt_multiline = False
prompt_vi_mode = get_bool_env_var(vi_mode_env_var)
prompt_wrap_lines = True
prompt_history_search = True
prompt_use_suggester = False

base_dir = os.path.dirname(os.path.abspath(fixpath(__file__)))

base_stub_dir = os.path.dirname(base_dir)
installed_stub_dir = os.path.join(coconut_home, ".coconut_stubs")

watch_interval = .1  # seconds

info_tabulation = 18  # offset for tabulated info messages

rtfd_url = "http://coconut.readthedocs.io/en/" + version_tag
tutorial_url = rtfd_url + "/HELP.html"
documentation_url = rtfd_url + "/DOCS.html"

new_issue_url = "https://github.com/evhub/coconut/issues/new"
report_this_text = "(you should report this at " + new_issue_url + ")"

exit_chars = (
    "\x04",  # Ctrl-D
    "\x1a",  # Ctrl-Z
)
ansii_escape = "\x1b"

# should match special characters above
reserved_command_symbols = exit_chars + (
    ansii_escape,
)

# always use atomic --xxx=yyy rather than --xxx yyy
coconut_run_args = ("--run", "--target=sys", "--line-numbers", "--quiet")
coconut_run_verbose_args = ("--run", "--target=sys", "--line-numbers")
coconut_import_hook_args = ("--target=sys", "--line-numbers", "--quiet")

default_mypy_args = (
    "--pretty",
)
verbose_mypy_args = (
    "--warn-unused-configs",
    "--warn-redundant-casts",
    "--warn-unused-ignores",
    "--warn-return-any",
    "--show-error-context",
    "--warn-incomplete-stub",
)

mypy_silent_non_err_prefixes = (
    "Success:",
)
mypy_silent_err_prefixes = (
    "Found ",
)
mypy_err_infixes = (
    ": error: ",
)

oserror_retcode = 127

mypy_install_arg = "install"

mypy_builtin_regex = re.compile(r"\b(reveal_type|reveal_locals)\b")

interpreter_uses_auto_compilation = True
interpreter_uses_coconut_breakpoint = True

coconut_pth_file = os.path.join(base_dir, "command", "resources", "zcoconut.pth")

interpreter_compiler_var = "__coconut_compiler__"

# -----------------------------------------------------------------------------------------------------------------------
# HIGHLIGHTER CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

shebang_regex = r'coconut(?:-run)?'

interp_only_builtins = (
    "reload",
    "exit",
    "quit",
)

coconut_specific_builtins = (
    "breakpoint",
    "help",
    "TYPE_CHECKING",
    "reduce",
    "takewhile",
    "dropwhile",
    "tee",
    "count",
    "makedata",
    "consume",
    "parallel_map",
    "addpattern",
    "recursive_iterator",
    "concurrent_map",
    "fmap",
    "starmap",
    "reiterable",
    "scan",
    "groupsof",
    "memoize",
    "zip_longest",
    "override",
    "flatten",
    "ident",
    "of",
    "flip",
    "const",
    "lift",
    "all_equal",
    "collectby",
    "multi_enumerate",
    "cartesian_product",
    "py_chr",
    "py_hex",
    "py_input",
    "py_int",
    "py_map",
    "py_object",
    "py_oct",
    "py_open",
    "py_print",
    "py_range",
    "py_str",
    "py_super",
    "py_zip",
    "py_filter",
    "py_reversed",
    "py_enumerate",
    "py_raw_input",
    "py_xrange",
    "py_repr",
    "py_breakpoint",
    "_namedtuple_of",
)

all_builtins = frozenset(python_builtins + coconut_specific_builtins)

magic_methods = (
    "__fmap__",
    "__iter_getitem__",
)

exceptions = (
    "MatchError",
)

new_operators = (
    r"@",
    r"\$",
    r"`",
    r"::",
    r";+",
    r"(?:<\*?\*?)?(?!\.\.\.)\.\.(?:\*?\*?>)?",  # ..
    r"\|\??\*?\*?>",
    r"<\*?\*?\|",
    r"->",
    r"\?\??",
    r"<:",
    "\u2192",  # ->
    "\\??\\*?\\*?\u21a6",  # |>
    "\u21a4\\*?\\*?",  # <|
    "<?\\*?\\*?\u2218\\*?\\*?>?",  # ..
    "\u22c5",  # *
    "\u2191",  # **
    "\xf7",  # /
    "\u207b",  # -
    "\xac=?",  # ~ !
    "\u2260",  # !=
    "\u2264",  # <=
    "\u2265",  # >=
    "\u2227",  # &
    "\u2229",  # &
    "\u2228",  # |
    "\u222a",  # |
    "\u22bb",  # ^
    "\u2295",  # ^
    "\xab",  # <<
    "\xbb",  # >>
    "\xd7",  # @
    "\u2026",  # ...
    "\u2286",  # C=
    "\u2287",  # ^reversed
    "\u228a",  # C!=
    "\u228b",  # ^reversed
)

# -----------------------------------------------------------------------------------------------------------------------
# INSTALLATION CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

package_name = "coconut" + ("-develop" if DEVELOP else "")

author = "Evan Hubinger"
author_email = "evanjhub@gmail.com"

description = "Simple, elegant, Pythonic functional programming."
website_url = "http://coconut-lang.org"

license_name = "Apache 2.0"

pure_python_env_var = "COCONUT_PURE_PYTHON"
PURE_PYTHON = get_bool_env_var(pure_python_env_var)

# the different categories here are defined in requirements.py,
#  anything after a colon is ignored but allows different versions
#  for different categories, and tuples denote the use of environment
#  markers as specified in requirements.py
all_reqs = {
    "main": (
    ),
    "cpython": (
        "cPyparsing",
    ),
    "purepython": (
        "pyparsing",
    ),
    "non-py26": (
        "pygments",
    ),
    "py2": (
        "futures",
        "backports.functools-lru-cache",
        ("prompt_toolkit", "mark2"),
    ),
    "py3": (
        ("prompt_toolkit", "mark3"),
    ),
    "py26": (
        "argparse",
    ),
    "jobs": (
        "psutil",
    ),
    "kernel": (
        ("ipython", "py2"),
        ("ipython", "py3"),
        ("ipykernel", "py2"),
        ("ipykernel", "py3"),
        ("jupyter-client", "py2"),
        ("jupyter-client", "py==35"),
        ("jupyter-client", "py36"),
        "jedi",
        ("pywinpty", "py2;windows"),
    ),
    "jupyter": (
        "jupyter",
        ("jupyter-console", "py2"),
        ("jupyter-console", "py==35"),
        ("jupyter-console", "py36"),
        ("jupyterlab", "py35"),
        ("jupytext", "py3"),
        "papermill",
    ),
    "mypy": (
        "mypy[python2]",
        "types-backports",
        ("typing_extensions", "py==35"),
        ("typing_extensions", "py36"),
    ),
    "watch": (
        "watchdog",
    ),
    "xonsh": (
        "xonsh",
    ),
    "backports": (
        ("trollius", "py2;cpy"),
        ("aenum", "py<34"),
        ("dataclasses", "py==36"),
        ("typing", "py<35"),
        ("typing_extensions", "py==35"),
        ("typing_extensions", "py36"),
    ),
    "dev": (
        ("pre-commit", "py3"),
        "requests",
        "vprof",
    ),
    "docs": (
        "sphinx",
        "pygments",
        "myst-parser",
        "pydata-sphinx-theme",
    ),
    "tests": (
        "pytest",
        "pexpect",
        ("numpy", "py34"),
        ("numpy", "py2;cpy"),
    ),
}

# min versions are inclusive
min_versions = {
    "cPyparsing": (2, 4, 7, 1, 2, 0),
    ("pre-commit", "py3"): (2, 20),
    "psutil": (5,),
    "jupyter": (1, 0),
    "types-backports": (0, 1),
    "futures": (3, 4),
    "backports.functools-lru-cache": (1, 6),
    "argparse": (1, 4),
    "pexpect": (4,),
    ("trollius", "py2;cpy"): (2, 2),
    "requests": (2, 28),
    ("numpy", "py34"): (1,),
    ("numpy", "py2;cpy"): (1,),
    ("dataclasses", "py==36"): (0, 8),
    ("aenum", "py<34"): (3,),
    "sphinx": (5, 3),
    "pydata-sphinx-theme": (0, 12),
    "myst-parser": (0, 18),
    "mypy[python2]": (0, 991),
    ("jupyter-console", "py36"): (6, 4),
    ("typing", "py<35"): (3, 1),

    # pinned reqs: (must be added to pinned_reqs below)

    # don't upgrade this; it breaks on Python 3.6
    ("jupyter-client", "py36"): (7, 1, 2),
    ("typing_extensions", "py36"): (4, 1),
    # don't upgrade these; they break on Python 3.5
    ("ipykernel", "py3"): (5, 5),
    ("ipython", "py3"): (7, 9),
    ("jupyter-console", "py==35"): (6, 1),
    ("jupyter-client", "py==35"): (6, 1, 12),
    ("jupytext", "py3"): (1, 8),
    ("jupyterlab", "py35"): (2, 2),
    "xonsh": (0, 9),
    ("typing_extensions", "py==35"): (3, 10),
    # don't upgrade this to allow all versions
    ("prompt_toolkit", "mark3"): (1,),
    # don't upgrade this; it breaks on Python 2.6
    "pytest": (3,),
    # don't upgrade this; it breaks on unix
    "vprof": (0, 36),
    # don't upgrade this; it breaks on Python 3.4
    "pygments": (2, 3),
    # don't upgrade these; they break on Python 2
    ("jupyter-client", "py2"): (5, 3),
    ("pywinpty", "py2;windows"): (0, 5),
    ("jupyter-console", "py2"): (5, 2),
    ("ipython", "py2"): (5, 4),
    ("ipykernel", "py2"): (4, 10),
    ("prompt_toolkit", "mark2"): (1,),
    "watchdog": (0, 10),
    "papermill": (1, 2),
    # don't upgrade this; it breaks with old IPython versions
    "jedi": (0, 17),
    # Coconut requires pyparsing 2
    "pyparsing": (2, 4, 7),
}

# should match the reqs with comments above
pinned_reqs = (
    ("jupyter-client", "py36"),
    ("typing_extensions", "py36"),
    ("jupyter-client", "py2"),
    ("ipykernel", "py3"),
    ("ipython", "py3"),
    ("jupyter-console", "py==35"),
    ("jupyter-client", "py==35"),
    ("jupytext", "py3"),
    ("jupyterlab", "py35"),
    "xonsh",
    ("typing_extensions", "py==35"),
    ("prompt_toolkit", "mark3"),
    "pytest",
    "vprof",
    "pygments",
    ("pywinpty", "py2;windows"),
    ("jupyter-console", "py2"),
    ("ipython", "py2"),
    ("ipykernel", "py2"),
    ("prompt_toolkit", "mark2"),
    "watchdog",
    "papermill",
    "jedi",
    "pyparsing",
)

# max versions are exclusive; None implies that the max version should
#  be generated by incrementing the min version; multiple Nones implies
#  that the element corresponding to the last None should be incremented
_ = None
max_versions = {
    ("jupyter-client", "py==35"): _,
    "pyparsing": _,
    "cPyparsing": (_, _, _),
    ("prompt_toolkit", "mark2"): _,
    "jedi": _,
    ("pywinpty", "py2;windows"): _,
}

allowed_constrained_but_unpinned_reqs = (
    "cPyparsing",
)

classifiers = (
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: Apache Software License",
    "Intended Audience :: Developers",
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
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Other",
    "Programming Language :: Other Scripting Engines",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Framework :: IPython",
    "Framework :: Jupyter",
    "Typing :: Typed",
)

search_terms = (
    "functional",
    "programming",
    "language",
    "compiler",
    "pattern",
    "pattern-matching",
    "algebraic",
    "data type",
    "data types",
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
    "compose",
    "partial",
    "application",
    "currying",
    "curry",
    "pipeline",
    "pipe",
    "unicode",
    "operator",
    "operators",
    "frozenset",
    "literal",
    "syntax",
    "destructuring",
    "assignment",
    "fold",
    "datamaker",
    "prepattern",
    "iterator",
    "none",
    "coalesce",
    "coalescing",
    "statement",
    "lru_cache",
    "memoization",
    "backport",
    "typing",
    "embed",
    "PEP 622",
    "overrides",
    "islice",
) + (
    coconut_specific_builtins
    + exceptions
    + magic_methods
    + reserved_vars
)

exclude_install_dirs = (
    os.path.join("coconut", "tests", "dest"),
    "docs",
    "pyston",
    "pyprover",
    "bbopt",
    "coconut-prelude",
)
exclude_docs_dirs = (
    ".pytest_cache",
    "README.*",
)

script_names = (
    "coconut",
    ("coconut-develop" if DEVELOP else "coconut-release"),
    ("coconut-py2" if PY2 else "coconut-py3"),
    "coconut-py" + str(sys.version_info[0]) + "." + str(sys.version_info[1]),
) + tuple(
    "coconut-v" + ".".join(version_tuple[:i]) for i in range(1, len(version_tuple) + 1)
)

pygments_lexers = (
    "coconut = coconut.highlighter:CoconutLexer",
    "coconut_python = coconut.highlighter:CoconutPythonLexer",
    "coconut_pycon = coconut.highlighter:CoconutPythonConsoleLexer",
)

requests_sleep_times = (0, 0.1, 0.2, 0.3, 0.4, 1)

# -----------------------------------------------------------------------------------------------------------------------
# INTEGRATION CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

# must be replicated in DOCS
coconut_kernel_kwargs = dict(target="sys", line_numbers=True, keep_lines=True, no_wrap=True)

icoconut_dir = os.path.join(base_dir, "icoconut")

icoconut_custom_kernel_name = "coconut"
icoconut_custom_kernel_dir = os.path.join(icoconut_dir, icoconut_custom_kernel_name)

icoconut_custom_kernel_install_loc = "/".join(("share", "jupyter", "kernels", icoconut_custom_kernel_name))
icoconut_custom_kernel_file_loc = "/".join(("coconut", "icoconut", icoconut_custom_kernel_name, "kernel.json"))

icoconut_default_kernel_names = (
    "coconut_py",
    "coconut_py2",
    "coconut_py3",
)
icoconut_default_kernel_dirs = tuple(
    os.path.join(icoconut_dir, kernel_name)
    for kernel_name in icoconut_default_kernel_names
)

icoconut_old_kernel_names = (
    "coconut2",
    "coconut3",
)

py_syntax_version = 3
mimetype = "text/x-python3"

all_keywords = keyword_vars + const_vars + reserved_vars

conda_build_env_var = "CONDA_BUILD"

# -----------------------------------------------------------------------------------------------------------------------
# DOCUMENTATION CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

without_toc = """
..
    <insert toctree here>
"""

with_toc = """
.. toctree::
   :maxdepth: 2

   FAQ
   HELP
   DOCS
   CONTRIBUTING
"""

project = "Coconut"
copyright = "2015-{y} Evan Hubinger, licensed under Apache 2.0".format(
    y=dt.datetime.now().year,
)

highlight_language = "coconut"
