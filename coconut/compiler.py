#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Compiles Coconut code into Python code.
"""

# Table of Contents:
#   - Imports
#   - Constants
#   - Exceptions
#   - Utilities
#   - Header Utilities
#   - Handlers
#   - Parser
#   - Processors
#   - Parser Handlers
#   - Grammar
#   - Endpoints

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from pyparsing import *
from .root import *
import traceback

import platform
if platform.python_implementation() != "PyPy":
    ParserElement.enablePackrat() # huge speedup in CPython, but can cause errors in PyPy

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

from zlib import crc32 as checksum # used for generating __coconut_hash__

specific_targets = ("2", "27", "3", "33", "35", "36")
targets = ("",) + specific_targets
pseudo_targets = {
    "26": "2",
    "32": "3",
    "34": "33"
}
sys_target = str(sys.version_info[0]) + str(sys.version_info[1])
if sys_target in pseudo_targets:
    pseudo_targets["sys"] = pseudo_targets[sys_target]
else:
    pseudo_targets["sys"] = sys_target
default_encoding = "UTF-8"
hash_prefix = "# __coconut_hash__ = "
hash_sep = "\x00"
openindent = "\u204b" # reverse pilcrow
closeindent = "\xb6" # pilcrow
strwrapper = "\u25b6" # right-pointing triangle
lnwrapper = "\u23f4" # left-pointing triangle
unwrapper = "\u23f9" # stop square
white = " \t\f"
downs = "([{" # opens parenthetical
ups = ")]}" # closes parenthetical
holds = "'\""
tabideal = 4 # worth of tabs in spaces for displaying
tabworth = 8 # worth of tabs in spaces for parsing (8 = Python standard)
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
    "nonlocal"
    )
const_vars = (
    "True",
    "False",
    "None"
    )
reserved_vars = ( # can be backslash-escaped
    "data",
    "match",
    "case",
    "async",
    "await"
    )
new_to_old_stdlib = { # old_name: (new_name, new_version_info)
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
    "tkinter.dialog": ("Dialog", (3,)),
    "tkinter.filedialog": ("FileDialog", (3,)),
    "tkinter.scrolledtext": ("ScrolledText", (3,)),
    "tkinter.simpledialog": ("SimpleDialog", (3,)),
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
    "io.StringIO": ("StringIO", (3,)),
    "io.BytesIO": ("BytesIO", (3,)),
    "collections.abc": ("collections", (3, 3))
}

ParserElement.setDefaultWhitespaceChars(white)

#-----------------------------------------------------------------------------------------------------------------------
# EXCEPTIONS:
#-----------------------------------------------------------------------------------------------------------------------

def printerr(*args):
    """Prints to standard error."""
    print(*args, file=sys.stderr)

def format_error(err_type, err_value, err_trace=None):
    """Properly formats the specified error."""
    if err_trace is None:
        err_name, err_msg = "".join(traceback.format_exception_only(err_type, err_value)).strip().split(": ", 1)
        err_name = err_name.split(".")[-1]
        return err_name + ": " + err_msg
    else:
        return "".join(traceback.format_exception(err_type, err_value, err_trace)).strip()

def get_error(verbose=False):
    """Properly formats the current error."""
    err_type, err_value, err_trace = sys.exc_info()
    if not verbose:
        err_trace = None
    return format_error(err_type, err_value, err_trace)

def clean(inputline, strip=True):
    """Cleans and strips a line."""
    if hasattr(sys.stdout, "encoding") and sys.stdout.encoding is not None:
        stdout_encoding = sys.stdout.encoding
    else:
        stdout_encoding = default_encoding
    inputline = inputline.replace(openindent, "").replace(closeindent, "")
    if strip:
        inputline = inputline.strip()
    return inputline.encode(stdout_encoding, "replace").decode(stdout_encoding)

class CoconutException(Exception):
    """Base Coconut exception."""
    def __init__(self, value, item=None):
        """Creates the Coconut exception."""
        self.value = value
        if item is not None:
            self.value += ": " + ascii(item)
    def __repr__(self):
        """Displays the Coconut exception."""
        return self.value
    def __str__(self):
        """Wraps __repr__."""
        return repr(self)

class CoconutSyntaxError(CoconutException):
    """Coconut SyntaxError."""
    def __init__(self, message, source=None, point=None, ln=None):
        """Creates the Coconut SyntaxError."""
        self.value = message
        if ln is not None:
            self.value += " (line " + str(ln) + ")"
        if source:
            if point is None:
                self.value += "\n" + " "*tabideal + clean(source)
            else:
                part = clean(source.splitlines()[lineno(point, source)-1], False).lstrip()
                point -= len(source) - len(part) # adjust all points based on lstrip
                part = part.rstrip() # adjust only points that are too large based on rstrip
                self.value += "\n" + " "*tabideal + part
                if point > 0:
                    if point >= len(part):
                        point = len(part) - 1
                    self.value += "\n" + " "*tabideal
                    for x in range(0, point):
                        if part[x] in white:
                            self.value += part[x]
                        else:
                            self.value += " "
                    self.value += "^"

class CoconutParseError(CoconutSyntaxError):
    """Coconut ParseError."""
    def __init__(self, source=None, point=None, lineno=None):
        """Creates The Coconut ParseError."""
        CoconutSyntaxError.__init__(self, "parsing failed", source, point, lineno)

class CoconutStyleError(CoconutSyntaxError):
    """Coconut --strict error."""
    def __init__(self, message, source=None, point=None, lineno=None):
        """Creates the --strict Coconut error."""
        message += " (disable --strict to dismiss)"
        CoconutSyntaxError.__init__(self, message, source, point, lineno)

class CoconutTargetError(CoconutSyntaxError):
    """Coconut --target error."""
    def __init__(self, message, source=None, point=None, lineno=None):
        """Creates the --target Coconut error."""
        message, target = message
        message += " (enable --target "+target+" to dismiss)"
        CoconutSyntaxError.__init__(self, message, source, point, lineno)

class CoconutWarning(CoconutSyntaxError):
    """Base Coconut warning."""

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
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

class tracer(object):
    """Debug tracer."""

    def __init__(self, show=printerr, on=False):
        """Creates the tracer."""
        self.show = show
        self.debug(on)

    def debug(self, on=True):
        """Changes the tracer's state."""
        self.on = on

    def trace(self, tag, original, location, tokens):
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

    def bind(self, item, tag):
        """Traces a parse element."""
        def callback(original, location, tokens):
            """Callback function constructed by tracer."""
            if self.on:
                self.trace(tag, original, location, tokens)
            return tokens
        bound = attach(item, callback)
        bound.setName(tag)
        return bound

#-----------------------------------------------------------------------------------------------------------------------
# HEADER UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------

def gethash(compiled):
    """Retrieves a hash from a header."""
    lines = compiled.splitlines()
    if len(lines) < 3 or not lines[2].startswith(hash_prefix):
        return None
    else:
        return lines[2][len(hash_prefix):]

def minify(compiled):
    """Performs basic minifications (fails with strings or non-tabideal indentation)."""
    compiled = compiled.strip()
    if compiled:
        out = []
        for line in compiled.splitlines():
            line = line.split("#", 1)[0].rstrip()
            if line:
                ind = 0
                while line.startswith(" "):
                    line = line[1:]
                    ind += 1
                if ind % tabideal != 0:
                    raise CoconutException("invalid indentation in", line)
                out.append(" "*(ind//tabideal) + line)
        compiled = "\n".join(out) + "\n"
    return compiled

def getheader(which, target="", usehash=None):
    """Generates the specified header."""
    if which == "none":
        return ""
    elif which == "initial" or which == "package":
        if target.startswith("2"):
            header = "#!/usr/bin/env python2"
        elif target.startswith("3"):
            header = "#!/usr/bin/env python3"
        else:
            header = "#!/usr/bin/env python"
        header += '''
# -*- coding: '''+default_encoding+''' -*-
'''
        if usehash is not None:
            header += hash_prefix + usehash + "\n"
        header += '''
# Compiled with Coconut version '''+VERSION_STR+'''

'''
        if which == "package":
            header += r'''"""Built-in Coconut utilities."""

'''
    elif usehash is not None:
        raise CoconutException("can only add a hash to an initial or package header, not "+str(which))
    else:
        header = ""
    if which != "initial":
        header += r'''# Coconut Header: --------------------------------------------------------------

'''
        if not target.startswith("3"):
            header += r'''from __future__ import print_function, absolute_import, unicode_literals, division
'''
        elif target_info(target) >= (3, 5):
            header += r'''from __future__ import generator_stop
'''
        if which == "module":
            header += r'''import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
import __coconut__
_coconut_sys.path.remove(_coconut_file_path)
for name in dir(__coconut__):
    if not name.startswith("__"):
        globals()[name] = getattr(__coconut__, name)
'''
        elif which == "package" or which == "code" or which == "file":
            if target.startswith("3"):
                header += PY3_HEADER
            elif target_info(target) >= (2, 7):
                header += PY27_HEADER
            elif target.startswith("2"):
                header += PY2_HEADER
            else:
                header += PYCHECK_HEADER
            if target.startswith("3"):
                header += r'''
class _coconut:'''
            else:
                header += r'''
class _coconut(object):'''
            header += r'''
    import collections, functools, imp, itertools, operator, types, copy
'''
            if target.startswith("2"):
                header += r'''    abc = collections'''
            else:
                header += r'''    if _coconut_sys.version_info < (3, 3):
        abc = collections
    else:
        import collections.abc as abc'''
            if target.startswith("3"):
                header += r'''
    IndexError, NameError, ValueError, map, zip, bytearray, dict, frozenset, getattr, hasattr, isinstance, iter, len, list, min, next, object, range, reversed, set, slice, super, tuple, repr = IndexError, NameError, ValueError, map, zip, bytearray, dict, frozenset, getattr, hasattr, isinstance, iter, len, list, min, next, object, range, reversed, set, slice, super, tuple, repr
'''
            else:
                header += r'''
    IndexError, NameError, ValueError, map, zip, bytearray, dict, frozenset, getattr, hasattr, isinstance, iter, len, list, min, next, object, range, reversed, set, slice, super, tuple, repr = IndexError, NameError, ValueError, map, zip, bytearray, dict, frozenset, getattr, hasattr, isinstance, iter, len, list, min, next, object, range, reversed, set, slice, super, tuple, staticmethod(repr)
'''
            header += r'''
class _coconut_MatchError(Exception):
    """Pattern-matching error."""
    __slots__ = ("pattern", "value")
def _coconut_igetitem(iterable, index):
    if isinstance(iterable, _coconut.range) or (_coconut.hasattr(iterable, "__coconut_is_lazy__") and iterable.__coconut_is_lazy__):
        return iterable[index]
    elif _coconut.hasattr(iterable, "__getitem__"):
        if _coconut.isinstance(index, _coconut.slice):
            return (x for x in iterable[index])
        else:
            return iterable[index]
    elif _coconut.isinstance(index, _coconut.slice):
        if (index.start is not None and index.start < 0) or (index.stop is not None and index.stop < 0) or (index.step is not None and index.step < 0):
            return (x for x in _coconut.tuple(iterable)[index])
        else:
            return _coconut.itertools.islice(iterable, index.start, index.stop, index.step)
    elif index < 0:
        return _coconut.collections.deque(iterable, maxlen=-index)[0]
    else:
        return _coconut.next(_coconut.itertools.islice(iterable, index, index + 1))'''
            if target.startswith("3"):
                header += r'''
class _coconut_compose:'''
            else:
                header += r'''
class _coconut_compose(object):'''
            header += r'''
    __slots__ = ("f", "g")
    def __init__(self, f, g):
        self.f, self.g = f, g
    def __call__(self, *args, **kwargs):
        return self.f(self.g(*args, **kwargs))
    def __repr__(self):
        return _coconut.repr(self.f) + ".." + _coconut.repr(self.g)
    def __reduce__(self):
        return (_coconut_compose, (self.f, self.g))
def _coconut_pipe(x, f): return f(x)
def _coconut_starpipe(xs, f): return f(*xs)
def _coconut_backpipe(f, x): return f(x)
def _coconut_backstarpipe(f, xs): return f(*xs)
def _coconut_bool_and(a, b): return a and b
def _coconut_bool_or(a, b): return a or b
def _coconut_minus(*args): return _coconut.operator.__neg__(*args) if len(args) < 2 else _coconut.operator.__sub__(*args)
@_coconut.functools.wraps(_coconut.itertools.tee)
def _coconut_tee(iterable, n=2):
    if _coconut.isinstance(iterable, _coconut.range) or hasattr(iterable, "__copy__"):
        return (iterable,) + _coconut.tuple(_coconut.copy.copy(iterable) for i in range(n - 1))
    else:
        return _coconut.itertools.tee(iterable, n)
class _coconut_map(_coconut.map):
    __slots__ = ("_func", "_iters")
    __doc__ = _coconut.map.__doc__
    __coconut_is_lazy__ = True # tells $[] to use .__getitem__
    def __new__(cls, function, *iterables):
        new_map = _coconut.map.__new__(cls, function, *iterables)
        new_map._func, new_map._iters = function, iterables
        return new_map
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(self._func, *(_coconut_igetitem(i, index) for i in self._iters))
        else:
            return self._func(*(_coconut_igetitem(i, index) for i in self._iters))
    def __reversed__(self):
        return self.__class__(self._func, *(_coconut.reversed(i) for i in self._iters))
    def __len__(self):
        return _coconut.min(_coconut.len(i) for i in self._iters)
    def __repr__(self):
        return "map(" + _coconut.repr(self._func) + ", " + ", ".join((_coconut.repr(i) for i in self._iters)) + ")"
    def __reduce_ex__(self, _):
        return (self.__class__, (self._func,) + self._iters)
    def __copy__(self):
        return self.__class__(self._func, *_coconut_map(_coconut.copy.copy, self._iters))
class zip(_coconut.zip):
    __slots__ = ("_iters",)
    __doc__ = _coconut.zip.__doc__
    __coconut_is_lazy__ = True # tells $[] to use .__getitem__
    def __new__(cls, *iterables):
        new_zip = _coconut.zip.__new__(cls, *iterables)
        new_zip._iters = iterables
        return new_zip
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(*(_coconut_igetitem(i, index) for i in self._iters))
        else:
            return (_coconut_igetitem(i, index) for i in self._iters)
    def __reversed__(self):
        return self.__class__(*(_coconut.reversed(i) for i in self._iters))
    def __len__(self):
        return _coconut.min(_coconut.len(i) for i in self._iters)
    def __repr__(self):
        return "zip(" + ", ".join((_coconut.repr(i) for i in self._iters)) + ")"
    def __reduce_ex__(self, _):
        return (self.__class__, self._iters)
    def __copy__(self):
        return self.__class__(*_coconut_map(_coconut.copy.copy, self._iters))'''
            if target.startswith("3"):
                header += r'''
class count:'''
            else:
                header += r'''
class count(object):'''
            header += r'''
    """count(start, step) returns an infinite iterator starting at start and increasing by step."""
    __slots__ = ("_start", "_step")
    __coconut_is_lazy__ = True # tells $[] to use .__getitem__
    def __init__(self, start=0, step=1):
        self._start, self._step = start, step
    def __iter__(self):
        while True:
            yield self._start
            self._start += self._step
    def __contains__(self, elem):
        return elem >= self._start and (elem - self._start) % self._step == 0
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice) and (index.start is None or index.start >= 0) and (index.stop is not None and index.stop >= 0):
            return _coconut_map(lambda x: self._start + x * self._step, _coconut.range(index.start if index.start is not None else 0, index.stop, index.step if index.step is not None else 1))
        elif index >= 0:
            return self._start + index * self._step
        else:
            raise _coconut.IndexError("count indices must be positive")
    def count(self, elem):
        """Count the number of times elem appears in the count."""
        return int(elem in self)
    def index(self, elem):
        """Find the index of elem in the count."""
        if elem not in self: raise _coconut.ValueError(_coconut.repr(elem) + " is not in count")
        return (elem - self._start) // self._step
    def __repr__(self):
        return "count(" + str(self._start) + ", " + str(self._step) + ")"
    def __reduce__(self):
        return (self.__class__, (self._start, self._step))
    def __copy__(self):
        return self.__class__(self._start, self._step)
class parallel_map(_coconut_map):
    """Multiprocessing implementation of map using concurrent.futures; requires arguments to be pickleable."""
    __slots__ = ()
    def __iter__(self):
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor() as executor:
            for x in executor.map(self._func, *self._iters):
                yield x
    def __repr__(self):
        return "parallel_" + _coconut_map.__repr__(self)
class concurrent_map(_coconut_map):
    """Multithreading implementation of map using concurrent.futures."""
    __slots__ = ()
    def __iter__(self):
        from concurrent.futures import ThreadPoolExecutor'''
            if target_info(target) >= (3, 5):
                header += r'''
        with ThreadPoolExecutor() as executor:'''
            else:
                header += r'''
        from multiprocessing import cpu_count
        with ThreadPoolExecutor(cpu_count() * 5) as executor:'''
            header += r'''
            for x in executor.map(self._func, *self._iters):
                yield x
    def __repr__(self):
        return "concurrent_" + _coconut_map.__repr__(self)
def recursive(func):
    """Decorates a function by optimizing it for tail recursion."""
    state = [True, None] # state = [is_top_level, (args, kwargs)]
    recurse = object()
    @_coconut.functools.wraps(func)
    def recursive_func(*args, **kwargs):
        """Tail Recursion Wrapper."""
        if state[0]:
            state[0] = False
            try:
                while True:
                    result = func(*args, **kwargs)
                    if result is recurse:
                        args, kwargs = state[1]
                        state[1] = None
                    else:
                        return result
            finally:
                state[0] = True
        else:
            state[1] = args, kwargs
            return recurse
    return recursive_func
def recursive_iterator(func):
    """Decorates a function by optimizing it for iterator recursion."""
    tee_store = {}
    @_coconut.functools.wraps(func)
    def recursive_iterator_func(*args, **kwargs):
        hashable_args_kwargs = args, _coconut.frozenset(kwargs.items())
        if hashable_args_kwargs in tee_store:
            to_tee = tee_store[hashable_args_kwargs]
        else:
            to_tee = func(*args, **kwargs)
        tee_store[hashable_args_kwargs], to_return = _coconut_tee(to_tee)
        return to_return
    return recursive_iterator_func
def addpattern(base_func):
    """Decorator to add a new case to a pattern-matching function, where the new case is checked last."""
    def pattern_adder(func):
        @_coconut.functools.wraps(func)
        def add_pattern_func(*args, **kwargs):
            try:
                return base_func(*args, **kwargs)
            except _coconut_MatchError:
                return func(*args, **kwargs)
        return add_pattern_func
    return pattern_adder
def prepattern(base_func):
    """Decorator to add a new case to a pattern-matching function, where the new case is checked first."""
    def pattern_prepender(func):
        @_coconut.functools.wraps(func)
        def pre_pattern_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except _coconut_MatchError:
                return base_func(*args, **kwargs)
        return pre_pattern_func
    return pattern_prepender
def datamaker(data_type):
    """Returns base data constructor of passed data type."""
    return _coconut.functools.partial(_coconut.super(data_type, data_type).__new__, data_type)
def consume(iterable, keep_last=0):
    """Fully exhaust iterable and return the last keep_last elements."""
    return _coconut.collections.deque(iterable, maxlen=keep_last) # fastest way to exhaust an iterator
MatchError, map, reduce, takewhile, dropwhile, tee = _coconut_MatchError, _coconut_map, _coconut.functools.reduce, _coconut.itertools.takewhile, _coconut.itertools.dropwhile, _coconut_tee
'''
        else:
            raise CoconutException("invalid header type", which)
        if which == "file" or which == "module":
            header += r'''
# Compiled Coconut: ------------------------------------------------------------

'''
    return header

#-----------------------------------------------------------------------------------------------------------------------
# HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------

def list_handle(tokens):
    """Properly formats lists."""
    out = []
    for x in range(0, len(tokens)-1, 2):
        out.append(tokens[x] + tokens[x+1])
    if len(tokens) % 2 == 1:
        out.append(tokens[-1])
    return " ".join(out)

def tokenlist(item, sep, suppress=True):
    """Creates a list of tokens matching the item."""
    if suppress:
        sep = sep.suppress()
    return item + ZeroOrMore(sep + item) + Optional(sep)

def itemlist(item, sep):
    """Creates a list of an item."""
    return attach(tokenlist(item, sep, suppress=False), list_handle)

def add_paren_handle(tokens):
    """Adds parentheses."""
    if len(tokens) == 1:
        return "(" + tokens[0] + ")"
    else:
        raise CoconutException("invalid tokens for parentheses adding", tokens)

def attr_handle(tokens):
    """Processes attrgetter literals."""
    if len(tokens) == 1:
        return '_coconut.operator.attrgetter("'+tokens[0]+'")'
    elif len(tokens) == 2:
        return '_coconut.operator.methodcaller("'+tokens[0]+'", '+tokens[1]+")"
    else:
        raise CoconutException("invalid attrgetter literal tokens", tokens)

def lazy_list_handle(tokens):
    """Processes lazy lists."""
    if len(tokens) == 0:
        return "_coconut.iter(())"
    else:
        return ("(" + lazy_item_var + "() for " + lazy_item_var + " in ("
            + "lambda: " + ", lambda: ".join(tokens) + ("," if len(tokens) == 1 else "") + "))")

def chain_handle(tokens):
    """Processes chain calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "_coconut.itertools.chain.from_iterable(" + lazy_list_handle(tokens) + ")"

def infix_error(tokens):
    """Raises inner infix error."""
    raise CoconutException("invalid inner infix tokens", tokens)

def infix_handle(tokens):
    """Processes infix calls."""
    func, args = get_infix_items(tokens, infix_handle)
    return "(" + func + ")(" + ", ".join(args) + ")"

def get_infix_items(tokens, callback=infix_error):
    """Performs infix token processing."""
    if len(tokens) < 3:
        raise CoconutException("invalid infix tokens", tokens)
    else:
        items = []
        for item in tokens[0]:
            items.append(item)
        for item in tokens[2]:
            items.append(item)
        if len(tokens) > 3:
            items.append(callback([[]]+tokens[3:]))
        args = []
        for arg in items:
            if arg:
                args.append(arg)
        return tokens[1], args

def op_funcdef_handle(tokens):
    """Processes infix defs."""
    func, args = get_infix_items(tokens)
    return func + "(" + ", ".join(args) + ")"

def pipe_handle(tokens):
    """Processes pipe calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        func = tokens.pop()
        op = tokens.pop()
        if op == "|>":
            return "(" + func + ")(" + pipe_handle(tokens) + ")"
        elif op == "|*>":
            return "(" + func + ")(*" + pipe_handle(tokens) + ")"
        elif op == "<|":
            return "(" + pipe_handle(tokens) + ")(" + func + ")"
        elif op == "<*|":
            return "(" + pipe_handle(tokens) + ")(*" + func + ")"
        else:
            raise CoconutException("invalid pipe operator", op)

def lambdef_handle(tokens):
    """Processes lambda calls."""
    if len(tokens) == 0:
        return "lambda:"
    elif len(tokens) == 1:
        return "lambda " + tokens[0] + ":"
    else:
        raise CoconutException("invalid lambda tokens", tokens)

def func_handle(tokens):
    """Processes mathematical function definitons."""
    if len(tokens) == 2:
        return "def " + tokens[0] + ": return " + tokens[1]
    else:
        raise CoconutException("invalid mathematical function definition tokens", tokens)

def match_func_handle(tokens):
    """Processes match mathematical function definitions."""
    if len(tokens) == 2:
        return tokens[0] + "return " + tokens[1] + "\n" + closeindent
    else:
        raise CoconutException("invalid pattern-matching mathematical function definition tokens", tokens)

def full_match_funcdef_handle(tokens):
    """Processes full match function definition."""
    if len(tokens) == 2:
        return tokens[0] + "".join(tokens[1]) + closeindent
    else:
        raise CoconutException("invalid pattern-matching function definition tokens", tokens)

def data_handle(tokens):
    """Processes data blocks."""
    if len(tokens) == 2:
        name, stmts = tokens
        attrs = ""
    elif len(tokens) == 3:
        name, attrs, stmts = tokens
    else:
        raise CoconutException("invalid data tokens", tokens)
    out = "class " + name + '(_coconut.collections.namedtuple("' + name + '", "' + attrs + '")):\n' + openindent
    rest = None
    if "simple" in stmts.keys() and len(stmts) == 1:
        out += "__slots__ = ()\n"
        rest = stmts[0]
    elif "docstring" in stmts.keys() and len(stmts) == 1:
        out += stmts[0] + "__slots__ = ()\n"
    elif "complex" in stmts.keys() and len(stmts) == 1:
        out += "__slots__ = ()\n"
        rest = "".join(stmts[0])
    elif "complex" in stmts.keys() and len(stmts) == 2:
        out += stmts[0] + "__slots__ = ()\n"
        rest = "".join(stmts[1])
    else:
        raise CoconutException("invalid inner data tokens", stmts)
    if rest is not None and rest != "pass\n":
        out += rest
    out += closeindent
    return out

def decorator_handle(tokens):
    """Processes decorators."""
    defs = []
    decorates = []
    for x in range(0, len(tokens)):
        if "simple" in tokens[x].keys() and len(tokens[x]) == 1:
            decorates.append("@"+tokens[x][0])
        elif "test" in tokens[x].keys() and len(tokens[x]) == 1:
            varname = decorator_var + "_" + str(x)
            defs.append(varname+" = "+tokens[x][0])
            decorates.append("@"+varname)
        else:
            raise CoconutException("invalid decorator tokens", tokens[x])
    return "\n".join(defs + decorates) + "\n"

def else_handle(tokens):
    """Processes compound else statements."""
    if len(tokens) == 1:
        return "\n" + openindent + tokens[0] + closeindent
    else:
        raise CoconutException("invalid compound else statement tokens", tokens)

class matcher(object):
    """Pattern-matching processor."""
    __slots__ = (
        "position",
        "iter_index",
        "checkdefs",
        "checks",
        "defs",
        "names",
        "others"
        )

    def __init__(self, checkdefs=None, names=None):
        """Creates the matcher."""
        self.position = 0
        self.iter_index = 0
        self.checkdefs = []
        if checkdefs is None:
            self.increment()
        else:
            for checks, defs in checkdefs:
                self.checkdefs.append([checks[:], defs[:]])
            self.checks = self.get_checks(-1)
            self.defs = self.get_defs(-1)
        if names is None:
            self.names = {}
        else:
            self.names = dict(names)
        self.others = []

    def duplicate(self):
        """Duplicates the matcher to others."""
        self.others.append(matcher(self.checkdefs, self.names))
        self.others[-1].set_checks(0, ["not "+match_check_var] + self.others[-1].get_checks(0))
        return self.others[-1]

    def get_checks(self, position):
        """Gets the checks at the position."""
        return self.checkdefs[position][0]

    def set_checks(self, position, checks):
        """Sets the checks at the position."""
        self.checkdefs[position][0] = checks

    def set_defs(self, position, defs):
        """Sets the defs at the position."""
        self.checkdefs[position][1] = defs

    def get_defs(self, position):
        """Gets the defs at the position."""
        return self.checkdefs[position][1]

    def add_check(self, check_item):
        """Adds a check universally."""
        self.checks.append(check_item)
        for other in self.others:
            other.add_check(check_item)

    def add_def(self, def_item):
        """Adds a def universally."""
        self.defs.append(def_item)
        for other in self.others:
            other.add_def(def_item)

    def set_position(self, position):
        """Sets the if-statement position."""
        if position > 0:
            while position >= len(self.checkdefs):
                self.checkdefs.append([[], []])
            self.checks = self.checkdefs[position][0]
            self.defs = self.checkdefs[position][1]
            self.position = position
        else:
            raise CoconutException("invalid match index: "+str(position))

    def increment(self, forall=False):
        """Advances the if-statement position."""
        self.set_position(self.position+1)
        if forall:
            for other in self.others:
                other.increment(True)

    def decrement(self, forall=False):
        """Decrements the if-statement position."""
        self.set_position(self.position-1)
        if forall:
            for other in self.others:
                other.decrement(True)

    def add_guard(self, cond):
        """Adds cond as a guard."""
        self.increment(True)
        self.add_check(cond)

    def match_dict(self, original, item):
        """Matches a dictionary."""
        if len(original) == 1:
            match = original[0]
        else:
            raise CoconutException("invalid dict match tokens", original)
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Mapping)")
        self.checks.append("_coconut.len("+item+") == "+str(len(match)))
        for x in range(0, len(match)):
            k,v = match[x]
            self.checks.append(k+" in "+item)
            self.match(v, item+"["+k+"]")

    def match_sequence(self, original, item):
        """Matches a sequence."""
        tail = None
        if len(original) == 2:
            series_type, match = original
        else:
            series_type, match, tail = original
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Sequence)")
        if tail is None:
            self.checks.append("_coconut.len("+item+") == "+str(len(match)))
        else:
            self.checks.append("_coconut.len("+item+") >= "+str(len(match)))
            if len(match):
                splice = "["+str(len(match))+":]"
            else:
                splice = ""
            if series_type == "(":
                self.defs.append(tail+" = _coconut.tuple("+item+splice+")")
            elif series_type == "[":
                self.defs.append(tail+" = _coconut.list("+item+splice+")")
            else:
                raise CoconutException("invalid series match type", series_type)
        for x in range(0, len(match)):
            self.match(match[x], item+"["+str(x)+"]")

    def match_iterator(self, original, item):
        """Matches an iterator."""
        tail = None
        if len(original) == 2:
            _, match = original
        else:
            _, match, tail = original
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Iterable)")
        itervar = match_iter_var + "_" + str(self.iter_index)
        self.iter_index += 1
        if tail is None:
            self.defs.append(itervar+" = _coconut.tuple("+item+")")
        else:
            self.defs.append(tail+" = _coconut.iter("+item+")")
            self.defs.append(itervar+" = _coconut.tuple(_coconut_igetitem("+tail+", _coconut.slice(None, "+str(len(match))+")))")
        self.increment()
        self.checks.append("_coconut.len("+itervar+") == "+str(len(match)))
        for x in range(0, len(match)):
            self.match(match[x], itervar+"["+str(x)+"]")
        self.decrement()

    def match_rsequence(self, original, item):
        """Matches a reverse sequence."""
        front, series_type, match = original
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Sequence)")
        self.checks.append("_coconut.len("+item+") >= "+str(len(match)))
        if len(match):
            splice = "[:"+str(-len(match))+"]"
        else:
            splice = ""
        if series_type == "(":
            self.defs.append(front+" = _coconut.tuple("+item+splice+")")
        elif series_type == "[":
            self.defs.append(front+" = _coconut.list("+item+splice+")")
        else:
            raise CoconutException("invalid series match type", series_type)
        for x in range(0, len(match)):
            self.match(match[x], item+"["+str(x-len(match))+"]")

    def match_msequence(self, original, item):
        """Matches a middle sequence."""
        series_type, head_match, middle, _, last_match = original
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Sequence)")
        self.checks.append("_coconut.len("+item+") >= "+str(len(head_match) + len(last_match)))
        if len(head_match) and len(last_match):
            splice = "["+str(len(head_match))+":"+str(-len(last_match))+"]"
        elif len(head_match):
            splice = "["+str(len(head_match))+":]"
        elif len(last_match):
            splice = "[:"+str(-len(last_match))+"]"
        else:
            splice = ""
        if series_type == "(":
            self.defs.append(middle+" = _coconut.tuple("+item+splice+")")
        elif series_type == "[":
            self.defs.append(middle+" = _coconut.list("+item+splice+")")
        else:
            raise CoconutException("invalid series match type", series_type)
        for x in range(0, len(head_match)):
            self.match(head_match[x], item+"["+str(x)+"]")
        for x in range(0, len(last_match)):
            self.match(last_match[x], item+"["+str(x-len(last_match))+"]")

    def match_const(self, original, item):
        """Matches a constant."""
        (match,) = original
        if match in const_vars:
            self.checks.append(item+" is "+match)
        else:
            self.checks.append(item+" == "+match)

    def match_var(self, original, item):
        """Matches a variable."""
        (setvar,) = original
        if setvar != wildcard:
            if setvar in self.names:
                self.checks.append(self.names[setvar]+" == "+item)
            else:
                self.defs.append(setvar+" = "+item)
                self.names[setvar] = item

    def match_set(self, original, item):
        """Matches a set."""
        if len(original) == 1:
            match = original[0]
        else:
            raise CoconutException("invalid set match tokens", original)
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Set)")
        self.checks.append("_coconut.len("+item+") == "+str(len(match)))
        for const in match:
            self.checks.append(const+" in "+item)

    def match_data(self, original, item):
        """Matches a data type."""
        data_type, match = original
        self.checks.append("_coconut.isinstance("+item+", "+data_type+")")
        self.checks.append("_coconut.len("+item+") == "+str(len(match)))
        for x in range(0, len(match)):
            self.match(match[x], item+"["+str(x)+"]")

    def match_paren(self, original, item):
        """Matches a paren."""
        (match,) = original
        self.match(match, item)

    def match_trailer(self, original, item):
        """Matches typedefs and as patterns."""
        if len(original) <= 1 or len(original) % 2 != 1:
            raise CoconutException("invalid trailer match tokens", original)
        else:
            match, trailers = original[0], original[1:]
            for i in range(0, len(trailers), 2):
                op, arg = trailers[i], trailers[i+1]
                if op == "is":
                    self.checks.append("_coconut.isinstance("+item+", "+arg+")")
                elif op == "as":
                    if arg in self.names:
                        self.checks.append(self.names[arg]+" == "+item)
                    elif arg != wildcard:
                        self.defs.append(arg+" = "+item)
                        self.names[arg] = item
                else:
                    raise CoconutException("invalid trailer match operation", op)
            self.match(match, item)

    def match_and(self, original, item):
        """Matches and."""
        for match in original:
            self.match(match, item)

    def match_or(self, original, item):
        """Matches or."""
        for x in range(1, len(original)):
            self.duplicate().match(original[x], item)
        self.match(original[0], item)

    matchers = {
        "dict": lambda self: self.match_dict,
        "iter": lambda self: self.match_iterator,
        "series": lambda self: self.match_sequence,
        "rseries": lambda self: self.match_rsequence,
        "mseries": lambda self: self.match_msequence,
        "const": lambda self: self.match_const,
        "var": lambda self: self.match_var,
        "set": lambda self: self.match_set,
        "data": lambda self: self.match_data,
        "paren": lambda self: self.match_paren,
        "trailer": lambda self: self.match_trailer,
        "and": lambda self: self.match_and,
        "or": lambda self: self.match_or
    }
    def match(self, original, item):
        """Performs pattern-matching processing."""
        for flag, handler in self.matchers.items():
            if flag in original.keys():
                return handler(self)(original, item)
        raise CoconutException("invalid inner match tokens", original)

    def out(self):
        out = ""
        closes = 0
        for checks, defs in self.checkdefs:
            if checks:
                out += "if (" + ") and (".join(checks) + "):\n" + openindent
                closes += 1
            if defs:
                out += "\n".join(defs) + "\n"
        out += match_check_var + " = True\n"
        out += closeindent * closes
        for other in self.others:
            out += other.out()
        return out

def match_handle(o, l, tokens, top=True):
    """Processes match blocks."""
    if len(tokens) == 3:
        matches, item, stmts = tokens
        cond = None
    elif len(tokens) == 4:
        matches, item, cond, stmts = tokens
    else:
        raise CoconutException("invalid outer match tokens", tokens)
    matching = matcher()
    matching.match(matches, match_to_var)
    if cond:
        matching.add_guard(cond)
    out = ""
    if top:
        out += match_check_var + " = False\n"
    out += match_to_var + " = " + item + "\n"
    out += matching.out()
    if stmts is not None:
        out += "if "+match_check_var+":" + "\n" + openindent + "".join(stmts) + closeindent
    return out

def case_to_match(tokens, item):
    """Converts case tokens to match tokens."""
    if len(tokens) == 2:
        matches, stmts = tokens
        return matches, item, stmts
    elif len(tokens) == 3:
        matches, cond, stmts = tokens
        return matches, item, cond, stmts
    else:
        raise CoconutException("invalid case match tokens", tokens)

def case_handle(o, l, tokens):
    """Processes case blocks."""
    if len(tokens) == 2:
        item, cases = tokens
        default = None
    elif len(tokens) == 3:
        item, cases, default = tokens
    else:
        raise CoconutException("invalid top-level case tokens", tokens)
    out = match_handle(o, l, case_to_match(cases[0], item))
    for case in cases[1:]:
        out += ("if not "+match_check_var+":\n" + openindent
            + match_handle(o, l, case_to_match(case, item), top=False) + closeindent)
    if default is not None:
        out += "if not "+match_check_var+default
    return out

def except_handle(tokens):
    """Processes except statements."""
    if len(tokens) == 1:
        errs, asname = tokens[0], None
    elif len(tokens) == 2:
        errs, asname = tokens
    else:
        raise CoconutException("invalid except tokens", tokens)
    out = "except "
    if "list" in tokens.keys():
        out += "(" + errs + ")"
    else:
        out += errs
    if asname is not None:
        out += " as " + asname
    return out

def set_to_tuple(tokens):
    """Converts set literal tokens to tuples."""
    if len(tokens) != 1:
        raise CoconutException("invalid set maker tokens", tokens)
    elif "comp" in tokens.keys() or "list" in tokens.keys():
        return "(" + tokens[0] + ")"
    elif "test" in tokens.keys():
        return "(" + tokens[0] + ",)"
    else:
        raise CoconutException("invalid set maker item", tokens[0])

def gen_imports(path, impas):
    """Generates import statements."""
    out = []
    parts = path.split("./") # denotes from ... import ...
    if len(parts) == 1:
        imp, = parts
        if impas == imp:
            out.append("import " + imp)
        elif "." not in impas:
            out.append("import " + imp + " as " + impas)
        else:
            fake_mods = impas.split(".")
            out.append("import " + imp + " as " + import_as_var)
            for i in range(1, len(fake_mods)):
                mod_name = ".".join(fake_mods[:i])
                out.append("try:")
                out.append(openindent + mod_name)
                out.append(closeindent + "except:")
                out.append(openindent + mod_name + ' = _coconut.imp.new_module("' + mod_name + '")')
                out.append(closeindent + "else:")
                out.append(openindent + "if not _coconut.isinstance(" + mod_name + ", _coconut.types.ModuleType):")
                out.append(openindent + mod_name + ' = _coconut.imp.new_module("' + mod_name + '")' + closeindent * 2)
            out.append(".".join(fake_mods) + " = " + import_as_var)
    else:
        imp_from, imp = parts
        if impas == imp:
            out.append("from " + imp_from + " import " + imp)
        else:
            out.append("from " + imp_from + " import " + imp + " as " + impas)
    return out

#-----------------------------------------------------------------------------------------------------------------------
# PARSER:
#-----------------------------------------------------------------------------------------------------------------------

class processor(object):
    """The Coconut processor."""
    tracing = tracer()
    trace = tracing.bind
    debug = tracing.debug
    using_autopep8 = False

    def __init__(self, target=None, strict=False, minify=False, linenumbers=False, debugger=printerr):
        """Creates a new processor."""
        self.debugger = debugger
        self.setup(target, strict, minify, linenumbers)
        self.preprocs = [self.prepare, self.str_proc, self.passthrough_proc, self.ind_proc]
        self.postprocs = [self.reind_proc, self.repl_proc, self.header_proc, self.polish]
        self.replprocs = [self.linenumber_repl, self.passthrough_repl, self.str_repl]
        self.reset()

    def setup(self, target=None, strict=False, minify=False, linenumbers=False):
        """Initializes target, strict, and minify."""
        if target is None:
            target = ""
        else:
            target = str(target).replace(".", "")
        if target in pseudo_targets:
            target = pseudo_targets[target]
        if target not in targets:
            raise CoconutException('unsupported target Python version "' + target
                + '" (supported targets are "' + '", "'.join(specific_targets) + '", or leave blank for universal)')
        self.target, self.strict, self.minify, self.linenumbers = target, strict, minify, linenumbers
        self.tablen = 1 if self.minify else tabideal

    def bind(self):
        """Binds reference objects to the proper parse actions."""
        self.endline <<= attach(self.endline_ref, self.endline_handle, copy=True)
        self.moduledoc_item <<= attach(self.moduledoc, self.set_docstring, copy=True)
        self.name <<= self.trace(attach(self.name_ref, self.name_handle, copy=True), "name")
        self.atom_item <<= self.trace(attach(self.atom_item_ref, self.item_handle, copy=True), "atom_item")
        self.simple_assign <<= self.trace(attach(self.simple_assign_ref, self.item_handle, copy=True), "simple_assign")
        self.set_literal <<= self.trace(attach(self.set_literal_ref, self.set_literal_handle, copy=True), "set_literal")
        self.set_letter_literal <<= self.trace(attach(self.set_letter_literal_ref, self.set_letter_literal_handle, copy=True), "set_letter_literal")
        self.classlist <<= self.trace(attach(self.classlist_ref, self.classlist_handle, copy=True), "classlist")
        self.import_stmt <<= self.trace(attach(self.import_stmt_ref, self.import_handle, copy=True), "import_stmt")
        self.complex_raise_stmt <<= self.trace(attach(self.complex_raise_stmt_ref, self.complex_raise_stmt_handle, copy=True), "complex_raise_stmt")
        self.augassign_stmt <<= self.trace(attach(self.augassign_stmt_ref, self.augassign_handle, copy=True), "augassign_stmt")
        self.dict_comp <<= self.trace(attach(self.dict_comp_ref, self.dict_comp_handle, copy=True), "dict_comp")
        self.destructuring_stmt <<= self.trace(attach(self.destructuring_stmt_ref, self.destructuring_stmt_handle, copy=True), "destructuring_stmt")
        self.name_match_funcdef <<= self.trace(attach(self.name_match_funcdef_ref, self.name_match_funcdef_handle, copy=True), "name_match_funcdef")
        self.op_match_funcdef <<= self.trace(attach(self.op_match_funcdef_ref, self.op_match_funcdef_handle, copy=True), "op_match_funcdef")
        self.yield_from <<= self.trace(attach(self.yield_from_ref, self.yield_from_handle, copy=True), "yield_from")
        self.u_string <<= attach(self.u_string_ref, self.u_string_check, copy=True)
        self.f_string <<= attach(self.f_string_ref, self.f_string_check, copy=True)
        self.typedef <<= attach(self.typedef_ref, self.typedef_check, copy=True)
        self.return_typedef <<= attach(self.return_typedef_ref, self.typedef_check, copy=True)
        self.matrix_at <<= attach(self.matrix_at_ref, self.matrix_at_check, copy=True)
        self.nonlocal_stmt <<= attach(self.nonlocal_stmt_ref, self.nonlocal_check, copy=True)
        self.star_assign_item <<= attach(self.star_assign_item_ref, self.star_assign_item_check, copy=True)
        self.classic_lambdef <<= attach(self.classic_lambdef_ref, self.lambdef_check, copy=True)
        self.async_funcdef <<= attach(self.async_funcdef_ref, self.async_stmt_check, copy=True)
        self.async_match_funcdef <<= attach(self.async_match_funcdef_ref, self.async_stmt_check, copy=True)
        self.async_block <<= attach(self.async_block_ref, self.async_stmt_check, copy=True)
        self.await_keyword <<= attach(self.await_keyword_ref, self.await_keyword_check, copy=True)

    def reset(self):
        """Resets references."""
        self.tracing.show = self.debugger
        self.indchar = None
        self.refs = []
        self.docstring = ""
        self.ichain_count = 0
        self.skips = set()
        self.bind()

    def genhash(self, package, code):
        """Generates a hash from code."""
        return hex(checksum(
                hash_sep.join(str(item) for item in (
                    VERSION_STR,
                    self.target,
                    self.minify,
                    self.linenumbers,
                    self.using_autopep8,
                    package,
                    code
                )).encode(default_encoding)
            ) & 0xffffffff) # necessary for cross-compatibility

    def adjust(self, ln):
        """Adjusts a line number."""
        adj_ln = 0
        i = 0
        while i < ln:
            adj_ln += 1
            if adj_ln not in self.skips:
                i += 1
        return adj_ln

    def reformat(self, snip, index=None):
        """Post processes a preprocessed snippet."""
        if index is None:
            return self.repl_proc(snip, careful=False, linenumbers=False)
        else:
            return (self.repl_proc(snip, careful=False, linenumbers=False),
                    len(self.repl_proc(snip[:index], careful=False, linenumbers=False)))

    def make_err(self, errtype, message, original, location, ln=None, reformat=True):
        """Generates an error of the specified type."""
        if ln is None:
            ln = self.adjust(lineno(location, original))
        errstr, index = line(location, original), col(location, original)-1
        if reformat:
            errstr, index = self.reformat(errstr, index)
        return errtype(message, errstr, index, ln)

    def add_ref(self, ref):
        """Adds a reference and returns the identifier."""
        try:
            index = self.refs.index(ref)
        except ValueError:
            self.refs.append(ref)
            index = len(self.refs) - 1
        return str(index)

    def get_ref(self, index):
        """Retrieves a reference."""
        try:
            return self.refs[int(index)]
        except (IndexError, ValueError):
            raise CoconutException("invalid reference", index)

    def wrap_str(self, text, strchar, multiline=False):
        """Wraps a string."""
        return strwrapper + self.add_ref((text, strchar, multiline)) + unwrapper

    def wrap_str_of(self, text):
        """Wraps a string of a string."""
        text_repr = ascii(text).lstrip("u")
        return self.wrap_str(text_repr[1:-1], text_repr[-1])

    def wrap_passthrough(self, text, multiline=True):
        """Wraps a passthrough."""
        if not multiline:
            text = text.lstrip()
        if multiline:
            out = "\\"
        else:
            out = "\\\\"
        out += self.add_ref(text) + unwrapper
        if not multiline:
            out += "\n"
        return out

    def wrap_comment(self, text):
        """Wraps a comment."""
        return "#" + self.add_ref(text) + unwrapper

    def wrap_linenumber(self, ln):
        """Wraps a linenumber."""
        return "#" + self.add_ref(ln) + lnwrapper

    def indebug(self):
        """Checks whether debug mode is active."""
        return self.tracing.on

    def todebug(self, tag, code):
        """If debugging, prints a debug message."""
        if self.indebug():
            self.tracing.show("["+str(tag)+"] "+ascii(code))

    def warn(self, warning):
        """Displays a warning."""
        try:
            raise warning
        except CoconutWarning:
            self.tracing.show(get_error(self.indebug()))

    def pre(self, inputstring, **kwargs):
        """Performs pre-processing."""
        out = str(inputstring)
        for proc in self.preprocs:
            out = proc(out, **kwargs)
            self.todebug(proc.__name__, out)
        self.todebug("skips", list(sorted(self.skips)))
        return out

    def post(self, tokens, **kwargs):
        """Performs post-processing."""
        if len(tokens) == 1:
            out = tokens[0]
            for proc in self.postprocs:
                out = proc(out, **kwargs)
                self.todebug(proc.__name__, out)
            return out
        else:
            raise CoconutException("multiple tokens leftover", tokens)

    def headers(self, header, usehash=None):
        """Gets a polished header."""
        return self.polish(getheader(header, self.target, usehash))

    def target_info(self):
        """Returns information on the current target as a version tuple."""
        return target_info(self.target)

    def should_indent(self, code):
        """Determines whether the next line should be indented."""
        last = code.splitlines()[-1].split("#", 1)[0].rstrip()
        return last.endswith(":") or change(last) < 0

    def parse(self, inputstring, parser, preargs, postargs):
        """Uses the parser to parse the inputstring."""
        self.reset()
        try:
            out = self.post(parser.parseString(self.pre(inputstring, **preargs)), **postargs)
        except ParseBaseException as err:
            err_line, err_index = self.reformat(err.line, err.col-1)
            raise CoconutParseError(err_line, err_index, self.adjust(err.lineno))
        except RuntimeError:
            raise CoconutException("maximum recursion depth exceeded (try again with a larger --recursionlimit)")
        return out

#-----------------------------------------------------------------------------------------------------------------------
# PROCESSORS:
#-----------------------------------------------------------------------------------------------------------------------

    def prepare(self, inputstring, strip=False, **kwargs):
        """Prepares a string for processing."""
        if strip:
            inputstring = inputstring.strip()
        return "\n".join(inputstring.splitlines())

    def str_proc(self, inputstring, **kwargs):
        """Processes strings and comments."""
        out = []
        found = None # store of characters that might be the start of a string
        hold = None
        # hold = [_comment]:
        _comment = 0 # the contents of the comment so far
        # hold = [_contents, _start, _stop]:
        _contents = 0 # the contents of the string so far
        _start = 1 # the string of characters that started the string
        _stop = 2 # store of characters that might be the end of the string
        x = 0
        skips = self.skips.copy()
        while x <= len(inputstring):
            if x == len(inputstring):
                c = "\n"
            else:
                c = inputstring[x]
            if hold is not None:
                if len(hold) == 1: # hold == [_comment]
                    if c == "\n":
                        if self.minify:
                            if out:
                                lines = "".join(out).splitlines()
                                lines[-1] = lines[-1].rstrip()
                                out = ["\n".join(lines)]
                            out.append(c)
                        else:
                            out.append(self.wrap_comment(hold[_comment]) + c)
                        hold = None
                    else:
                        hold[_comment] += c
                elif hold[_stop] is not None:
                    if c == "\\":
                        hold[_contents] += hold[_stop] + c
                        hold[_stop] = None
                    elif c == hold[_start][0]:
                        hold[_stop] += c
                    elif len(hold[_stop]) > len(hold[_start]):
                        raise self.make_err(CoconutSyntaxError, "invalid number of string closes", inputstring, x, reformat=False)
                    elif hold[_stop] == hold[_start]:
                        out.append(self.wrap_str(hold[_contents], hold[_start][0], True))
                        hold = None
                        x -= 1
                    else:
                        if c == "\n":
                            if len(hold[_start]) == 1:
                                raise self.make_err(CoconutSyntaxError, "linebreak in non-multiline string", inputstring, x, reformat=False)
                            else:
                                skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                        hold[_contents] += hold[_stop]+c
                        hold[_stop] = None
                elif count_end(hold[_contents], "\\") % 2 == 1:
                    if c == "\n":
                        skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    hold[_contents] += c
                elif c == hold[_start]:
                    out.append(self.wrap_str(hold[_contents], hold[_start], False))
                    hold = None
                elif c == hold[_start][0]:
                    hold[_stop] = c
                else:
                    if c == "\n":
                        if len(hold[_start]) == 1:
                            raise self.make_err(CoconutSyntaxError, "linebreak in non-multiline string", inputstring, x, reformat=False)
                        else:
                            skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    hold[_contents] += c
            elif found is not None:
                if c == found[0]:
                    found += c
                elif len(found) == 1: # found == "_"
                    if c == "\n":
                        raise self.make_err(CoconutSyntaxError, "linebreak in non-multiline string", inputstring, x, reformat=False)
                    else:
                        hold = [c, found, None] # [_contents, _start, _stop]
                        found = None
                elif len(found) == 2: # found == "__"
                    out.append(self.wrap_str("", found[0], False))
                    found = None
                    x -= 1
                elif len(found) == 3: # found == "___"
                    if c == "\n":
                        skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    hold = [c, found, None] # [_contents, _start, _stop]
                    found = None
                else:
                    raise self.make_err(CoconutSyntaxError, "invalid number of string starts", inputstring, x, reformat=False)
            elif c == "#":
                hold = [""] # [_comment]
            elif c in holds:
                found = c
            else:
                out.append(c)
            x += 1
        if hold is not None or found is not None:
            raise self.make_err(CoconutSyntaxError, "unclosed string", inputstring, x, reformat=False)
        else:
            self.skips = skips
            return "".join(out)

    def passthrough_proc(self, inputstring, **kwargs):
        """Processes python passthroughs."""
        out = []
        found = None # store of characters that might be the start of a passthrough
        hold = None # the contents of the passthrough so far
        count = None # current parenthetical level
        multiline = None
        skips = self.skips.copy()
        for x in range(0, len(inputstring)):
            c = inputstring[x]
            if hold is not None:
                count += change(c)
                if count >= 0 and c == hold:
                    out.append(self.wrap_passthrough(found, multiline))
                    found = None
                    hold = None
                    count = None
                    multiline = None
                else:
                    if c == "\n":
                        skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    found += c
            elif found:
                if c == "\\":
                    found = ""
                    hold = "\n"
                    count = 0
                    multiline = False
                elif c == "(":
                    found = ""
                    hold = ")"
                    count = -1
                    multiline = True
                else:
                    out.append("\\" + c)
                    found = None
            elif c == "\\":
                found = True
            else:
                out.append(c)
        if hold is not None or found is not None:
            raise self.make_err(CoconutSyntaxError, "unclosed passthrough", inputstring, x)
        else:
            self.skips = skips
            return "".join(out)

    def leading(self, inputstring):
        """Counts leading whitespace."""
        count = 0
        for x in range(0, len(inputstring)):
            if inputstring[x] == " ":
                if self.indchar is None:
                    self.indchar = " "
                count += 1
            elif inputstring[x] == "\t":
                if self.indchar is None:
                    self.indchar = "\t"
                count += tabworth - x % tabworth
            else:
                break
            if self.indchar != inputstring[x]:
                if self.strict:
                    raise self.make_err(CoconutStyleError, "found mixing of tabs and spaces", inputstring, x)
                else:
                    self.warn(self.make_err(CoconutWarning, "found mixing of tabs and spaces", inputstring, x))
        return count

    def ind_proc(self, inputstring, **kwargs):
        """Processes indentation and fixes line/file endings."""
        lines = inputstring.splitlines()
        new = []
        levels = []
        count = 0
        current = None
        skips = self.skips.copy()
        for ln in range(0, len(lines)):
            line = lines[ln]
            ln += 1
            if line and line[-1] in white:
                if self.strict:
                    raise self.make_err(CoconutStyleError, "found trailing whitespace", line, len(line), self.adjust(ln))
                else:
                    line = line.rstrip()
            if new:
                last = new[-1].split("#", 1)[0].rstrip()
            else:
                last = None
            if not line or line.lstrip().startswith("#"):
                if count >= 0:
                    new.append(line)
                else:
                    skips = addskip(skips, self.adjust(ln))
            elif last is not None and last.endswith("\\"):
                if self.strict:
                    raise self.make_err(CoconutStyleError, "found backslash continuation", last, len(last), self.adjust(ln-1))
                else:
                    skips = addskip(skips, self.adjust(ln))
                    new[-1] = last[:-1]+" "+line
            elif count < 0:
                skips = addskip(skips, self.adjust(ln))
                new[-1] = last+" "+line
            else:
                check = self.leading(line)
                if current is None:
                    if check:
                        raise self.make_err(CoconutSyntaxError, "illegal initial indent", line, 0, self.adjust(ln))
                    else:
                        current = 0
                elif check > current:
                    levels.append(current)
                    current = check
                    line = openindent + line
                elif check in levels:
                    point = levels.index(check) + 1
                    line = closeindent*(len(levels[point:]) + 1) + line
                    levels = levels[:point]
                    current = levels.pop()
                elif current != check:
                    raise self.make_err(CoconutSyntaxError, "illegal dedent to unused indentation level", line, 0, self.adjust(ln))
                new.append(line)
            count += change(line)
        self.skips = skips
        if new:
            last = new[-1].split("#", 1)[0].rstrip()
            if last.endswith("\\"):
                raise self.make_err(CoconutSyntaxError, "illegal final backslash continuation", last, len(last), self.adjust(len(new)))
            if count != 0:
                raise self.make_err(CoconutSyntaxError, "unclosed parenthetical", new[-1], len(new[-1]), self.adjust(len(new)))
        new.append(closeindent*len(levels))
        return "\n".join(new)

    def reind_proc(self, inputstring, **kwargs):
        """Adds back indentation."""
        out = []
        level = 0
        for line in inputstring.splitlines():
            line = line.strip()
            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.rstrip()
                comment = "#" + comment
            else:
                comment = ""
            while line.startswith(openindent) or line.startswith(closeindent):
                if line[0] == openindent:
                    level += 1
                elif line[0] == closeindent:
                    level -= 1
                line = line[1:].lstrip()
            if line and not line.startswith("#"):
                line = " "*self.tablen*level + line
            while line.endswith(openindent) or line.endswith(closeindent):
                if line[-1] == openindent:
                    level += 1
                elif line[-1] == closeindent:
                    level -= 1
                line = line[:-1].rstrip()
            out.append(line + comment)
        return "\n".join(out)

    def linenumber_repl(self, inputstring, linenumbers=None, careful=True, **kwargs):
        """Adds in linenumbers."""
        if self.linenumbers:
            if linenumbers is None:
                linenumbers = True
            out = []
            ln = 1
            fix = False
            for line in inputstring.splitlines():
                try:
                    if line.endswith(lnwrapper):
                        line, index = line[:-1].rsplit("#", 1)
                        ln = self.get_ref(index)
                        if not isinstance(ln, int):
                            raise CoconutException("invalid reference for a linenumber", ln)
                        line = line.rstrip()
                        fix = True
                    elif fix:
                        ln += 1
                        fix = False
                    if linenumbers and line and not line.lstrip().startswith("#"):
                        if self.minify:
                            line += self.wrap_comment(str(ln))
                        else:
                            line += self.wrap_comment("line "+str(ln))
                except CoconutException:
                    if careful:
                        raise
                    fix = False
                out.append(line)
            return "\n".join(out)
        elif linenumbers:
            raise CoconutException("linenumbers must be enabled to pass it as an argument")
        else:
            return inputstring

    def passthrough_repl(self, inputstring, careful=True, **kwargs):
        """Adds back passthroughs."""
        out = []
        index = None
        for x in range(len(inputstring)+1):
            c = inputstring[x] if x != len(inputstring) else None
            try:
                if index is not None:
                    if c is not None and c in nums:
                        index += c
                    elif c == unwrapper and index:
                        ref = self.get_ref(index)
                        if not isinstance(ref, str):
                            raise CoconutException("invalid reference for a passthrough", ref)
                        out.append(ref)
                        index = None
                    elif c != "\\" or index:
                        out.append("\\" + index)
                        if c is not None:
                            out.append(c)
                        index = None
                elif c is not None:
                    if c == "\\":
                        index = ""
                    else:
                        out.append(c)
            except CoconutException:
                if careful:
                    raise
                if index is not None:
                    out.append(index)
                    index = None
                out.append(c)
        return "".join(out)

    def str_repl(self, inputstring, careful=True, **kwargs):
        """Adds back strings."""
        out = []
        comment = None
        string = None
        for x in range(len(inputstring)+1):
            c = inputstring[x] if x != len(inputstring) else None
            try:
                if comment is not None:
                    if c is not None and c in nums:
                        comment += c
                    elif c == unwrapper and comment:
                        ref = self.get_ref(comment)
                        if not isinstance(ref, str):
                            raise CoconutException("invalid reference for a comment", ref)
                        if out and not out[-1].endswith("\n"):
                            out.append(" ")
                        out.append("#" + ref)
                        comment = None
                    else:
                        raise CoconutException("invalid comment marker in", line(x, inputstring))
                elif string is not None:
                    if c is not None and c in nums:
                        string += c
                    elif c == unwrapper and string:
                        ref = self.get_ref(string)
                        if not isinstance(ref, tuple):
                            raise CoconutException("invalid reference for a str", ref)
                        text, strchar, multiline = ref
                        if multiline:
                            out.append(strchar*3 + text + strchar*3)
                        else:
                            out.append(strchar + text + strchar)
                        string = None
                    else:
                        raise CoconutException("invalid string marker in", line(x, inputstring))
                elif c is not None:
                    if c == "#":
                        comment = ""
                    elif c == strwrapper:
                        string = ""
                    else:
                        out.append(c)
            except CoconutException:
                if careful:
                    raise
                if comment is not None:
                    out.append(comment)
                    comment = None
                if string is not None:
                    out.append(string)
                    string = None
                out.append(c)
        return "".join(out)

    def repl_proc(self, inputstring, **kwargs):
        """Processes using replprocs."""
        for repl in self.replprocs:
            inputstring = repl(inputstring, **kwargs)
        return inputstring

    def header_proc(self, inputstring, header="file", initial="initial", usehash=None, **kwargs):
        """Adds the header."""
        pre_header = getheader(initial, self.target, usehash)
        main_header = getheader(header, self.target)
        if self.minify:
            main_header = minify(main_header)
        return pre_header + self.docstring + main_header + inputstring

    def polish(self, inputstring, **kwargs):
        """Does final polishing touches."""
        return "\n".join(inputstring.rstrip().splitlines()) + "\n"

    def autopep8(self, arglist=[]):
        """Enables autopep8 integration."""
        if self.using_autopep8:
            self.postprocs.pop()
        else:
            self.using_autopep8 = True
        import autopep8
        args = autopep8.parse_args(["autopep8"] + arglist)
        def pep8_fixer(code, **kwargs):
            """Automatic PEP8 fixer."""
            return autopep8.fix_code(code, options=args)
        self.postprocs.append(pep8_fixer)

#-----------------------------------------------------------------------------------------------------------------------
# PARSER HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------

    def set_docstring(self, original, location, tokens):
        """Sets the docstring."""
        if len(tokens) == 2:
            self.docstring = self.reformat(tokens[0]) + "\n\n"
            return tokens[1]
        else:
            raise CoconutException("invalid docstring tokens", tokens)

    def yield_from_handle(self, tokens):
        """Processes Python 3.3 yield from."""
        if len(tokens) != 1:
            raise CoconutException("invalid yield from tokens", tokens)
        elif self.target_info() < (3, 3):
            return (yield_from_var + " = " + tokens[0]
                + "\nfor " + yield_item_var + " in " + yield_from_var + ":\n"
                + openindent + "yield " + yield_item_var + "\n" + closeindent)
        else:
            return "yield from " + tokens[0]

    def endline_handle(self, original, location, tokens):
        """Inserts line number comments when in linenumbers mode."""
        if len(tokens) != 1:
            raise CoconutException("invalid endline tokens", tokens)
        out = tokens[0]
        if self.minify:
            out = out[0]
        if self.linenumbers:
            out = self.wrap_linenumber(self.adjust(lineno(location, original))) + out
        return out

    def item_handle(self, original, location, tokens):
        """Processes items."""
        out = tokens.pop(0)
        for trailer in tokens:
            if isinstance(trailer, str):
                out += trailer
            elif len(trailer) == 1:
                if trailer[0] == "$[]":
                    out = "_coconut.functools.partial(_coconut_igetitem, "+out+")"
                elif trailer[0] == "$":
                    out = "_coconut.functools.partial(_coconut.functools.partial, "+out+")"
                elif trailer[0] == "[]":
                    out = "_coconut.functools.partial(_coconut.operator.__getitem__, "+out+")"
                elif trailer[0] == ".":
                    out = "_coconut.functools.partial(_coconut.getattr, "+out+")"
                elif trailer[0] == "$(":
                    raise self.make_err(CoconutSyntaxError, "a partial application argument is required", original, location)
                else:
                    raise CoconutException("invalid trailer symbol", trailer[0])
            elif len(trailer) == 2:
                if trailer[0] == "$(":
                    out = "_coconut.functools.partial("+out+", "+trailer[1]+")"
                elif trailer[0] == "$[":
                    if 0 < len(trailer[1]) <= 3:
                        args = []
                        for x in range(0, len(trailer[1])):
                            arg = trailer[1][x]
                            if not arg:
                                arg = "None"
                            args.append(arg)
                        out = "_coconut_igetitem(" + out
                        if len(args) == 1:
                            out += ", " + args[0]
                        else:
                            out += ", _coconut.slice(" + ", ".join(args) + ")"
                        out += ")"
                    else:
                        raise CoconutException("invalid iterator slice args", trailer[1])
                elif trailer[0] == "..":
                    out = "_coconut_compose("+out+", "+trailer[1]+")"
                else:
                    raise CoconutException("invalid special trailer", trailer[0])
            else:
                raise CoconutException("invalid trailer tokens", trailer)
        return out

    def augassign_handle(self, tokens):
        """Processes assignments."""
        if len(tokens) == 3:
            name, op, item = tokens
            out = ""
            if op == "|>=":
                out += name+" = ("+item+")("+name+")"
            elif op == "|*>=":
                out += name+" = ("+item+")(*"+name+")"
            elif op == "<|=":
                out += name+" = "+name+"(("+item+"))"
            elif op == "<*|=":
                out += name+" = "+name+"(*("+item+"))"
            elif op == "..=":
                out += name+" = (lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)))("+name+", ("+item+"))"
            elif op == "::=":
                ichain_var = lazy_chain_var+"_"+str(self.ichain_count) # necessary to prevent a segfault caused by self-reference
                out += ichain_var+" = "+name+"\n"
                out += name+" = _coconut.itertools.chain.from_iterable("+lazy_list_handle([ichain_var, "("+item+")"])+")"
                self.ichain_count += 1
            else:
                out += name+" "+op+" "+item
            return out
        else:
            raise CoconutException("invalid assignment tokens", tokens)

    def classlist_handle(self, original, location, tokens):
        """Processes class inheritance lists."""
        if len(tokens) == 0:
            if self.target.startswith("3"):
                return ""
            else:
                return "(_coconut.object)"
        elif len(tokens) == 1 and len(tokens[0]) == 1:
            if "tests" in tokens[0]:
                return "(" + tokens[0][0] + ")"
            elif "args" in tokens[0]:
                if self.target.startswith("3"):
                    return "(" + tokens[0][0] + ")"
                else:
                    raise self.make_err(CoconutTargetError, ("found Python 3 keyword class definition", "3"), original, location)
            else:
                raise CoconutException("invalid inner classlist token", tokens[0])
        else:
            raise CoconutException("invalid classlist tokens", tokens)

    def import_handle(self, original, location, tokens):
        """Universalizes imports."""
        if len(tokens) == 1:
            imp_from, imports = None, tokens[0]
        elif len(tokens) == 2:
            imp_from, imports = tokens
            if imp_from == "__future__":
                raise self.make_err(CoconutSyntaxError, "illegal from __future__ import (Coconut does these automatically)", original, location)
        else:
            raise CoconutException("invalid import tokens", tokens)
        importmap = [] # [((imp | old_imp, imp, version_check), impas), ...]
        for imps in imports:
            if len(imps) == 1:
                imp, impas = imps[0], imps[0]
            else:
                imp, impas = imps
            if imp_from is not None:
                imp = imp_from + "./" + imp # marker for from ... import ...
            old_imp = None
            path = imp.split(".")
            for i in reversed(range(1, len(path)+1)):
                base, exts = ".".join(path[:i]), path[i:]
                clean_base = base.replace("/", "")
                if clean_base in new_to_old_stdlib:
                    old_imp, version_check = new_to_old_stdlib[clean_base]
                    if exts:
                        if "/" in base:
                            old_imp += "./"
                        else:
                            old_imp += "."
                        old_imp += ".".join(exts)
                    break
            if old_imp is None:
                paths = (imp,)
            elif self.target.startswith("2"):
                paths = (old_imp,)
            elif not self.target or self.target_info() < version_check:
                paths = (old_imp, imp, version_check)
            else:
                paths = (imp,)
            importmap.append((paths, impas))
        stmts = []
        for paths, impas in importmap:
            if len(paths) == 1:
                more_stmts = gen_imports(paths[0], impas)
                stmts.extend(more_stmts)
            else:
                first, second, version_check = paths
                stmts.append("if _coconut_sys.version_info < " + str(version_check) + ":")
                first_stmts = gen_imports(first, impas)
                first_stmts[0] = openindent + first_stmts[0]
                first_stmts[-1] += closeindent
                stmts.extend(first_stmts)
                stmts.append("else:")
                second_stmts = gen_imports(second, impas)
                second_stmts[0] = openindent + second_stmts[0]
                second_stmts[-1] += closeindent
                stmts.extend(second_stmts)
        return "\n".join(stmts)

    def complex_raise_stmt_handle(self, tokens):
        """Processes Python 3 raise from statement."""
        if len(tokens) != 2:
            raise CoconutException("invalid raise from tokens", tokens)
        elif self.target.startswith("3"):
            return "raise " + tokens[0] + " from " + tokens[1]
        else:
            return (raise_from_var + " = " + tokens[0] + "\n"
                + raise_from_var + ".__cause__ = " + tokens[1] + "\n"
                + "raise " + raise_from_var)

    def dict_comp_handle(self, original, location, tokens):
        """Processes Python 2.7 dictionary comprehension."""
        if len(tokens) != 3:
            raise CoconutException("invalid dictionary comprehension tokens", tokens)
        elif self.target.startswith("3"):
            key, val, comp = tokens
            return "{" + key + ": " + val + " " + comp + "}"
        else:
            key, val, comp = tokens
            return "dict(((" + key + "), (" + val + ")) " + comp + ")"

    def name_handle(self, original, location, tokens):
        """Handles variable names."""
        if len(tokens) != 1:
            raise CoconutException("invalid name tokens", tokens)
        elif tokens[0].startswith(reserved_prefix):
            if self.strict:
                raise self.make_err(CoconutStyleError, "found use of a reserved variable", original, location)
            else:
                self.warn(self.make_err(CoconutWarning, "found use of a reserved variable", original, location))
            return tokens[0]
        else:
            return tokens[0]

    def pattern_error(self, original, loc):
        """Constructs a pattern-matching error message."""
        base_line = clean(self.reformat(line(loc, original)))
        line_wrap = self.wrap_str_of(base_line)
        repr_wrap = self.wrap_str_of(ascii(base_line))
        return ("if not " + match_check_var + ":\n" + openindent
            + match_err_var + ' = _coconut_MatchError("pattern-matching failed for " '
            + repr_wrap + ' " in " + _coconut.repr(_coconut.repr(' + match_to_var + ")))\n"
            + match_err_var + ".pattern = " + line_wrap + "\n"
            + match_err_var + ".value = " + match_to_var
            + "\nraise " + match_err_var + "\n" + closeindent)

    def destructuring_stmt_handle(self, original, loc, tokens):
        """Processes match assign blocks."""
        if len(tokens) == 2:
            matches, item = tokens
            out = match_handle(original, loc, (matches, item, None))
            out += self.pattern_error(original, loc)
            return out
        else:
            raise CoconutException("invalid destructuring assignment tokens", tokens)

    def name_match_funcdef_handle(self, original, loc, tokens):
        """Processes match defs."""
        if len(tokens) == 2:
            func, matches = tokens
            cond = None
        elif len(tokens) == 3:
            func, matches, cond = tokens
        else:
            raise CoconutException("invalid match function definition tokens", tokens)
        matching = matcher()
        matching.match_sequence(("(", matches), match_to_var)
        if cond is not None:
            matching.add_guard(cond)
        out = "def " + func + " (*" + match_to_var + "):\n" + openindent
        out += match_check_var + " = False\n"
        out += matching.out()
        out += self.pattern_error(original, loc)
        return out

    def op_match_funcdef_handle(self, original, loc, tokens):
        """Processes infix match defs."""
        if len(tokens) == 3:
            name_tokens = get_infix_items(tokens)
        elif len(tokens) == 4:
            name_tokens = get_infix_items(tokens[:-1]) + tuple(tokens[-1:])
        else:
            raise CoconutException("invalid infix match function definition tokens", tokens)
        return self.name_match_funcdef_handle(original, loc, name_tokens)

    def check_strict(self, name, original, location, tokens):
        """Checks that syntax meets --strict requirements."""
        if len(tokens) != 1:
            raise CoconutException("invalid "+name+" tokens", tokens)
        elif self.strict:
            raise self.make_err(CoconutStyleError, "found "+name, original, location)
        else:
            return tokens[0]

    def lambdef_check(self, original, location, tokens):
        """Checks for Python-style lambdas."""
        return self.check_strict("Python-style lambda", original, location, tokens)

    def u_string_check(self, original, location, tokens):
        """Checks for Python2-style unicode strings."""
        return self.check_strict("Python-2-style unicode string", original, location, tokens)

    def check_py(self, version, name, original, location, tokens):
        """Checks for Python-version-specific syntax."""
        if len(tokens) != 1:
            raise CoconutException("invalid "+name+" tokens", tokens)
        elif self.target_info() < target_info(version):
            raise self.make_err(CoconutTargetError, ("found Python "+version+" " + name, version), original, location)
        else:
            return tokens[0]

    def typedef_check(self, original, location, tokens):
        """Checks for Python 3 type defs."""
        return self.check_py("3", "type annotation", original, location, tokens)

    def nonlocal_check(self, original, location, tokens):
        """Checks for Python 3 nonlocal statement."""
        return self.check_py("3", "nonlocal statement", original, location, tokens)

    def star_assign_item_check(self, original, location, tokens):
        """Checks for Python 3 starred assignment."""
        return self.check_py("3", "starred assignment", original, location, tokens)

    def matrix_at_check(self, original, location, tokens):
        """Checks for Python 3.5 matrix multiplication."""
        return self.check_py("35", "matrix multiplication", original, location, tokens)

    def async_stmt_check(self, original, location, tokens):
        """Checks for Python 3.5 async statement."""
        return self.check_py("35", "async statement", original, location, tokens)

    def await_keyword_check(self, original, location, tokens):
        """Checks for Python 3.5 await expression."""
        return self.check_py("35", "await expression", original, location, tokens)

    def f_string_check(self, original, location, tokens):
        """Checks for Python 3.5 format strings."""
        return self.check_py("36", "format string", original, location, tokens)

    def set_literal_handle(self, tokens):
        """Converts set literals to the right form for the target Python."""
        if len(tokens) != 1:
            raise CoconutException("invalid set literal tokens", tokens)
        elif len(tokens[0]) != 1:
            raise CoconutException("invalid set literal item", tokens[0])
        elif self.target_info() < (2, 7):
            return "_coconut.set(" + set_to_tuple(tokens[0]) + ")"
        else:
            return "{" + tokens[0][0] + "}"

    def set_letter_literal_handle(self, tokens):
        """Processes set literals."""
        if len(tokens) == 1:
            set_type = tokens[0]
            if set_type == "s":
                return "_coconut.set()"
            elif set_type == "f":
                return "_coconut.frozenset()"
            else:
                raise CoconutException("invalid set type", set_type)
        elif len(tokens) == 2:
            set_type, set_items = tokens
            if len(set_items) != 1:
                raise CoconutException("invalid set literal item", tokens[0])
            elif set_type == "s":
                return self.set_literal_handle([set_items])
            elif set_type == "f":
                return "_coconut.frozenset(" + set_to_tuple(set_items) + ")"
            else:
                raise CoconutException("invalid set type", set_type)
        else:
            raise CoconutException("invalid set literal tokens", tokens)

#-----------------------------------------------------------------------------------------------------------------------
# GRAMMAR:
#-----------------------------------------------------------------------------------------------------------------------

    comma = Literal(",")
    unsafe_dot = Literal(".")
    dot = ~Literal("..")+unsafe_dot
    dubstar = Literal("**")
    star = ~dubstar+Literal("*")
    at = Literal("@")
    arrow = Literal("->") | fixto(Literal("\u2192"), "->")
    dubcolon = Literal("::")
    unsafe_colon = Literal(":")
    colon = ~dubcolon+unsafe_colon
    semicolon = Literal(";")
    eq = Literal("==")
    equals = ~eq+Literal("=")
    lbrack = Literal("[")
    rbrack = Literal("]")
    lbrace = Literal("{")
    rbrace = Literal("}")
    lbanana = ~Literal("(|)")+~Literal("(|>)")+~Literal("(|*>)")+Literal("(|")
    rbanana = Literal("|)")
    lparen = ~lbanana+Literal("(")
    rparen = ~rbanana+Literal(")")
    plus = Literal("+")
    minus = ~Literal("->")+Literal("-")
    dubslash = Literal("//")
    slash = ~dubslash+Literal("/")
    pipeline = Literal("|>") | fixto(Literal("\u21a6"), "|>")
    starpipe = Literal("|*>") | fixto(Literal("*\u21a6"), "|*>")
    backpipe = Literal("<|") | fixto(Literal("\u21a4"), "<|")
    backstarpipe = Literal("<*|") | fixto(Literal("\u21a4*"), "<*|")
    amp = Literal("&") | fixto(Literal("\u2227") | Literal("\u2229"), "&")
    caret = Literal("^") | fixto(Literal("\u22bb") | Literal("\u2295"), "^")
    bar = ~Literal("|>")+~Literal("|*>")+Literal("|") | fixto(Literal("\u2228") | Literal("\u222a"), "|")
    percent = Literal("%")
    dotdot = ~Literal("...")+Literal("..") | fixto(Literal("\u2218"), "..")
    dollar = Literal("$")
    ellipses = fixto(Literal("...") | Literal("\u2026"), "...")
    lshift = Literal("<<") | fixto(Literal("\xab"), "<<")
    rshift = Literal(">>") | fixto(Literal("\xbb"), ">>")
    tilde = Literal("~") | fixto(~Literal("\xac=")+Literal("\xac"), "~")
    underscore = Literal("_")
    pound = Literal("#")
    backtick = Literal("`")
    dubbackslash = Literal("\\\\")
    backslash = ~dubbackslash+Literal("\\")

    lt = ~Literal("<<")+~Literal("<=")+Literal("<")
    gt = ~Literal(">>")+~Literal(">=")+Literal(">")
    le = Literal("<=") | fixto(Literal("\u2264"), "<=")
    ge = Literal(">=") | fixto(Literal("\u2265"), ">=")
    ne = Literal("!=") | fixto(Literal("\xac=") | Literal("\u2260"), "!=")

    mul_star = fixto(star | Literal("\u22c5"), "*")
    exp_dubstar = fixto(dubstar | Literal("\u2191"), "**")
    neg_minus = fixto(minus | Literal("\u207b"), "-")
    sub_minus = fixto(minus | Literal("\u2212"), "-")
    div_slash = fixto(slash | Literal("\xf7")+~slash, "/")
    div_dubslash = fixto(dubslash | Combine(Literal("\xf7")+slash), "//")
    matrix_at_ref = fixto(at | Literal("\xd7"), "@")
    matrix_at = Forward()

    name = Forward()
    name_ref = Regex(r"(?![0-9])\w+")
    for k in keywords + const_vars:
        name_ref = ~Keyword(k) + name_ref
    for k in reserved_vars:
        name_ref |= backslash.suppress() + Keyword(k)
    name_ref = condense(name_ref)
    dotted_name = condense(name + ZeroOrMore(dot + name))

    integer = Combine(Word(nums) + ZeroOrMore(underscore.suppress() + Word(nums)))
    binint = Combine(Word("01") + ZeroOrMore(underscore.suppress() + Word("01")))
    octint = Combine(Word("01234567") + ZeroOrMore(underscore.suppress() + Word("01234567")))
    hexint = Combine(Word(hexnums) + ZeroOrMore(underscore.suppress() + Word(hexnums)))

    basenum = Combine(integer + dot + Optional(integer) | Optional(integer) + dot + integer) | integer
    sci_e = Combine(CaselessLiteral("e") + Optional(plus | neg_minus))
    numitem = Combine(basenum + sci_e + integer) | basenum
    complex_i = CaselessLiteral("j") | fixto(CaselessLiteral("i"), "j")
    complex_num = Combine(numitem + complex_i)
    bin_num = Combine(CaselessLiteral("0b") + Optional(underscore.suppress()) + binint)
    oct_num = Combine(CaselessLiteral("0o") + Optional(underscore.suppress()) + octint)
    hex_num = Combine(CaselessLiteral("0x") + Optional(underscore.suppress()) + hexint)
    number = bin_num | oct_num | hex_num | complex_num | numitem

    moduledoc_item = Forward()
    unwrap = Literal(unwrapper)
    string_item = Combine(Literal(strwrapper) + integer + unwrap)
    comment = Combine(pound + integer + unwrap)
    passthrough = Combine(backslash + integer + unwrap)
    passthrough_block = Combine(fixto(dubbackslash, "\\", copy=True) + integer + unwrap)

    endline = Forward()
    endline_ref = condense(OneOrMore(Literal("\n")))
    lineitem = Combine(Optional(comment) + endline)
    newline = condense(OneOrMore(lineitem))
    start_marker = StringStart()
    moduledoc_marker = condense(ZeroOrMore(lineitem) - Optional(moduledoc_item))
    end_marker = StringEnd()
    indent = Literal(openindent)
    dedent = Literal(closeindent)

    u_string = Forward()
    f_string = Forward()
    bit_b = Optional(CaselessLiteral("b"))
    raw_r = Optional(CaselessLiteral("r"))
    b_string = Combine((bit_b + raw_r | raw_r + bit_b) + string_item)
    unicode_u = CaselessLiteral("u").suppress()
    u_string_ref = Combine((unicode_u + raw_r | raw_r + unicode_u) + string_item)
    format_f = CaselessLiteral("f")
    f_string_ref = Combine((format_f + raw_r | raw_r + format_f) + string_item)
    string = trace(b_string | u_string | f_string, "string")
    moduledoc = string + newline
    docstring = condense(moduledoc, copy=True)

    augassign = (
        Combine(pipeline + equals)
        | Combine(starpipe + equals)
        | Combine(backpipe + equals)
        | Combine(backstarpipe + equals)
        | Combine(dotdot + equals)
        | Combine(dubcolon + equals)
        | Combine(div_dubslash + equals)
        | Combine(div_slash + equals)
        | Combine(exp_dubstar + equals)
        | Combine(mul_star + equals)
        | Combine(plus + equals)
        | Combine(sub_minus + equals)
        | Combine(percent + equals)
        | Combine(amp + equals)
        | Combine(bar + equals)
        | Combine(caret + equals)
        | Combine(lshift + equals)
        | Combine(rshift + equals)
        | Combine(matrix_at + equals)
        )

    comp_op = (le | ge | ne | lt | gt | eq
               | addspace(Keyword("not") + Keyword("in"))
               | Keyword("in")
               | addspace(Keyword("is") + Keyword("not"))
               | Keyword("is")
               )

    test = Forward()
    expr = Forward()
    comp_for = Forward()
    test_nochain = Forward()
    test_nocond = Forward()

    testlist = itemlist(test, comma)
    multi_testlist = addspace(OneOrMore(condense(test + comma)) + Optional(test))

    yield_from = Forward()
    dict_comp = Forward()
    yield_classic = addspace(Keyword("yield") + testlist)
    yield_from_ref = Keyword("yield").suppress() + Keyword("from").suppress() + test
    yield_expr = yield_from | yield_classic
    dict_comp_ref = lbrace.suppress() + test + colon.suppress() + test + comp_for + rbrace.suppress()
    dict_item = condense(lbrace + Optional(itemlist(addspace(condense(test + colon) + test), comma)) + rbrace)
    test_expr = yield_expr | testlist

    op_item = (
        fixto(pipeline, "_coconut_pipe", copy=True)
        | fixto(starpipe, "_coconut_starpipe", copy=True)
        | fixto(backpipe, "_coconut_backpipe", copy=True)
        | fixto(backstarpipe, "_coconut_backstarpipe", copy=True)
        | fixto(dotdot, "_coconut_compose", copy=True)
        | fixto(Keyword("and"), "_coconut_bool_and", copy=True)
        | fixto(Keyword("or"), "_coconut_bool_or", copy=True)
        | fixto(minus, "_coconut_minus", copy=True)
        | fixto(dot, "_coconut.getattr", copy=True)
        | fixto(dubcolon, "_coconut.itertools.chain", copy=True)
        | fixto(dollar, "_coconut.functools.partial", copy=True)
        | fixto(exp_dubstar, "_coconut.operator.__pow__", copy=True)
        | fixto(mul_star, "_coconut.operator.__mul__", copy=True)
        | fixto(div_dubslash, "_coconut.operator.__floordiv__", copy=True)
        | fixto(div_slash, "_coconut.operator.__truediv__", copy=True)
        | fixto(percent, "_coconut.operator.__mod__", copy=True)
        | fixto(plus, "_coconut.operator.__add__", copy=True)
        | fixto(amp, "_coconut.operator.__and__", copy=True)
        | fixto(caret, "_coconut.operator.__xor__", copy=True)
        | fixto(bar, "_coconut.operator.__or__", copy=True)
        | fixto(lshift, "_coconut.operator.__lshift__", copy=True)
        | fixto(rshift, "_coconut.operator.__rshift__", copy=True)
        | fixto(lt, "_coconut.operator.__lt__", copy=True)
        | fixto(gt, "_coconut.operator.__gt__", copy=True)
        | fixto(eq, "_coconut.operator.__eq__", copy=True)
        | fixto(le, "_coconut.operator.__le__", copy=True)
        | fixto(ge, "_coconut.operator.__ge__", copy=True)
        | fixto(ne, "_coconut.operator.__ne__", copy=True)
        | fixto(tilde, "_coconut.operator.__inv__", copy=True)
        | fixto(matrix_at, "_coconut.operator.__matmul__", copy=True)
        | fixto(Keyword("not"), "_coconut.operator.__not__", copy=True)
        | fixto(Keyword("is"), "_coconut.operator.is_", copy=True)
        | fixto(Keyword("in"), "_coconut.operator.__contains__", copy=True)
    )
    op_atom = lparen.suppress() + op_item + rparen.suppress()

    typedef = Forward()
    typedef_ref = addspace(condense(name + colon) + test)
    tfpdef = typedef | name
    callarg = test
    default = Optional(condense(equals + test))

    argslist = Optional(itemlist(condense(dubstar + tfpdef | star + tfpdef | tfpdef + default), comma))
    varargslist = Optional(itemlist(condense(dubstar + name | star + name | name + default), comma))
    callargslist = Optional(
        attach(addspace(test + comp_for), add_paren_handle)
        | itemlist(condense(dubstar + callarg | star + callarg | callarg + default), comma)
        | op_item
        )
    parameters = condense(lparen + argslist + rparen)

    testlist_comp = addspace(test + comp_for) | testlist
    list_comp = condense(lbrack + Optional(testlist_comp) + rbrack)
    func_atom = name | op_atom | condense(lparen + Optional(yield_expr | testlist_comp) + rparen)
    keyword_atom = Keyword(const_vars[0])
    for x in range(1, len(const_vars)):
        keyword_atom |= Keyword(const_vars[x])
    string_atom = addspace(OneOrMore(string))
    passthrough_atom = addspace(OneOrMore(passthrough))
    methodcaller_args = itemlist(condense(callarg + default), comma) | op_item
    attr_atom = attach(dot.suppress() + name + Optional(lparen.suppress() + methodcaller_args + rparen.suppress()), attr_handle)
    set_literal = Forward()
    set_letter_literal = Forward()
    set_s = fixto(CaselessLiteral("s"), "s")
    set_f = fixto(CaselessLiteral("f"), "f")
    set_letter = set_s | set_f
    setmaker = Group(addspace(test + comp_for)("comp") | multi_testlist("list") | test("test"))
    set_literal_ref = lbrace.suppress() + setmaker + rbrace.suppress()
    set_letter_literal_ref = set_letter + lbrace.suppress() + Optional(setmaker) + rbrace.suppress()
    lazy_items = Optional(test + ZeroOrMore(comma.suppress() + test) + Optional(comma.suppress()))
    lazy_list = attach(lbanana.suppress() + lazy_items + rbanana.suppress(), lazy_list_handle)
    const_atom = (
        keyword_atom
        | number
        | string_atom
        )
    known_atom = (
        const_atom
        | ellipses
        | attr_atom
        | list_comp
        | dict_comp
        | dict_item
        | set_literal
        | set_letter_literal
        | lazy_list
        )
    atom = trace(
        known_atom
        | passthrough_atom
        | func_atom
        , "atom")

    slicetest = Optional(test_nochain)
    sliceop = condense(unsafe_colon + slicetest)
    subscript = condense(slicetest + sliceop + Optional(sliceop)) | test
    subscriptlist = itemlist(subscript, comma)
    slicetestgroup = Optional(test_nochain, default="")
    sliceopgroup = unsafe_colon.suppress() + slicetestgroup
    subscriptgroup = Group(slicetestgroup + sliceopgroup + Optional(sliceopgroup) | test)
    simple_trailer = condense(lbrack + subscriptlist + rbrack) | condense(dot + name)
    complex_trailer = (
        Group(condense(dollar + lparen) + callargslist + rparen.suppress())
        | condense(lparen + callargslist + rparen)
        | Group(dotdot + func_atom)
        | Group(condense(dollar + lbrack) + subscriptgroup + rbrack.suppress())
        | Group(condense(dollar + lbrack + rbrack))
        | Group(dollar)
        | Group(condense(lbrack + rbrack))
        | Group(dot)
        )
    trailer = simple_trailer | complex_trailer

    atom_item = Forward()
    atom_item_ref = atom + ZeroOrMore(trailer)
    simple_assign = Forward()
    simple_assign_ref = (name | passthrough_atom) + ZeroOrMore(ZeroOrMore(~simple_trailer+complex_trailer) + OneOrMore(simple_trailer))

    assignlist = Forward()
    star_assign_item = Forward()
    simple_assignlist = parenwrap(lparen, itemlist(simple_assign, comma), rparen)
    base_assign_item = condense(simple_assign | lparen + assignlist + rparen | lbrack + assignlist + rbrack)
    star_assign_item_ref = condense(star + base_assign_item)
    assign_item = star_assign_item | base_assign_item
    assignlist <<= itemlist(assign_item, comma)

    factor = Forward()
    await_keyword = Forward()
    await_keyword_ref = Keyword("await")
    power = trace(condense(addspace(Optional(await_keyword) + atom_item) + Optional(exp_dubstar + factor)), "power")
    unary = plus | neg_minus | tilde

    factor <<= trace(condense(ZeroOrMore(unary) + power), "factor")

    mulop = mul_star | div_dubslash | div_slash | percent | matrix_at
    term = addspace(factor + ZeroOrMore(mulop + factor))
    arith = plus | sub_minus
    arith_expr = addspace(term + ZeroOrMore(arith + term))

    shift = lshift | rshift
    shift_expr = addspace(arith_expr + ZeroOrMore(shift + arith_expr))
    and_expr = addspace(shift_expr + ZeroOrMore(amp + shift_expr))
    xor_expr = addspace(and_expr + ZeroOrMore(caret + and_expr))
    or_expr = addspace(xor_expr + ZeroOrMore(bar + xor_expr))

    chain_expr = attach(or_expr + ZeroOrMore(dubcolon.suppress() + or_expr), chain_handle)

    infix_expr = Forward()
    infix_op = condense(backtick.suppress() + chain_expr + backtick.suppress())
    infix_item = attach(Group(Optional(chain_expr)) + infix_op + Group(Optional(infix_expr)), infix_handle)
    infix_expr <<= infix_item | chain_expr
    nochain_infix_expr = Forward()
    nochain_infix_item = attach(Group(Optional(or_expr)) + infix_op + Group(Optional(nochain_infix_expr)), infix_handle)
    nochain_infix_expr <<= nochain_infix_item | or_expr

    pipe_op = pipeline | starpipe | backpipe | backstarpipe
    pipe_expr = attach(infix_expr + ZeroOrMore(pipe_op + infix_expr), pipe_handle)
    nochain_pipe_expr = attach(nochain_infix_expr + ZeroOrMore(pipe_op + nochain_infix_expr), pipe_handle)

    expr <<= trace(pipe_expr, "expr")
    comparison = addspace(expr + ZeroOrMore(comp_op + expr))
    not_test = addspace(ZeroOrMore(Keyword("not")) + comparison)
    and_test = addspace(not_test + ZeroOrMore(Keyword("and") + not_test))
    or_test = addspace(and_test + ZeroOrMore(Keyword("or") + and_test))
    test_item = trace(or_test, "test_item")
    nochain_expr = trace(nochain_pipe_expr, "nochain_expr")
    nochain_comparison = addspace(nochain_expr + ZeroOrMore(comp_op + nochain_expr))
    nochain_not_test = addspace(ZeroOrMore(Keyword("not")) + nochain_comparison)
    nochain_and_test = addspace(nochain_not_test + ZeroOrMore(Keyword("and") + nochain_not_test))
    nochain_or_test = addspace(nochain_and_test + ZeroOrMore(Keyword("or") + nochain_and_test))
    nochain_test_item = trace(nochain_or_test, "nochain_test_item")

    classic_lambdef = Forward()
    classic_lambdef_params = parenwrap(lparen, varargslist, rparen)
    new_lambdef_params = lparen.suppress() + varargslist + rparen.suppress()
    classic_lambdef_ref = addspace(Keyword("lambda") + condense(classic_lambdef_params + colon))
    new_lambdef = attach(new_lambdef_params + arrow.suppress(), lambdef_handle)
    implicit_lambdef = fixto(arrow, "lambda _=None:")
    lambdef_base = classic_lambdef | new_lambdef | implicit_lambdef
    lambdef = trace(addspace(lambdef_base + test), "lambdef")
    lambdef_nocond = trace(addspace(lambdef_base + test_nocond), "lambdef_nocond")
    lambdef_nochain = trace(addspace(lambdef_base + test_nochain), "lambdef_nochain")

    test <<= lambdef | addspace(test_item + Optional(Keyword("if") + test_item + Keyword("else") + test))
    test_nocond <<= lambdef_nocond | test_item
    test_nochain <<= lambdef_nochain | addspace(nochain_test_item + Optional(Keyword("if") + nochain_test_item + Keyword("else") + test_nochain))

    simple_stmt = Forward()
    simple_compound_stmt = Forward()
    stmt = Forward()
    suite = Forward()
    base_suite = Forward()
    classlist = Forward()

    classlist_ref = Optional(
        lparen.suppress() + rparen.suppress()
        | Group(
            lparen.suppress() + testlist("tests") + rparen.suppress()
            | lparen.suppress() + callargslist("args") + rparen.suppress()
            )
        )
    classdef = condense(addspace(Keyword("class") - name) + classlist + suite)
    comp_iter = Forward()
    comp_for <<= addspace(Keyword("for") + assignlist + Keyword("in") + test_item + Optional(comp_iter))
    comp_if = addspace(Keyword("if") + test_nocond + Optional(comp_iter))
    comp_iter <<= comp_for | comp_if

    complex_raise_stmt = Forward()
    pass_stmt = Keyword("pass")
    break_stmt = Keyword("break")
    continue_stmt = Keyword("continue")
    return_stmt = addspace(Keyword("return") - Optional(testlist))
    simple_raise_stmt = addspace(Keyword("raise") + Optional(test))
    complex_raise_stmt_ref = Keyword("raise").suppress() + test + Keyword("from").suppress() - test
    raise_stmt = complex_raise_stmt | simple_raise_stmt
    flow_stmt = break_stmt | continue_stmt | return_stmt | raise_stmt | yield_expr

    dotted_as_name = Group(dotted_name - Optional(Keyword("as").suppress() - name))
    import_as_name = Group(name - Optional(Keyword("as").suppress() - name))
    import_names = Group(parenwrap(lparen, tokenlist(dotted_as_name, comma), rparen, tokens=True))
    import_from_names = Group(parenwrap(lparen, tokenlist(import_as_name, comma), rparen, tokens=True))
    import_name = Keyword("import").suppress() - import_names
    import_from = (Keyword("from").suppress()
        - condense(ZeroOrMore(unsafe_dot) + dotted_name | OneOrMore(unsafe_dot))
        - Keyword("import").suppress() - (Group(star) | import_from_names))
    import_stmt = Forward()
    import_stmt_ref = import_from | import_name

    nonlocal_stmt = Forward()
    namelist = parenwrap(lparen, itemlist(name, comma), rparen)
    global_stmt = addspace(Keyword("global") - namelist)
    nonlocal_stmt_ref = addspace(Keyword("nonlocal") - namelist)
    del_stmt = addspace(Keyword("del") - simple_assignlist)
    with_item = addspace(test - Optional(Keyword("as") - name))

    match = Forward()
    matchlist_list = Group(Optional(tokenlist(match, comma)))
    matchlist_tuple = Group(Optional(match + OneOrMore(comma.suppress() + match) + Optional(comma.suppress()) | match + comma.suppress()))
    match_const = const_atom | condense(equals.suppress() + atom_item)
    matchlist_set = Group(Optional(tokenlist(match_const, comma)))
    match_pair = Group(match_const + colon.suppress() + match)
    matchlist_dict = Group(Optional(tokenlist(match_pair, comma)))
    match_list = lbrack + matchlist_list + rbrack.suppress()
    match_tuple = lparen + matchlist_tuple + rparen.suppress()
    match_lazy = lbanana + matchlist_list + rbanana.suppress()
    base_match = Group(
        match_const("const")
        | (lparen.suppress() + match + rparen.suppress())("paren")
        | (lbrace.suppress() + matchlist_dict + rbrace.suppress())("dict")
        | (Optional(set_s.suppress()) + lbrace.suppress() + matchlist_set + rbrace.suppress())("set")
        | ((match_list | match_tuple | match_lazy) + dubcolon.suppress() + name)("iter")
        | match_lazy("iter")
        | (match_list + plus.suppress() + name + plus.suppress() + match_list)("mseries")
        | (match_tuple + plus.suppress() + name + plus.suppress() + match_tuple)("mseries")
        | ((match_list | match_tuple) + Optional(plus.suppress() + name))("series")
        | (name + plus.suppress() + (match_list | match_tuple))("rseries")
        | (name + lparen.suppress() + matchlist_list + rparen.suppress())("data")
        | name("var")
        )
    matchlist_trailer = base_match + OneOrMore(Keyword("as") + name | Keyword("is") + atom_item)
    as_match = Group(matchlist_trailer("trailer")) | base_match
    matchlist_and = as_match + OneOrMore(Keyword("and").suppress() + as_match)
    and_match = Group(matchlist_and("and")) | as_match
    matchlist_or = and_match + OneOrMore(Keyword("or").suppress() + and_match)
    or_match = Group(matchlist_or("or")) | and_match
    match <<= trace(or_match, "match")

    else_suite = condense(colon + trace(attach(simple_compound_stmt, else_handle, copy=True), "else_suite")) | suite
    else_stmt = condense(Keyword("else") - else_suite)

    match_guard = Optional(Keyword("if").suppress() + test)
    full_suite = colon.suppress() + Group((newline.suppress() + indent.suppress() + OneOrMore(stmt) + dedent.suppress()) | simple_stmt)
    full_match = trace(attach(
        Keyword("match").suppress() + match + Keyword("in").suppress() - test - match_guard - full_suite
        , match_handle), "full_match")
    match_stmt = condense(full_match - Optional(else_stmt))

    destructuring_stmt = Forward()
    destructuring_stmt_ref = match + equals.suppress() - test_expr - newline.suppress()
    match_assign_stmt = Keyword("match").suppress() + destructuring_stmt

    case_match = trace(Group(
        Keyword("match").suppress() - match - Optional(Keyword("if").suppress() - test) - full_suite
        ), "case_match")
    case_stmt = attach(
        Keyword("case").suppress() + test - colon.suppress() - newline.suppress()
        - indent.suppress() - Group(OneOrMore(case_match))
        - dedent.suppress() - Optional(Keyword("else").suppress() - else_suite)
        , case_handle)

    assert_stmt = addspace(Keyword("assert") - testlist)
    if_stmt = condense(addspace(Keyword("if") - condense(test - suite))
                       - ZeroOrMore(addspace(Keyword("elif") - condense(test - suite)))
                       - Optional(else_stmt)
                       )
    while_stmt = addspace(Keyword("while") - condense(test - suite - Optional(else_stmt)))
    for_stmt = addspace(Keyword("for") - assignlist - Keyword("in") - condense(testlist - suite - Optional(else_stmt)))
    except_clause = attach(Keyword("except").suppress() + (
            multi_testlist("list") | test("test")
        ) - Optional(Keyword("as").suppress() - name), except_handle)
    try_stmt = condense(Keyword("try") - suite + (
        Keyword("finally") - suite
        | (
            OneOrMore(except_clause - suite) - Optional(Keyword("except") - suite)
            | Keyword("except") - suite
          ) - Optional(else_stmt) - Optional(Keyword("finally") - suite)
        ))
    with_stmt = addspace(Keyword("with") - condense(itemlist(with_item, comma) - suite))

    return_typedef = Forward()
    async_funcdef = Forward()
    async_block = Forward()
    name_funcdef = condense(name + parameters)
    op_funcdef_arg = name | condense(lparen.suppress() + tfpdef + Optional(default) + rparen.suppress())
    op_funcdef_name = backtick.suppress() + name + backtick.suppress()
    op_funcdef = attach(Group(Optional(op_funcdef_arg)) + op_funcdef_name + Group(Optional(op_funcdef_arg)), op_funcdef_handle)
    return_typedef_ref = addspace(arrow + test)
    base_funcdef = addspace((op_funcdef | name_funcdef) + Optional(return_typedef))
    funcdef = addspace(Keyword("def") + condense(base_funcdef + suite))
    math_funcdef = attach(Keyword("def").suppress() + base_funcdef + equals.suppress() - test_expr, func_handle) - newline
    async_funcdef_ref = addspace(Keyword("async") + (funcdef | math_funcdef))
    async_block_ref = addspace(Keyword("async") + (with_stmt | for_stmt))

    name_match_funcdef = Forward()
    op_match_funcdef = Forward()
    async_match_funcdef = Forward()
    name_match_funcdef_ref = name + lparen.suppress() + matchlist_list + match_guard + rparen.suppress()
    op_match_funcdef_arg = lparen.suppress() + match + rparen.suppress()
    op_match_funcdef_ref = Group(Optional(op_match_funcdef_arg)) + op_funcdef_name + Group(Optional(op_match_funcdef_arg)) + match_guard
    base_match_funcdef = Keyword("def").suppress() + (op_match_funcdef | name_match_funcdef)
    full_match_funcdef = trace(attach(base_match_funcdef + full_suite, full_match_funcdef_handle), "base_match_funcdef")
    math_match_funcdef = attach(
        Optional(Keyword("match").suppress()) + base_match_funcdef + equals.suppress() - test_expr
        , match_func_handle) - newline
    match_funcdef = Optional(Keyword("match").suppress()) + full_match_funcdef
    async_match_funcdef_ref = addspace(
        (Optional(Keyword("match")).suppress() + Keyword("async") | Keyword("async") + Optional(Keyword("match")).suppress())
        + (full_match_funcdef | math_match_funcdef))
    async_stmt = async_block | async_funcdef | async_match_funcdef_ref

    data_args = Optional(lparen.suppress() + Optional(itemlist(~underscore + name, comma)) + rparen.suppress())
    data_suite = colon.suppress() - Group(
        (newline.suppress() + indent.suppress() + Optional(docstring) + Group(OneOrMore(stmt)) + dedent.suppress())("complex")
        | (newline.suppress() + indent.suppress() + docstring + dedent.suppress() | docstring)("docstring")
        | simple_stmt("simple"))
    datadef = condense(attach(Keyword("data").suppress() + name - data_args - data_suite, data_handle))

    simple_decorator = condense(dotted_name + Optional(lparen + callargslist + rparen))("simple")
    complex_decorator = test("test")
    decorators = attach(OneOrMore(at.suppress() - Group(simple_decorator ^ complex_decorator) - newline.suppress()), decorator_handle)
    decoratable_stmt = (
        classdef
        | datadef
        | funcdef
        | async_funcdef
        | async_match_funcdef
        | match_funcdef
        | math_funcdef
        | math_match_funcdef
        )
    decorated = condense(decorators - decoratable_stmt)

    passthrough_stmt = condense(passthrough_block - (base_suite | newline))

    simple_compound_stmt <<= (
        if_stmt
        | try_stmt
        | case_stmt
        | match_stmt
        | passthrough_stmt
        )
    compound_stmt = trace(
        decoratable_stmt
        | with_stmt
        | while_stmt
        | for_stmt
        | async_stmt
        | simple_compound_stmt
        | decorated
        | match_assign_stmt
        , "compound_stmt")
    keyword_stmt = (
        del_stmt
        | pass_stmt
        | flow_stmt
        | import_stmt
        | global_stmt
        | nonlocal_stmt
        | assert_stmt
        )
    augassign_stmt = Forward()
    augassign_stmt_ref = simple_assign + augassign + test_expr
    expr_stmt = trace(addspace(
                      augassign_stmt
                      | ZeroOrMore(assignlist + equals) + test_expr
                      ), "expr_stmt")

    small_stmt = trace(keyword_stmt | expr_stmt, "small_stmt")
    simple_stmt <<= trace(condense(itemlist(small_stmt, semicolon) + newline), "simple_stmt")
    stmt <<= trace(compound_stmt | simple_stmt | destructuring_stmt, "stmt")
    base_suite <<= condense(newline + indent - OneOrMore(stmt) - dedent)
    suite <<= trace(condense(colon + base_suite) | addspace(colon + simple_stmt), "suite")
    line = trace(newline | stmt, "line")

    single_input = trace(condense(Optional(line) - ZeroOrMore(newline)), "single_input")
    file_input = trace(condense(moduledoc_marker - ZeroOrMore(line)), "file_input")
    eval_input = trace(condense(testlist - ZeroOrMore(newline)), "eval_input")

    single_parser = condense(start_marker - single_input - end_marker)
    file_parser = condense(start_marker - file_input - end_marker)
    eval_parser = condense(start_marker - eval_input - end_marker)

#-----------------------------------------------------------------------------------------------------------------------
# ENDPOINTS:
#-----------------------------------------------------------------------------------------------------------------------

    def parse_single(self, inputstring):
        """Parses line code."""
        return self.parse(inputstring, self.single_parser, {}, {"header": "none", "initial": "none"})

    def parse_file(self, inputstring, addhash=True):
        """Parses file code."""
        if addhash:
            usehash = self.genhash(False, inputstring)
        else:
            usehash = None
        return self.parse(inputstring, self.file_parser, {}, {"header": "file", "usehash": usehash})

    def parse_exec(self, inputstring):
        """Parses exec code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "file", "initial": "none"})

    def parse_module(self, inputstring, addhash=True):
        """Parses module code."""
        if addhash:
            usehash = self.genhash(True, inputstring)
        else:
            usehash = None
        return self.parse(inputstring, self.file_parser, {}, {"header": "module", "usehash": usehash})

    def parse_block(self, inputstring):
        """Parses block code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "none", "initial": "none"})

    def parse_eval(self, inputstring):
        """Parses eval code."""
        return self.parse(inputstring, self.eval_parser, {"strip": True}, {"header": "none", "initial": "none"})

    def parse_debug(self, inputstring):
        """Parses debug code."""
        return self.parse(inputstring, self.file_parser, {"strip": True}, {"header": "none", "initial": "none"})
